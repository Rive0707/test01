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

def start_timer():
    if "time_left" not in st.session_state:
        st.session_state.time_left = 30
    timer_placeholder = st.empty()
    start_time = time.time()
    total_time = st.session_state.time_left

    while st.session_state.time_left > 0 and not st.session_state.answered:
        elapsed_time = time.time() - start_time
        st.session_state.time_left = max(0, total_time - int(elapsed_time))
        m, s = divmod(st.session_state.time_left, 60)
        with timer_placeholder.container(): # containerで囲む
            st.metric("残り時間", f"{m:02d}:{s:02d}")
        time.sleep(0.1)

    if st.session_state.time_left <= 0 and not st.session_state.answered:
        st.session_state.answer_message = "時間切れ！次の問題に進みます。"
        st.session_state.progress['incorrect'] += 1
        save_progress(st.session_state.progress)
        st.session_state.answered = True #時間切れで回答済みにする
        st.experimental_rerun()  # ★UIを更新して次の問題へ移行★
    elif st.session_state.answered:
        timer_placeholder.empty()


        # 時間切れの場合の処理
        if st.session_state.time_left == 0 and not st.session_state.answered:
            st.session_state.answer_message = "時間切れ！次の問題に進みます。"
            st.session_state.progress['incorrect'] += 1
            save_progress(st.session_state.progress)
            next_question()  # 次の問題に進む

        st.session_state.timer_active = False
        timer_placeholder.empty()  # タイマー表示をクリア



        # 時間切れの場合の処理
        if st.session_state.time_left == 0 and not st.session_state.answered:
            st.session_state.answer_message = "時間切れ！次の問題に進みます。"
            st.session_state.progress['incorrect'] += 1
            save_progress(st.session_state.progress)
            next_question()  # 次の問題へ進む

        st.session_state.timer_active = False
        timer_placeholder.empty()  # タイマー表示をクリア


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
    if "timer_started" not in st.session_state:
        st.session_state.timer_started = False

    progress = st.session_state.progress

    # サイドバー: スコア表示と設定
    with st.sidebar:
        st.header("スコア")
        st.write(f"正解: {progress['correct']}")
        st.write(f"不正解: {progress['incorrect']}")

        if progress['incorrect_words']:
            if st.checkbox("間違えた単語を復習する"):
                st.session_state.review_mode = True
            else:
                st.session_state.review_mode = False
        else:
            st.write("間違えた単語はありません")

        if st.button("スコアをリセット"):
            st.session_state.progress = {"correct": 0, "incorrect": 0, "incorrect_words": []}
            save_progress(st.session_state.progress)
            st.experimental_rerun()

    # CSVファイルとイメージファイルのアップロード
    uploaded_file = st.file_uploader("単語CSVファイルをアップロードしてください", type="csv")
    uploaded_images = st.file_uploader("画像ファイルをアップロードしてください", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_images:
        for uploaded_image in uploaded_images:
            st.session_state.image_files[uploaded_image.name] = uploaded_image.getvalue()

    if uploaded_file:
        word_data = load_data(uploaded_file)

        if word_data is not None:
            if st.session_state.review_mode:
                words_to_study = st.session_state.progress['incorrect_words']
                if not words_to_study:
                    st.info("復習する単語はありません。")
                    return
            else:
                if st.session_state.shuffled_words is None:
                    st.session_state.shuffled_words = shuffle_questions(word_data)
                words_to_study = st.session_state.shuffled_words

            if st.session_state.question_progress < len(words_to_study):
                current_word = words_to_study[st.session_state.question_progress]
                st.session_state.current_word = current_word

                st.subheader(current_word['英単語'])

                # 画像表示
                if '画像' in current_word and current_word['画像'] in st.session_state.image_files:
                    image_bytes = st.session_state.image_files[current_word['画像']]
                    image = load_image(image_bytes)
                    if image:
                        st.image(image, use_column_width=True)

                # 音声再生
                audio_base64 = text_to_audio_base64(current_word['英単語'])
                if audio_base64:
                    st.markdown(
                        f'<audio autoplay controls src="data:audio/mpeg;base64,{audio_base64}"></audio>',
                        unsafe_allow_html=True,
                    )

                options = [current_word['日本語訳']]
                while len(options) < 4:
                    random_word = random.choice(words_to_study)
                    if random_word['日本語訳'] not in options:
                        options.append(random_word['日本語訳'])
                random.shuffle(options)
                st.session_state.options = options

                if not st.session_state.answered:
                  if not st.session_state.timer_started:
                    st.session_state.timer_started = True
                    start_timer()

                  for option in st.session_state.options:
                      if st.button(option):
                          st.session_state.selected_option = option
                          st.session_state.answered = True
                          check_answer(current_word)
                          st.experimental_rerun()

                if st.session_state.answer_message:
                    st.write(st.session_state.answer_message)
                    if st.button("次の問題へ"):
                        next_question()

            else:
                st.write("問題は以上です！")
                st.balloons()

if __name__ == "__main__":
    main()
