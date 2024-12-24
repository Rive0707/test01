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

    # 出題例
    st.write("ここに問題や選択肢が表示されます。")
    if st.session_state.answer_message:
        st.warning(st.session_state.answer_message)
        if "正解" in st.session_state.answer_message:
            st.success(st.session_state.answer_message)
        else:
            st.error(st.session_state.answer_message)

if __name__ == "__main__":
    main()
