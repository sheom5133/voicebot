import streamlit as st
import openai
from audiorecorder import audiorecorder
import os
from datetime import datetime
from gtts import gTTS
import base64

def STT(audio):
    filename='input.mp3'
    audio.export(filename, format="mp3")
    with open(filename, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    os.remove(filename)
    return transcript.text

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    gpt_message = response.choices[0].message
    return gpt_message.content

def TTS(response):
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

    os.remove(filename)

def main():
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide")

    st.header("음성 비서 프로그램")

    st.markdown("---")

    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
        """     
        - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다. 
        - 답변은 OpenAI의 GPT 모델을 활용했습니다. 
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
        """
        )

        st.markdown("")
    
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    with st.sidebar:

        openai.api_key = st.text_input(label="OPENAI API 키", 
                                       placeholder="Enter Your API Key", 
                                       value="", 
                                       type="password")
        
        st.markdown("---")

        model = st.radio(label="GPT 모델",options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = audiorecorder()
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            st.audio(audio.export().read())
            question = STT(audio)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] += [("user", now, question)]
            st.session_state["messages"] += [{"role": "user", "content": question}]

    with col2:
        st.subheader("질문/답변")

        if  (audio.duration_seconds > 0)  and (st.session_state["check_reset"]==False):
            response = ask_gpt(st.session_state["messages"], model)

            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                             unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                             unsafe_allow_html=True)
                    st.write("")

            TTS(response)

        else:
            st.session_state["check_reset"] = False

if __name__=="__main__":
    main()