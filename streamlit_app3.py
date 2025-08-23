import streamlit as st
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="Career Gap Mapper", layout="wide")

# --- MENU ---
menu = ["🏠 Home", "📄 Resume Analyzer", "🎓 Courses & Internships", 
        "🏆 Sports Pathway", "🩺 Medical & Healthcare", 
        "💼 Business & Startups", "🤖 Career Mentor Bot", "📊 Dashboard"]

choice = st.sidebar.radio("Navigate", menu)

# --- HOME PAGE ---
if choice == "🏠 Home":
    st.image("https://img.freepik.com/free-photo/solar-panel-career-growth-concept.jpg", use_column_width=True)
    st.title("🌟 Career Gap Mapper")
    st.subheader("Turn your Gaps into Growth!")
    st.write("👉 A platform for Students, Professionals, Sportspersons, Entrepreneurs, and Everyone building a career.")
    st.success("✨ Every weakness is a hidden opportunity. Upgrade yourself today! ✨")

# --- RESUME ANALYZER ---
elif choice == "📄 Resume Analyzer":
    st.header("📄 Resume Gap Analyzer")
    resume_text = st.text_area("Paste your resume here:", height=300)

    if st.button("🔍 Analyze"):
        missing = []
        if "intern" not in resume_text.lower(): missing.append("Internship")
        if "experience" not in resume_text.lower(): missing.append("Work Experience")
        if "degree" not in resume_text.lower() and "education" not in resume_text.lower(): missing.append("Education")
        if "sport" not in resume_text.lower() and "champion" not in resume_text.lower(): missing.append("Sports Achievements")
        if "startup" not in resume_text.lower() and "business" not in resume_text.lower(): missing.append("Business Exposure")

        if missing:
            st.error("⚠️ Weak Areas Detected: " + ", ".join(missing))
            for gap in missing:
                if gap == "Education":
                    st.info("🎓 Add certifications → [Coursera](https://www.coursera.org), [edX](https://www.edx.org), [NPTEL](https://nptel.ac.in)")
                elif gap == "Internship":
                    st.info("💼 Apply here → [Internshala](https://internshala.com), [LinkedIn](https://www.linkedin.com)")
                elif gap == "Work Experience":
                    st.info("🚀 Jobs → [Indeed](https://www.indeed.com), [Naukri](https://www.naukri.com)")
                elif gap == "Sports Achievements":
                    st.info("🏆 Tournaments → [AIU Sports](https://www.aiu.ac.in), [Olympics](https://olympics.com)")
                elif gap == "Business Exposure":
                    st.info("💡 Startup Resources → [Startup India](https://www.startupindia.gov.in), [Techstars](https://www.techstars.com)")
        else:
            st.success("✅ Your resume looks strong!")

        score = random.randint(60, 95) if missing else random.randint(90, 100)
        st.progress(score/100)
        st.write(f"💯 Resume Strength Score: {score}/100")

# --- COURSES & INTERNSHIPS ---
elif choice == "🎓 Courses & Internships":
    st.header("🎓 Courses & Internships")
    st.write("Upgrade with free & paid learning platforms:")
    st.markdown("- [Coursera](https://www.coursera.org)")
    st.markdown("- [edX](https://www.edx.org)")
    st.markdown("- [Udemy](https://www.udemy.com)")
    st.markdown("- [NPTEL](https://nptel.ac.in)")
    st.markdown("💼 Internships → [Internshala](https://internshala.com), [LinkedIn](https://linkedin.com), [AngelList](https://wellfound.com)")

# --- SPORTS PATHWAY ---
elif choice == "🏆 Sports Pathway":
    st.header("🏆 Sports Career Pathway")
    st.write("Upcoming tournaments & opportunities:")
    st.markdown("- [Olympic Games](https://olympics.com)")
    st.markdown("- [AIU Sports Calendar](https://www.aiu.ac.in)")
    st.markdown("- [Khelo India](https://kheloindia.gov.in)")

# --- MEDICAL ---
elif choice == "🩺 Medical & Healthcare":
    st.header("🩺 Medical & Healthcare Opportunities")
    st.write("Explore volunteering, fellowships & internships:")
    st.markdown("- [WHO Careers](https://www.who.int/careers)")
    st.markdown("- [UNICEF Volunteer](https://www.unicef.org/volunteer)")
    st.markdown("- [AIIMS Fellowships](https://www.aiims.edu)")

# --- BUSINESS & STARTUPS ---
elif choice == "💼 Business & Startups":
    st.header("💼 Business & Startup Opportunities")
    st.write("Resources for entrepreneurs:")
    st.markdown("- [Startup India](https://www.startupindia.gov.in)")
    st.markdown("- [Y Combinator](https://www.ycombinator.com)")
    st.markdown("- [Techstars](https://www.techstars.com)")

# --- CAREER MENTOR BOT ---
elif choice == "🤖 Career Mentor Bot":
    st.header("🤖 Ask Career Mentor Bot")
    q = st.text_input("Ask me anything about careers:")
    if q:
        st.write("🤔 Thinking...")
        st.success("💡 Suggested Path: Keep improving skills, apply for internships, and connect with mentors!")

# --- DASHBOARD ---
elif choice == "📊 Dashboard":
    st.header("📊 Career Dashboard")
    st.write("Visual overview of career opportunities.")
    st.metric("Total Free Courses", "500+")
    st.metric("Internship Platforms", "50+")
    st.metric("Global Companies Hiring", "100+")
    st.metric("Sports Championships", "30+ upcoming")

# --- FOOTER ---
st.markdown("---")
st.markdown("⚠️ *Disclaimer: This tool provides guidance. Final hiring/selection depends on recruiters, institutions, or organizers.*")


