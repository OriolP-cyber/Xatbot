import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import wave
import io
from langchain_openai import ChatOpenAI
import speech_recognition as sr

# Obtener la clave API desde los secretos de Streamlit
api_key = st.secrets["openai"]["api_key"]

# Inicializar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, openai_api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Definir un procesador de audio para Streamlit WebRTC
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_data = None

    def recv(self, frame):
        # Convertir el frame de WebRTC a formato WAV en memoria
        self.audio_data = frame.to_ndarray()
        return frame

# Función para transcribir audio
def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_data)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ca-ES")

# Iniciar la captura de audio desde el micrófono con Streamlit WebRTC
def record_audio():
    webrtc_streamer(
        key="audio-stream",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )

# Lógica para grabar audio cuando se presiona el botón "Gravar audio"
if st.button("Gravar audio"):
    st.session_state.recording = True
    st.session_state.audio_data = None  # Reiniciar datos de audio anteriores

# Si se está grabando, iniciar la grabación
if "recording" in st.session_state and st.session_state.recording:
    record_audio()  # Iniciar la grabación con WebRTC

# Procesar audio grabado, si existe
if st.session_state.get("audio_data"):
    audio_data = st.session_state.audio_data
    text = transcribe_audio(audio_data)
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
