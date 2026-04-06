import streamlit as st
from PyPDF2 import PdfReader


st.title("Upload Your CV")

# رفع الملف
uploaded_file = st.file_uploader("Choose a CV file (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    # عرض اسم الملف
    st.success(f"Uploaded file: {uploaded_file.name}")

    # لو عايز تقرأ محتوى PDF أو DOCX ممكن تضيف هنا
    # مثال لو PDF:
    if uploaded_file.type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        st.text_area("CV Content (first 500 chars)", text)