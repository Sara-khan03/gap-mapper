import streamlit as st
import pdfplumber
import docx2txt
import re
import random

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Career Gap Mapper",
    layout="wide",
    page_icon="🎯",
)

# ---------------- STYLING ---------------- #
st.markdown("""
    <style>
    .main { background-color: #f9fafc; }
    .big-title { font-size: 40px; font-weight: bold; color: #2E86AB; }
    .subtitle { font-size: 22px; color: #1B4F72; }
    .encourage { font-size: 18px; font-style: italic; color: #117A65; }
    .highlight { background-color: #fffae6; padding: 4px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- GLOBAL RESUME TEXT ---------------- #
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""

# ---------------- RESUME ANALYZER ---------------- #
def analyze_resume(text, field):
    issues = []
    suggestions = []
    keywords = []

    if "internship" not in text.lower():
        issues.append("No internship experience mentioned.")
        suggestions.append("Apply for internships related to your field.")
        keywords.append("internship")

    if "project" not in text.lower():
        issues.append("Projects not highlighted.")
        suggestions.append("Add relevant field projects.")
        keywords.append("project")

    if len(text.split()) < 150:
        issues.append("Resume seems short.")
        suggestions.append("Add achievements, certifications, experiences.")
        keywords.append("experience")

    if "skills" not in text.lower():
        issues.append("Skills section missing.")
        suggestions.append("Add technical, soft, and field-specific skills.")
        keywords.append("skills")

    # Field specific
    if field == "Technology" and "python" not in text.lower():
        suggestions.append("Python is in-demand – consider learning it.")
        keywords.append("python")

    if field == "Business" and "finance" not in text.lower():
        suggestions.append("Add finance/business-related terms.")
        keywords.append("finance")

    return issues, suggestions, set(keywords)

# ---------------- COURSES & INTERNSHIPS ---------------- #
courses = {
    "Technology": [
        {"title": "Python for Everybody", "type": "Free", "desc": "Learn Python from basics.", "skill": "python"},
        {"title": "Data Science Specialization (Coursera)", "type": "Paid", "desc": "Complete data science roadmap.", "skill": "data science"},
        {"title": "Full-Stack Web Development (FreeCodeCamp)", "type": "Free", "desc": "Learn web development.", "skill": "web development"},
        {"title": "AI/ML Specialization (Udemy)", "type": "Paid", "desc": "Machine Learning from scratch.", "skill": "machine learning"},
    ],
    "Sports": [
        {"title": "Sports Nutrition (Alison)", "type": "Free", "desc": "Learn athlete diet science.", "skill": "nutrition"},
        {"title": "Sports Coaching (FutureLearn)", "type": "Paid", "desc": "Professional coaching methods.", "skill": "coaching"},
        {"title": "Sports Analytics (Coursera)", "type": "Paid", "desc": "Apply data to sports.", "skill": "sports analytics"},
    ],
    "Medical": [
        {"title": "Public Health (edX)", "type": "Free", "desc": "Basics of public health.", "skill": "public health"},
        {"title": "AI in Medicine (Coursera)", "type": "Paid", "desc": "How AI is transforming medicine.", "skill": "ai medicine"},
        {"title": "Surgery Basics (MedMastery)", "type": "Paid", "desc": "Surgical skills for beginners.", "skill": "surgery"},
    ],
    "Business": [
        {"title": "Finance for Non-Finance (Coursera)", "type": "Paid", "desc": "Core finance skills.", "skill": "finance"},
        {"title": "Entrepreneurship (Harvard)", "type": "Paid", "desc": "Start and grow a business.", "skill": "entrepreneurship"},
        {"title": "Digital Marketing (Udemy)", "type": "Paid", "desc": "Complete digital marketing.", "skill": "marketing"},
    ]
}

internships = {
    "Technology": [
        {"title": "Google Summer of Code", "req": "Strong coding skills", "paid": True},
        {"title": "Microsoft Internship", "req": "CS background, problem solving", "paid": True},
        {"title": "Startup Tech Internships", "req": "Web/AI projects", "paid": False},
    ],
    "Sports": [
        {"title": "Sports Authority of India Internship", "req": "Sports science knowledge", "paid": True},
        {"title": "Football Coaching Internship", "req": "Training experience", "paid": False},
    ],
    "Medical": [
        {"title": "WHO Internship", "req": "Public health interest", "paid": False},
        {"title": "AIIMS Delhi Internship", "req": "Medical student background", "paid": True},
    ],
    "Business": [
        {"title": "KPMG Internship", "req": "Finance/Accounting skills", "paid": True},
        {"title": "Startup India Internship", "req": "Entrepreneurial mindset", "paid": False},
    ]
}

# ---------------- NAVIGATION ---------------- #
menu = st.sidebar.radio("Navigate", ["Home + Resume Analyzer", "Courses & Internships"])

# ---------------- HOME + RESUME ANALYZER ---------------- #
if menu == "Home + Resume Analyzer":
    st.markdown("<p class='big-title'>🎯 Career Gap Mapper</p>", unsafe_allow_html=True)
    st.markdown("<p class='encourage'>Turn your career gaps into stepping stones for success!</p>", unsafe_allow_html=True)

    field = st.selectbox("Choose your field:", ["Technology", "Sports", "Medical", "Business"])
    uploaded = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])

    if uploaded:
        text = ""
        if uploaded.name.endswith(".pdf"):
            with pdfplumber.open(uploaded) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        else:
            text = docx2txt.process(uploaded)

        st.session_state["resume_text"] = text

        st.subheader("Resume Analysis 🔍")
        issues, suggestions, missing_keywords = analyze_resume(text, field)

        if issues:
            st.error("Weaknesses Found:")
            for i in issues:
                st.write("- ", i)
        else:
            st.success("Your resume looks strong!")

        st.info("Suggestions for Improvement:")
        for s in suggestions:
            st.write("✅ ", s)

        st.session_state["missing_keywords"] = missing_keywords

# ---------------- COURSES & INTERNSHIPS ---------------- #
elif menu == "Courses & Internships":
    st.header("📚 Courses & Internships")
    field = st.selectbox("Choose your field:", ["Technology", "Sports", "Medical", "Business"])

    st.subheader("Recommended Courses")
    for c in courses[field]:
        st.markdown(f"**{c['title']}** ({c['type']})")
        st.write("📘", c["desc"])
        if "missing_keywords" in st.session_state and c["skill"].lower() in st.session_state["missing_keywords"]:
            st.markdown(f"<span class='highlight'>⚠️ This skill is missing in your resume</span>", unsafe_allow_html=True)
        st.write("")

    st.subheader("Internships")
    for i in internships[field]:
        st.markdown(f"**{i['title']}**")
        st.write("📝 Requirement:", i["req"])
        st.write("💰 Paid:", "Yes" if i["paid"] else "No")
        if "missing_keywords" in st.session_state and any(word in i["req"].lower() for word in st.session_state["missing_keywords"]):
            st.markdown(f"<span class='highlight'>⚠️ You might lack the requirement listed</span>", unsafe_allow_html=True)
        st.write("")
