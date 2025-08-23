import streamlit as st
import pdfplumber
import docx2txt
import pandas as pd
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Career Gap Mapper", layout="wide")

# ----------------- HELPER FUNCTIONS -----------------
def extract_text_from_resume(uploaded_file):
    """Extract text from uploaded resume (PDF or DOCX)."""
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        text = docx2txt.process(uploaded_file)
    return text

def analyze_resume(text):
    """Very basic resume analysis to detect missing key elements."""
    suggestions = []
    if "intern" not in text.lower():
        suggestions.append("Add an internship or project experience to strengthen your profile.")
    if "skill" not in text.lower():
        suggestions.append("Highlight key technical and soft skills clearly.")
    if "experience" not in text.lower():
        suggestions.append("Mention professional or volunteer experiences.")
    if "education" not in text.lower():
        suggestions.append("Add an Education section with degrees and achievements.")
    if len(text.split()) < 150:
        suggestions.append("Your resume seems too short. Add more details about achievements, roles, and responsibilities.")

    return suggestions if suggestions else ["Your resume looks strong! Keep applying and improving."]

def get_courses_and_internships(field):
    """Return free and paid courses, internship portals based on field."""
    resources = {
        "Technology": {
            "Courses": [
                ("FreeCodeCamp (Free)", "https://www.freecodecamp.org/"),
                ("Coursera - Data Science", "https://www.coursera.org/"),
                ("Udemy Python Bootcamp", "https://www.udemy.com/")
            ],
            "Internships": [
                ("Internshala Tech Internships", "https://internshala.com/"),
                ("AngelList (Tech Startups)", "https://wellfound.com/")
            ]
        },
        "Business": {
            "Courses": [
                ("Harvard Online Business", "https://online.hbs.edu/"),
                ("edX - Business Analytics", "https://www.edx.org/")
            ],
            "Internships": [
                ("LinkedIn Business Internships", "https://www.linkedin.com/jobs/"),
                ("Glassdoor Internships", "https://www.glassdoor.com/Job/internship-jobs.htm")
            ]
        },
        "Medical": {
            "Courses": [
                ("Coursera - Medical Neuroscience", "https://www.coursera.org/"),
                ("edX - Public Health", "https://www.edx.org/")
            ],
            "Internships": [
                ("Internshala Healthcare Internships", "https://internshala.com/"),
                ("WHO Internship Programme", "https://www.who.int/careers/internship-programme")
            ]
        },
        "Sports": {
            "Courses": [
                ("Coursera - Sports Management", "https://www.coursera.org/"),
                ("Udemy - Fitness Trainer", "https://www.udemy.com/")
            ],
            "Internships": [
                ("Internshala Sports Internships", "https://internshala.com/"),
                ("IOC Internship", "https://olympics.com/ioc/careers")
            ]
        }
    }
    return resources.get(field, {})

def get_events(field, city):
    """Return competitions & events (dummy dataset for now)."""
    data = {
        "Technology": [
            {"name": "Google Summer of Code", "desc": "Open-source coding program", "deadline": "April 2025", "link": "https://summerofcode.withgoogle.com/", "city": "Online"},
            {"name": "HackMIT", "desc": "MIT’s biggest hackathon", "deadline": "Sept 2025", "link": "https://hackmit.org/", "city": "Boston"}
        ],
        "Business": [
            {"name": "Hult Prize", "desc": "Global entrepreneurship competition", "deadline": "Oct 2025", "link": "https://www.hultprize.org/", "city": "Online"},
            {"name": "Case Study Competition - IIM", "desc": "Business problem solving", "deadline": "Aug 2025", "link": "https://iimjobs.com/", "city": "Delhi"}
        ],
        "Medical": [
            {"name": "WHO Hackathon", "desc": "Public health innovation", "deadline": "Dec 2025", "link": "https://www.who.int/", "city": "Online"},
            {"name": "Medical Research Summit", "desc": "Present healthcare research", "deadline": "Nov 2025", "link": "https://research.com/", "city": "London"}
        ],
        "Sports": [
            {"name": "National Athletics Championship", "desc": "Track & Field championship", "deadline": "Sept 2025", "link": "https://sportsauthorityofindia.nic.in/", "city": "Delhi"},
            {"name": "FIFA Volunteer Program", "desc": "Assist in international football events", "deadline": "Oct 2025", "link": "https://fifa.com/", "city": "Online"}
        ]
    }
    events = data.get(field, [])
    if city != "All":
        events = [e for e in events if e["city"].lower() == city.lower() or e["city"].lower() == "online"]
    return events

# ----------------- NAVIGATION -----------------
menu = ["Resume Analyzer & Home", "Courses & Internships", "Events & Competitions", "Career Roadmap"]
choice = st.sidebar.radio("Navigate", menu)

# ----------------- PAGE: RESUME ANALYZER + HOME -----------------
if choice == "Resume Analyzer & Home":
    st.title("🌟 Career Gap Mapper - Resume Analyzer")
    st.write("Upload your resume and get personalized improvement suggestions, career roadmap, and opportunities.")

    uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        resume_text = extract_text_from_resume(uploaded_file)
        st.subheader("📋 Resume Analysis Report")
        feedback = analyze_resume(resume_text)
        for f in feedback:
            st.warning(f)

# ----------------- PAGE: COURSES & INTERNSHIPS -----------------
elif choice == "Courses & Internships":
    st.title("📚 Courses & Internship Opportunities")
    field = st.selectbox("Select your field", ["Technology", "Business", "Medical", "Sports"])
    resources = get_courses_and_internships(field)
    if resources:
        st.subheader("🎓 Recommended Courses")
        for course, link in resources["Courses"]:
            st.markdown(f"- [{course}]({link})")
        st.subheader("💼 Internship Platforms")
        for intern, link in resources["Internships"]:
            st.markdown(f"- [{intern}]({link})")

# ----------------- PAGE: EVENTS -----------------
elif choice == "Events & Competitions":
    st.title("🏆 Upcoming Competitions, Hackathons & Opportunities")
    field = st.selectbox("Select your field", ["Technology", "Business", "Medical", "Sports"])
    city = st.text_input("Enter your city (or type 'All' for everything):", "All")
    events = get_events(field, city)
    if events:
        for e in events:
            st.markdown(f"### {e['name']}")
            st.write(f"**Description:** {e['desc']}")
            st.write(f"**Deadline:** {e['deadline']}")
            st.write(f"[🔗 Registration Link]({e['link']})")
            st.info(f"Location: {e['city']}")
    else:
        st.warning("No events found for this field/city. Try 'All'.")

# ----------------- PAGE: CAREER ROADMAP -----------------
elif choice == "Career Roadmap":
    st.title("🛤️ Career Roadmap Generator")
    st.write("Based on your resume analysis, here are steps you can follow:")
    st.markdown("""
    - Complete at least one **internship** or hands-on project.  
    - Learn new **technical/soft skills** from free/paid courses.  
    - Participate in **competitions & hackathons** for exposure.  
    - Network on **LinkedIn, AngelList, or sports federations**.  
    - Build a strong **portfolio** or **research paper/publication** if academic.  
    """)

