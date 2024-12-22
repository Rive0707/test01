import streamlit as st
from gtts import gTTS
import base64

def text_to_audio_base64(text, lang="en"):
    """gTTSで音声を生成し、base64形式で返す"""
    tts = gTTS(text=text, lang=lang)
    with open("temp.mp3", "wb") as f:
        tts.write_to_fp(f)
    with open("temp.mp3", "rb") as f:
        audio_data = f.read()
    # Base64エンコードして返す
    return base64.b64encode(audio_data).decode()

st.title("音声再生アプリ（iPhone対応）")

# ユーザー入力
text = st.text_input("音声に変換したいテキストを入力してください", "Hello, iPhone!")

if st.button("音声再生"):
    try:
        # Base64エンコードされた音声データを取得
        audio_base64 = text_to_audio_base64(text)
        
        # 音声をHTMLタグとして埋め込む
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
