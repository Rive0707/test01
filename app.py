import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os
import json
from PIL import Image
import io
import threading
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

# 画像をロード
def load_image(image_bytes):
    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None

# 問題をランダムに並び替える
def shuffle_questions(words):
    return random.sample(words, len(words))

# 次へボタンのコールバック関数
def next_question():
    if st.session_state.answered:  # 回答済みの場合のみ次の問題へ
        st.session_state.question_progress += 1
        st.session_state.options = []  # 選択肢をリセット
        st.session_state.selected_option = None  # 選択肢をリセット
        st.session_state.answered = False  # 回答状態をリセット
        st.session_state.answer_message = None  # 回答メッセージをリセット
        st.session_state.time_left = 30  # タイマーをリセット

# 回答ボタンのコールバック関数
def check_answer(current_word):
    if not st.session_state.answered:  # 未回答の場合のみ処理
        if st.session_state.selected_option == current_word['日本語訳']:
            st.session_state.answer_message = "正解です！"
            st.session_state.progress['correct'] += 1
        else:
            st.session_state.answer_message = f"不正解！正解は: {current_word['日本語訳']}"
            st.session_state.progress['incorrect'] += 1
            if current_word not in st.session_state.progress['incorrect_words']:
                st.session_state.progress['incorrect_words'].append(current_word)
        save_progress(st.session_state.progress)
        st.session_state.answered = True

# タイマーを開始する関数
def start_timer():
    total_time = st.session_state.time_left
    while total_time > 0:
        if st.session_state.answered:  # ユーザーが回答した場合、タイマー停止
            break

        time.sleep(1)
        total_time -= 1
        st.session_state.time_left = total_time  # 残り時間をセッションに保存

        # タイマーの更新を表示
        st.session_state.timer_placeholder.metric("残り時間", f"{total_time // 60:02d}:{total_time % 60:02d}")

    if total_time == 0 and not st.session_state.answered:
        st.session_state.answer_message = "時間切れ！次の問題に進みます。"
        st.session_state.progress['incorrect'] += 1
        save_progress(st.session_state.progress)
        next_question()  # 次の問題に進む

    st.session_state.timer_active = False  # タイマー停止

# メイン関数
def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を楽しく学習しよう！")

    # セッション状態初期化
    if "progress" not in st.session_state:
        st.session_state.progress = load_progress()
    if "current_word" not in st.session_state:
        st.session_state.current_word = None
    if "options" not in st.session_state:
        st.session_state.options = []
    if "review_mode" not in st.session_state:
        st.session_state.review_mode = False
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None
    if "question_progress" not in st.session_state:
        st.session_state.question_progress = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "answer_message" not in st.session_state:
        st.session_state.answer_message = None
    if "shuffled_words" not in st.session_state:
        st.session_state.shuffled_words = None
    if "image_files" not in st.session_state:
        st.session_state.image_files = {}
    if "time_left" not in st.session_state:
        st.session_state.time_left = 30

    progress = st.session_state.progress

    # サイドバー: スコア表示と設定
    st.sidebar.markdown("### スコア")
    st.sidebar.write(f"**正解数:** {progress['correct']}")
    st.sidebar.write(f"**不正解数:** {progress['incorrect']}")

    # CSVファイルのアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = load_data(uploaded_file)

        # 出題
        if word_data:
            current_word = word_data.iloc[st.session_state.question_progress]

            # 英単語と例文表示
            st.write(f"**英単語:** {current_word['英単語']}")
            st.write(f"_例文:_ {current_word['例文']}")

            # タイマー表示
            if "timer_placeholder" not in st.session_state:
                st.session_state.timer_placeholder = st.empty()

            if not st.session_state.answered:
                if "timer_thread" not in st.session_state:
                    st.session_state.timer_thread = threading.Thread(target=start_timer)
                    st.session_state.timer_thread.start()

            # 回答の処理
            if st.button("回答する", disabled=st.session_state.answered):
                check_answer(current_word)

            if st.session_state.answer_message:
                st.success(st.session_state.answer_message) if "正解" in st.session_state.answer_message else st.error(st.session_state.answer_message)

            # 次の問題へ
            if st.session_state.answered and st.button("次へ"):
                next_question()

if __name__ == "__main__":
    main()

