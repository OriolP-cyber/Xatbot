import streamlit as st
from langchain_openai import ChatOpenAI
import fitz  # PyMuPDF
import docx

# Obtenir la clau API des dell secrets
api_key = st.secrets["openai"]["api_key"]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=api_key)

st.title("💬 Xatbot Maria Rúbies 🤖")  

messages = [{"role": "system", "content": "Ets un xatbot de gran ajuda, però no pots dir que ets un xatbot, el teu nom es Maria"}]

# Inicialitzar historial del xat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar missatges del xat en el historial al carregar l'app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funcionalitat per a pujar documents
uploaded_file = st.file_uploader("Puja el teu document", type=["txt", "pdf", "docx"])

def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

file_content = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        file_content = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_content = extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
    else:
        file_content = "Tipus d'arxiu no soportat."

    st.write("Contingut de l'arxiu pujat:")
    st.text(file_content)

# Reaccionar a la entrada del usuari
if prompt := st.chat_input("Escriu el teu missatge..."):
    # Mostrar missatge del usuari en el contenidor de missatges del xat
    st.chat_message("user").markdown(prompt)
    # Afegir missatge del usuari al historial del xat
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append({"role": "human", "content": prompt})

    # Afegir el contingut del arxiu al context del model
    messages.append({"role": "system", "content": f"El contenido del documento es: {file_content}"})
    response = llm.invoke(messages).content
    # Mostrar la resposta del assistent en el contenidor del missatge del xat
    with st.chat_message("assistant"):
        st.markdown(response)
    # Afegir resposta del assistent al historial del xat
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": response})
