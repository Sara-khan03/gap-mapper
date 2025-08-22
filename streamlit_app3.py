# app.py — Career Gap Mapper (Universal)
# Run: streamlit run app.py

import io
import os
import re
import math
import textwrap
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Defensive imports (report errors in-app rather than crash)
try:
    from rapidfuzz import fuzz, process
except Exception:
    st.error("Missing dependency: rapidfuzz. Add it to requirements.txt and redeploy.")
    raise

try:
    import docx2txt
except Exception:
    docx2txt = None

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

# spaCy: attempt to import and auto-download model if needed
try:
    import spacy
    from spacy.util import is_package
except Exception:
    spacy = None

# Try to load en_core_web_sm, download if missing
def ensure_spacy_model():
    global spacy
    if spacy is None:
        return None
    try:
        if not is_package("en_core_web_sm"):
            # attempt download
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except Exception:
        try:
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except Exception:
            return None

nlp = ensure_spacy_model()

st.set_page_config(page_title="Career Gap Mapper — Universal", page_icon="🧭", layout="wide")
st.title("🧭 Career Gap Mapper — Universal")
st.caption("Works for students, professionals, sportspersons, medical staff, business roles, creatives — get a personalized gap map & roadmap.")

# --------------------------
# Skill ontology (editable)
# --------------------------
ONTOLOGY = {
    "Technology / Data": {
        "skills": {
            "python": 5, "java": 4, "c++": 3, "sql": 5, "machine learning": 5, "deep learning": 4,
            "nlp": 4, "computer vision": 4, "pytorch": 3, "tensorflow": 3, "data visualization": 4,
            "tableau": 3, "power bi": 3, "aws": 4, "azure": 4, "git": 3, "docker": 3, "communication": 4
        }
    },
    "Business / Management": {
        "skills": {
            "financial analysis": 5, "excel": 4, "market research": 4, "product management": 5,
            "strategic planning": 5, "presentation": 4, "negotiation": 4, "communication": 5,
            "project management": 5, "sql": 3
        }
    },
    "Medical / Healthcare": {
        "skills": {
            "patient care": 5, "diagnosis": 5, "clinical documentation": 5, "pharmacology": 4,
            "infection control": 5, "emr/ehr": 4, "triage": 4, "bsl/bls": 5, "communication": 5, "ethics": 5
        }
    },
    "Sports / Performance": {
        "skills": {
            "strength conditioning": 5, "endurance training": 5, "agility": 4, "injury prevention": 5,
            "sports nutrition": 4, "recovery protocols": 5, "tactical awareness": 4, "mental resilience": 5,
            "video analysis": 3, "teamwork": 5
        }
    },
    "Design / Creative": {
        "skills": {
            "ui design": 5, "ux research": 5, "wireframing": 4, "prototyping": 4, "figma": 4,
            "illustrator": 3, "photoshop": 3, "accessibility": 5, "portfolio storytelling": 5
        }
    },
    "Education / Teaching": {
        "skills": {
            "lesson planning": 5, "classroom management": 5, "assessment design": 5,
            "differentiated instruction": 5, "edtech tools": 4, "student engagement": 5, "communication": 5
        }
    }
}

# Generic recommendations and project ideas (can expand)
RECS = {
    "python": ["Automate the Boring Stuff (projects)", "30-day Python scripting plan"],
    "sql": ["Mode Analytics SQL Tutorial", "Kaggle SQL micro-courses"],
    "machine learning": ["Coursera ML / DeepLearning.AI specialization", "Small project: churn prediction"],
    "deep learning": ["DeepLearning.AI TensorFlow Specialization", "Image classifier mini-project"],
    "nlp": ["HuggingFace course", "Text classification mini-project"],
    "communication": ["Join Toastmasters", "Weekly presentation challenge"],
    "project management": ["Scrum simulation", "CAPM/Coursera short course"],
    "patient care": ["OSCE-style mock scenarios", "Shadowing clinicians"],
    "injury prevention": ["Prehab routines curriculum", "Sports physio workshop"],
    "ui design": ["30-day Daily UI challenge", "Design system case study"]
}

