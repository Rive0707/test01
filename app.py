import streamlit as st
import pandas as pd
import random
from gTTS import gTTS
import base64
import os
import json
from PIL import Image
import io

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

    progress = st.session_state.progress

    # サイドバー: スコア表示と設定
    st.sidebar.markdown("### スコア")
    st.sidebar.write(f"**正解数:** {progress['correct']}")
    st.sidebar.write(f"**不正解数:** {progress['incorrect']}")

    if st.sidebar.button("進捗をリセット"):
        st.session_state.progress = {"correct": 0, "incorrect": 0, "incorrect_words": []}
        save_progress(st.session_state.progress)
        st.session_state.current_word = None
        st.session_state.options = []
        st.session_state.selected_option = None
        st.session_state.question_progress = 0
        st.session_state.answered = False
        st.session_state.answer_message = None
        st.session_state.shuffled_words = None

    # CSVファイルとイメージファイルのアップロード
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")
    with col2:
        uploaded_images = st.file_uploader("画像をアップロードしてください", type=None, accept_multiple_files=True)

    # 画像ファイルの処理
    if uploaded_images:
        st.session_state.image_files = {}
        for image_file in uploaded_images:
            image_name = os.path.splitext(image_file.name)[0]
            st.session_state.image_files[image_name] = image_file.read()

    if uploaded_file:
        word_data = load_data(uploaded_file)

        # 出題モード選択と問題のシャッフル
        if st.session_state.review_mode:
            if not st.session_state.shuffled_words:
                st.session_state.shuffled_words = shuffle_questions([word for word in progress['incorrect_words'] if word])
            words_to_study = st.session_state.shuffled_words
            st.info("復習モードで学習中です。")
        else:
            if not st.session_state.shuffled_words:
                st.session_state.shuffled_words = shuffle_questions(word_data.to_dict(orient="records"))
            words_to_study = st.session_state.shuffled_words

        # 出題
        if words_to_study:
            if st.session_state.question_progress >= len(words_to_study):
                st.info("すべての単語を学習しました！")
                if st.button("最初からやり直す"):
                    st.session_state.progress = {"correct": 0, "incorrect": 0, "incorrect_words": []}
                    save_progress(st.session_state.progress)
                    st.session_state.question_progress = 0
            else:
                current_word = words_to_study[st.session_state.question_progress]
                st.session_state.current_word = current_word

                st.write(f"**英単語:** {current_word['英単語']}")
                st.write(f"**例文:** {current_word['例文']}")

                # 画像表示
                if current_word['英単語'] in st.session_state.image_files:
                    image_bytes = st.session_state.image_files[current_word['英単語']]
                    image = load_image(image_bytes)
                    if image:
                        st.image(image, caption=f"{current_word['英単語']} の画像")

                # 選択肢の作成
                options = [current_word['日本語訳']]
                while len(options) < 4:
                    option = random.choice(word_data['日本語訳'])
                    if option not in options:
                        options.append(option)
                random.shuffle(options)
                st.session_state.options = options

                # 音声再生ボタン
                if st.button("音声再生"):
                    audio_base64 = text_to_audio_base64(current_word['英単語'])
                    st.markdown(f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

                # 選択肢の表示と回答ボタン
                selected_option = st.radio("意味を選んでください", options)
                st.session_state.selected_option = selected_option

                if st.button("回答する"):
                    check_answer(current_word)

                if st.session_state.answer_message:
                    st.write(st.session_state.answer_message)

                # 次へボタン
                if st.button("次へ"):
                    next_question()

if __name__ == "__main__":
    main()

