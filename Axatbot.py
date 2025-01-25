import streamlit as st
import requests
import time
from langchain_openai import ChatOpenAI

# Obtener la clave API desde los secretos de Streamlit
api_key = st.secrets["openai"]["api_key"]
assemblyai_api_key = st.secrets["assemblyai"]["api_key"]

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

# Función para transcribir audio usando AssemblyAI
def transcribe_audio(audio_data):
    headers = {
        "authorization": assemblyai_api_key,
        "content-type": "application/json"
    }

    # Subir el archivo de audio
    upload_response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=headers,
        files={"file": audio_data}
    )

    if upload_response.status_code != 200:
        st.write(f"Error al subir el archivo: {upload_response.json()}")
        return None

    audio_url = upload_response.json().get("upload_url")
    if not audio_url:
        st.write("No se pudo obtener la URL del archivo subido.")
        return None

    # Solicitar la transcripción
    transcript_request = {
        "audio_url": audio_url
    }
    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=transcript_request,
        headers=headers
    )

    if transcript_response.status_code != 200:
        st.write(f"Error al solicitar la transcripción: {transcript_response.json()}")
        return None

    transcript_id = transcript_response.json().get("id")
    if not transcript_id:
        st.write("No se recibió un ID de transcripción.")
        return None

    # Esperar hasta que se complete la transcripción
    while True:
        transcript_result = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        )

        if transcript_result.status_code != 200:
            st.write(f"Error al obtener el resultado de la transcripción: {transcript_result.json()}")
            return None

        transcript_status = transcript_result.json().get("status")
        if transcript_status == "completed":
            return transcript_result.json().get("text")
        elif transcript_status == "failed":
            st.write("La transcripción ha fallado.")
            return None

        time.sleep(5)

# Lógica para subir y procesar audio
uploaded_file = st.file_uploader("Sube un archivo de audio", type=["wav", "mp3"])

if uploaded_file is not None:
    audio_data = uploaded_file.read()
    text = transcribe_audio(audio_data)
    if text:
        st.write("**Tu:** ", text)
        st.session_state.messages.append({"role": "user", "content": text})
        response = llm.predict_messages(st.session_state.messages).content
        st.write("**Respuesta del modelo:** ", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Reactivar la entrada de texto
if prompt := st.chat_input("Escriu el teu missatge..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = llm.predict_messages(st.session_state.messages).content
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
