import streamlit as st
import random
import pandas as pd
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

# メイン関数
def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を楽しく学習しよう！")

    progress = load_progress()

    st.sidebar.markdown("### スコア")
    st.sidebar.write(f"**正解数:** {progress['correct']}")
    st.sidebar.write(f"**不正解数:** {progress['incorrect']}")

    if st.sidebar.button("進捗をリセット"):
        progress = {"correct": 0, "incorrect": 0, "incorrect_words": []}
        save_progress(progress)
        st.experimental_rerun()

    # CSVファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = load_data(uploaded_file)

        if "review_mode" not in st.session_state:
            st.session_state.review_mode = False

        if st.sidebar.button("復習モードを開始"):
            if progress['incorrect_words']:
                st.session_state.review_mode = True
            else:
                st.sidebar.info("不正解の単語がありません。")

        if st.sidebar.button("通常モードに戻る"):
            st.session_state.review_mode = False

        # 出題モード選択
        if st.session_state.review_mode:
            words_to_study = progress['incorrect_words']
            st.info("復習モードで学習中です。")
        else:
            words_to_study = word_data.to_dict(orient="records")

        # 単語をランダムに選ぶ
        if words_to_study:
            if "current_word" not in st.session_state:
                st.session_state.current_word = random.choice(words_to_study)

            current_word = st.session_state.current_word

            st.write(f"**英単語:** {current_word['英単語']}")
            st.write(f"_例文:_ {current_word['例文']}")

            # 音声再生
            play_word_button = st.button("単語を再生")
            if play_word_button:
                audio_base64 = text_to_audio_base64(current_word['英単語'])
                audio_html = f"""
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)

            play_example_button = st.button("例文を再生")
            if play_example_button:
                audio_base64 = text_to_audio_base64(current_word['例文'])
                audio_html = f"""
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)

            # 選択肢をシャッフル
            options = [current_word['日本語訳']]
            while len(options) < 4:
                option = random.choice(word_data['日本語訳'])
                if option not in options:
                    options.append(option)
            random.shuffle(options)

            # 初期選択肢を保持
            if "selected_option" not in st.session_state:
                st.session_state.selected_option = None

            # ラジオボタンのインデックスを選択された選択肢に設定
            selected_option = st.radio(
                "意味を選んでください", 
                options, 
                index=options.index(st.session_state.selected_option) if st.session_state.selected_option else None
            )

            # 選択肢が変更された場合にその選択肢を保存
            if selected_option != st.session_state.selected_option:
                st.session_state.selected_option = selected_option

            # 「回答する」ボタンが押されたときの処理
            if st.button("回答する"):
                if st.session_state.selected_option:
                    if st.session_state.selected_option == current_word['日本語訳']:
                        st.success("正解です！")
                        progress['correct'] += 1
                    else:
                        st.error(f"不正解！正解は: {current_word['日本語訳']}")
                        progress['incorrect'] += 1
                        progress['incorrect_words'].append(current_word)

                    save_progress(progress)
                    # 次の問題に進むために、現在の問題を削除して、進めるようにする
                    del st.session_state.current_word
                    st.session_state.selected_option = None  # 選択肢をリセット
                    st.experimental_rerun()  # 回答後、問題を次に進める
                else:
                    st.warning("答えを選んでから回答してください。")

        else:
            st.info("すべての単語を学習しました！")

if __name__ == "__main__":
    main()
