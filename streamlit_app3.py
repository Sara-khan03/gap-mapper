import streamlit as st
import pdfplumber
import docx2txt

st.set_page_config(page_title="Career Gap Mapper", layout="wide")

# Sidebar Navigation (removed separate analyzer)
menu = [
    "🏠 Home (Resume Analyzer)", "🎓 Courses & Internships",
    "🧭 Career Roadmaps", "📅 Events", "🎁 Inspire Me"
]
choice = st.sidebar.radio("Navigate", menu)

# -------- Helper Functions ----------
def extract_text_from_resume(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    elif file.name.endswith(".docx"):
        text = docx2txt.process(file)
    else:  # TXT
        text = file.read().decode("utf-8")
    return text

def analyze_resume(text, field):
    findings = {"skills": [], "education": [], "internships": [], "certifications": []}
    text_lower = text.lower()

    # Base keywords
    base_skills = ["leadership", "communication", "teamwork", "project", "excel"]
    edu_keywords = ["bachelor", "master", "phd", "mba", "degree", "school"]
    intern_keywords = ["internship", "trainee", "apprentice"]
    cert_keywords = ["certified", "certificate", "certification", "coursera", "udemy", "edx"]

    # Field-specific keywords
    field_keywords = {
        "Tech": ["python", "java", "c++", "machine learning", "ai", "data science", "sql", "cloud"],
        "Medical": ["mbbs", "doctor", "nurse", "surgery", "clinical", "patient", "pharma"],
        "Sports": ["athlete", "tournament", "championship", "medal", "training", "fitness"],
        "Business": ["management", "strategy", "finance", "marketing", "startup", "sales"]
    }

    # Check skills
    for skill in base_skills + field_keywords.get(field, []):
        if skill in text_lower:
            findings["skills"].append(skill)

    # Other checks
    for edu in edu_keywords:
        if edu in text_lower:
            findings["education"].append(edu)
    for i in intern_keywords:
        if i in text_lower:
            findings["internships"].append(i)
    for c in cert_keywords:
        if c in text_lower:
            findings["certifications"].append(c)

    return findings

def suggest_actions(results, field):
    suggestions = []

    if not results["internships"]:
        suggestions.append("📌 No internships found — apply for internships to gain experience.")
    if not results["certifications"]:
        suggestions.append("📌 No certifications found — add at least 1-2 industry-recognized certifications.")
    if len(results["skills"]) < 3:
        suggestions.append("📌 Very few skills detected — improve your skillset.")

    # Field-specific suggestions
    if field == "Tech":
        suggestions += [
            "💻 Learn coding & problem-solving on [LeetCode](https://leetcode.com)",
            "☁️ Get cloud certification: [AWS Training](https://aws.amazon.com/training/)",
            "📊 Data skills: [Kaggle](https://kaggle.com)"
        ]
    elif field == "Medical":
        suggestions += [
            "🏥 Join medical conferences on [WHO Events](https://www.who.int/news-room/events)",
            "📖 Free courses: [Medscape](https://www.medscape.org)",
            "💉 Research internships: [PubMed Clinical Trials](https://clinicaltrials.gov)"
        ]
    elif field == "Sports":
        suggestions += [
            "⚽ Check upcoming tournaments: [Khelo India](https://kheloindia.gov.in)",
            "💪 Fitness & diet courses: [Coursera Sports Science](https://www.coursera.org/specializations/sport-science)",
            "🏆 Apply for sports internships: [Internshala Sports](https://internshala.com)"
        ]
    elif field == "Business":
        suggestions += [
            "📈 Learn finance & marketing: [Coursera MBA Essentials](https://www.coursera.org/learn/essentials-of-mba)",
            "🤝 Networking: [LinkedIn Business](https://linkedin.com)",
            "🚀 Explore startup programs: [Y Combinator](https://www.ycombinator.com)"
        ]

    return suggestions

# -------- PAGES ----------
if choice == "🏠 Home (Resume Analyzer)":
    st.title("🚀 Career Gap Mapper — Resume Analyzer")
    st.subheader("Helping Everyone: Students | Sportspersons | Medical | Business | Tech")
    st.write("Upload your resume to detect **gaps** and get **personalized career suggestions** 🌟")

    field = st.selectbox("Select your career field:", ["Tech", "Medical", "Sports", "Business"])
    uploaded = st.file_uploader("📤 Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded:
        text = extract_text_from_resume(uploaded)
        results = analyze_resume(text, field)

        st.subheader("🔎 Resume Insights")
        st.write("**Skills Found:**", results["skills"] if results["skills"] else "❌ None detected")
        st.write("**Education Mentioned:**", results["education"] if results["education"] else "❌ None detected")
        st.write("**Internships:**", results["internships"] if results["internships"] else "❌ None detected")
        st.write("**Certifications:**", results["certifications"] if results["certifications"] else "❌ None detected")

        st.subheader("⚠️ Gaps Identified & Suggestions")
        actions = suggest_actions(results, field)
        for act in actions:
            st.markdown(f"- {act}")

    else:
        st.info("⬆️ Upload a resume file to get started")

# --- COURSES & INTERNSHIPS ---
elif choice == "🎓 Courses & Internships":
    st.title("🎓 Courses & Internships")
    st.markdown("Boost your resume with these resources:")
    st.write("- [Coursera](https://coursera.org)")
    st.write("- [Internshala](https://internshala.com)")
    st.write("- [Kaggle](https://kaggle.com)")

# --- ROADMAPS ---
elif choice == "🧭 Career Roadmaps":
    st.title("🧭 Career Roadmaps")
    st.write("Step-by-step learning paths for careers.")

# --- EVENTS ---
elif choice == "📅 Events":
    st.title("📅 Events & Competitions")
    st.write("- [Devpost Hackathons](https://devpost.com/hackathons)")
    st.write("- [Khelo India](https://kheloindia.gov.in)")
    st.write("- [Medical Conferences](https://www.who.int/news-room/events)")

# --- INSPIRE ME ---
elif choice == "🎁 Inspire Me":
    st.title("🎁 Inspire Me")
    st.success("💡 Every gap is an opportunity to grow!")
