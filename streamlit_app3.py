import streamlit as st
import pdfplumber
import docx2txt
import requests
from bs4 import BeautifulSoup

# ------------------ Helper Functions ------------------

def extract_text_from_resume(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    else:
        return None

def analyze_resume(text):
    gaps = []
    if "internship" not in text.lower():
        gaps.append("No internships found")
    if "project" not in text.lower():
        gaps.append("No projects found")
    if "certificate" not in text.lower() and "course" not in text.lower():
        gaps.append("No certifications or courses listed")
    if not gaps:
        return "✅ Strong Resume!", []
    return "⚠️ Resume has gaps", gaps

def fetch_devpost_hackathons():
    try:
        url = "https://devpost.com/hackathons"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        events = []
        for card in soup.select(".card-item")[:5]:
            name = card.select_one(".hackathon-title").get_text(strip=True)
            link = "https://devpost.com" + card.select_one("a")["href"]
            deadline = card.select_one(".submission-deadline").get_text(strip=True) if card.select_one(".submission-deadline") else "TBD"
            events.append({"name": name, "link": link, "deadline": deadline})
        return events
    except:
        return []

# ------------------ App Layout ------------------

st.set_page_config(page_title="Career Gap Mapper", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Resume Analyzer",
    "🎯 Events & Competitions",
    "📚 Courses & Internships",
    "🌍 Location Selector",
    "🤖 Career Chatbot"
])

# ------------------ Resume Analyzer ------------------
if page == "🏠 Resume Analyzer":
    st.title("📄 Career Gap Mapper + Resume Analyzer")

    uploaded_file = st.file_uploader("Upload your Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        text = extract_text_from_resume(uploaded_file)
        if text:
            result, gaps = analyze_resume(text)
            st.subheader(result)
            if gaps:
                st.write("### Gaps Found:")
                for g in gaps:
                    st.warning(g)
            else:
                st.success("Your resume looks solid! 🚀")

# ------------------ Events & Competitions ------------------
elif page == "🎯 Events & Competitions":
    st.title("🎯 Upcoming Events & Competitions")
    field = st.selectbox("Choose your field:", ["Tech", "Sports", "Medical", "Business"])

    if field == "Tech":
        st.subheader("💻 Live Hackathons (Devpost)")
        events = fetch_devpost_hackathons()
        if events:
            for e in events:
                st.markdown(f"**[{e['name']}]({e['link']})** – Deadline: {e['deadline']}")
        else:
            st.warning("⚠️ Could not fetch live hackathons. Showing fallback list.")
            st.write("- AI Hackathon (Nov 2025)")
            st.write("- Global Dev Challenge (Dec 2025)")

    elif field == "Sports":
        st.subheader("🏆 Sports Competitions")
        st.write("- National Athletics Championship – Reg: Oct 2025 – [Register Here](https://www.indianathletics.in/)")
        st.write("- Football League Trials – Reg: Nov 2025 – [Details](https://www.the-aiff.com/)")

    elif field == "Medical":
        st.subheader("🩺 Medical Conferences & Research Events")
        st.write("- World Medical Innovation Forum – May 2026 – [Register](https://worldmedicalinnovation.org/)")
        st.write("- Indian Medical Research Conference – Feb 2026 – [Details](https://icmr.nic.in/)")

    elif field == "Business":
        st.subheader("📊 Business & Entrepreneurship Events")
        st.write("- Startup India Innovation Summit – Jan 2026 – [Register](https://www.startupindia.gov.in/)")
        st.write("- Global Entrepreneurs Conference – Mar 2026 – [Details](https://www.ges2025.org/)")

# ------------------ Courses & Internships ------------------
elif page == "📚 Courses & Internships":
    st.title("📚 Recommended Courses & Internships")
    st.write("We recommend based on gaps in your resume")

    st.subheader("🎓 Courses")
    st.write("- [Coursera: Data Science Specialization](https://www.coursera.org/) – Paid – Reg closes Dec 2025")
    st.write("- [edX: Business Management](https://www.edx.org/) – Free – Reg closes Jan 2026")
    st.write("- [Udemy: Full Stack Development](https://www.udemy.com/) – Paid – Ongoing")

    st.subheader("💼 Internships")
    st.write("- Google STEP Internship – Apply by Nov 2025 – [Apply Here](https://careers.google.com/)")
    st.write("- WHO Public Health Internship – Apply by Dec 2025 – [Apply](https://www.who.int/careers)")
    st.write("- Sports Analytics Intern @ ESPN – Apply by Jan 2026 – [Details](https://espncareers.com/)")

# ------------------ Location Selector ------------------
elif page == "🌍 Location Selector":
    st.title("🌍 Select Your Location")
    country = st.selectbox("Choose your country:", ["India", "USA", "UK"])
    if country == "India":
        city = st.selectbox("Choose your city:", ["Delhi", "Mumbai", "Bengaluru", "Chennai"])
    elif country == "USA":
        city = st.selectbox("Choose your city:", ["New York", "San Francisco", "Chicago"])
    elif country == "UK":
        city = st.selectbox("Choose your city:", ["London", "Manchester", "Birmingham"])
    st.success(f"✅ You selected: {city}, {country}")

# ------------------ Chatbot ------------------
elif page == "🤖 Career Chatbot":
    st.title("🤖 Career Tips Bot")
    user_input = st.text_input("Ask me anything about your career:")

    if user_input:
        if "internship" in user_input.lower():
            st.info("💡 Internships boost your resume. Check '📚 Courses & Internships' for live opportunities.")
        elif "course" in user_input.lower():
            st.info("📚 Upskill with free & paid courses. See recommendations in the Courses page.")
        elif "competition" in user_input.lower():
            st.info("🏆 Competitions can give exposure! See '🎯 Events & Competitions'.")
        else:
            st.info("I suggest improving your resume by adding projects, internships, and certifications.")
