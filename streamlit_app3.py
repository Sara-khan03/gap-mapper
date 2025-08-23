import streamlit as st
import pdfplumber
import docx2txt
import requests
from datetime import datetime

# ----------------- STATIC DATA -----------------
courses_data = {
    "Technology": [
        {"title": "Python for Everybody (Free)", "link": "https://www.coursera.org/specializations/python", 
         "requirements": "Beginner friendly", "start": "Anytime", "end": "Self-paced"},
        {"title": "Data Science Professional Certificate (Paid)", "link": "https://www.coursera.org/professional-certificates/ibm-data-science", 
         "requirements": "Basic Python", "start": "2025-09-01", "end": "2026-01-01"},
    ],
    "Business": [
        {"title": "Introduction to Business (Free)", "link": "https://online.hbs.edu", 
         "requirements": "None", "start": "Anytime", "end": "Self-paced"},
        {"title": "Wharton Business Strategy (Paid)", "link": "https://www.coursera.org/specializations/wharton-strategy", 
         "requirements": "Bachelor’s degree preferred", "start": "2025-10-01", "end": "2026-02-01"},
    ],
    "Medical": [
        {"title": "Basics of Clinical Research", "link": "https://nptel.ac.in", 
         "requirements": "Medical/Science background", "start": "2025-09-15", "end": "2026-01-30"},
    ],
    "Sports": [
        {"title": "Sports Nutrition Fundamentals", "link": "https://www.edx.org", 
         "requirements": "Interest in sports", "start": "2025-09-10", "end": "2026-02-10"},
    ],
    "Law": [
        {"title": "International Law (Free)", "link": "https://www.coursera.org/learn/international-law", 
         "requirements": "None", "start": "Anytime", "end": "Self-paced"},
    ],
    "Arts & Design": [
        {"title": "Graphic Design Specialization", "link": "https://www.coursera.org/specializations/graphic-design", 
         "requirements": "Creativity & computer access", "start": "Anytime", "end": "Self-paced"},
    ]
}

internships_data = {
    "Technology": [
        {"title": "Web Development Intern", "company": "Google", "location": "Bangalore", 
         "stipend": "₹20,000/month", "requirements": "HTML, CSS, JS", 
         "start": "2025-09-01", "end": "2025-09-20", "link": "https://careers.google.com"},
    ],
    "Business": [
        {"title": "Marketing Intern", "company": "Unilever", "location": "Mumbai", 
         "stipend": "₹15,000/month", "requirements": "MBA Student", 
         "start": "2025-09-05", "end": "2025-09-25", "link": "https://unilever.com/careers"},
    ],
    "Medical": [
        {"title": "Clinical Research Intern", "company": "AIIMS", "location": "Delhi", 
         "stipend": "₹10,000/month", "requirements": "Medical student", 
         "start": "2025-09-10", "end": "2025-09-30", "link": "https://aiims.edu"},
    ],
    "Sports": [
        {"title": "Sports Analyst Intern", "company": "ESPN India", "location": "Hyderabad", 
         "stipend": "₹12,000/month", "requirements": "Sports knowledge, analytics", 
         "start": "2025-09-15", "end": "2025-10-05", "link": "https://espncricinfo.com"},
    ]
}

# ----------------- HELPER FUNCTIONS -----------------
def extract_text_from_resume(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        text = docx2txt.process(uploaded_file)
    return text.lower()

def analyze_resume(text):
    missing = []
    if "internship" not in text:
        missing.append("Internship experience")
    if "project" not in text:
        missing.append("Project experience")
    if "python" not in text:
        missing.append("Python skill (for tech fields)")
    return missing

# ----------------- STREAMLIT APP -----------------
def main():
    st.set_page_config(page_title="Career Gap Mapper", layout="wide")
    st.title("🧭 Career Gap Mapper")
    st.write("Upload your resume & get personalized recommendations (Courses, Internships, Events).")

    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    field = st.selectbox("Select your career field", list(courses_data.keys()))
    location = st.text_input("Enter your city (for internships)", "")

    if uploaded_file:
        text = extract_text_from_resume(uploaded_file)
        st.subheader("📑 Resume Analysis")
        missing = analyze_resume(text)
        if missing:
            st.warning("⚠️ Gaps Found in Resume:")
            for m in missing:
                st.write(f"- {m}")
        else:
            st.success("✅ Your resume looks strong!")

        # ---------- Recommended Courses ----------
        st.subheader("🎓 Recommended Courses")
        for c in courses_data.get(field, []):
            st.markdown(f"**[{c['title']}]({c['link']})**")
            st.write(f"📝 Requirements: {c['requirements']}")
            st.write(f"📅 Start: {c['start']} → {c['end']}")
            st.write("---")

        # ---------- Recommended Internships ----------
        st.subheader("💼 Recommended Internships")
        for i in internships_data.get(field, []):
            if location.lower() in i["location"].lower() or location == "":
                st.markdown(f"**{i['title']}** at **{i['company']}** ({i['location']})")
                st.write(f"💰 Stipend: {i['stipend']}")
                st.write(f"📝 Requirements: {i['requirements']}")
                st.write(f"📅 Apply: {i['start']} → {i['end']}")
                st.markdown(f"[Apply Here]({i['link']})")
                st.write("---")

if __name__ == "__main__":
    main()
