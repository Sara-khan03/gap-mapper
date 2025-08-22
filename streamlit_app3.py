import io
import os
import re
import math
import base64
import textwrap
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from rapidfuzz import fuzz, process
import docx2txt
from PyPDF2 import PdfReader

import spacy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ------------------------------
# Init / Config
# ------------------------------
st.set_page_config(page_title="Career Gap Mapper (Universal)", page_icon="🧭", layout="wide")
st.title("🧭 Career Gap Mapper — Universal")
st.caption("Upload your resume, paste a target role/JD, and get a personalized gap map, recommendations, and a learning roadmap.")

@st.cache_resource(show_spinner=False)
def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return None

nlp = load_nlp()

# ------------------------------
# Domain Skill Ontology (editable)
# Each skill has optional weight (importance) 1–5 and tags
# ------------------------------
ONTOLOGY = {
    "Technology / Data": {
        "skills": {
            "python": 5, "java": 4, "c++": 4, "javascript": 4, "react": 3, "node.js": 3,
            "sql": 5, "data modeling": 4, "machine learning": 5, "deep learning": 4,
            "nlp": 4, "computer vision": 4, "tensorflow": 3, "pytorch": 3,
            "cloud": 4, "aws": 4, "azure": 4, "gcp": 4,
            "docker": 3, "kubernetes": 3, "git": 3, "linux": 3,
            "data visualization": 4, "tableau": 3, "power bi": 3,
            "communication": 4, "problem solving": 4, "agile": 3
        }
    },
    "Business / Management": {
        "skills": {
            "financial analysis": 5, "excel": 4, "sql": 3, "power bi": 3, "tableau": 3,
            "market research": 4, "product management": 5, "pricing": 4,
            "strategic planning": 5, "stakeholder management": 4,
            "presentation": 4, "negotiation": 4, "communication": 5, "project management": 5
        }
    },
    "Medical / Healthcare": {
        "skills": {
            "patient assessment": 5, "clinical documentation": 5, "diagnostics": 5,
            "pharmacology": 4, "infection control": 5, "emr/ehr": 4, "telemedicine": 3,
            "basic life support": 5, "advanced cardiac life support": 5,
            "bedside manner": 4, "triage": 4, "medical research": 3,
            "teamwork": 4, "communication": 5, "ethics": 5
        }
    },
    "Sports / Performance": {
        "skills": {
            "strength conditioning": 5, "endurance training": 5, "agility": 4,
            "injury prevention": 5, "sports nutrition": 4, "recovery protocols": 5,
            "tactical awareness": 4, "video analysis": 3,
            "mental resilience": 5, "teamwork": 5, "leadership": 4, "communication": 4,
            "performance analytics": 4, "gps tracking": 3
        }
    },
    "Design / Creative": {
        "skills": {
            "ui design": 5, "ux research": 5, "wireframing": 4, "prototyping": 4,
            "figma": 4, "adobe xd": 3, "illustrator": 3, "photoshop": 3,
            "interaction design": 4, "accessibility": 5, "visual hierarchy": 4,
            "design systems": 4, "motion design": 3, "communication": 4, "portfolio storytelling": 5
        }
    },
    "Education / Teaching": {
        "skills": {
            "lesson planning": 5, "classroom management": 5, "assessment design": 5,
            "differentiated instruction": 5, "edtech tools": 4, "lms": 4,
            "student engagement": 5, "communication": 5, "parent liaison": 4,
            "curriculum design": 5, "research methods": 3
        }
    }
}

# Map of generic recs per skill root token
RECS = {
    # generic across domains
    "communication": ["Toastmasters practice plan", "Teach-back method sessions", "Weekly presentation challenge"],
    "project management": ["PMI CAPM prep", "2-week Scrum simulation", "Jira basics live practice"],
    "sql": ["Kaggle SQL micro-courses", "Mode Analytics SQL Tutorial", "Build a warehouse demo"],
    "python": ["Automate the Boring Stuff", "30-day Python scripting plan", "DataCamp intro track"],
    "data visualization": ["Makeover Monday (Tableau)", "Storytelling with Data drills"],
    "patient assessment": ["OSCE-style mock scenarios", "Shadow a clinician 2x/week"],
    "injury prevention": ["Prehab routine template", "Sports physio workshop"],
    "ui design": ["Daily UI challenge (30 days)", "Design Systems crash course"],
    "lesson planning": ["Backward design templates", "Universal Design for Learning (UDL)"]
}

