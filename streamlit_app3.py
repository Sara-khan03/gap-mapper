import streamlit as st
import random

# --- Title ---
st.set_page_config(page_title="Career Gap Mapper", layout="wide")
st.title("🌟 Career Gap Mapper")
st.write("Turn your weaknesses into opportunities with smart guidance!")

# --- Input Resume ---
resume_text = st.text_area("📄 Paste Your Resume Here:", height=300)

# --- City Selection ---
city = st.selectbox("🌍 Select Your City:", ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune", "Other"])

# --- Resume Analyzer ---
if st.button("🔍 Analyze My Resume"):
    st.subheader("📊 Resume Analysis Result")

    missing = []
    if "intern" not in resume_text.lower():
        missing.append("Internship")
    if "experience" not in resume_text.lower():
        missing.append("Work Experience")
    if "education" not in resume_text.lower() and "degree" not in resume_text.lower():
        missing.append("Education")
    if "sport" not in resume_text.lower() and "champion" not in resume_text.lower():
        missing.append("Sports Achievements")
    if "business" not in resume_text.lower() and "startup" not in resume_text.lower():
        missing.append("Business/Leadership")

    # Show weak areas
    if missing:
        st.error("⚠️ Weak Areas Detected: " + ", ".join(missing))
        st.write("Here’s how you can fix them:")

        if "Education" in missing:
            st.info("🎓 Suggested Courses: [Coursera](https://www.coursera.org), [edX](https://www.edx.org), [NPTEL](https://nptel.ac.in)")

        if "Internship" in missing:
            st.info("💼 Find Internships: [Internshala](https://internshala.com), [AngelList](https://wellfound.com), [LinkedIn](https://www.linkedin.com)")

        if "Work Experience" in missing:
            st.info("🚀 Jobs Platforms: [Indeed](https://www.indeed.com), [Naukri](https://www.naukri.com), [LinkedIn Jobs](https://www.linkedin.com/jobs)")

        if "Sports Achievements" in missing:
            st.info("🏆 Upcoming Tournaments: [AIU Sports Calendar](https://www.aiu.ac.in), [Olympic Sports](https://olympics.com)")

        if "Business/Leadership" in missing:
            st.info("💡 Startup Resources: [Startup India](https://www.startupindia.gov.in), [Y Combinator](https://www.ycombinator.com), [Techstars](https://www.techstars.com)")

    else:
        st.success("✅ Great! Your resume looks strong and balanced across multiple fields!")

    # Score Meter
    score = random.randint(60, 95) if missing else random.randint(90, 100)
    st.progress(score / 100)
    st.write(f"💯 Resume Strength Score: {score}/100")

# --- Extra Tools ---
st.sidebar.title("🔗 Quick Links")
st.sidebar.markdown("[Google Careers](https://careers.google.com/)")
st.sidebar.markdown("[Microsoft Careers](https://careers.microsoft.com/)")
st.sidebar.markdown("[Amazon Jobs](https://www.amazon.jobs/)")
st.sidebar.markdown("[Infosys Careers](https://www.infosys.com/careers)")
st.sidebar.markdown("[TCS Careers](https://www.tcs.com/careers)")

# --- Motivational Quote ---
st.markdown("---")
st.markdown("✨ *Every gap is a hidden opportunity. Upgrade yourself today!* ✨")


