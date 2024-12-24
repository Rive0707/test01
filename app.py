import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os
import json
import time

# スコアと進捗を保存するファイル
PROGRESS_FILE = "progress.json"

# 進捗データの初期化
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    else:
        return {"correct": 0, "incorrect": 0, "incorrect_words": []}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# 音声生成関数
def text_to_audio_base64(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    with open("temp.mp3", "wb") as f:
        tts.write_to_fp(f)
    with open("temp.mp3", "rb") as f:
        audio_data = f.read()
    return base64.b64encode(audio_data).decode()

# CSVデータをロード
def load_data(file_path):
    return pd.read_csv(file_path)

# タイマーの管理
def start_timer():
    if "time_left" not in st.session_state:
        st.session_state.time_left = 30
    timer_placeholder = st.empty()  # タイマー表示用のプレースホルダー
    while st.session_state.time_left > 0:
        timer_placeholder.warning(f"残り時間: {st.session_state.time_left} 秒", icon="⏳")
        time.sleep(1)
        st.session_state.time_left -= 1
        if st.session_state.answered:
            break
    if st.session_state.time_left == 0 and not st.session_state.answered:
        st.session_state.answer_message = "時間切れ！次の問題に進みます。"
        st.session_state.progress["incorrect"] += 1
        save_progress(st.session_state.progress)
        next_question()
    timer_placeholder.empty()

# 次へボタンのコールバック関数
def next_question():
    if st.session_state.answered or st.session_state.time_left == 0:
        st.session_state.question_progress += 1
        st.session_state.options = []  # 選択肢をリセット
        st.session_state.selected_option = None  # 選択肢をリセット
        st.session_state.answered = False  # 回答状態をリセット
        st.session_state.answer_message = None  # 回答メッセージをリセット
        st.session_state.time_left = 30  # タイマーをリセット

# 回答ボタンのコールバック関数
def check_answer(current_word):
    if not st.session_state.answered:
        if st.session_state.selected_option == current_word["日本語訳"]:
            st.session_state.answer_message = "正解です！"
            st.session_state.progress["correct"] += 1
        else:
            st.session_state.answer_message = f"不正解！正解は: {current_word['日本語訳']}"
            st.session_state.progress["incorrect"] += 1
            if current_word not in st.session_state.progress["incorrect_words"]:
                st.session_state.progress["incorrect_words"].append(current_word)
        save_progress(st.session_state.progress)
        st.session_state.answered = True

# メイン関数
def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を楽しく学習しよう！")

    # セッション状態初期化
    if "progress" not in st.session_state:
        st.session_state.progress = load_progress()
    if "question_progress" not in st.session_state:
        st.session_state.question_progress = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "answer_message" not in st.session_state:
        st.session_state.answer_message = None
    if "time_left" not in st.session_state:
        st.session_state.time_left = 30

    progress = st.session_state.progress

    # タイマー開始
    start_timer()

    # CSVファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = load_data(uploaded_file)

        # 出題
        if st.session_state.question_progress < len(word_data):
            current_word = word_data.iloc[st.session_state.question_progress]

            # 表示
            st.write(f"**英単語:** {current_word['英単語']}")
            st.write(f"_例文:_ {current_word['例文'].replace(current_word['英単語'], f'<span style=\"color:red;\">{current_word['英単語']}</span>')}", unsafe_allow_html=True)

            if st.button("単語を再生"):
                audio_base64 = text_to_audio_base64(current_word["英単語"])
                audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
                st.markdown(audio_html, unsafe_allow_html=True)

            if not st.session_state.options:
                options = [current_word["日本語訳"]] + random.sample(
                    [opt for opt in word_data["日本語訳"] if opt != current_word["日本語訳"]],
                    3,
                )
                random.shuffle(options)
                st.session_state.options = options

            st.session_state.selected_option = st.radio(
                "意味を選んでください", st.session_state.options, key="radio_selection"
            )

            if st.button("回答する", disabled=st.session_state.answered):
                check_answer(current_word)

            if st.session_state.answer_message:
                if "正解" in st.session_state.answer_message:
                    st.success(st.session_state.answer_message)
                else:
                    st.error(st.session_state.answer_message, icon="❌")

            if st.button("次へ", disabled=not st.session_state.answered):
                next_question()
        else:
            st.info("すべての単語を学習しました！")

if __name__ == "__main__":
    main()

