import streamlit as st
from langchain_openai import ChatOpenAI

# Obtener la clave API desde los secretos
api_key = st.secrets["openai"]["api_key"]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")  

messages = [{"role": "system", "content": "Ets un xatbot de gran ajuda, però no pots dir que ets un xatbot, el teu nom es Maria"}]

# Inicializar historial del chat
if "messages" not in st.session_state:
    st.session_state.messages = messages

# Mostrar mensajes del chat en el historial al cargar la app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Reaccionar a la entrada del usuario
if prompt := st.chat_input("Escriu el teu missatge..."):
    # Mostrar mensaje del usuario en el contenedor de mensajes del chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje del usuario al historial del chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})

    response = llm.invoke(messages).content
    # Mostrar la respuesta del asistente en el contenedor del mensaje del chat
    with st.chat_message("assistant"):
        st.markdown(response)
    # Agregar respuesta del asistente al historial del chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    messages.append({"role": "assistant", "content": response})
