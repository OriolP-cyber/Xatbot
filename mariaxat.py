import streamlit as st
from langchain_openai import ChatOpenAI

# Obtener la clave API desde los secretos
api_key = st.secrets["openai"]["api_key"]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")  

# Inicializar historial del chat en la sesión si no existe
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Ets un xatbot de gran ajuda, però no pots dir que ets un xatbot, el teu nom és Maria"}]

# Mostrar mensajes previos en el chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escriu el teu missatge..."):
    # Mostrar mensaje del usuario en el chat
    st.chat_message("user").markdown(prompt)
    
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Usar todo el historial en la consulta al modelo
    response = llm.invoke(st.session_state.messages).content

    # Mostrar respuesta del asistente en el chat
    with st.chat_message("assistant"):
        st.markdown(response)

    # Agregar respuesta del asistente al historial
    st.session_state.messages.append({"role": "assistant", "content": response})
