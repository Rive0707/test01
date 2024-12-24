import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os
import json

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

# 回答ボタンのコールバック関数
def check_answer(current_word):
    if st.session_state.selected_option == current_word['日本語訳']:
        st.success("正解です！")
        st.session_state.progress['correct'] += 1
    else:
        st.error(f"不正解！正解は: {current_word['日本語訳']}")
        st.session_state.progress['incorrect'] += 1
        if current_word not in st.session_state.progress['incorrect_words']:
            st.session_state.progress['incorrect_words'].append(current_word)
    save_progress(st.session_state.progress)

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
    if "studied_words" not in st.session_state:
        st.session_state.studied_words = []

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
        st.session_state.studied_words = []

    # CSVファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = load_data(uploaded_file)
        all_words = word_data.to_dict(orient="records")

        if st.sidebar.button("復習モードを開始"):
            if progress['incorrect_words']:
                st.session_state.review_mode = True
                st.session_state.studied_words = [] # 復習モード開始時にリセット
            else:
                st.sidebar.info("不正解の単語がありません。")

        if st.sidebar.button("通常モードに戻る"):
            st.session_state.review_mode = False
            st.session_state.studied_words = [] # 通常モード開始時にリセット

        # 出題モード選択
        if st.session_state.review_mode:
            words_to_study = progress['incorrect_words'].copy()
            random.shuffle(words_to_study) # 復習モードでもシャッフル
            st.info("復習モードで学習中です。")
        else:
            words_to_study = all_words.copy()
            random.shuffle(words_to_study) # 通常モードでシャッフル

        # 出題
        if words_to_study:
            available_words = [word for word in words_to_study if word not in st.session_state.studied_words]

            if not available_words:
                st.info("すべての単語を学習しました！")
                st.session_state.studied_words = [] # 学習完了後リセット
            else:
                current_word = random.choice(available_words)
                st.session_state.studied_words.append(current_word)

                st.write(f"**英単語:** {current_word['英単語']}")
                st.write(f"_例文:_ {current_word['例文']}")

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
                    while len(options) < 4:
                        option = random.choice(word_data['日本語訳'])
                        if option not in options:
                            options.append(option)
                    random.shuffle(options)
                    st.session_state.options = options

                st.session_state.selected_option = st.radio(
                    "意味を選んでください", st.session_state.options, key="radio_selection"
                )

                if st.button("回答する"):
                    check_answer(current_word)
                    st.session_state.options = [] # 選択肢をリセット

        else:
            st.info("CSVファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
