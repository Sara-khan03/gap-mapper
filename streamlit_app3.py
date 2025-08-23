import streamlit as st
import datetime
import re

# ------------------- APP HEADER -------------------
st.set_page_config(page_title="Career Gap Mapper", page_icon="🧭", layout="wide")

st.markdown(
    """
    <div style="text-align:center;">
        <h1 style="color:#FFA500;">🧭 Career Gap Mapper</h1>
        <h3 style="color:#00BFFF;">Map your career journey, find gaps, and get guidance 🚀</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------- INPUT OPTIONS -------------------
st.subheader("📂 Upload Resume or Paste Career History")
uploaded_file = st.file_uploader("Upload Resume (TXT format)", type=["txt"])
career_text = ""

if uploaded_file:
    career_text = uploaded_file.read().decode("utf-8")
else:
    career_text = st.text_area("Or paste your career history here:", height=200)

# ------------------- DOMAIN SELECTION -------------------
domain = st.selectbox(
    "Select your domain",
    ["Student", "Sportsperson", "Medical Professional", "Business/Entrepreneur", "Other"]
)

# ------------------- GAP ANALYSIS FUNCTION -------------------
def analyze_gaps(text):
    years = re.findall(r"\b(19|20)\d{2}\b", text)
    years = sorted(set(map(int, years)))
    
    if not years:
        return [], "⚠️ No years detected. Please provide career/education timeline with years."
    
    gaps = []
    for i in range(len(years) - 1):
        if years[i+1] - years[i] > 1:
            gaps.append((years[i], years[i+1]))
    
    return years, gaps

# ------------------- RUN ANALYSIS -------------------
if st.button("🔍 Analyze Career Gaps"):
    if career_text.strip():
        years, gaps = analyze_gaps(career_text)
        
        if years:
            st.success(f"📅 Career Timeline Detected: {years[0]} → {years[-1]}")
            
            if gaps:
                st.warning("⚠️ Career Gaps Found:")
                for g in gaps:
                    st.write(f" - Gap between {g[0]} and {g[1]}")
            else:
                st.success("✅ No major career gaps detected. Well done!")
            
            # ------------------- DOMAIN BASED SUGGESTIONS -------------------
            st.subheader("🎯 Personalized Suggestions")
            if domain == "Student":
                st.info("📘 Keep learning new skills during breaks. Online certifications can cover gaps.")
            elif domain == "Sportsperson":
                st.info("⚽ Highlight training, tournaments, or fitness programs even during breaks.")
            elif domain == "Medical Professional":
                st.info("🩺 Show internships, research, or volunteer work during study breaks.")
            elif domain == "Business/Entrepreneur":
                st.info("💼 Document experiments, freelancing, or networking even if startups failed.")
            else:
                st.info("🌍 Show volunteer work, freelancing, or learning during gaps.")
            
            # ------------------- MOTIVATIONAL QUOTE -------------------
            st.markdown(
                f"""
                <div style="background:#f0f0f0; padding:15px; border-radius:10px; text-align:center;">
                    <h4>"Every gap is an opportunity to learn, grow, and restart stronger 💪"</h4>
                </div>
                """, unsafe_allow_html=True
            )
            
            # ------------------- REPORT DOWNLOAD -------------------
            report = f"Career Timeline: {years[0]} - {years[-1]}\n"
            if gaps:
                report += "Gaps Detected:\n"
                for g in gaps:
                    report += f"- {g[0]} to {g[1]}\n"
            else:
                report += "No major gaps detected.\n"
            report += f"\nSuggestions for {domain} provided."
            
            st.download_button("📥 Download Gap Report", report, file_name="career_gap_report.txt")
        else:
            st.error("❌ Could not detect any valid years in the input.")
    else:
        st.error("⚠️ Please upload or paste your career history first.")
