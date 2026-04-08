import streamlit as st
from PyPDF2 import PdfReader
import re
import spacy

st.title("Upload Your CV")
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
text = ""


def extract_gender(text):
    text = text.lower()
    if any(word in text for word in ["male"]):
        return "Male"
    elif any(word in text for word in ["female"]):
        return "Female"
    else:
        return None

def extract_email(text):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(pattern, text)
    return emails[0] if emails else None

def extract_phone(text):
    # 1️⃣ نشيل أي newline أو formatting
    text = text.replace("\n", " ")

    # 2️⃣ نشيل أي حاجة مش رقم أو +
    cleaned = re.sub(r"[^\d+]", "", text)

    # 3️⃣ نبحث عن رقم مصري
    pattern = r"(?:\+20|0)?1[0125]\d{8}"
    phones = re.findall(pattern, cleaned)

    return phones[0] if phones else None

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
     
        for page in reader.pages:
            text += page.extract_text()
        st.text_area("CV Content ", text, height= 200)
        phone = extract_phone(text)
        st.title(phone)

        email = extract_email(text)

        st.title(email)

        doc = nlp(text)
        cities_list = ["Cairo"]
        for ent in doc.ents:
            if ent.label_ == "GPE" and ent.text[:100] in cities_list:  # Geo-political entity
              st.title(ent.text)
              break
        






