import streamlit as st
import random

st.set_page_config(page_title="Career Gap Mapper", layout="wide")

# Sidebar menu
menu = [
    "📄 Resume Analyzer", "🏠 Home", "🎓 Courses & Internships",
    "🧭 Career Roadmaps", "📊 Skill Radar", "🏆 Sports Pathway",
    "🩺 Medical & Healthcare", "💼 Business & Startups",
    "📅 Events", "🎁 Inspire Me", "🤖 Career Mentor Bot"
]
choice = st.sidebar.radio("Navigate", menu)

# --- RESUME ANALYZER (default first page) ---
if choice == "📄 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    st.subheader("Upload your resume and discover missing skills, internships, and growth opportunities 🚀")

    uploaded = st.file_uploader("📤 Upload your resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if uploaded:
        st.success("✅ Resume uploaded successfully!")

        # Fake AI analysis simulation
        st.markdown("### 🔎 Weakness Detected:")
        st.write("• No internships found")
        st.write("• Lacks leadership experience")
        st.write("• Missing certifications in latest tools")

        st.markdown("### 💡 Suggestions:")
        st.write("• Apply for internships → [Internshala](https://internshala.com)")
        st.write("• Earn certifications → [Coursera](https://coursera.org) / [edX](https://edx.org)")
        st.write("• Add leadership/volunteer work")

        st.markdown("### 🎯 Recommended Next Steps:")
        st.write("1. Take a short project-based course")
        st.write("2. Join a hackathon → [Devpost](https://devpost.com/hackathons)")
        st.write("3. Add updated resume to [LinkedIn](https://linkedin.com)")

    else:
        st.info("⬆️ Please upload your resume to analyze strengths and weaknesses")

# --- HOME ---
elif choice == "🏠 Home":
    st.title("🚀 Career Gap Mapper")
    st.subheader("Find and fix gaps in your career journey 🌟")
    st.markdown("""
    This platform helps **students, professionals, sportspersons, doctors, entrepreneurs, and job-seekers**  
    to analyze their resume, discover missing skills, find internships, and explore upcoming opportunities.  
    """)
    st.image("https://cdn.pixabay.com/photo/2016/11/29/02/00/adult-1868750_1280.jpg", 
             caption="Empower your career with the right skills", use_container_width=True)

# --- COURSES & INTERNSHIPS ---
elif choice == "🎓 Courses & Internships":
    st.header("🎓 Courses & Internships")
    st.markdown("Here are some free and paid resources to strengthen your profile:")

    st.subheader("📚 Courses")
    st.markdown("- [FreeCodeCamp](https://www.freecodecamp.org/) → Free coding & web dev")
    st.markdown("- [Coursera](https://www.coursera.org/) → Data Science, Business, Healthcare")
    st.markdown("- [Khan Academy](https://www.khanacademy.org/) → Basics & fundamentals")

    st.subheader("💼 Internships")
    st.markdown("- [Internshala](https://internshala.com)")
    st.markdown("- [LinkedIn Internships](https://www.linkedin.com/jobs/internship-jobs)")
    st.markdown("- [Glassdoor](https://www.glassdoor.com/Job/internship-jobs-SRCH_KO0,10.htm)")

# --- ROADMAPS ---
elif choice == "🧭 Career Roadmaps":
    st.header("🧭 Career Roadmaps")
    career = st.selectbox("Choose your field:", ["Data Scientist", "Software Engineer", "Doctor", "Athlete", "Entrepreneur"])
    if career == "Data Scientist":
        st.markdown("""
        1️⃣ Learn Python & Statistics → [Coursera](https://www.coursera.org)  
        2️⃣ Do projects on [Kaggle](https://www.kaggle.com)  
        3️⃣ Internship → [Internshala](https://internshala.com)  
        4️⃣ Apply for jobs → [LinkedIn](https://linkedin.com)  
        """)
    elif career == "Athlete":
        st.markdown("""
        1️⃣ Join local sports clubs  
        2️⃣ Compete at district/state level  
        3️⃣ Scholarships → [Khelo India](https://kheloindia.gov.in)  
        4️⃣ Train for nationals/international championships  
        """)

# --- EVENTS ---
elif choice == "📅 Events":
    st.header("📅 Upcoming Events")
    st.subheader("Hackathons & Tech Competitions")
    st.markdown("- [Devpost Hackathons](https://devpost.com/hackathons)")
    st.markdown("- [Kaggle Competitions](https://www.kaggle.com/competitions)")

    st.subheader("Sports Events")
    st.markdown("- [Olympics](https://olympics.com)")
    st.markdown("- [Khelo India](https://kheloindia.gov.in)")

    st.subheader("Medical Conferences")
    st.markdown("- [WHO Events](https://www.who.int/news-room/events)")
    st.markdown("- [AIIMS Workshops](https://www.aiims.edu)")

# --- INSPIRE ME ---
elif choice == "🎁 Inspire Me":
    st.header("🎁 Inspire Me!")
    quotes = [
        "Dream big, work hard, stay focused.",
        "Every weakness is a chance to grow.",
        "Opportunities don't happen, you create them."
    ]
    st.success("💡 " + random.choice(quotes))

    st.subheader("🎓 Random Free Course")
    st.markdown("- [FreeCodeCamp](https://www.freecodecamp.org)")

    st.subheader("🏆 Random Competition")
    st.markdown("- [Hackerearth Challenges](https://www.hackerearth.com/challenges/)")

# Footer
st.markdown("---")
st.markdown("⚠️ This tool suggests career resources. Final success depends on your effort 🚀")