# Domain-specific project ideas (portfolio-friendly)
PROJECTS = {
    "Technology / Data": [
        "End-to-end churn prediction with SHAP explanations",
        "MLOps-lite pipeline: data → train → deploy (FastAPI + Docker)"
    ],
    "Business / Management": [
        "Market sizing + pricing strategy deck from public data",
        "KPI dashboard (profitability, retention, CAC/LTV) with a simulated dataset"
    ],
    "Medical / Healthcare": [
        "Build a triage decision-support mock app using guidelines",
        "Analyze synthetic EMR data for infection control trends"
    ],
    "Sports / Performance": [
        "GPS/accelerometer session analyzer with load management",
        "Video breakdown tool for tactical events (open-source footage)"
    ],
    "Design / Creative": [
        "Accessible design system (WCAG AA) with tokens + Figma kit",
        "UX research case study: recruit, test, synthesize, prototype"
    ],
    "Education / Teaching": [
        "Micro-MOOC with interactive quizzes + analytics",
        "Adaptive learning prototype using item-response theory (IRT)"
    ]
}

def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9+.# ]", " ", s.lower()).replace("  ", " ").strip()

def read_resume(file) -> str:
    name = file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for p in reader.pages:
            t = p.extract_text() or ""
            text += "\n" + t
        return text
    elif name.endswith(".docx"):
        # need saved temp file for docx2txt
        tmp = f"/tmp/{name}"
        with open(tmp, "wb") as f:
            f.write(file.getbuffer())
        return docx2txt.process(tmp) or ""
    elif name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    else:
        return ""

def keyword_skillset():
    # Build a unique canon list of skills across all domains
    bag = set()
    weights = {}
    for dom, cfg in ONTOLOGY.items():
        for sk, w in cfg["skills"].items():
            bag.add(sk)
            weights[sk] = max(weights.get(sk, 0), w)
    return sorted(bag), weights

ALL_SKILLS, GLOBAL_WEIGHTS = keyword_skillset()

def extract_skills_freeform(text: str, top_n=80, cutoff=80):
    """
    Fuzzy match chunks in resume/JD against our global skill dictionary.
    Returns unique canonical skills.
    """
    text_norm = normalize(text)
    tokens = set(re.split(r"[\s,/;|()\[\]-]+", text_norm))
    # generate candidate n-grams up to 3
    grams = set(tokens)
    words = text_norm.split()
    for n in [2, 3]:
        grams.update(" ".join(words[i:i+n]) for i in range(len(words)-n+1))
    grams = [g for g in grams if 2 <= len(g) <= 40]

    matches = process.extract(
        grams, ALL_SKILLS, scorer=fuzz.WRatio, limit=top_n
    )
    picked = []
    for cand, score, canon in matches:
        if score >= cutoff:
            picked.append(canon)
    return sorted(set(picked))

def weight_for(skill: str, domain: str) -> int:
    if domain in ONTOLOGY and skill in ONTOLOGY[domain]["skills"]:
        return ONTOLOGY[domain]["skills"][skill]
    return GLOBAL_WEIGHTS.get(skill, 3)

def suggest_recs(skill: str, domain: str):
    out = []
    # domain flavored recs
    if domain in PROJECTS:
        # add generic but keep domain-specific via project list separately
        pass
    # generic recs by root token
    root = skill.split()[0]
    out += RECS.get(skill, []) + RECS.get(root, [])
    # fallbacks
    if not out:
        out = [f"Find a mentor-guided micro-project focusing on **{skill}**",
               f"1-page brief + demo artifact for **{skill}**",
               f"Daily 20-min drills for **{skill}** (4 weeks)"]
    return list(dict.fromkeys(out))[:3]

