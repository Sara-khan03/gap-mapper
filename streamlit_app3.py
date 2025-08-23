import streamlit as st
import random
import requests

st.set_page_config(page_title="Career Gap Mapper", layout="wide")

menu = ["🏠 Home", "📄 Resume Analyzer", "🎓 Courses & Internships", 
        "🧭 Career Roadmaps", "📊 Skill Radar", "🏆 Sports Pathway", 
        "🩺 Medical & Healthcare", "💼 Business & Startups", 
        "📅 Events", "🎁 Inspire Me", "🤖 Career Mentor Bot"]

choice = st.sidebar.radio("Navigate", menu)

# --- ROADMAP PAGE ---
if choice == "🧭 Career Roadmaps":
    st.header("🧭 Career Roadmaps")
    career = st.selectbox("Choose your field:", ["Data Scientist", "Software Engineer", "Doctor", "Athlete", "Entrepreneur"])
    if career == "Data Scientist":
        st.markdown("""
        1️⃣ Learn Python & Statistics → [Coursera](https://www.coursera.org)  
        2️⃣ Practice projects on Kaggle → [Kaggle](https://www.kaggle.com)  
        3️⃣ Do an internship → [Internshala](https://internshala.com)  
        4️⃣ Apply for jobs → [LinkedIn](https://linkedin.com)  
        """)
    elif career == "Athlete":
        st.markdown("""
        1️⃣ Join local sports clubs  
        2️⃣ Compete at district/state level  
        3️⃣ Apply for scholarships → [Khelo India](https://kheloindia.gov.in)  
        4️⃣ Train for nationals/international championships  
        """)

# --- SKILL RADAR ---
elif choice == "📊 Skill Radar":
    st.header("📊 Skill Gap Radar Chart")
    st.write("⚡ (Coming soon: Upload resume → see radar chart of skills vs demand)")

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

    st.subheader("Startup Pitch Events")
    st.markdown("- [Y Combinator Demo Days](https://www.ycombinator.com)")
    st.markdown("- [Startup India Events](https://www.startupindia.gov.in)")

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
