import streamlit as st
import pdfplumber
import docx2txt
from datetime import datetime

# ----------------- STATIC DATA -----------------
courses_data = {
    "Technology": [
        {"title": "Python for Everybody (Free)", "link": "https://www.coursera.org/specializations/python", 
         "requirements": "Beginner friendly", "start": "Anytime", "end": "Self-paced"},
        {"title": "Data Science Certificate (Paid)", "link": "https://www.coursera.org/professional-certificates/ibm-data-science", 
         "requirements": "Basic Python", "start": "2025-09-01", "end": "2026-01-01"},
    ],
    "Business": [
        {"title": "Intro to Business (Free)", "link": "https://online.hbs.edu", 
         "requirements": "None", "start": "Anytime", "end": "Self-paced"},
        {"title": "Wharton Strategy (Paid)", "link": "https://www.coursera.org/specializations/wharton-strategy", 
         "requirements": "Bachelor’s degree preferred", "start": "2025-10-01", "end": "2026-02-01"},
    ],
    "Medical": [
        {"title": "Basics of Clinical Research", "link": "https://nptel.ac.in", 
         "requirements": "Medical/Science background", "start": "2025-09-15", "end": "2026-01-30"},
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
    ]
}

competitions_data = {
    "Technology": [
        {"name": "Kaggle ML Competition", "details": "Work on real-world ML problems.", 
         "deadline": "2025-09-30", "link": "https://www.kaggle.com"},
        {"name": "Devpost Hackathon", "details": "Build innovative apps in 48 hours.", 
         "deadline": "2025-10-15", "link": "https://devpost.com"},
    ],
    "Business": [
        {"name": "Hult Prize", "details": "Global business case competition.", 
         "deadline": "2025-09-20", "link": "https://hultprize.org"},
        {"name": "BCG Strategy Challenge", "details": "Solve consulting business cases.", 
         "deadline": "2025-10-10", "link": "https://bcg.com"},
    ],
    "Medical": [
        {"name": "WHO Health Research Summit", "details": "Present research papers.", 
         "deadline": "2025-11-01", "link": "https://who.int"},
    ],
    "Sports": [
        {"name": "National Athletics Championship", "details": "Compete at national level.", 
         "deadline": "2025-09-20", "link": "https://sportsauthorityofindia.nic.in"},
        {"name": "State Football Trials", "details": "Selection for state team.", 
         "deadline": "2025-09-30", "link": "https://aiff.com"},
    ],
    "Law": [
        {"name": "Moot Court Competition", "details": "Argue simulated legal cases.", 
         "deadline": "2025-10-05", "link": "https://barcouncilofindia.org"},
    ],
    "Arts & Design": [
        {"name": "Adobe Design Contest", "details": "Submit your creative portfolios.", 
         "deadline": "2025-09-25", "link": "https://adobe.com"},
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

def analyze_resume(text, field):
    missing = []
    if field == "Sports":
        if "competition" not in text and "tournament" not in text:
            missing.append("Sports achievements/competitions not highlighted")
    else:
        if "internship" not in text:
            missing.append("Internship experience")
        if "project" not in text:
            missing.append("Project experience")
    return missing

def career_tips_bot(user_input, field):
    response = ""
    if field == "Technology":
        if "project" in user_input:
            response = "Work on open-source projects on GitHub to showcase your coding skills."
        elif "internship" in user_input:
            response = "Apply on platforms like Internshala, AngelList, and LinkedIn. Build side projects to stand out."
        else:
            response = "Stay updated with tech trends, participate in hackathons, and strengthen your DSA skills."
    elif field == "Sports":
        if "training" in user_input:
            response = "Join local academies and register with state sports associations for advanced training."
        elif "competition" in user_input:
            response = "Start with district-level competitions, then progress to state and national tournaments."
        else:
            response = "Maintain a regular fitness schedule, track your performance, and seek mentorship from coaches."
    elif field == "Business":
        response = "Engage in case study competitions, improve networking skills, and follow Harvard Business Review insights."
    elif field == "Medical":
        response = "Participate in medical conferences, publish research, and join clinical internships for practical exposure."
    elif field == "Law":
        response = "Join moot courts, publish legal articles, and follow judgments from top courts to build knowledge."
    elif field == "Arts & Design":
        response = "Build a strong portfolio, participate in online design challenges, and stay creative every day."
    else:
        response = "Keep learning, building, and networking in your chosen field."
    return response

# ----------------- STREAMLIT APP -----------------
def main():
    st.set_page_config(page_title="Career Gap Mapper", layout="wide")

    # Sidebar Navigation
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Courses & Internships", "Events & Competitions", "Career Tips Bot"])

    # -------------- Home --------------
    if page == "Home":
        st.title("🧭 Career Gap Mapper")
        st.write("Upload your resume & get personalized career roadmap.")

        uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        field = st.selectbox("Select your career field", ["Technology","Business","Medical","Sports","Law","Arts & Design"])
        location = st.text_input("Enter your city (for internships)", "")

        if uploaded_file:
            text = extract_text_from_resume(uploaded_file)
            st.subheader("📑 Resume Analysis")
            missing = analyze_resume(text, field)
            if missing:
                st.warning("⚠️ Gaps Found in Resume:")
                for m in missing:
                    st.write(f"- {m}")
            else:
                st.success("✅ Your resume looks strong!")

    # -------------- Courses & Internships --------------
    elif page == "Courses & Internships":
        st.title("🎓 Recommended Courses & Internships")
        field = st.selectbox("Select your field", ["Technology","Business","Medical","Sports","Law","Arts & Design"])
        location = st.text_input("Enter city (for internships)", "")

        if field == "Sports":
            st.info("⚽ For Sports, internships are not relevant. Please check Competitions page instead.")
        else:
            st.subheader("Courses")
            for c in courses_data.get(field, []):
                st.markdown(f"**[{c['title']}]({c['link']})**")
                st.write(f"📝 Requirements: {c['requirements']}")
                st.write(f"📅 {c['start']} → {c['end']}")
                st.write("---")

            st.subheader("Internships")
            for i in internships_data.get(field, []):
                if location.lower() in i["location"].lower() or location == "":
                    st.markdown(f"**{i['title']}** at **{i['company']}** ({i['location']})")
                    st.write(f"💰 Stipend: {i['stipend']}")
                    st.write(f"📝 Requirements: {i['requirements']}")
                    st.write(f"📅 Apply: {i['start']} → {i['end']}")
                    st.markdown(f"[Apply Here]({i['link']})")
                    st.write("---")

    # -------------- Events & Competitions --------------
    elif page == "Events & Competitions":
        st.title("🏆 Events & Competitions")
        field = st.selectbox("Select your field", ["Technology","Business","Medical","Sports","Law","Arts & Design"])

        for e in competitions_data.get(field, []):
            st.markdown(f"**[{e['name']}]({e['link']})**")
            st.write(f"📄 {e['details']}")
            st.write(f"📅 Registration Deadline: {e['deadline']}")
            st.write("---")

    # -------------- Career Tips Bot --------------
    elif page == "Career Tips Bot":
        st.title("🤖 Career Tips Bot")
        field = st.selectbox("Select your field", ["Technology","Business","Medical","Sports","Law","Arts & Design"])
        user_input = st.text_input("Ask a career-related question:")

        if user_input:
            response = career_tips_bot(user_input.lower(), field)
            st.success(f"💡 {response}")

if __name__ == "__main__":
    main()