def roadmap(missing_list, weeks=8, domain="Technology / Data"):
    """
    Distribute missing skills into a week-by-week plan by weight.
    """
    if not missing_list:
        return []

    items = sorted(missing_list, key=lambda x: (-x['weight'], x['skill']))
    buckets = [[] for _ in range(weeks)]
    # round-robin by importance
    idx = 0
    for it in items:
        buckets[idx % weeks].append(it)
        idx += 1

    start = datetime.today()
    plan = []
    for w, skills in enumerate(buckets, start=1):
        if not skills:
            continue
        wk_start = (start + timedelta(days=(w-1)*7)).strftime("%b %d")
        wk_end   = (start + timedelta(days=(w*7-1))).strftime("%b %d")
        plan.append({
            "week": f"Week {w} ({wk_start}–{wk_end})",
            "focus": [s["skill"] for s in skills],
            "actions": sum([s["recs"] for s in skills], [])
        })
    return plan

def plot_radar(skills_scored, title="Skill Radar"):
    labels = [s['skill'] for s in skills_scored][:10]  # limit chart clutter
    if not labels:
        return None
    values = [s['score'] for s in skills_scored][:10]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values = np.concatenate((values, [values[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.15)
    ax.set_thetagrids(angles * 180/np.pi, labels)
    ax.set_title(title)
    ax.set_rlim(0, 100)
    return fig

def make_pdf_report(summary, table_df, radar_png=None):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    y = H - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Career Gap Mapper — Universal")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 20

    for line in textwrap.wrap(summary, width=95):
        c.drawString(40, y, line)
        y -= 14

    y -= 10
    if radar_png is not None:
        try:
            img = ImageReader(radar_png)
            c.drawImage(img, 40, y-220, width=250, height=250, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 280, "Top Gaps & Actions:")
    c.setFont("Helvetica", 10)

    # Print up to 10 missing with 1 action each
    y = 260
    show_rows = table_df[table_df["Status"] == "Missing"].head(10).to_dict(orient="records")
    for row in show_rows:
        if y < 80:
            c.showPage(); y = H - 60; c.setFont("Helvetica", 10)
        skill = row["Skill"]
        action = row.get("Top Action", "-")
        c.drawString(40, y, f"• {skill}: {action}")
        y -= 14

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

# ------------------------------
# UI Layout
# ------------------------------
left, right = st.columns([1,1])

with left:
    st.subheader("1) Upload Resume")
    up = st.file_uploader("PDF / DOCX / TXT", type=["pdf","docx","txt"])

    st.subheader("2) Target Role / Goal")
    domain = st.selectbox("Select domain", list(ONTOLOGY.keys()))
    role = st.text_input("Role title (free text)", placeholder="e.g., Data Scientist, Physiotherapist, Striker, Product Manager")
    jd = st.text_area("Paste Job Description or describe your goal", height=180,
                      placeholder="Paste JD here or describe the responsibilities/expectations for your target role...")

    st.subheader("3) Self-ratings (optional)")
    st.caption("Boost/penalize specific skills to reflect your confidence (0–100).")
    self_rate_inputs = {}
    for sk in list(ONTOLOGY[domain]["skills"].keys())[:10]:
        self_rate_inputs[sk] = st.slider(f"{sk}", 0, 100, 60)

with right:
    st.subheader("4) Analyze")
    run = st.button("Run Career Gap Mapping", type="primary", use_container_width=True)

    result_container = st.container()

# ------------------------------
# Execution
# ------------------------------
if run:
    if up is None and not jd.strip():
        st.warning("Please upload a resume and/or paste a target JD/goal.")
        st.stop()

    resume_text = read_resume(up) if up else ""
    target_text = jd

    # Extract skills
    res_skills = set(extract_skills_freeform(resume_text, top_n=120, cutoff=82)) if resume_text else set()
    jd_skills  = set(extract_skills_freeform(target_text, top_n=120, cutoff=82)) if target_text else set()

    # If JD empty, use domain skills as required set
    required_pool = jd_skills if jd_skills else set(ONTOLOGY[domain]["skills"].keys())

    # Build scored table
    rows = []
    for sk in sorted(required_pool):
        present = sk in res_skills
        w = weight_for(sk, domain)
        self_score = self_rate_inputs.get(sk, 60)
        base_score = 80 if present else 20
        # Weighted overall: presence + self rating + importance
        overall = int(0.5*base_score + 0.3*self_score + 0.2*(w*20))
        status = "Present" if present else "Missing"
        recs = suggest_recs(sk, domain)
        rows.append({
            "Skill": sk,
            "Importance(1-5)": w,
            "Status": status,
            "Self Rating(0-100)": self_score,
            "Score(0-100)": overall,
            "Top Action": recs[0],
            "More Actions": "; ".join(recs)
        })

    df = pd.DataFrame(rows).sort_values(["Status","Importance(1-5)","Score(0-100)"], ascending=[True, False, False])
    present_df = df[df["Status"]=="Present"]
    missing_df = df[df["Status"]=="Missing"]

    # Build radar on top 10 by importance
    radar_items = []
    for _, r in df.sort_values("Importance(1-5)", ascending=False).head(10).iterrows():
        radar_items.append({"skill": r["Skill"], "score": r["Score(0-100)"]})

    fig = plot_radar(radar_items, title=f"{domain} — Top Skills Radar")

    with result_container:
        st.markdown("### Results")
        c1, c2, c3 = st.columns([1,1,1])

        c1.metric("Matched skills", int(present_df.shape[0]))
        c2.metric("Missing skills", int(missing_df.shape[0]))
        avg_score = int(df["Score(0-100)"].mean()) if not df.empty else 0
        c3.metric("Overall readiness", avg_score)

        st.markdown("#### Skills Table")
        st.dataframe(df, use_container_width=True, height=360)

        if fig:
            st.markdown("#### Skill Radar")
            st.pyplot(fig, clear_figure=True, use_container_width=False)

        # Domain project ideas
        st.markdown("#### Portfolio-Ready Project Ideas")
        for idea in PROJECTS.get(domain, []):
            st.markdown(f"- {idea}")

        # Roadmap
        missing_payload = []
        for _, r in missing_df.iterrows():
            missing_payload.append({
                "skill": r["Skill"],
                "weight": r["Importance(1-5)"],
                "recs": RECS.get(r["Skill"], [r["Top Action"]])
            })

        weeks = st.slider("Roadmap length (weeks)", 4, 16, 8, help="Auto-distributes missing skills by importance.")
        plan = roadmap(missing_payload, weeks=weeks, domain=domain)

        st.markdown("#### Learning Roadmap")
        if not plan:
            st.info("No missing skills detected for the selected domain/goal — nice! Consider deepening strengths or expanding the scope.")
        else:
            for wk in plan:
                with st.expander(wk["week"], expanded=False):
                    st.markdown("**Focus:** " + ", ".join(wk["focus"]))
                    st.markdown("**Actions:**")
                    for a in wk["actions"][:6]:
                        st.markdown(f"- {a}")

        # Export buttons
        st.markdown("#### Export")
        # CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV (skills table)", csv, file_name="career_gap_map.csv", mime="text/csv")

        # PDF (render radar to buffer)
        radar_png_buf = None
        if fig:
            radar_png_buf = io.BytesIO()
            fig.savefig(radar_png_buf, format="png", bbox_inches="tight")
            radar_png_buf.seek(0)

        # Summary text
        summary = (
            f"Domain: {domain} | Role: {role or '—'} | "
            f"Matched: {present_df.shape[0]} | Missing: {missing_df.shape[0]} | "
            f"Readiness: {avg_score}/100. "
            f"This report highlights your top strengths and the most impactful gaps with a week-by-week plan."
        )

        pdf_buf = make_pdf_report(summary, df, radar_png=radar_png_buf)
        st.download_button("🧾 Download PDF Report", data=pdf_buf, file_name="career_gap_report.pdf", mime="application/pdf")

        st.markdown("---")
        st.markdown("**Tips**")
        st.markdown("- Tune self-ratings to reflect confidence; the radar and roadmap update instantly.")
        st.markdown("- If you don’t have a JD, leave it blank and the app uses the domain skill map as the target.")
        st.markdown("- Edit the ontology dictionaries in code to fit your market/roles even better.")

# Footer
st.caption("Made with ❤️ to help anyone — students, clinicians, athletes, managers, designers, teachers — map and close their career gaps.")
