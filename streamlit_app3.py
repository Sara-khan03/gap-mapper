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
    </style>
""", unsafe_allow_html=True)

# ---------------- RESUME ANALYZER ---------------- #
def analyze_resume(text, field):
    issues = []
    suggestions = []

    # Weakness checks
    if "internship" not in text.lower():
        issues.append("No internship experience mentioned.")
        suggestions.append("Consider applying for internships. [Internshala](https://internshala.com) or [LinkedIn](https://linkedin.com/jobs).")

    if "project" not in text.lower():
        issues.append("Projects not highlighted.")
        suggestions.append("Add field-related projects to showcase practical skills.")

    if len(text.split()) < 150:
        issues.append("Resume seems too short.")
        suggestions.append("Add more details like skills, achievements, certifications.")

    if "skills" not in text.lower():
        issues.append("Skills section missing.")
        suggestions.append("Clearly mention technical, soft, and field-specific skills.")

    if field == "Technology" and "python" not in text.lower():
        suggestions.append("Python is highly in demand in Tech roles – consider learning it.")

    if field == "Business" and "finance" not in text.lower():
        suggestions.append("Consider strengthening business/finance keywords.")

    return issues, suggestions

# ---------------- EVENTS & COMPETITIONS ---------------- #
def get_events(field):
    data = {
        "Technology": [
            {"name": "Global AI Hackathon", "date": "Oct 2025", "link": "https://devpost.com", "desc": "Build innovative AI solutions."},
            {"name": "Open Source Fest", "date": "Dec 2025", "link": "https://github.com", "desc": "Collaborate on open source projects."}
        ],
        "Sports": [
            {"name": "National Athletics Championship", "date": "Sep 2025", "link": "https://sportsauthorityofindia.nic.in", "desc": "Track & field events."},
            {"name": "Inter-City Football Cup", "date": "Nov 2025", "link": "https://aiff.com", "desc": "Local football competition."}
        ],
        "Medical": [
            {"name": "World Health Congress", "date": "Oct 2025", "link": "https://who.int", "desc": "Global healthcare innovations."},
            {"name": "AI in Medicine Summit", "date": "Nov 2025", "link": "https://medtech.com", "desc": "Intersection of AI & Healthcare."}
        ],
        "Business": [
            {"name": "Startup Pitch Fest", "date": "Oct 2025", "link": "https://startupindia.gov.in", "desc": "Pitch your business idea."},
            {"name": "Global Finance Summit", "date": "Nov 2025", "link": "https://forbes.com", "desc": "Networking for business leaders."}
        ],
    }
    return data.get(field, [])

# ---------------- COURSES & INTERNSHIPS ---------------- #
courses = {
    "Technology": ["Python Basics - FreeCodeCamp", "Data Science - Coursera", "AI/ML - Udemy"],
    "Sports": ["Sports Nutrition - Alison", "Athlete Training - FutureLearn", "Sports Analytics - Coursera"],
    "Medical": ["Public Health - edX", "Surgery Basics - MedMastery", "AI in Medicine - Coursera"],
    "Business": ["Finance - Coursera", "Entrepreneurship - Harvard Online", "Digital Marketing - Udemy"]
}

internships = {
    "Technology": ["Google Summer of Code", "Microsoft Internship", "TCS Ignite"],
    "Sports": ["Sports Authority of India Internships", "Fitness Startups", "Coaching Internships"],
    "Medical": ["Hospital Internships", "WHO Internships", "AIIMS Delhi Internship"],
    "Business": ["KPMG Internship", "PwC India Internship", "Start-up Internships"]
}

# ---------------- NAVIGATION ---------------- #
menu = st.sidebar.radio("Navigate", ["Home + Resume Analyzer", "Courses & Internships", "Events & Competitions", "Career Tips Bot", "Resources"])

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

        st.subheader("Resume Analysis 🔍")
        issues, suggestions = analyze_resume(text, field)

        if issues:
            st.error("Weaknesses Found:")
            for i in issues:
                st.write("- ", i)
        else:
            st.success("Your resume looks strong!")

        st.info("Suggestions for Improvement:")
        for s in suggestions:
            st.write("✅ ", s)

# ---------------- COURSES & INTERNSHIPS ---------------- #
elif menu == "Courses & Internships":
    st.header("📚 Courses & Internships")
    field = st.selectbox("Choose your field:", ["Technology", "Sports", "Medical", "Business"])

    st.subheader("Recommended Courses")
    for c in courses[field]:
        st.write("📘", c)

    st.subheader("Internships")
    for i in internships[field]:
        st.write("💼", i)

# ---------------- EVENTS & COMPETITIONS ---------------- #
elif menu == "Events & Competitions":
    st.header("🏆 Events & Competitions")
    field = st.selectbox("Select your field:", ["Technology", "Sports", "Medical", "Business"])

    events = get_events(field)
    for e in events:
        st.markdown(f"### {e['name']} ({e['date']})")
        st.write(e["desc"])
        st.markdown(f"[🔗 Register Here]({e['link']})")

# ---------------- CAREER TIPS BOT ---------------- #
elif menu == "Career Tips Bot":
    st.header("🤖 AI Career Assistant")
    query = st.text_input("Ask me anything about careers (skills, jobs, tips)...")
    if query:
        responses = [
            "Focus on building projects to showcase your skills.",
            "Networking on LinkedIn can open hidden opportunities.",
            "Consistency in learning is more important than speed."
        ]
        st.write("💡", random.choice(responses))

# ---------------- RESOURCES ---------------- #
elif menu == "Resources":
    st.header("🌐 Career Resources Hub")
    st.write("📄 Resume Templates: [Canva](https://www.canva.com/resumes/templates/)")
    st.write("💻 Freelancing: [Upwork](https://upwork.com), [Fiverr](https://fiverr.com)")
    st.write("🎓 Scholarships: [DAAD](https://daad.de), [Chevening](https://chevening.org)")
    st.write("🏆 Competitions: [Kaggle](https://kaggle.com), [Devpost](https://devpost.com)")

st.markdown("---")
st.caption("⚠️ Disclaimer: This is a career guidance tool. Always verify details from official sources before applying.")
