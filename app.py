import streamlit as st
from gtts import gTTS
import tempfile
import os

# Streamlit アプリのタイトル
st.title("音声再生アプリ（iPhone対応）")

# テキスト入力
text = st.text_input("音声に変換したいテキストを入力してください", "Hello, iPhone!")

if st.button("音声再生"):
    # gTTS を使って音声を生成
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        st.audio(tmp.name, format="audio/mp3")  # 音声をストリーム再生
        # ファイルを削除（iPhone Safari の互換性維持のため、ここで削除しない）
