import streamlit as st

st.set_page_config(
    page_title="GenAI Legal Assistant",
    layout="wide"
)

st.title("📄 GenAI-Powered Legal Assistant for SMEs")
st.write("Upload a contract file to analyze risks and clauses.")

uploaded_file = st.file_uploader(
    "Upload Contract (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    st.success("File uploaded successfully!")
