import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os

# データをロード
def load_data(file_path):
    return pd.read_csv(file_path)

# 音声生成とBase64エンコード
def text_to_audio_base64(text, lang="en"):
    """gTTSで音声を生成し、base64形式で返す"""
    tts = gTTS(text=text, lang=lang)
    with open("temp.mp3", "wb") as f:
        tts.write_to_fp(f)
    with open("temp.mp3", "rb") as f:
        audio_data = f.read()
    # Base64エンコードして返す
    return base64.b64encode(audio_data).decode()

# 音声再生用HTML埋め込み
def play_audio(text, lang="en"):
    audio_base64 = text_to_audio_base64(text, lang)
    audio_html = f"""
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# 初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "incorrect_words" not in st.session_state:
    st.session_state.incorrect_words = []

# メイン関数
def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を学びながらスコアを上げよう！")
    
    # CSVファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")
    
    if uploaded_file:
        word_data = load_data(uploaded_file)
        
        # 現在の問題を取得
        current_question_index = st.session_state.current_question
        if current_question_index >= len(word_data):
            st.success(f"学習終了！ 最終スコア: {st.session_state.score}")
            if st.session_state.incorrect_words:
                st.write("復習が必要な単語:")
                for word in st.session_state.incorrect_words:
                    st.write(f"- {word}")
            return

        current_word = word_data.iloc[current_question_index]
        
        st.write(f"**英単語:** {current_word['英単語']}")
        st.write(f"_例文:_ {current_word['例文']}")
        
        # 例文音声再生ボタン
        if st.button("例文を再生", key=f"example_{current_question_index}"):
            play_audio(current_word["例文"])

        # 単語音声再生ボタン
        if st.button("単語を再生", key=f"word_{current_question_index}"):
            play_audio(current_word["英単語"])
        
        # 選択肢をシャッフル
        options = [current_word['日本語訳']]
        while len(options) < 4:
            option = random.choice(word_data['日本語訳'])
            if option not in options:
                options.append(option)
        random.shuffle(options)
        
        # 選択肢
        selected_option = st.radio("意味を選んでください", options, key=f"radio_{current_question_index}")
        
        # 回答ボタン
        if st.button("回答する"):
            if selected_option == current_word['日本語訳']:
                st.success("正解です！")
                st.session_state.score += 1
            else:
                st.error(f"不正解！正解は: {current_word['日本語訳']}")
                st.session_state.incorrect_words.append(current_word['英単語'])
            
            # 次の問題へ
            st.session_state.current_question += 1

        # 現在のスコア表示
        st.write(f"現在のスコア: {st.session_state.score}")
    else:
        st.info("単語データをアップロードしてください。")

if __name__ == "__main__":
    main()

