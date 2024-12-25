import streamlit as st
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

# スコアと進捗を保存するファイル
PROGRESS_FILE = "progress.json"
TIMER_DURATION = 30  # 制限時間（秒）

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

# 例文中の単語をハイライトする関数
def highlight_word_in_sentence(sentence, word):
    pattern = re.compile(f'({word})', re.IGNORECASE)
    highlighted = pattern.sub(r'<span style="color: red;">\1</span>', sentence)
    return highlighted

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

# ZIPファイルから画像を読み込む
def load_images_from_zip(zip_file):
    images = {}
    with zipfile.ZipFile(zip_file) as z:
        for filename in z.namelist():
            if not filename.endswith('/'):
                base_name = os.path.splitext(os.path.basename(filename))[0]
                try:
                    with z.open(filename) as f:
                        image_data = f.read()
                        try:
                            Image.open(io.BytesIO(image_data))
                            images[base_name] = image_data
                        except:
                            continue
                except:
                    continue
    return images

def load_image(image_bytes):
    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None

def shuffle_questions(words):
    return random.sample(words, len(words))

def next_question():
    if st.session_state.answered or st.session_state.time_expired:
        st.session_state.question_progress += 1
        st.session_state.options = []
        st.session_state.selected_option = None
        st.session_state.answered = False
        st.session_state.answer_message = None
        st.session_state.start_time = time.time()
        st.session_state.time_expired = False

def check_answer(current_word):
    if not st.session_state.answered and not st.session_state.time_expired:
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
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    if "time_expired" not in st.session_state:
        st.session_state.time_expired = False

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
        st.session_state.start_time = time.time()
        st.session_state.time_expired = False

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")
    with col2:
        uploaded_zip = st.file_uploader("画像フォルダ（ZIP形式）をアップロードしてください", type="zip")
        
    if uploaded_zip:
        st.session_state.image_files = load_images_from_zip(uploaded_zip)
        st.success(f"{len(st.session_state.image_files)}個の画像を読み込みました。")

    if uploaded_file:
        word_data = load_data(uploaded_file)

        if st.sidebar.button("復習モードを開始"):
            if progress['incorrect_words']:
                st.session_state.review_mode = True
                st.session_state.question_progress = 0
                st.session_state.answered = False
                st.session_state.answer_message = None
                st.session_state.shuffled_words = shuffle_questions(progress['incorrect_words'])
                st.session_state.start_time = time.time()
            else:
                st.sidebar.info("不正解の単語がありません。")

        if st.sidebar.button("通常モードに戻る"):
            st.session_state.review_mode = False
            st.session_state.question_progress = 0
            st.session_state.answered = False
            st.session_state.answer_message = None
            st.session_state.shuffled_words = shuffle_questions(word_data.to_dict(orient="records"))
            st.session_state.start_time = time.time()

        if st.session_state.review_mode:
            if not st.session_state.shuffled_words:
                st.session_state.shuffled_words = shuffle_questions([word for word in progress['incorrect_words'] if word])
            words_to_study = st.session_state.shuffled_words
            st.info("復習モードで学習中です。")
        else:
            if not st.session_state.shuffled_words:
                st.session_state.shuffled_words = shuffle_questions(word_data.to_dict(orient="records"))
            words_to_study = st.session_state.shuffled_words

        # 総問題数と現在の問題番号を表示
        st.write(f"**問題 {st.session_state.question_progress + 1} / {len(words_to_study)}**")

        if words_to_study:
            if st.session_state.question_progress >= len(words_to_study):
                st.info("すべての単語を学習しました！")
                if st.button("最初からやり直す"):
                    st.session_state.question_progress = 0
                    st.session_state.shuffled_words = shuffle_questions(words_to_study)
                    st.session_state.answered = False
                    st.session_state.answer_message = None
                    st.session_state.options = []
                    st.session_state.start_time = time.time()
                    st.session_state.time_expired = False
            else:
                current_word = words_to_study[st.session_state.question_progress]

                # タイマー表示
                elapsed_time = time.time() - st.session_state.start_time
                remaining_time = max(0, TIMER_DURATION - elapsed_time)
                
                # プログレスバーでタイマーを表示
                progress_bar = st.progress(remaining_time / TIMER_DURATION)
                st.write(f"残り時間: {int(remaining_time)}秒")

                # 時間切れチェック
                if remaining_time <= 0 and not st.session_state.answered and not st.session_state.time_expired:
                    st.session_state.time_expired = True
                    st.session_state.progress['incorrect'] += 1
                    if current_word not in st.session_state.progress['incorrect_words']:
                        st.session_state.progress['incorrect_words'].append(current_word)
                    save_progress(st.session_state.progress)
                    st.error(f"時間切れ！正解は: {current_word['日本語訳']}")

                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**英単語:** {current_word['英単語']}")
                    # 例文中の単語をハイライト表示
                    highlighted_sentence = highlight_word_in_sentence(current_word['例文'], current_word['英単語'])
                    st.markdown(f"_例文:_ {highlighted_sentence}", unsafe_allow_html=True)

                with col2:
                    if current_word['英単語'] in st.session_state.image_files:
                        image_data = st.session_state.image_files[current_word['英単語']]
                        image = load_image(image_data)
                        if image:
                            st.image(image, use_column_width=True)

                if st.button("単語を再生"):
                    audio_base64 = text_to_audio_base64(current_word['英単語'])
                    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
                    st.markdown(audio_html, unsafe_allow_html=True)

                if st.button("例文を再生"):
                    audio_base64 = text_to_audio_base64(current_word['例文'])
                    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
                    st.markdown(audio_html, unsafe_allow_html=True)

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

                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if st.button("回答する", disabled=st.session_state.answered or st.session_state.time_expired):
                        check_answer(current_word)

                if st.session_state.answer_message:
                    if "正解" in st.session_state.answer_message:
                        st.success(st.session_state.answer_message)
                    else:
                        st.markdown(f'<p style="color: red;">{st.session_state.answer_message}</p>', unsafe_allow_html=True)

                if st.button("次へ", disabled=not (st.session_state.answered or st.session_state.time_expired)):
                    next_question()
        else:
            st.info("すべての単語を学習しました！")

if __name__ == "__main__":
    main()
