# app.py — Career Gap Mapper (Field-Aware, Live APIs + Fallbacks)
import io
import re
import json
import time
import base64
import requests
import datetime as dt
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
import numpy as np

# PDF/DOCX parsing (optional; included in requirements)
import pdfplumber
import docx2txt

# ----------------------------- App Config ----------------------------- #
st.set_page_config(
    page_title="Career Gap Mapper",
    page_icon="🧭",
    layout="wide"
)

# ----------------------------- Utilities ----------------------------- #
@st.cache_data(show_spinner=False)
def load_countries() -> Dict[str, List[str]]:
    """Static country -> city lists, extend as needed."""
    return {
        "India": ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"],
        "USA": ["New York", "San Francisco", "Chicago", "Seattle", "Austin", "Los Angeles", "Boston", "Atlanta", "Dallas", "Miami"],
        "UK": ["London", "Manchester", "Birmingham", "Leeds", "Edinburgh", "Glasgow", "Bristol", "Liverpool", "Cardiff"],
    }

def section_title(title: str, emoji: str = "✨"):
    st.markdown(f"### {emoji} {title}")

def pill(text: str, color: str = "#0ea5e9"):
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:white;
            padding:4px 10px;
            border-radius:999px;
            font-size:0.85rem;">
            {text}
        </span>
        """,
        unsafe_allow_html=True
    )

def pretty_date(date_str: str) -> str:
    try:
        return dt.datetime.fromisoformat(date_str).strftime("%d %b %Y")
    except:
        return date_str

# ----------------------------- Resume Parsing ----------------------------- #
def parse_resume(file) -> str:
    """
    Return the raw text of a resume file (pdf, docx, txt).
    """
    if file is None:
        return ""
    name = file.name.lower()
    if name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            full_text = []
            for page in pdf.pages:
                full_text.append(page.extract_text() or "")
        return "\n".join(full_text)
    elif name.endswith(".docx"):
        # Streamlit uploads file-like bytes; docx2txt expects a path or file-like
        # Save to buffer temporary
        content = file.read()
        tmp_path = "uploaded_resume.docx"
        with open(tmp_path, "wb") as f:
            f.write(content)
        text = docx2txt.process(tmp_path) or ""
        return text
    else:
        # assume text
        return file.read().decode("utf-8", errors="ignore")

def extract_profile(text: str) -> Dict[str, Any]:
    """
    Super-simple keyword extractor for demo (skills, edu, exp years).
    """
    lower = text.lower()
    # naive year-of-experience guess
    exp_years = 0
    m = re.search(r"(\d+)\+?\s*(years|yrs)", lower)
    if m:
        try:
            exp_years = int(m.group(1))
        except:
            pass

    skills_found = sorted(list(set(re.findall(r"(python|java|sql|react|excel|communication|leadership|ml|data analysis|marketing|sales|finance|nursing|clinical|football|cricket|athletics|design)", lower))))
    edu = []
    for line in text.splitlines():
        if re.search(r"(b\.?tech|m\.?tech|bsc|msc|mba|b\.?com|mbbs|md|bpt|bba|phd|diploma|high school)", line.lower()):
            edu.append(line.strip())

    has_projects = bool(re.search(r"(project|capstone|portfolio|github)", lower))
    has_intern = bool(re.search(r"(intern|internship|trainee)", lower))
    has_cert = bool(re.search(r"(certificate|certification|coursera|udemy|edx)", lower))

    return {
        "exp_years": exp_years,
        "skills": skills_found,
        "education": edu[:5],
        "has_projects": has_projects,
        "has_internship": has_intern,
        "has_certifications": has_cert
    }

def analyze_gaps(profile: Dict[str, Any], field: str) -> Dict[str, Any]:
    """
    Produce a basic analysis and recommendations depending on field & profile.
    """
    recs = []
    flags = []

    # Common gaps
    if not profile["has_projects"]:
        flags.append("No projects/portfolio mentioned.")
        recs.append("Add 2–3 concise project bullets with outcomes and links (GitHub/Portfolio).")

    if not profile["has_internship"] and field in ["Technology", "Business", "Medical"]:
        flags.append("No internships listed.")
        recs.append("Apply to 1–2 short internships or externships to gain recent practical exposure.")

    if not profile["has_certifications"]:
        recs.append("Add at least one verified certification (free or paid) relevant to your field.")

    # Field specific
    if field == "Technology":
        must_skills = {"python", "sql", "git", "data analysis"}
        missing = must_skills - set(profile["skills"])
        if missing:
            flags.append(f"Missing tech core skills: {', '.join(sorted(missing))}.")
            recs.append("Complete a focused course in core programming, SQL, and Git basics.")
    elif field == "Business":
        must_skills = {"excel", "communication", "leadership"}
        missing = must_skills - set(profile["skills"])
        if missing:
            flags.append(f"Missing essential business skills: {', '.join(sorted(missing))}.")
            recs.append("Showcase a case-study project (market analysis, P&L model, or go-to-market plan).")
    elif field == "Medical":
        must_skills = {"nursing", "clinical"}
        missing = must_skills - set(profile["skills"])
        if missing:
            flags.append(f"Clinical exposure not obvious: {', '.join(sorted(missing))}.")
            recs.append("Add clinical rotations, CME credits, and patient-care cases (de-identified).")
    elif field == "Sports":
        must_skills = {"football", "cricket", "athletics"}
        if not set(profile["skills"]) & must_skills:
            flags.append("Specific sport not clear.")
            recs.append("Specify your primary sport, position/event, stats (PBs), and recent tournaments/trials.")

    score = 100
    score -= 10 if not profile["has_projects"] else 0
    score -= 10 if (field in ["Technology", "Business", "Medical"] and not profile["has_internship"]) else 0
    score -= 5 if not profile["has_certifications"] else 0
    score = max(30, score)

    return {
        "score": score,
        "flags": flags,
        "recommendations": recs
    }

# ----------------------------- Live APIs (with fallbacks) ----------------------------- #
@st.cache_data(show_spinner=False, ttl=1800)
def fetch_remotive_jobs(query: str, location: str) -> List[Dict[str, Any]]:
    """
    Remotive public jobs API (works for internships & jobs). No auth required.
    """
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {"search": query}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("jobs", [])
        # Lightweight mapping
        out = []
        for j in data[:30]:
            out.append({
                "title": j.get("title"),
                "company": j.get("company_name"),
                "location": j.get("candidate_required_location") or "Remote",
                "url": j.get("url")
            })
        return out
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=1800)
def try_devpost_upcoming() -> List[Dict[str, Any]]:
    """
    Devpost upcoming hackathons (unofficial; may fail). We try and fallback.
    """
    try:
        # Unofficial/test endpoint. If this fails, fallback list will be used.
        url = "https://devpost.com/api/hackathons?status=upcoming"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        items = []
        for h in data[:20]:
            items.append({
                "name": h.get("title") or h.get("name", "Hackathon"),
                "org": h.get("organization_name") or "Devpost",
                "start": h.get("start_date") or "",
                "end": h.get("end_date") or "",
                "city": h.get("location") or "Online",
                "link": h.get("url") or h.get("hackathon_url")
            })
        return items
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=1800)
def sports_events_by_country(country: str) -> List[Dict[str, Any]]:
    """
    Use TheSportsDB sample endpoints (no key) and fallback curated events.
    """
    events = []
    try:
        # Example: pull some soccer leagues and list
        url = "https://www.thesportsdb.com/api/v1/json/1/all_leagues.php"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        leagues = r.json().get("leagues", [])[:30]
        for L in leagues:
            sport = L.get("strSport")
            name = L.get("strLeague")
            if not sport or not name:
                continue
            # Map by sport popularity per country (very rough)
            if country in ["India"] and sport in ["Cricket", "Soccer", "Athletics", "Tennis", "Badminton"]:
                events.append({
                    "name": f"{name} – Selection/Trials Window",
                    "sport": sport,
                    "city": "Varies",
                    "dates": "Check federation calendar",
                    "link": f"https://www.google.com/search?q={name.replace(' ', '+')}+trials+{country}"
                })
            elif country in ["USA", "UK"] and sport in ["Basketball", "Soccer", "Athletics", "Tennis"]:
                events.append({
                    "name": f"{name} – Open Trials/Qualifiers",
                    "sport": sport,
                    "city": "Varies",
                    "dates": "Check league calendar",
                    "link": f"https://www.google.com/search?q={name.replace(' ', '+')}+tryouts+{country}"
                })
        # Deduplicate by name
        seen = set()
        uniq = []
        for e in events:
            if e["name"] not in seen:
                uniq.append(e)
                seen.add(e["name"])
        return uniq[:30]
    except Exception:
        return []

def course_search_links(keyword: str):
    """Generate universal search links (Coursera/edX/Udemy/ClassCentral)."""
    q = keyword.replace(" ", "+")
    return {
        "Coursera": f"https://www.coursera.org/search?query={q}",
        "edX": f"https://www.edx.org/search?q={q}",
        "Udemy": f"https://www.udemy.com/courses/search/?q={q}",
        "Class Central": f"https://www.classcentral.com/search?q={q}"
    }

# ----------------------------- Sidebar (Global) ----------------------------- #
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?q=80&w=1200&auto=format&fit=crop",
        use_column_width=True,
        caption="Map your gaps. Level up faster."
    )
    st.markdown("## Navigation")
    page = st.radio(
        "",
        ["🏠 Home + Resume Analyzer", "🌍 Location Selector", "🏆 Events & Competitions", "🎓 Courses & Internships", "🤖 Career Tips Bot", "📚 Resources"],
        index=0
    )
    st.caption("Tip: Upload a resume on Home for tailored gaps & suggestions.")

# ----------------------------- HOME + ANALYZER ----------------------------- #
if page == "🏠 Home + Resume Analyzer":
    st.title("🧭 Career Gap Mapper")
    st.subheader("Upload your resume and we’ll map your gaps with field-aware suggestions.")

    c1, c2 = st.columns([2, 1])
    with c1:
        field = st.selectbox("Your field", ["Technology", "Business", "Medical", "Sports", "Arts", "Other"])

        resume_file = st.file_uploader(
            "Upload Resume (PDF/DOCX/TXT)", 
            type=["pdf", "docx", "txt"]
        )

        raw_text = parse_resume(resume_file) if resume_file else ""
        if resume_file:
            st.success(f"Parsed: {resume_file.name}")
            st.text_area("Extracted Text (preview)", raw_text[:4000], height=180)

        if st.button("Analyze Resume", type="primary"):
            if not raw_text:
                st.warning("Please upload a resume first.")
            else:
                prof = extract_profile(raw_text)
                result = analyze_gaps(prof, field)

                st.success(f"Overall Readiness Score: {result['score']}/100")
                if result["flags"]:
                    section_title("Key Gaps", "🚩")
                    for f in result["flags"]:
                        st.markdown(f"- {f}")

                section_title("Recommendations", "🛠️")
                for r in result["recommendations"]:
                    st.markdown(f"- {r}")

                # Field-aware quick links
                section_title("Next Steps", "➡️")
                if field == "Technology":
                    links = course_search_links("python sql git data analysis")
                elif field == "Business":
                    links = course_search_links("excel financial modeling marketing analytics")
                elif field == "Medical":
                    links = course_search_links("clinical skills public health biostatistics")
                elif field == "Sports":
                    links = course_search_links("sports training strength conditioning nutrition")
                elif field == "Arts":
                    links = course_search_links("graphic design portfolio branding")
                else:
                    links = course_search_links("career development")

                cols = st.columns(4)
                for i, (name, url) in enumerate(links.items()):
                    with cols[i % 4]:
                        st.markdown(f"[{name}]({url})")

    with c2:
        st.markdown("### Why use Career Gap Mapper?")
        st.write("- Field-aware gap analysis")
        st.write("- Live internships & events (where possible)")
        st.write("- Curated plans + course links")
        st.write("- Works for tech, business, medical, sports, arts & more")

# ----------------------------- LOCATION SELECTOR ----------------------------- #
elif page == "🌍 Location Selector":
    st.title("🌍 Choose your Location & Field")
    countries = load_countries()
    field = st.selectbox("Field", ["Technology", "Business", "Medical", "Sports", "Arts", "Other"])
    country = st.selectbox("Country", list(countries.keys()))
    city = st.selectbox("City", countries[country])

    st.info(f"Selected: **{city}, {country}** — Field: **{field}**")

    # Show something meaningful immediately
    if field in ["Technology", "Business", "Medical"]:
        section_title(f"Top Picks in {city}", "💼")
        st.write("- Leading employers, internship hotspots, and meetups in your city.")
        st.write("- Try the **Events & Competitions** and **Courses & Internships** pages for live data.")
    elif field == "Sports":
        section_title(f"Sports High-Performance Centers in/near {city}", "🥇")
        st.write("- Check national/state associations & stadium academies.")
        st.write("- Visit **Events & Competitions** for live trials and tournaments.")
    else:
        section_title(f"Creative & Cultural Hubs in {city}", "🎨")
        st.write("- Community centers, art schools, local theaters.")
        st.write("- Explore **Events & Competitions** for exhibitions & fests.")

# ----------------------------- EVENTS & COMPETITIONS ----------------------------- #
elif page == "🏆 Events & Competitions":
    st.title("🏆 Events & Competitions (Live where possible)")

    field = st.selectbox("Choose field", ["Technology", "Business", "Medical", "Sports", "Arts", "Other"])
    countries = load_countries()
    country = st.selectbox("Country", list(countries.keys()), index=0)
    city = st.selectbox("City", countries[country], index=0)

    if field == "Technology":
        pill("Tech Hackathons & Challenges")
        live = try_devpost_upcoming()
        if live:
            st.success("Loaded upcoming Devpost hackathons (beta).")
            df = pd.DataFrame(live)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Couldn’t fetch Devpost (network/API). Showing curated list.")
            curated = [
                {"name":"City AI Datathon", "org":"City Tech Community", "start":"2026-01-10", "end":"2026-01-12", "city":city, "link":"https://ai.devpost.com/"},
                {"name":"Cloud Builders Challenge", "org":"Cloud Org", "start":"2026-02-01", "end":"2026-02-28", "city":"Online", "link":"https://devpost.com/"},
                {"name":"Open Source Sprint", "org":"FOSS Group", "start":"2026-03-05", "end":"2026-03-07", "city":city, "link":"https://hackathons.example.com"},
            ]
            st.dataframe(pd.DataFrame(curated), use_container_width=True)

    elif field == "Sports":
        pill("Sports Trials, Meets & Tournaments")
        events = sports_events_by_country(country)
        if events:
            st.success("Loaded federation/league calendars (sample).")
            st.dataframe(pd.DataFrame(events), use_container_width=True)
        else:
            st.warning("Couldn’t fetch sports events live. Showing curated city list.")
            curated = [
                {"name":"National Athletics Open", "sport":"Athletics", "city":city, "dates":"Dec 2025", "link":"https://sportsauthority.example.com"},
                {"name":"State Football Trials", "sport":"Football", "city":city, "dates":"Jan 2026", "link":"https://footballfederation.example.com"},
                {"name":"City Cricket Camp", "sport":"Cricket", "city":city, "dates":"Feb 2026", "link":"https://cricketboard.example.com"},
            ]
            st.dataframe(pd.DataFrame(curated), use_container_width=True)

    elif field == "Business":
        pill("Business Case Competitions & Summits")
        curated = [
            {"name":"Finance Case Study Championship", "org":"Biz League", "start":"2026-01-15", "end":"2026-01-20", "city":city, "link":"https://casecomp.example.com"},
            {"name":"Entrepreneurship Summit", "org":f"{city} Startup Hub", "start":"2026-02-10", "end":"2026-02-12", "city":city, "link":"https://startup.example.com"},
        ]
        st.dataframe(pd.DataFrame(curated), use_container_width=True)

    elif field == "Medical":
        pill("Medical Conferences & Public Health Challenges")
        curated = [
            {"name":"Medical Innovations Expo", "org":"Health Assoc", "start":"2026-01-25", "end":"2026-01-27", "city":city, "link":"https://medexpo.example.com"},
            {"name":"Public Health Hackathon", "org":"City Health Org", "start":"2026-02-14", "end":"2026-02-16", "city":"Online", "link":"https://publichealth.example.com"},
        ]
        st.dataframe(pd.DataFrame(curated), use_container_width=True)

    elif field == "Arts":
        pill("Arts Festivals & Exhibitions")
        curated = [
            {"name":"City Art Biennale", "org":"Art Council", "start":"2026-03-01", "end":"2026-03-15", "city":city, "link":"https://art.example.com"},
            {"name":"Music & Dance Festival", "org":f"{city} Culture Dept", "start":"2026-02-05", "end":"2026-02-08", "city":city, "link":"https://culture.example.com"},
        ]
        st.dataframe(pd.DataFrame(curated), use_container_width=True)
    else:
        pill("General Opportunities")
        curated = [
            {"name":"Community Innovation Challenge", "org":"Civic Lab", "start":"2026-01-12", "end":"2026-01-14", "city":city, "link":"https://civiclab.example.com"},
        ]
        st.dataframe(pd.DataFrame(curated), use_container_width=True)

# ----------------------------- COURSES & INTERNSHIPS ----------------------------- #
elif page == "🎓 Courses & Internships":
    st.title("🎓 Recommended Courses & Internships (Live where possible)")

    field = st.selectbox("Choose field", ["Technology", "Business", "Medical", "Sports", "Arts", "Other"])
    query = st.text_input("Search keyword", value="data analyst" if field == "Technology" else field.lower())

    # Internships/Jobs (Tech/Business/Medical get jobs; Sports/Arts show competitions/training)
    if field in ["Technology", "Business", "Medical"]:
        section_title("Live Internships & Jobs (Remotive)", "💼")
        jobs = fetch_remotive_jobs(query, "Remote")
        if jobs:
            st.dataframe(pd.DataFrame(jobs), use_container_width=True)
        else:
            st.warning("Couldn’t fetch live jobs. Showing curated roles.")
            curated = [
                {"title":"Business Analyst Intern", "company":"Local Startup", "location":"Hybrid", "url":"https://careers.example.com"},
                {"title":"Clinical Research Trainee", "company":"Med Institute", "location":"Onsite", "url":"https://medcareers.example.com"},
            ]
            st.dataframe(pd.DataFrame(curated), use_container_width=True)
    else:
        section_title("Competitions/Training Instead of Internships", "🏅")
        if field == "Sports":
            curated = [
                {"program":"Strength & Conditioning Camp", "location":"City Stadium", "dates":"Jan–Feb 2026", "requirements":"U18/U21 categories"},
                {"program":"Open Athletics Trials", "location":"State Sports Complex", "dates":"Feb 2026", "requirements":"Time standards"},
            ]
        else:  # Arts/Other
            curated = [
                {"program":"Portfolio Masterclass", "location":"Art Academy", "dates":"Jan 2026", "requirements":"Portfolio samples"},
                {"program":"Community Theater Residency", "location":"City Theater", "dates":"Jan–Mar 2026", "requirements":"Audition"},
            ]
        st.dataframe(pd.DataFrame(curated), use_container_width=True)

    section_title("Courses (links + curated picks)", "📚")
    linkset = course_search_links(query)
    cols = st.columns(4)
    for i, (name, url) in enumerate(linkset.items()):
        with cols[i % 4]:
            st.markdown(f"[{name}]({url})")

    st.markdown("#### Curated Courses with Dates & Requirements")
    if field == "Technology":
        data = [
            {"course":"Google Data Analytics (Coursera)","type":"Paid/Financial Aid","start":"Rolling","end":"Self-paced","requirements":"None","link":"https://www.coursera.org/professional-certificates/google-data-analytics"},
            {"course":"SQL for Data Analysis (Mode)","type":"Free","start":"Anytime","end":"Self-paced","requirements":"None","link":"https://mode.com/sql-tutorial"},
            {"course":"Git & GitHub (Udacity)","type":"Free","start":"Anytime","end":"Self-paced","requirements":"None","link":"https://www.udacity.com/course/version-control-with-git--ud123"},
        ]
    elif field == "Business":
        data = [
            {"course":"Excel to MySQL (Coursera)","type":"Paid/FA","start":"Rolling","end":"Self-paced","requirements":"Basic Excel","link":"https://www.coursera.org/specializations/excel-mysql"},
            {"course":"Marketing Analytics (edX)","type":"Paid/FA","start":"Jan 2026","end":"12 weeks","requirements":"None","link":"https://www.edx.org/"},
        ]
    elif field == "Medical":
        data = [
            {"course":"Epidemiology (Coursera)","type":"Free/Paid","start":"Rolling","end":"Self-paced","requirements":"None","link":"https://www.coursera.org/learn/epidemiology"},
            {"course":"Global Health (edX)","type":"Free/Paid","start":"Jan 2026","end":"8 weeks","requirements":"None","link":"https://www.edx.org/"},
        ]
    elif field == "Sports":
        data = [
            {"course":"Sports Nutrition Basics","type":"Free","start":"Anytime","end":"Self-paced","requirements":"None","link":"https://www.classcentral.com/"},
            {"course":"Strength & Conditioning Fundamentals","type":"Paid","start":"Monthly","end":"4 weeks","requirements":"None","link":"https://www.classcentral.com/"},
        ]
    elif field == "Arts":
        data = [
            {"course":"Graphic Design Fundamentals","type":"Free","start":"Anytime","end":"Self-paced","requirements":"None","link":"https://www.coursera.org/"},
            {"course":"Branding for Designers","type":"Paid","start":"Monthly","end":"4 weeks","requirements":"Portfolio","link":"https://www.udemy.com/"},
        ]
    else:
        data = [
            {"course":"Career Planning 101","type":"Free","start":"Anytime","end":"Self-paced","requirements":"None","link":"https://www.classcentral.com/"},
        ]
    st.dataframe(pd.DataFrame(data), use_container_width=True)

# ----------------------------- CAREER TIPS BOT ----------------------------- #
elif page == "🤖 Career Tips Bot":
    st.title("🤖 Career Tips Bot")
    st.write("Ask about gaps, resumes, interviews, or city-specific ideas.")

    if "chat" not in st.session_state:
        st.session_state.chat = [
            {"role":"assistant","content":"Hi! Ask me about resumes, courses, internships, or events."}
        ]

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    faq = [
        ("resume", "Keep impact bullets: action verb + what + result (with numbers)."),
        ("intern", "Search targeted internships via Remotive/LinkedIn. Customize your resume for each role."),
        ("course", "Prefer hands-on courses with projects and a certificate you can share."),
        ("events", "Hackathons and case comps help you network and fill gaps fast."),
        ("sports", "List personal bests, primary position, and trials/competitions in past 12 months."),
    ]

    def bot_reply(msg: str) -> str:
        m = msg.lower()
        for k, v in faq:
            if k in m:
                return v
        if "city" in m:
            return "Use the Location page to set your country/city and see tailored items."
        return "Great question! Tailor your resume to the field, fill missing skills with short projects/certifications, and keep applying weekly."

    user_msg = st.chat_input("Type your question…")
    if user_msg:
        st.session_state.chat.append({"role":"user", "content": user_msg})
        ans = bot_reply(user_msg)
        st.session_state.chat.append({"role":"assistant", "content": ans})
        with st.chat_message("user"): st.write(user_msg)
        with st.chat_message("assistant"): st.write(ans)

# ----------------------------- RESOURCES ----------------------------- #
elif page == "📚 Resources":
    st.title("📚 Resources")
    st.write("- Resume templates: Google Docs, Overleaf CV, CANVA")
    st.write("- Portfolio hosting: GitHub Pages, Notion, Behance")
    st.write("- Practice: LeetCode / HackerRank (tech), CaseCoach (business), SAI Calendar (sports)")
    st.write("- Networking: LinkedIn – alumni search, local meetups")

st.markdown("---")
st.caption("This tool uses public APIs when available and falls back to curated data. Always verify dates/requirements on the official pages.")
