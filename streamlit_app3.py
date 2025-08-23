import streamlit as st
import pdfplumber
import docx2txt
import requests
from bs4 import BeautifulSoup

# ============================
# UTILS: Resume Parsing
# ============================
def extract_text_from_resume(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    elif uploaded_file.name.endswith(".docx"):
        return docx2txt.process(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    else:
        return ""

def analyze_resume(text):
    gaps = []
    suggestions = []

    if "internship" not in text.lower():
        gaps.append("⚠️ No internships found")
        suggestions.append("Add internships or real-world projects to strengthen experience.")
    if "project" not in text.lower():
        gaps.append("⚠️ Projects missing")
        suggestions.append("Include personal or academic projects to showcase skills.")
    if "python" not in text.lower() and "java" not in text.lower():
        gaps.append("⚠️ No programming language skills detected")
        suggestions.append("Add technical skills like Python, Java, etc.")
    if "team" not in text.lower() and "lead" not in text.lower():
        gaps.append("⚠️ Teamwork/leadership not mentioned")
        suggestions.append("Mention teamwork, leadership, or communication skills.")

    return gaps, suggestions

# ============================
# UTILS: Scraping Events
# ============================
def fetch_devpost_events(field):
    url = "https://devpost.com/hackathons?challenge_type[]=online"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        events = []
        for card in soup.select('.hackathon-tile'):
            title = card.select_one('.title').get_text(strip=True) if card.select_one('.title') else "No Title"
            desc = card.select_one('.challenge-description').get_text(strip=True) if card.select_one('.challenge-description') else "No Description"
            link = "https://devpost.com" + card.find('a')['href']
            tag_text = card.get_text().lower()
            if field.lower() in tag_text or field.lower() in title.lower():
                events.append({"name": title, "desc": desc, "link": link})
        return events[:5]
    except Exception:
        return []

def fetch_kaggle_events():
    url = "https://www.kaggle.com/competitions"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        comps = []
        for card in soup.select('.competition-card__title'):
            comps.append({
                "name": card.get_text(strip=True),
                "link": "https://www.kaggle.com/competitions"
            })
        return comps[:5]
    except Exception:
        return []

# ============================
# STREAMLIT APP
# ============================
st.set_page_config(page_title="Career Gap Mapper", layout="wide")

menu = ["Home & Resume Analyzer", "Career Roadmap", "Courses & Internships", "Events & Competitions"]
choice = st.sidebar.radio("Navigate", menu)

# ============================
# HOME + RESUME ANALYZER
# ============================
if choice == "Home & Resume Analyzer":
    st.markdown("<h1 style='text-align:center;color:#2c3e50;'>📄 Career Gap Mapper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Analyze your resume and find gaps with personalized suggestions 🚀</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        text = extract_text_from_resume(uploaded_file)
        if text.strip():
            gaps, suggestions = analyze_resume(text)
            st.subheader("🔍 Resume Analysis")
            if gaps:
                st.error("⚠️ Gaps found in your resume:")
                for g in gaps:
                    st.write("- " + g)
            else:
                st.success("✅ No major gaps found! Your resume looks strong.")

            st.subheader("💡 Suggestions")
            for s in suggestions:
                st.info(s)
        else:
            st.warning("Could not read content from resume.")

# ============================
# CAREER ROADMAP
# ============================
elif choice == "Career Roadmap":
    st.title("🛣️ Career Roadmap")
    st.write("Here’s a step-by-step path to strengthen your profile:")
    roadmap = [
        "📌 Complete at least 2 internships in your field.",
        "📌 Work on 3+ projects (open-source, academic, personal).",
        "📌 Get certified (Coursera, Udemy, Google, AWS).",
        "📌 Participate in 2+ competitions/hackathons.",
        "📌 Network via LinkedIn, GitHub, and local meetups."
    ]
    for step in roadmap:
        st.success(step)

# ============================
# COURSES & INTERNSHIPS
# ============================
elif choice == "Courses & Internships":
    st.title("🎓 Courses & Internship Opportunities")

    st.subheader("Recommended Free Courses")
    st.markdown("- [Coursera Free Courses](https://www.coursera.org/courses?query=free)")
    st.markdown("- [Udemy Free Courses](https://www.udemy.com/courses/free/)")
    st.markdown("- [edX Free Courses](https://www.edx.org/course?price=free)")

    st.subheader("Internship Portals")
    st.markdown("- [Internshala](https://internshala.com)")
    st.markdown("- [LinkedIn Internships](https://www.linkedin.com/jobs/internships/)")
    st.markdown("- [Glassdoor Internships](https://www.glassdoor.com/Job/internship-jobs-SRCH_KO0,10.htm)")

# ============================
# EVENTS & COMPETITIONS
# ============================
elif choice == "Events & Competitions":
    st.title("🏆 Upcoming Events, Hackathons & Competitions")
    field = st.selectbox("Select your field of interest", ["Technology", "Business", "Medical", "Sports"])

    st.subheader("🔥 Devpost Hackathons")
    dev_events = fetch_devpost_events(field)
    if dev_events:
        for ev in dev_events:
            st.markdown(f"**{ev['name']}**")
            st.write(ev['desc'])
            st.markdown(f"[🔗 Register here]({ev['link']})")
            st.markdown("---")
    else:
        st.info("No relevant Devpost hackathons found right now.")

    if field == "Technology":
        st.subheader("🤖 Kaggle Competitions")
        kaggle_events = fetch_kaggle_events()
        if kaggle_events:
            for ev in kaggle_events:
                st.markdown(f"**{ev['name']}** - [🔗 View]({ev['link']})")
        else:
            st.info("No Kaggle competitions found right now.")
