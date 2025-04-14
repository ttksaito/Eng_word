import streamlit as st
import pandas as pd
from gtts import gTTS
import tempfile
import os
import datetime
from io import BytesIO


st.title("📚 英語例文学習アプリ")
excel_file = "duo3.xlsx"

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file).dropna(how='all').reset_index(drop=True)
    
    # 初期化
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    if 'current_example_idx' not in st.session_state:
        st.session_state.current_example_idx = 0
    if 'answer_visible' not in st.session_state:  # キー名を変更
        st.session_state.answer_visible = False
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'incorrect_count' not in st.session_state:
        st.session_state.incorrect_count = 0
    
    # セクション選択画面
    if st.session_state.selected_section is None:
        st.subheader("勉強するセクションの選択")
        
        # セクションごとの統計情報を表示
        sections = df['Section'].unique()
        
        # セクション情報をテーブルで表示
        section_data = []
        for section in sections:
            section_examples = df[df['Section'] == section]
            example_count = len(section_examples)
            
            # 最新の学習日と正答率を取得
            last_study_date = None
            correct_rate = None
            
            if 'Section' in df.columns and '学習日' in df.columns:
                section_df = df[df['Section'] == section]
                if not section_df.empty and '学習日' in section_df.columns and not pd.isna(section_df['学習日'].iloc[0]):
                    last_study_date = section_df['学習日'].iloc[0]
                    
                    if '正答数' in section_df.columns and '誤答数' in section_df.columns:
                        total_correct = section_df['正答数'].sum()
                        total_attempts = total_correct + section_df['誤答数'].sum()
                        
                        if total_attempts > 0:
                            correct_rate = (total_correct / total_attempts) * 100
            
            section_data.append({
                "Section": f"Section {int(section)}",
                "例文数": example_count,
                "学習日": last_study_date.strftime("%Y/%m/%d/%a") if last_study_date else "",
                "正答率": f"{correct_rate:.1f}%" if correct_rate is not None else ""
            })
        
        section_df = pd.DataFrame(section_data)
        st.table(section_df)
        
        # セクション選択
        selected_section_num = st.selectbox(
            "学習するセクションを選択してください:",
            options=sections,
            format_func=lambda x: f"Section {int(x)}"
        )
        
        if st.button("学習開始"):
            st.session_state.selected_section = selected_section_num
            st.session_state.current_example_idx = 0
            st.session_state.answer_visible = False  # 変数名を変更
            st.rerun()
    
    # 例文学習画面
    else:
        # 選択されたセクションの例文を取得
        section_examples = df[df['Section'] == st.session_state.selected_section].reset_index(drop=True)
        
        # 全ての例文が終了したかチェック
        if st.session_state.current_example_idx >= len(section_examples):
            st.success("🎉 このセクションの全ての例文を完了しました！")
            
            # 学習データを保存
            today = datetime.datetime.now()
            for i, row in section_examples.iterrows():
                idx = df[(df['Section'] == st.session_state.selected_section) & 
                         (df['見出しNo'] == row['見出しNo'])].index
                if len(idx) > 0:
                    df.loc[idx[0], '学習日'] = today
            
            df.to_excel(excel_file, index=False)
            
            if st.button("セクション選択に戻る"):
                st.session_state.selected_section = None
                st.session_state.current_example_idx = 0
                st.session_state.answer_visible = False  # 変数名を変更
                st.session_state.correct_count = 0
                st.session_state.incorrect_count = 0
                st.rerun()
        else:
            # ヘッダー
            cols = st.columns([3, 1])
            with cols[0]:
                st.subheader(f"Section {int(st.session_state.selected_section)} - 例文 {st.session_state.current_example_idx + 1}/{len(section_examples)}")
            with cols[1]:
                st.markdown('<div style="text-align: right; width: 100%;">', unsafe_allow_html=True)
                if st.button("セクション選択に戻る", key="back_to_sections"):
                    st.session_state.selected_section = None
                    st.session_state.current_example_idx = 0
                    st.session_state.answer_visible = False  # 変数名を変更
                    st.session_state.correct_count = 0
                    st.session_state.incorrect_count = 0
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            current_example = section_examples.iloc[st.session_state.current_example_idx]
            sentence = current_example['例文']
            
            # 音声再生
            # with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            #     tts = gTTS(sentence, lang='en')
            #     tts.save(fp.name)
            #     temp_filename = fp.name
                
            audio_col, button_col = st.columns([1, 1])

            with audio_col:
                # gTTSでメモリ上に音声生成
                tts = gTTS(sentence, lang='en')
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)

                st.audio(audio_bytes, format='audio/mp3')
            
            # with audio_col:
            #     with open(temp_filename, "rb") as audio_file:
            #         st.audio(audio_file.read(), format='audio/mp3')
            
            # 回答表示ボタン - キー名と変数名を異なるものにする
            with button_col:
                st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;">', unsafe_allow_html=True)
                if st.button("回答表示", key="display_answer_button"):  # キー名を変更
                    st.session_state.answer_visible = True  # 変数名を変更
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # # 一時ファイルの削除
            # try:
            #     os.unlink(temp_filename)
            # except:
            #     pass
            
            # 回答表示
            if st.session_state.answer_visible:  # 変数名を変更
                st.write(sentence)
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("正解", key="correct_button"):
                        st.session_state.correct_count += 1
                        idx = df[(df['Section'] == st.session_state.selected_section) & 
                                 (df['見出しNo'] == current_example['見出しNo'])].index
                        if len(idx) > 0:
                            if '正答数' not in df:
                                df['正答数'] = 0
                            df.loc[idx[0], '正答数'] = df.loc[idx[0], '正答数'] + 1 if not pd.isna(df.loc[idx[0], '正答数']) else 1
                        df.to_excel(excel_file, index=False)
                        st.session_state.current_example_idx += 1
                        st.session_state.answer_visible = False  # 変数名を変更
                        st.rerun()
                
                with col2:
                    if st.button("不正解", key="incorrect_button"):
                        st.session_state.incorrect_count += 1
                        idx = df[(df['Section'] == st.session_state.selected_section) & 
                                 (df['見出しNo'] == current_example['見出しNo'])].index
                        if len(idx) > 0:
                            if '誤答数' not in df:
                                df['誤答数'] = 0
                            df.loc[idx[0], '誤答数'] = df.loc[idx[0], '誤答数'] + 1 if not pd.isna(df.loc[idx[0], '誤答数']) else 1
                        df.to_excel(excel_file, index=False)
                        st.session_state.current_example_idx += 1
                        st.session_state.answer_visible = False  # 変数名を変更
                        st.rerun()
            
            # 学習状況
            st.sidebar.header("学習状況")
            st.sidebar.write(f"学習中のセクション: Section {int(st.session_state.selected_section)}")
            st.sidebar.write(f"進捗: {st.session_state.current_example_idx}/{len(section_examples)}")
            
            total = st.session_state.correct_count + st.session_state.incorrect_count
            correct_rate = (st.session_state.correct_count / total * 100) if total > 0 else 0
            
            st.sidebar.write(f"正解数: {st.session_state.correct_count}")
            st.sidebar.write(f"不正解数: {st.session_state.incorrect_count}")
            st.sidebar.write(f"正答率: {correct_rate:.1f}%")
            
            # プログレスバー
            progress = st.session_state.current_example_idx / len(section_examples)
            st.sidebar.progress(progress)
else:
    st.error("ファイル「duo3.xlsx」が同じフォルダに存在しません。ファイルを置いてください。")
