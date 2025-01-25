import streamlit as st
import sounddevice as sd
import wave
import numpy as np
import io
from langchain.chat_models import ChatOpenAI
import speech_recognition as sr

# Obtener la clave API desde los secretos de Streamlit
api_key = st.secrets["openai"]["api_key"]

# Inicializar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4", temperature=1, openai_api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Función para grabar audio
def record_audio(duration=5, samplerate=44100):
    st.write("🎙️ Iniciando grabación...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()  # Esperar a que termine la grabación

    # Convertir datos de audio en formato WAV
    audio_bytes = io.BytesIO()
    with wave.open(audio_bytes, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # Tamaño de muestra: 16 bits (2 bytes)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    st.write("✅ Grabación completada.")
    return audio_bytes.getvalue()


# Función para transcribir audio
def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_data)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ca-ES")


# Lógica para grabar audio cuando se presiona el botón "Gravar audio"
if st.button("Gravar audio"):
    st.session_state.recording = True
    st.session_state.audio_data = None  # Reiniciar datos de audio anteriores

# Si se está grabando, iniciar la grabación
if "recording" in st.session_state and st.session_state.recording:
    audio_data = record_audio()  # Iniciar la grabación
    st.session_state.audio_data = audio_data
    st.session_state.recording = False  # Detener la grabación para obtener audio

# Procesar audio grabado, si existe
if st.session_state.get("audio_data"):
    text = transcribe_audio(st.session_state.audio_data)
    if text:
        st.write("**Tu:** ", text)
        st.session_state.messages.append({"role": "user", "content": text})
        response = llm.predict_messages(st.session_state.messages).content
        st.write("**Resposta del model:** ", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Reactivar la entrada de texto
if prompt := st.chat_input("Escriu el teu missatge..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = llm.predict_messages(st.session_state.messages).content
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
