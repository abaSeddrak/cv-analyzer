import streamlit as st
from PyPDF2 import PdfReader
import re
import spacy
import json
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

# DB
from database import SessionLocal, engine, Base
from models import CV
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
st.write("KEY:", OPENAI_API_KEY)
st.title("CV Analyzer AI 🚀")

# تحميل NLP
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# =========================
# Extraction Functions
# =========================

def extract_email(text):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(pattern, text)
    return emails[0] if emails else None


def extract_phone(text):
    text = text.replace("\n", " ")
    cleaned = re.sub(r"[^\d+]", "", text)
    pattern = r"(?:\+20|0)?1[0125]\d{8}"
    phones = re.findall(pattern, cleaned)
    return phones[0] if phones else None


def extract_name(text):
    first_line = text.split("\n")[0]
    return first_line.strip()


def extract_city(doc):
    cities_list = ["Cairo", "Alexandria", "Giza"]
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text in cities_list:
            return ent.text
    return None


def extract_skills(text):
    skills_keywords = [
        "flutter", "dart", "firebase", "api",
        "python", "java", "sql", "react"
    ]

    found = []
    for skill in skills_keywords:
        if skill.lower() in text.lower():
            found.append(skill)

    return found


# =========================
# AI Evaluation
# =========================

def evaluate_cv_with_ai(cv_data):
    prompt = f"""
    You are an HR expert.

    Evaluate this candidate based on the following:

    Name: {cv_data.get("name")}
    Skills: {cv_data.get("skills")}
    City: {cv_data.get("city")}

    Return ONLY JSON:
    {{
      "overall_score": number,
      "recommendation": "Reject or Consider or Strong Hire"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an HR expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result_text = response.choices[0].message.content

        return json.loads(result_text)

    except Exception as e:
        print("AI Error:", e)
        return {
            "overall_score": 50,
            "recommendation": "Consider"
        }


# =========================
# Upload CV
# =========================

uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])

if uploaded_file:

    text = ""

    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        text += page.extract_text()

    st.subheader("Extracted Text")
    st.text_area("", text, height=200)

    # NLP
    doc = nlp(text)

    # Extract Data
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    city = extract_city(doc)
    skills = extract_skills(text)

    st.subheader("Extracted Data")
    st.write("Name:", name)
    st.write("Email:", email)
    st.write("Phone:", phone)
    st.write("City:", city)
    st.write("Skills:", skills)

    # =========================
    # AI Evaluation
    # =========================

    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,
        "skills": skills
    }

    if st.button("Evaluate CV 🤖"):

        with st.spinner("Analyzing..."):

            ai_result = evaluate_cv_with_ai(payload)

            score = ai_result.get("overall_score")
            recommendation = ai_result.get("recommendation")

            st.success(f"Score: {score}")
            st.success(f"Recommendation: {recommendation}")

            # =========================
            # Save to DB
            # =========================

            new_cv = CV(
                name=name,
                email=email,
                phone=phone,
                city=city,
                score=score,
                recommendation=recommendation
            )

            db.add(new_cv)
            db.commit()
            db.refresh(new_cv)

            # =========================
            # Send to API
            # =========================

            api_payload = {
                "name": name,
                "email": email,
                "phone": phone,
                "city": city,
                "score": score,
                "recommendation": recommendation
            }

            try:
                response = requests.post(
                    "https://cv-analyzer-5i6i.onrender.com/cvs",
                    json=api_payload
                )

                if response.status_code == 200:
                    st.success("Saved to API ✅")
                else:
                    st.error(f"API Error: {response.text}")

            except Exception as e:
                st.error(f"Connection Error: {e}")