import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os

# データをロード
def load_data(file_path):
    return pd.read_csv(file_path)

# 音声生成と再生
def play_audio(text, lang="en"):
    """gTTSで音声を生成し、base64形式で返す"""
    tts = gTTS(text=text, lang=lang)
    temp_path = "temp.mp3"
    tts.save(temp_path)
    with open(temp_path, "rb") as f:
        audio_data = f.read()
    os.remove(temp_path)
    # Base64エンコードして返す
    return base64.b64encode(audio_data).decode()

# メイン関数
def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を学習しよう！")

    # CSVファイルアップロード
    uploaded_file = st.file_uploader("単語データ（CSV形式）をアップロードしてください", type="csv")

    if uploaded_file:
        word_data = load_data(uploaded_file)

        # 単語をランダムに選ぶ
        current_word = random.choice(word_data.to_dict(orient="records"))

        st.write(f"**英単語:** {current_word['英単語']}")
        st.write(f"_例文:_ {current_word['例文']}")

        # 音声再生
        if st.button("音声を再生する"):
            try:
                audio_base64 = play_audio(current_word['英単語'])
                audio_html = f"""
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"音声生成中にエラーが発生しました: {e}")

        # 選択肢をシャッフル
        options = [current_word['日本語訳']]
        while len(options) < 4:
            option = random.choice(word_data['日本語訳'].tolist())
            if option not in options:
                options.append(option)
        random.shuffle(options)

        # 回答ボタン
        selected_option = st.radio("意味を選んでください", options)
        if st.button("回答する"):
            if selected_option == current_word['日本語訳']:
                st.success("正解です！")
            else:
                st.error(f"不正解！正解は: {current_word['日本語訳']}")
    else:
        st.info("単語データをアップロードしてください。")

if __name__ == "__main__":
    main()
