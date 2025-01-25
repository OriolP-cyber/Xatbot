import streamlit as st
import pyaudio
import wave
import numpy as np
import io
from langchain_openai import ChatOpenAI
import speech_recognition as sr

# Obtenir la clau API des dels secrets
api_key = st.secrets["openai"]["api_key"]

# Inicialitzar model de lenguatge
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")

# Inicialitzar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar missategs previs
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funció gravar audio
def record_audio(duration=5, samplerate=44100):
    st.write("Iniciando grabación...")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=2, rate=samplerate, input=True, frames_per_buffer=1024)
    frames = []

    for _ in range(0, int(samplerate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_bytes = io.BytesIO()
    with wave.open(audio_bytes, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(samplerate)
        wf.writeframes(b''.join(frames))
    return audio_bytes.getvalue()

# Funció transcriure audio
def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_data)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ca-ES")

# Lógica per gravar audio quan es presiona el botó "Gravar audio"
if st.button("Gravar audio"):
    st.session_state.recording = True
    st.session_state.audio_data = None  # Reiniciar dades audio anteriors

# Si se está gravant, iniciem la gravació
if "recording" in st.session_state and st.session_state.recording:
    audio_data = record_audio()  # Inicia la gravació
    st.session_state.audio_data = audio_data
    st.session_state.recording = False  # Dete la gravació per obtener audio

# Procesar audio gravat, si existeix
if st.session_state.get("audio_data"):
    text = transcribe_audio(st.session_state.audio_data)
    if text:
        st.write("tu: ", text)
        st.session_state.messages.append({"role": "user", "content": text})
        response = llm.invoke(st.session_state.messages).content
        st.write("Resposta del model: ", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Reactivar la entrada de text
if prompt := st.chat_input("Escriu el teu missatge..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = llm.invoke(st.session_state.messages).content
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})