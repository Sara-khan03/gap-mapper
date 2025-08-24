import streamlit as st
import pandas as pd
import random

# Load cities dataset
@st.cache_data
def load_cities():
    df = pd.read_csv("https://raw.githubusercontent.com/datasets/world-cities/master/data/world-cities.csv")
    return df

cities_df = load_cities()

# --- Sidebar Navigation ---
st.sidebar.title("🌟 Career Gap Mapper")
page = st.sidebar.radio("Navigate", [
    "🏠 Home + Resume Analyzer",
    "📚 Courses & Internships",
    "🎯 Events & Competitions",
    "🗺 Career Roadmap",
    "🤖 Career Tips Bot",
    "📂 Resources"
])

# --- Location Selection (Global Improvement) ---
st.sidebar.subheader("🌍 Select Location")
countries = sorted(cities_df['country'].unique())
selected_country = st.sidebar.selectbox("Select your country:", countries)

filtered_cities = cities_df[cities_df['country'] == selected_country]
selected_city = st.sidebar.selectbox("Select your city:", filtered_cities['name'].unique())

st.sidebar.success(f"📍 {selected_city}, {selected_country}")

# --- Fake Resume Analyzer (basic keyword check) ---
def analyze_resume(text, field):
    weaknesses = []
    recommendations = []

    if field == "tech":
        if "python" not in text.lower():
            weaknesses.append("Python missing")
            recommendations.append("Learn Python – free on Kaggle or paid on Coursera.")
        if "internship" not in text.lower():
            weaknesses.append("No internship")
            recommendations.append("Apply on Internshala, AngelList, or LinkedIn.")
    elif field == "sports":
        if "championship" not in text.lower():
            weaknesses.append("No championships mentioned")
            recommendations.append("Register for Khelo India or district-level tournaments.")
    elif field == "medical":
        if "clinical" not in text.lower():
            weaknesses.append("No clinical exposure")
            recommendations.append("Join clinical volunteering or hospital internships.")
    elif field == "business":
        if "finance" not in text.lower():
            weaknesses.append("Finance missing")
            recommendations.append("Take CFA basics or free YouTube finance courses.")

    return weaknesses, recommendations


# --- Page: Home + Resume Analyzer ---
if page == "🏠 Home + Resume Analyzer":
    st.title("🏠 Career Gap Mapper + Resume Analyzer")

    field = st.selectbox("Choose your career field:", ["tech", "sports", "medical", "business"])
    uploaded_file = st.file_uploader("Upload your resume (TXT or PDF for demo)", type=["txt"])

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.text_area("📄 Resume Content", text, height=200)

        weaknesses, recs = analyze_resume(text, field)

        st.subheader("📉 Weaknesses Found")
        if weaknesses:
            for w in weaknesses:
                st.error(f"- {w}")
        else:
            st.success("No major weaknesses detected!")

        st.subheader("✅ Recommendations")
        for r in recs:
            st.info(r)


# --- Page: Courses & Internships ---
elif page == "📚 Courses & Internships":
    st.title("📚 Recommended Courses & Internships")

    field = st.selectbox("Choose your field:", ["tech", "sports", "medical", "business"])

    if field == "tech":
        st.subheader("Courses")
        st.write("🔹 [CS50 (Free)](https://cs50.harvard.edu/)")
        st.write("🔹 [Coursera: Google Data Analytics (Paid)](https://www.coursera.org/professional-certificates/google-data-analytics)")
        st.subheader("Internships")
        st.write("💼 LinkedIn Tech Internships – Rolling applications")
        st.write("💼 Internshala Python/AI internships – Registration open")

    elif field == "sports":
        st.subheader("Competitions / Training")
        st.write("🏆 Khelo India University Games – Registration till Sept 2025")
        st.write("🏆 Asian Games qualifiers – City-based selections")

    elif field == "medical":
        st.subheader("Courses")
        st.write("🔹 [Coursera: Anatomy Specialization (Paid)](https://www.coursera.org/specializations/anatomy)")
        st.write("🔹 [Medscape CME (Free)](https://www.medscape.org/)")
        st.subheader("Internships")
        st.write("💼 Hospital volunteering – Apply directly in local hospitals")

    elif field == "business":
        st.subheader("Courses")
        st.write("🔹 [Wharton MBA Free Courses](https://online.wharton.upenn.edu/)")
        st.write("🔹 [Coursera: Financial Markets by Yale](https://www.coursera.org/learn/financial-markets-global)")
        st.subheader("Internships")
        st.write("💼 Deloitte Summer Internship – Closes Nov 2025")
        st.write("💼 Goldman Sachs Internship – Apply till Dec 2025")


# --- Page: Events & Competitions ---
elif page == "🎯 Events & Competitions":
    st.title("🎯 Upcoming Events & Competitions")

    field = st.selectbox("Choose your field:", ["tech", "sports", "medical", "business"])

    if field == "tech":
        st.write("💻 Hackathons on [Devpost](https://devpost.com/hackathons)")
        st.write("💻 MLH Global Hack Week – October 2025")

    elif field == "sports":
        st.write("⚽ Khelo India Games – State level qualifiers")
        st.write("🏸 Badminton National Open – Registrations till Nov 2025")

    elif field == "medical":
        st.write("🩺 World Health Summit Asia – Feb 2026, Singapore")
        st.write("🩺 Indian Medical Congress – Delhi, March 2026")

    elif field == "business":
        st.write("📊 Startup India Innovation Summit – Jan 2026, Mumbai")
        st.write("📊 TiE Global Pitch Fest – Online, Rolling entries")


# --- Page: Career Roadmap ---
elif page == "🗺 Career Roadmap":
    st.title("🗺 Career Roadmap")
    st.info("🚀 Your step-by-step personalized career roadmap will be displayed here (future upgrade).")


# --- Page: Career Tips Bot ---
elif page == "🤖 Career Tips Bot":
    st.title("🤖 Career Tips Bot")

    field = st.selectbox("Select your field:", ["tech", "sports", "medical", "business"])
    user_q = st.text_input("Ask me about your career:")

    def career_bot(question, field):
        q = question.lower()
        if field == "tech":
            if "internship" in q:
                return "Search on LinkedIn, Internshala, and AngelList – tech startups hire year-round."
            elif "course" in q:
                return "Try CS50 (free) or Google Cloud Certification."
            else:
                return "Build projects, open-source, and grow your GitHub!"
        elif field == "sports":
            return "Focus on upcoming competitions like Khelo India and local leagues."
        elif field == "medical":
            return "Attend medical conferences, do hospital internships, and keep learning via CME."
        elif field == "business":
            return "Networking + MBA/Masters + internships at Deloitte/GS can help."
        return "Please choose your field for more precise tips!"

    if user_q:
        st.info(career_bot(user_q, field))


# --- Page: Resources ---
elif page == "📂 Resources":
    st.title("📂 Resources")
    st.write("📘 Free Resume Templates: [Canva](https://www.canva.com/resumes/templates/)")
    st.write("📘 Job Boards: [LinkedIn](https://linkedin.com), [Indeed](https://indeed.com)")
    st.write("📘 Learning Platforms: [Coursera](https://coursera.org), [edX](https://edx.org)")
