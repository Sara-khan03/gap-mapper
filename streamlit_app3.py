import streamlit as st
import re
from datetime import datetime

# App title and description
st.markdown('''
    <div style="text-align:center;">
        <h1 style="color:#FFA500;">🧭 Career Gap Mapper</h1>
        <h3 style="color:#00BFFF;">Map your career journey, find gaps, and get guidance 🚀</h3>
    </div>
    ''', unsafe_allow_html=True)

st.write("Upload your resume text (or paste manually) and we’ll analyze for possible gaps in education, work, sports, medical, or business journeys.")

# Resume input
resume_text = st.text_area("📄 Paste your Resume / CV text here:")

if st.button("Analyze Career Gaps"):
    if not resume_text.strip():
        st.warning("⚠️ Please paste your resume text first.")
    else:
        st.subheader("🔍 Analysis Results:")

        # Simple regex checks for key sections
        education_found = bool(re.search(r"(education|degree|university|college|school)", resume_text, re.I))
        work_found = bool(re.search(r"(experience|internship|company|organization|employer)", resume_text, re.I))
        sports_found = bool(re.search(r"(sports|athlete|tournament|championship|fitness)", resume_text, re.I))
        medical_found = bool(re.search(r"(medical|health|doctor|hospital|treatment)", resume_text, re.I))
        business_found = bool(re.search(r"(business|startup|entrepreneur|venture|investment)", resume_text, re.I))

        gaps = []
        if not education_found:
            gaps.append("📘 Education background is missing or unclear.")
        if not work_found:
            gaps.append("💼 Work experience not highlighted.")
        if not sports_found:
            gaps.append("⚽ Sports/Extracurricular achievements not found.")
        if not medical_found:
            gaps.append("🩺 Medical/health-related details are missing.")
        if not business_found:
            gaps.append("📊 Business/entrepreneurship aspects are not mentioned.")

        if gaps:
            for g in gaps:
                st.error(g)
        else:
            st.success("✅ Your resume looks well-rounded! No major gaps found.")

        # Suggestions
        st.subheader("💡 Suggestions to Improve Resume:")
        if not education_found:
            st.info("👉 Add your degrees, certifications, or relevant courses.")
        if not work_found:
            st.info("👉 Mention internships, jobs, or volunteer experience.")
        if not sports_found:
            st.info("👉 Include extracurriculars like sports, clubs, or competitions.")
        if not medical_found:
            st.info("👉 Highlight any medical/health training or relevant achievements.")
        if not business_found:
            st.info("👉 If applicable, add business ventures, leadership, or startup experiences.")

# Footer
st.markdown("---")
st.markdown("🌟 *Career Gap Mapper helps you identify missing parts in your journey and guides you to build a stronger profile.*")


