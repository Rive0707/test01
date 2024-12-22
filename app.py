import streamlit as st
from gtts import gTTS
import base64

def play_audio_via_html(text):
    tts = gTTS(text=text, lang="en")
    with open("output.mp3", "wb") as f:
        tts.write_to_fp(f)

    with open("output.mp3", "rb") as f:
        audio_data = f.read()
        b64_audio = base64.b64encode(audio_data).decode()

    audio_html = f"""
    <audio controls>
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def main():
    st.title("iPhone対応の英単語学習アプリ")
    word = "apple"

    if st.button("発音を再生"):
        play_audio_via_html(word)

if __name__ == "__main__":
    main()
