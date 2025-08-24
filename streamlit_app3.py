import streamlit as st
import pandas as pd

# Load world cities (CSV should be in repo or use external dataset)
@st.cache_data
def load_cities():
    df = pd.read_csv("https://raw.githubusercontent.com/datasets/world-cities/master/data/world-cities.csv")
    return df

cities_df = load_cities()

st.title("🌍 Career Gap Mapper")

# --- City selection ---
st.subheader("Enter Your City")
selected_city = st.selectbox("Select your city:", cities_df['name'].unique())

if selected_city:
    city_data = cities_df[cities_df['name'] == selected_city].iloc[0]
    st.success(f"📍 You selected: {city_data['name']}, {city_data['country']}")

# --- Chatbot ---
st.subheader("💬 Career Tips Bot")

user_question = st.text_input("Ask me anything about your career:")

def career_bot_response(question, field):
    q = question.lower()
    if field == "tech":
        if "internship" in q:
            return "You can find great internships on Internshala, LinkedIn, and AngelList. Startups are actively hiring!"
        elif "event" in q or "hackathon" in q:
            return "Check out Devpost and MLH Hackathons – amazing for networking and projects!"
        else:
            return "For tech, focus on building projects, GitHub profile, and certifications (AWS, Google Cloud)."
    
    elif field == "sports":
        if "competition" in q:
            return "Look into Khelo India, National Sports Championships, and upcoming Asian Games qualifiers."
        else:
            return "Sports careers grow with discipline and networking. Connect with your local sports federation."

    elif field == "medical":
        if "conference" in q:
            return "Upcoming medical conferences: Indian Medical Congress, World Health Summit Asia."
        else:
            return "Focus on continuous learning. NEET-PG prep or short courses on Coursera/Medscape are great."

    elif field == "business":
        if "internship" in q:
            return "Try Goldman Sachs, Deloitte, or startup incubators in your city."
        else:
            return "Business careers thrive on networking. Attend TiE Global, Startup India events, or local pitch fests."

    else:
        return "Tell me your field (tech, sports, medical, business) so I can guide you better."

# For demo, assume field is chosen already
user_field = st.selectbox("Choose your field:", ["tech", "sports", "medical", "business"])

if user_question:
    st.info(career_bot_response(user_question, user_field))