PROJECTS = {
    "Technology / Data": ["End-to-end ML project with explanations (SHAP)", "MLOps-lite pipeline: train → serve (FastAPI + Docker)"],
    "Business / Management": ["KPI dashboard with simulated data", "Market sizing & pricing strategy deck"],
    "Medical / Healthcare": ["Triage mock app", "Analyze synthetic EMR for infection-control patterns"],
    "Sports / Performance": ["GPS session analyzer", "Video breakdown tool for tactics"],
    "Design / Creative": ["Accessible design system + Figma kit", "UX research case study + prototype"],
    "Education / Teaching": ["Micro-course with quizzes", "Adaptive learning prototype"]
}

# --------------------------
# Utility helpers
# --------------------------
def normalize(text: str) -> str:
    if not text:
        return ""
    s = re.sub(r"[^a-z0-9+.# ]", " ", text.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_skill_bag():
    bag = []
    weights = {}
    for dom, cfg in ONTOLOGY.items():
        for sk, w in cfg["skills"].items():
            canon = sk.lower()
            bag.append(canon)
            weights[canon] = max(weights.get(canon, 0), w)
    bag = sorted(set(bag))
    return bag, weights

ALL_SKILLS, SKILL_WEIGHTS = build_skill_bag()

def extract_text_from_uploaded(file) -> str:
    """Extract text from uploaded file (pdf/docx/txt)."""
    name = getattr(file, "name", "")
    if name.lower().endswith(".pdf"):
        if PdfReader is None:
            st.warning("PyPDF2 not available; cannot parse PDF. Please install PyPDF2.")
            return ""
        try:
            reader = PdfReader(file)
            pages = []
            for p in reader.pages:
                text = p.extract_text() or ""
                pages.append(text)
            return "\n".join(pages)
        except Exception:
            # try reading bytes fallback
            try:
                file.seek(0)
                content = file.read().decode("utf-8", errors="ignore")
                return content
            except Exception:
                return ""
    elif name.lower().endswith(".docx"):
        if docx2txt is None:
            st.warning("docx2txt not available; cannot parse DOCX. Please add docx2txt to requirements.")
            return ""
        tmp = f"/tmp/{name}"
        with open(tmp, "wb") as f:
            f.write(file.getbuffer())
        try:
            return docx2txt.process(tmp) or ""
        except Exception:
            return ""
    else:
        try:
            return file.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""

def fuzzy_extract_skills(text: str, top_n=120, cutoff=80):
    """
    Fuzzy-match n-grams from text against ALL_SKILLS using rapidfuzz.
    Returns canonical skills that pass cutoff.
    """
    txt = normalize(text)
    words = txt.split()
    candidates = set(words)
    # build 2-grams and 3-grams
    for n in (2,3):
        for i in range(len(words)-n+1):
            candidates.add(" ".join(words[i:i+n]))
    candidates = [c for c in candidates if 2 <= len(c) <= 40]

    matches = process.extract(
        candidates, ALL_SKILLS, scorer=fuzz.WRatio, limit=top_n
    )
    chosen = set()
    for cand, score, canon in matches:
        if score >= cutoff:
            chosen.add(canon)
    return sorted(chosen)

def score_skill_row(skill, present, importance, self_rating=60):
    """
    Compute a heuristic readiness score for a skill 0-100.
    present: bool
    importance: 1-5
    self_rating: 0-100 (user-provided)
    """
    base = 90 if present else 20
    score = int(0.5*base + 0.3*max(0, self_rating) + 0.2*(importance*20))
    return min(100, max(0, score))

def suggest_actions(skill):
    s = skill.lower()
    out = []
    # exact recs
    if s in RECS:
        out += RECS[s]
    # root matches
    root = s.split()[0]
    if root in RECS:
        out += RECS[root]
    if not out:
        out = [f"Find a short project focused on '{skill}'", f"Mentor review & 2-week focused practice for '{skill}'"]
    return out[:3]

def generate_roadmap(missing_skills_info, weeks=8):
    """
    Simple distribution of missing skills across weeks (round-robin by importance)
    missing_skills_info: list of dicts {'skill':..., 'weight':..., 'recs': [...]}
    """
    if not missing_skills_info:
        return []
    items = sorted(missing_skills_info, key=lambda x: (-x['weight'], x['skill']))
    buckets = [[] for _ in range(weeks)]
    for idx, item in enumerate(items):
        buckets[idx % weeks].append(item)
    start = datetime.today()
    plan = []
    for w, bucket in enumerate(buckets, start=1):
        if not bucket:
            continue
        wk_start = (start + timedelta(days=(w-1)*7)).strftime("%b %d")
        wk_end = (start + timedelta(days=w*7-1)).strftime("%b %d")
        plan.append({
            "week": f"Week {w} ({wk_start}–{wk_end})",
            "focus": [b['skill'] for b in bucket],
            "actions": sum([b['recs'] for b in bucket], [])[:6]
        })
    return plan

def radar_figure(skills_scored, title="Skill Radar"):
    labels = [s['skill'] for s in skills_scored][:8]
    if not labels:
        return None
    values = [s['score'] for s in skills_scored][:8]
    # complete loop
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    values = values + values[:1]
    angles = angles + angles[:1]

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(title)
    ax.set_ylim(0,100)
    return fig

# --------------------------
# UI
# --------------------------
st.sidebar.markdown("## ▶️ Inputs")
with st.sidebar:
    domain = st.selectbox("Target domain", list(ONTOLOGY.keys()), index=0)
    role_title = st.text_input("Role title (optional)", placeholder="e.g., Data Scientist, Physiotherapist, Striker")
    use_jd = st.checkbox("Paste Job Description / Role details", value=True)
    jd_text = st.text_area("Job Description / Role expectations", height=160, placeholder="Paste JD or describe the role responsibilities here...") if use_jd else ""
    weeks = st.slider("Roadmap length (weeks)", min_value=4, max_value=16, value=8)
    cutoff = st.slider("Fuzzy match cutoff (quality vs recall)", 60, 95, 82)

st.header("1) Upload resume (PDF / DOCX / TXT)")
uploaded = st.file_uploader("Upload your resume file", type=["pdf","docx","txt"])

st.markdown("Optional: adjust your confidence for common skills in this domain (affects scoring).")
self_rates = {}
col1, col2 = st.columns(2)
with col1:
    sks_sample = list(ONTOLOGY[domain]["skills"].keys())[:6]
    for sk in sks_sample:
        self_rates[sk] = st.slider(f"{sk} confidence", 0, 100, 60)
with col2:
    for sk in list(ONTOLOGY[domain]["skills"].keys())[6:12]:
        self_rates[sk] = st.slider(f"{sk} confidence", 0, 100, 60)

analyze_btn = st.button("🔎 Run Career Gap Mapping")

# --------------------------
# Run analysis
# --------------------------
if analyze_btn:
    with st.spinner("Analyzing resume and role..."):
        resume_text = ""
        if uploaded:
            resume_text = extract_text_from_uploaded(uploaded) or ""
        # If resume missing but user pasted JD, still proceed (use domain skills)
        target_text = jd_text.strip()

        # Extract skills
        resume_skills = set()
        jd_skills = set()

        if resume_text:
            resume_skills = set(fuzzy_extract_skills(resume_text, cutoff=cutoff))
        if target_text:
            jd_skills = set(fuzzy_extract_skills(target_text, cutoff=cutoff))
        if not jd_skills:
            # fallback to domain skill list
            jd_skills = set([s.lower() for s in ONTOLOGY[domain]["skills"].keys()])

        # Build results table
        rows = []
        for sk in sorted(jd_skills):
            importance = ONTOLOGY[domain]["skills"].get(sk, SKILL_WEIGHTS.get(sk, 3))
            present = sk in resume_skills
            self_rating = self_rates.get(sk, 60)
            score = score_skill_row(sk, present, importance, self_rating)
            actions = suggest_actions(sk)
            rows.append({
                "Skill": sk,
                "Importance": importance,
                "Status": "Present" if present else "Missing",
                "SelfRating": self_rating,
                "Score": score,
                "TopAction": actions[0],
                "MoreActions": " | ".join(actions)
            })
        df = pd.DataFrame(rows).sort_values(["Status","Importance","Score"], ascending=[True, False, False])

        # Summary metrics
        present_df = df[df["Status"]=="Present"]
        missing_df = df[df["Status"]=="Missing"]
        matched_count = present_df.shape[0]
        missing_count = missing_df.shape[0]
        readiness = int(df["Score"].mean()) if not df.empty else 0

        # Radar plot
        skills_scored = df.sort_values("Importance", ascending=False).head(8)[["Skill","Score"]].to_dict(orient="records")
        fig_radar = radar_figure(skills_scored, title=f"{domain} — Top Skills Radar")

        # Roadmap
        missing_payload = []
        for _, r in missing_df.iterrows():
            missing_payload.append({"skill": r["Skill"], "weight": int(r["Importance"]), "recs": r["MoreActions"].split(" | ")})

        plan = generate_roadmap(missing_payload, weeks=weeks)

    # --------------------------
    # Results UI
    # --------------------------
    st.header("Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Matched skills", matched_count)
    c2.metric("Missing skills", missing_count)
    c3.metric("Overall readiness", f"{readiness}/100")

    st.subheader("Skills table")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    if fig_radar:
        st.subheader("Skill radar (top items)")
        st.pyplot(fig_radar)

    st.subheader("Top missing skills & actions")
    for _, r in missing_df.head(10).iterrows():
        st.markdown(f"**{r['Skill']}** (importance {r['Importance']}) — {r['TopAction']}")
        st.caption(r["MoreActions"])

    st.subheader("Suggested portfolio / project ideas")
    for p in PROJECTS.get(domain, [])[:5]:
        st.markdown(f"- {p}")

    st.subheader("Learning roadmap")
    if not plan:
        st.info("No missing skills detected — great! Consider deepening strengths or expanding scope.")
    else:
        for wk in plan:
            with st.expander(wk["week"], expanded=False):
                st.markdown("**Focus:** " + ", ".join(wk["focus"]))
                st.markdown("**Actions:**")
                for a in wk["actions"]:
                    st.markdown(f"- {a}")

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download skills CSV", csv, file_name="career_gap_skills.csv", mime="text/csv")

    # Create a simple PDF summary
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        def make_pdf(summary_text, df_table, radar_fig=None):
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            W, H = A4
            y = H - 40
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Career Gap Mapper — Universal")
            y -= 20
            c.setFont("Helvetica", 10)
            for line in textwrap.wrap(summary_text, width=95):
                c.drawString(40, y, line)
                y -= 14
            y -= 8
            # top gaps
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Top missing skills & top action")
            y -= 16
            c.setFont("Helvetica", 10)
            for _, row in df_table[df_table["Status"]=="Missing"].head(8).iterrows():
                if y < 80:
                    c.showPage()
                    y = H - 40
                c.drawString(45, y, f"• {row['Skill']} → {row['TopAction']}")
                y -= 14
            c.showPage()
            c.save()
            buf.seek(0)
            return buf

        summary_text = f"Domain: {domain} | Role: {role_title or '—'} | Matched: {matched_count} | Missing: {missing_count} | Readiness: {readiness}/100"
        pdf_buf = make_pdf(summary_text, df)
        st.download_button("🧾 Download PDF summary", data=pdf_buf, file_name="career_gap_summary.pdf", mime="application/pdf")
    except Exception as e:
        st.warning("PDF export not available (missing reportlab).")

    st.success("Analysis complete ✅")

st.markdown("---")
st.caption("Made to help anyone — students, athletes, clinicians, managers, designers, and teachers — map and close real career gaps.")
