import streamlit as st
import requests
import pdfplumber
import docx2txt
import os

# -------------------- Sidebar Navigation --------------------
st.sidebar.title("Career Gap Mapper")
page = st.sidebar.radio(
    "Go to",
    ["Home & Resume Analyzer", "Courses & Internships", "Events & Competitions",
     "Career Tips Bot", "Resources", "Location Selector"]
)

# -------------------- Helper: Resume Analyzer --------------------
def analyze_resume(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        text += docx2txt.process(file)
    elif file.name.endswith(".txt"):
        text += str(file.read(), "utf-8")
    else:
        return "Unsupported file format."
    
    if not text.strip():
        return "Couldn’t extract text from resume."
    
    # Simple check
    feedback = []
    if "internship" not in text.lower():
        feedback.append("⚠️ No internships found in resume.")
    if "project" not in text.lower():
        feedback.append("⚠️ No projects found in resume.")
    if "experience" not in text.lower():
        feedback.append("⚠️ Work experience missing.")
    
    if not feedback:
        feedback.append("✅ Resume looks strong! Keep it up.")
    return "\n".join(feedback)

# -------------------- Home & Resume Analyzer --------------------
if page == "Home & Resume Analyzer":
    st.title("🚀 Career Gap Mapper")
    st.write("Upload your resume and get feedback with career growth suggestions.")
    
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    if uploaded_file:
        feedback = analyze_resume(uploaded_file)
        st.subheader("Resume Analysis Result:")
        st.write(feedback)

# -------------------- Courses & Internships --------------------
elif page == "Courses & Internships":
    st.title("🎓 Recommended Courses & Internships")
    st.write("Here are some curated opportunities:")
    
    st.subheader("Free Courses")
    st.markdown("- [Python for Everybody (Coursera)](https://www.coursera.org/specializations/python)")
    st.markdown("- [Intro to Machine Learning (Kaggle)](https://www.kaggle.com/learn/intro-to-machine-learning)")
    
    st.subheader("Paid Courses")
    st.markdown("- [Full-Stack Web Development (Udemy)](https://www.udemy.com/course/the-complete-web-developer-course/)")
    st.markdown("- [AI & Deep Learning (Coursera)](https://www.coursera.org/specializations/deep-learning)")
    
    st.subheader("Internships")
    st.markdown("- [Google Internship Portal](https://careers.google.com/students/)")
    st.markdown("- [Microsoft Internships](https://careers.microsoft.com/students/us/en)")
    st.markdown("- [Internshala (India)](https://internshala.com/)")

# -------------------- Events & Competitions --------------------
elif page == "Events & Competitions":
    st.title("🏆 Events & Competitions")
    st.write("Live opportunities based on your field.")
    
    # Tech Example (Devpost)
    try:
        response = requests.get("https://devpost.com/api/hackathons?status=open")
        data = response.json()
        st.subheader("Tech Hackathons (from Devpost)")
        for hack in data.get("hackathons", [])[:5]:
            st.markdown(f"- [{hack['title']}]({hack['url']}) - Deadline: {hack.get('submission_period_dates')}")
    except:
        st.warning("⚠️ Could not fetch live hackathons. Showing fallback.")
        st.markdown("- [Fallback Hackathon Example](https://devpost.com)")

    # Sports Example (Static fallback for now)
    st.subheader("Sports Competitions")
    st.markdown("- [National Athletics Championship](https://indianathletics.in/) - July 2025")
    st.markdown("- [State Level Football Tournament] - August 2025")

# -------------------- Career Tips Bot --------------------
elif page == "Career Tips Bot":
    st.title("🤖 Career Tips Assistant")
    user_q = st.text_input("Ask me about resume, internships, or career growth:")
    if user_q:
        st.write("✅ Tip: Stay consistent, keep updating your skills, and apply widely.")

# -------------------- Resources --------------------
elif page == "Resources":
    st.title("📚 Career Resources")
    st.markdown("- [LinkedIn Learning](https://www.linkedin.com/learning/)")
    st.markdown("- [FreeCodeCamp](https://www.freecodecamp.org/)")
    st.markdown("- [Khan Academy](https://www.khanacademy.org/)")
    st.markdown("- [Naukri Jobs](https://www.naukri.com/)")

# -------------------- Location Selector --------------------
elif page == "Location Selector":
    st.title("🌍 Find Opportunities Near You")
    country = st.selectbox("Select your country:", ["India", "USA", "UK", "Canada"])
    if country == "India":
        city = st.selectbox("Select city:", ["Delhi", "Mumbai", "Bangalore", "Chennai"])
    elif country == "USA":
        city = st.selectbox("Select city:", ["New York", "San Francisco", "Chicago"])
    else:
        city = st.text_input("Enter your city:")
    
    if city:
        st.success(f"Showing opportunities in **{city}, {country}** (future integration here).")
