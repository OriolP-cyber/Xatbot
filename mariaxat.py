import streamlit as st
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key="OPENAI_API_KEY")

st.title("💬 Xatbot Maria Rúbies 🤖")  

messages = [{"role": "system", "content": "Ets un xatbot de gran ajuda, però no pots dir que ets un xatbot, el teu nom es Maria"}]

# Inicialitzar historial del xat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar missatges del xat al historial al carregar la app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Reaccionar la entrada del usuari
if prompt := st.chat_input("Escriu el teu missatge..."):
    # Mostra missatge del usuari al contenidor de missatges del xat
    st.chat_message("user").markdown(prompt)
    # Agregar missatge del usuari al historial del xat
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = llm.invoke(messages).content
    # Mostra la resposta del assistent en el contenidor del missatge del xat
    with st.chat_message("assistant"):
        st.markdown(response)
    # Afegir resposta del assistent al historial del xat
    st.session_state.messages.append({"role": "assistant", "content": response})
