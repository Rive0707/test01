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

# カスタムタイマーコンポーネントのHTML/JavaScript
def create_timer_html(duration):
    return f"""
    <div id="timer" style="font-size: 36px; font-weight: bold; text-align: center; margin: 10px 0;">
        {duration}
    </div>
    <div class="progress" style="height: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
        <div id="progress-bar" class="progress-bar" style="width: 100%; height: 100%; background-color: #0066cc; border-radius: 10px; transition: width 1s linear;">
        </div>
    </div>

    <script>
        var duration = {duration};
        var timeLeft = duration;
        var timer = document.getElementById('timer');
        var progressBar = document.getElementById('progress-bar');
        
        function updateTimer() {{
            if (timeLeft > 0) {{
                timeLeft -= 1;
                timer.textContent = timeLeft;
                timer.style.color = timeLeft < 10 ? 'red' : 'black';
                
                // プログレスバーの更新
                var percentage = (timeLeft / duration) * 100;
                progressBar.style.width = percentage + '%';
                
                if (timeLeft === 0) {{
                    // 時間切れの場合、Streamlitに通知
                    window.parent.postMessage({{
                        type: 'streamlit:timeExpired',
                        value: true
                    }}, '*');
                }}
            }}
        }}
        
        // 1秒ごとにタイマーを更新
        var interval = setInterval(updateTimer, 1000);
        
        // コンポーネントがアンマウントされたときのクリーンアップ
        window.addEventListener('beforeunload', function() {{
            clearInterval(interval);
        }});
    </script>
    """

# その他の既存の関数はそのまま維持...

def main():
    st.title("英単語学習アプリ")
    st.subheader("英単語を楽しく学習しよう！")

    # セッション状態の初期化（既存のコードを維持）...

    # ファイルアップロード部分（既存のコードを維持）...

    if uploaded_file:
        word_data = load_data(uploaded_file)

        # モード選択部分（既存のコードを維持）...

        if words_to_study:
            if st.session_state.question_progress >= len(words_to_study):
                st.info("すべての単語を学習しました！")
                if st.button("最初からやり直す"):
                    # リセット処理（既存のコードを維持）...
                    pass
            else:
                current_word = words_to_study[st.session_state.question_progress]

                # タイマーの表示
                timer_placeholder = st.empty()
                with timer_placeholder:
                    if not st.session_state.answered and not st.session_state.time_expired:
                        components.html(
                            create_timer_html(TIMER_DURATION),
                            height=100,
                        )

                # 時間切れの処理
                if st.session_state.time_expired:
                    st.error(f"時間切れ！正解は: {current_word['日本語訳']}")
                    time.sleep(1)
                    move_to_next_question()

                # 残りの問題表示部分（既存のコードを維持）...

                # 回答処理
                if st.button("回答する", disabled=st.session_state.answered or st.session_state.time_expired):
                    check_answer(current_word)

                # 回答メッセージの表示（既存のコードを維持）...

        else:
            st.info("すべての単語を学習しました！")

if __name__ == "__main__":
    main()
