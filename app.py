import streamlit as st
import pandas as pd
from gtts import gTTS
import random
import tempfile
import os

st.title("📚 単語学習アプリ")
excel_file = "duo 3.0.xlsx"

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file).dropna(how='all').reset_index(drop=True)
    
    # 初期化
    for key in ['sentence_idx', 'word_idx', 'answered', 'selected_answer', 'choices', 'is_correct']:
        if key not in st.session_state:
            st.session_state[key] = None
    
    if st.session_state.sentence_idx is None:
        st.session_state.sentence_idx = 0
        st.session_state.word_idx = 1
        st.session_state.answered = False
        st.session_state.selected_answer = ""
        st.session_state.choices = []
        st.session_state.is_correct = False
    
    sentence_idx = st.session_state.sentence_idx
    word_idx = st.session_state.word_idx
    max_word_idx = (len(df.columns) - 2) // 2
    
    # 全ての英文が終了したかチェック
    if sentence_idx >= len(df):
        st.success("🎉 全ての英文を完了しました！")
        if st.button("最初から始める"):
            st.session_state.sentence_idx = 0
            st.session_state.word_idx = 1
            st.session_state.answered = False
            st.session_state.selected_answer = ""
            st.session_state.choices = []
            st.session_state.is_correct = False
            st.rerun()
    else:
        # タイトルと次の英文ボタンを横に並べる
        cols = st.columns([3, 1])
        with cols[0]:
            st.subheader("英文を再生")
        with cols[1]:
            # 右端に寄せるためのスタイル
            st.markdown('<div style="text-align: right; width: 100%;">', unsafe_allow_html=True)
            if st.button("次の英文", key="next_sentence"):
                st.session_state.sentence_idx += 1
                st.session_state.word_idx = 1
                st.session_state.answered = False
                st.session_state.selected_answer = ""
                st.session_state.choices = []
                st.session_state.is_correct = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        sentence = df.loc[sentence_idx, '英文']
        st.write(sentence)
        
        # 音声再生
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(sentence, lang='en')
            tts.save(fp.name)
            temp_filename = fp.name
            
        with open(temp_filename, "rb") as audio_file:
            st.audio(audio_file.read(), format='audio/mp3')
        
        # 一時ファイルの削除
        try:
            os.unlink(temp_filename)
        except:
            pass
            
        # 単語テスト実施
        if word_idx <= max_word_idx and pd.notna(df.loc[sentence_idx, f'単語{word_idx}']):
            word = df.loc[sentence_idx, f'単語{word_idx}']
            correct_answer = df.loc[sentence_idx, f'日本語訳{word_idx}']
            
            # 選択肢を生成・固定（初回のみ）
            if not st.session_state.choices:
                choices = [correct_answer]
                while len(choices) < 4:
                    random_row = random.randint(0, len(df)-1)
                    random_word_idx = random.randint(1, max_word_idx)
                    dummy_answer = df.loc[random_row, f'日本語訳{random_word_idx}']
                    if pd.notna(dummy_answer) and dummy_answer not in choices:
                        choices.append(dummy_answer)
                random.shuffle(choices)
                st.session_state.choices = choices
            
            choices = st.session_state.choices
                    
            # 単語の意味を問う質問
            st.write(f"### 「{word}」の意味は？")
            
            # 選択肢を表示
            selected_option = st.radio(
                "",  # ラベルを空にして見出しと選択肢の間のスペースを減らす
                choices,
                index=choices.index(st.session_state.selected_answer) if st.session_state.selected_answer in choices else 0,
                key=f'radio_{sentence_idx}_{word_idx}'
            )
            
            # 「回答する」と「次の単語へ」ボタンを並べて表示
            button_cols = st.columns([1, 1, 2])  # 3列に分割し、最後の列は空けておく
            
            with button_cols[0]:
                answer_button = st.button("回答する")
            
            with button_cols[1]:
                next_word_button = st.button("次の単語へ")
            
            # 回答ボタンが押された場合の処理
            if answer_button:
                st.session_state.selected_answer = selected_option
                st.session_state.answered = True
                st.session_state.is_correct = (selected_option == correct_answer)
                st.rerun()
            
            # 次の単語ボタンが押された場合の処理
            if next_word_button:
                st.session_state.word_idx += 1
                st.session_state.answered = False
                st.session_state.selected_answer = ""
                st.session_state.choices = []
                st.session_state.is_correct = False
                st.rerun()
            
            # 結果表示（回答済みの場合のみ）
            if st.session_state.answered:
                if st.session_state.selected_answer == correct_answer:
                    st.success("✅ 正解！")
                else:
                    st.error(f"❌ 不正解！正解は「{correct_answer}」")
        else:
            st.info("この英文の単語テストは終了しました。次の英文に進んでください。")
            
            if st.button("次の英文へ"):
                st.session_state.sentence_idx += 1
                st.session_state.word_idx = 1
                st.session_state.answered = False
                st.session_state.selected_answer = ""
                st.session_state.choices = []
                st.session_state.is_correct = False
                if st.session_state.sentence_idx >= len(df):
                    st.success("🎉 全ての英文を完了しました！")
                st.rerun()
else:
    st.error("ファイル「duo 3.0.xlsx」が同じフォルダに存在しません。ファイルを置いてください。")