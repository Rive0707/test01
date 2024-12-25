import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from gtts import gTTS
import base64
import os
import json
from PIL import Image
import io
import zipfile
import time
import re

# 定数
PROGRESS_FILE = "progress.json"
TIMER_DURATION = 30

# タイマーリセット関数
def reset_timer():
    st.session_state.time_remaining = TIMER_DURATION
    st.session_state.time_expired = False

# タイマーHTML生成関数
def create_timer_html(time_remaining):
    return f"""
    <div style="font-size: 24px; text-align: center; margin: 10px 0;">
        残り時間: <span style="color: {'red' if time_remaining < 10 else 'black'};">{time_remaining}</span> 秒
    </div>
    """

# タイマー更新関数
def update_timer():
    if st.session_state.time_remaining > 0:
        st.session_state.time_remaining -= 1
    else:
        st.session_state.time_expired = True

# セッション状態の初期化
if "progress" not in st.session_state:
    st.session_state.progress = {
        "correct": 0,
        "incorrect": 0,
        "incorrect_words": []
    }
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
if "time_remaining" not in st.session_state:
    st.session_state.time_remaining = TIMER_DURATION
if "time_expired" not in st.session_state:
    st.session_state.time_expired = False

# 進捗データのロード・保存
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"correct": 0, "incorrect": 0, "incorrect_words": []}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# 問題を次に進める
def move_to_next_question():
    st.session_state.question_progress += 1
    st.session_state.options = []
    st.session_state.selected_option = None
    st.session_state.answered = False
    st.session_state.answer_message = None
    reset_timer()  # タイマーをリセット
    st.experimental_rerun()

# 回答をチェック
def check_answer(current_word):
    if not st.session_state.answered and not st.session_state.time_expired:
        if st.session_state.selected_option == current_word['日本語訳']:
            st.session_state.answer_message = "<div style='color: green; font-weight: bold;'>正解です！</div>"
            st.session_state.progress['correct'] += 1
        else:
            st.session_state.answer_message = (
                f"<div style='color: red; font-weight: bold;'>不正解！正解は: {current_word['日本語訳']}</div>"
            )
            st.session_state.progress['incorrect'] += 1
            if current_word not in st.session_state.progress['incorrect_words']:
                st.session_state.progress['incorrect_words'].append(current_word)
        save_progress(st.session_state.progress)
        st.session_state.answered = True

# メイン関数
def main():
    st.title("英単語学習アプリ")

    # サイドバーの設定
    st.sidebar.markdown("### スコア")
    st.sidebar.write(f"**正解数:** {st.session_state.progress['correct']}")
    st.sidebar.write(f"**不正解数:** {st.session_state.progress['incorrect']}")

    if st.sidebar.button("進捗をリセット"):
        st.session_state.progress = {
            "correct": 0,
            "incorrect": 0,
            "incorrect_words": []
        }
        save_progress(st.session_state.progress)
        st.experimental_rerun()

    # ファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = pd.read_csv(uploaded_file)
        if not st.session_state.shuffled_words:
            st.session_state.shuffled_words = random.sample(
                word_data.to_dict(orient="records"), len(word_data)
            )

        words_to_study = st.session_state.shuffled_words

        # 現在の問題を取得
        if st.session_state.question_progress >= len(words_to_study):
            st.info("すべての単語を学習しました！")
            if st.button("最初からやり直す"):
                st.session_state.question_progress = 0
                st.session_state.shuffled_words = random.sample(
                    word_data.to_dict(orient="records"), len(word_data)
                )
                reset_timer()
                st.experimental_rerun()
        else:
            current_word = words_to_study[st.session_state.question_progress]

            # タイマーの表示
            timer_placeholder = st.empty()
            with timer_placeholder:
                components.html(create_timer_html(st.session_state.time_remaining), height=50)

            # タイマーの更新
            if not st.session_state.time_expired and not st.session_state.answered:
                update_timer()

            # 問題の表示
            st.write(f"**英単語:** {current_word['英単語']}")

            # 回答選択肢の表示
            if not st.session_state.options:
                options = [current_word['日本語訳']]
                all_answers = word_data['日本語訳'].tolist()
                wrong_answers = [ans for ans in all_answers if ans != current_word['日本語訳']]
                options.extend(random.sample(wrong_answers, 3))
                random.shuffle(options)
                st.session_state.options = options

            st.session_state.selected_option = st.radio(
                "意味を選んでください", st.session_state.options, key="radio_selection"
            )

            # 回答ボタン
            if st.button("回答する", key="answer_button", disabled=st.session_state.answered or st.session_state.time_expired):
                check_answer(current_word)

            # 正解・不正解メッセージの表示
            if st.session_state.answer_message:
                st.markdown(st.session_state.answer_message, unsafe_allow_html=True)

            # 次へボタン
            if st.button("次へ", key="next_button", disabled=not st.session_state.answered):
                move_to_next_question()

if __name__ == "__main__":
    main()

