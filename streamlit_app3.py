# Career Gap Mapper — Streamlit (single file)
# Domains: Data/Software, Medicine, Business/Entrepreneur, Sports (Athlete), plus more roles
# Features: Resume keyword scan, self-assessment, gap radar, 12-week roadmap, resources, tracker, export, coach bot.

import re
from textwrap import dedent
from datetime import date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Career Gap Mapper", page_icon="🧭", layout="wide")

# ---------------------- Utilities ----------------------
def norm(x, a=0, b=5):
    try:
        x = float(x)
    except Exception:
        return 0.0
    return float(np.clip(x, a, b))

def radar_chart(categories, current, target):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=current + [current[0]],
                                  theta=categories + [categories[0]],
                                  fill='toself', name='You (now)'))
    fig.add_trace(go.Scatterpolar(r=target + [target[0]],
                                  theta=categories + [categories[0]],
                                  name='Target'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True, height=430, margin=dict(l=30, r=30, t=40, b=10)
    )
    return fig

def parse_resume(text, skill_keywords):
    """Very simple keyword counter -> returns rough (0..5) estimates per skill."""
    text_low = text.lower()
    scores = {}
    for skill, kws in skill_keywords.items():
        hits = 0
        for kw in kws:
            hits += len(re.findall(rf"\b{re.escape(kw.lower())}\b", text_low))
        # Map hits to 0..5 nonlinearly
        if hits == 0: s = 0
        elif hits == 1: s = 2
        elif hits <= 3: s = 3
        elif hits <= 6: s = 4
        else: s = 5
        scores[skill] = s
    return scores

def make_12_week_plan(gaps_sorted, hours_per_week):
    """Distribute top gaps into 12 weeks. Heavier gaps get more hours."""
    if not gaps_sorted:
        return []
    base_hours = max(2, int(hours_per_week))
    weights = np.array([g['gap'] for g in gaps_sorted], dtype=float)
    if weights.sum() == 0:
        weights = np.ones_like(weights)
    weights = weights / weights.sum()
    weekly_alloc = (weights * base_hours).clip(min=1.0)
    weeks = list(range(1, 13))
    plan = []
    for w in weeks:
        tasks = []
        for i, g in enumerate(gaps_sorted):
            hrs = weekly_alloc[i]
            verb = {
                "Theory": "Read/notes",
                "Coding": "Code drills",
                "Tactics": "Drills",
                "Endurance": "Train",
                "Strength": "Gym",
                "Communication": "Practice",
                "Leadership": "Lead",
                "Research": "Review papers",
                "Clinical": "Shadow/OSCE",
                "Business": "Prototype",
                "Security": "Lab"
            }
            v = None
            for k in verb:
                if k.lower() in g["skill"].lower():
                    v = verb[k]
                    break
            if v is None:
                v = "Practice"
            tasks.append({
                "skill": g["skill"],
                "focus": f"{v}: {g['recommendation']}",
                "hours": float(np.round(hrs, 1))
            })
        plan.append({"week": w, "tasks": tasks})
    return plan

def export_markdown(profile, gaps, plan, resources):
    md = [f"# Career Gap Report — {date.today().isoformat()}",
          f"**Domain/Role:** {profile['name']}  ",
          f"**Hours/Week Planned:** {profile['hours_per_week']}  ",
          ""]
    md.append("## Gap Summary")
    if not gaps:
        md.append("_No significant gaps detected. Great job!_")
    else:
        md.append("| Skill | You | Target | Gap | Priority | Recommendation |")
        md.append("|---|---:|---:|---:|---:|---|")
        for g in gaps:
            md.append(f"| {g['skill']} | {g['current']:.1f} | {g['target']:.1f} | "
                      f"{g['gap']:.1f} | {g['priority']} | {g['recommendation']} |")
    md.append("")
    md.append("## 12-Week Roadmap")
    for wk in plan:
        md.append(f"### Week {wk['week']}")
        for t in wk["tasks"]:
            md.append(f"- **{t['skill']}** — {t['focus']} _(~{t['hours']} h)_")
    md.append("")
    md.append("## Resources")
    for cat, links in resources.items():
        md.append(f"### {cat}")
        for title, url in links:
            md.append(f"- [{title}]({url})")
    return "\n".join(md)

# ---------------------- Domain Library ----------------------
ROLE_LIBRARY = {
    # Existing roles
    "Data Science (Entry)":
    {
        "skills": {
            "Python": 4.0, "Statistics": 4.0, "ML Fundamentals": 4.0,
            "Data Wrangling (Pandas/SQL)": 4.0, "Visualization": 3.5,
            "MLOps/Basics": 2.5, "Communication": 3.5, "Projects/Portfolio": 4.0
        },
        "keywords": {
            "Python": ["python", "numpy", "pandas", "scikit-learn"],
            "Statistics": ["probability", "hypothesis test", "p-value", "anova"],
            "ML Fundamentals": ["regression", "classification", "clustering", "random forest", "xgboost"],
            "Data Wrangling (Pandas/SQL)": ["sql", "joins", "pandas", "etl"],
            "Visualization": ["matplotlib", "seaborn", "plotly", "dashboard"],
            "MLOps/Basics": ["mlops", "docker", "pipeline", "deployment"],
            "Communication": ["presented", "stakeholder", "storytelling"],
            "Projects/Portfolio": ["github", "kaggle", "project", "case study"]
        },
        "resources": {
            "Core": [
                ("Python for Data Analysis (book)", "https://wesmckinney.com/book/"),
                ("scikit-learn docs", "https://scikit-learn.org/stable/"),
            ],
            "Practice": [
                ("Kaggle", "https://www.kaggle.com/"),
                ("UCI ML Repository", "https://archive.ics.uci.edu/"),
            ],
            "MLOps": [
                ("Made With ML", "https://madewithml.com/"),
            ],
        }
    },

    "Software Engineering (Entry)":
    {
        "skills": {
            "CS Fundamentals": 4.0, "Data Structures": 4.0, "Algorithms": 4.0,
            "Backend / APIs": 3.5, "Frontend Basics": 3.0,
            "Testing": 3.0, "DevOps Basics": 2.5, "Communication": 3.5
        },
        "keywords": {
            "CS Fundamentals": ["os", "networks", "database", "oop"],
            "Data Structures": ["array", "hash", "tree", "graph", "stack", "queue"],
            "Algorithms": ["complexity", "greedy", "dp", "two pointers"],
            "Backend / APIs": ["api", "rest", "node", "django", "flask", "spring"],
            "Frontend Basics": ["html", "css", "react", "vue"],
            "Testing": ["unit test", "pytest", "jest", "ci"],
            "DevOps Basics": ["docker", "git", "ci/cd"],
            "Communication": ["stakeholder", "cross-functional"]
        },
        "resources": {
            "Core": [
                ("LeetCode", "https://leetcode.com/"),
                ("CS50", "https://cs50.harvard.edu/"),
            ],
            "Backend": [
                ("FastAPI docs", "https://fastapi.tiangolo.com/"),
            ],
            "Frontend": [
                ("React docs", "https://react.dev/"),
            ]
        }
    },

    "Medicine (Student/Resident)":
    {
        "skills": {
            "Anatomy/Physiology": 4.0, "Clinical Reasoning": 4.0, "Diagnostics": 3.5,
            "Procedures/OSCE": 3.5, "Research/Literature": 3.0,
            "Communication & Empathy": 4.0, "Ethics/Compliance": 4.0
        },
        "keywords": {
            "Anatomy/Physiology": ["anatomy", "physiology", "pathology"],
            "Clinical Reasoning": ["differential", "management", "protocol"],
            "Diagnostics": ["ecg", "imaging", "labs"],
            "Procedures/OSCE": ["osce", "procedures", "simulation"],
            "Research/Literature": ["pubmed", "cohort", "randomized", "systematic review"],
            "Communication & Empathy": ["counsel", "patient education"],
            "Ethics/Compliance": ["hipaa", "ethics", "consent"]
        },
        "resources": {
            "Core": [
                ("AMBOSS (trial)", "https://www.amboss.com/"),
                ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/")
            ],
            "Skills": [
                ("NEJM — Procedures", "https://www.nejm.org/medical-videos")
            ],
        }
    },

    "Business / Entrepreneur":
    {
        "skills": {
            "Opportunity Sizing": 4.0, "Customer Discovery": 4.0, "MVP/Prototyping": 4.0,
            "Go-to-Market": 3.5, "Finance & Unit Economics": 4.0,
            "Leadership & Hiring": 3.5, "Pitch & Story": 4.0
        },
        "keywords": {
            "Opportunity Sizing": ["tam", "sam", "som", "market"],
            "Customer Discovery": ["interviews", "personas", "jobs-to-be-done"],
            "MVP/Prototyping": ["prototype", "mvp", "no-code"],
            "Go-to-Market": ["pricing", "channels", "growth"],
            "Finance & Unit Economics": ["cac", "ltv", "margin", "cohort"],
            "Leadership & Hiring": ["hiring", "org", "team"],
            "Pitch & Story": ["pitch", "deck", "storytelling"]
        },
        "resources": {
            "Core": [
                ("YC Startup School", "https://www.startupschool.org/"),
                ("Lean Startup (summary)", "https://en.wikipedia.org/wiki/Lean_startup")
            ],
            "Finance": [
                ("Unit economics explainer", "https://a16z.com/2015/09/22/16-metrics/"),
            ],
        }
    },

    "Sports (Athlete)":
    {
        "skills": {
            "Technique/Tactics": 4.0, "Strength": 4.0, "Endurance": 4.0,
            "Mobility/Recovery": 3.5, "Nutrition": 3.5, "Mindset/Focus": 4.0
        },
        "keywords": {
            "Technique/Tactics": ["tactics", "drills", "coach"],
            "Strength": ["strength", "weights", "gym"],
            "Endurance": ["endurance", "intervals", "aerobic"],
            "Mobility/Recovery": ["mobility", "physio", "recovery"],
            "Nutrition": ["nutrition", "diet", "macros"],
            "Mindset/Focus": ["mindset", "visualization", "routine"]
        },
        "resources": {
            "Core": [
                ("Science of Ultra", "https://www.scienceofultra.com/"),
                ("Stronger by Science", "https://www.strongerbyscience.com/")
            ],
            "Recovery": [
                ("The Ready State (blog)", "https://thereadystate.com/blog/")
            ]
        }
    },

    # ---------------- New roles below ----------------
    "Full-stack Software Engineer":
    {
        "skills": {
            "Frontend (React/SPA)": 4.0, "Backend (API/DB)": 4.0, "System Design": 3.5,
            "Testing/QA": 3.5, "DevOps/Cloud": 3.5, "Security Basics": 3.0,
            "Product Sense": 3.0, "Communication": 3.5
        },
        "keywords": {
            "Frontend (React/SPA)": ["react", "redux", "spa", "typescript"],
            "Backend (API/DB)": ["rest", "graphql", "postgres", "mysql", "django", "node", "spring"],
            "System Design": ["scalability", "load balancer", "cache", "queue", "microservices"],
            "Testing/QA": ["unit test", "integration test", "jest", "pytest", "cypress"],
            "DevOps/Cloud": ["docker", "kubernetes", "aws", "gcp", "ci/cd"],
            "Security Basics": ["owasp", "auth", "jwt", "cors"],
            "Product Sense": ["a/b test", "analytics", "kpi"],
            "Communication": ["stakeholder", "design doc", "rfc"]
        },
        "resources": {
            "Core": [
                ("System Design Primer", "https://github.com/donnemartin/system-design-primer"),
                ("React docs", "https://react.dev/")
            ],
            "Backend": [
                ("FastAPI docs", "https://fastapi.tiangolo.com/")
            ],
            "DevOps": [
                ("Docker docs", "https://docs.docker.com/")
            ]
        }
    },

    "Product Manager":
    {
        "skills": {
            "User Research": 4.0, "Prioritization/Strategy": 4.0, "Roadmapping": 3.5,
            "Data & Experimentation": 3.5, "Spec Writing": 4.0, "Stakeholder Mgmt": 4.0,
            "GTM/Launch": 3.5, "Leadership": 3.5
        },
        "keywords": {
            "User Research": ["interviews", "personas", "journey map"],
            "Prioritization/Strategy": ["r Ice", "ranks", "strategy", "vision", "okr"],
            "Roadmapping": ["roadmap", "quarter", "milestone"],
            "Data & Experimentation": ["a/b test", "cohort", "sql", "ga4", "mixpanel"],
            "Spec Writing": ["prd", "requirements", "acceptance criteria"],
            "Stakeholder Mgmt": ["alignment", "stakeholder", "review"],
            "GTM/Launch": ["launch", "messaging", "pricing"],
            "Leadership": ["influence", "cross-functional"]
        },
        "resources": {
            "Core": [
                ("SVPG Articles", "https://www.svpg.com/articles/"),
                ("Reforge Essays", "https://www.reforge.com/blog")
            ],
            "Data": [
                ("Experimentation guide", "https://www.optimizely.com/optimization-glossary/ab-testing/")
            ]
        }
    },

    "Cybersecurity Analyst (Blue Team)":
    {
        "skills": {
            "Security Fundamentals": 4.0, "SIEM/Monitoring": 4.0, "Incident Response": 4.0,
            "Threat Intel": 3.5, "Network/Endpoint": 3.5, "Scripting/Automation": 3.0,
            "Reporting/Comms": 3.5
        },
        "keywords": {
            "Security Fundamentals": ["cissp", "security+", "cia triad", "nist"],
            "SIEM/Monitoring": ["siem", "splunk", "elk", "alerts", "detection"],
            "Incident Response": ["ir", "triage", "containment", "forensics"],
            "Threat Intel": ["mitre att&ck", "ioc", "tactics", "ttp"],
            "Network/Endpoint": ["ids", "ips", "edr", "wireshark", "pcap"],
            "Scripting/Automation": ["python", "bash", "automation"],
            "Reporting/Comms": ["postmortem", "rca", "stakeholder"]
        },
        "resources": {
            "Core": [
                ("MITRE ATT&CK", "https://attack.mitre.org/"),
                ("Blue Team Handbook (ref)", "https://www.blueteamhandbook.com/")
            ],
            "Labs": [
                ("TryHackMe (Blue)", "https://tryhackme.com/"),
            ]
        }
    },

    "Cardiology Resident":
    {
        "skills": {
            "Cardiac Physiology": 4.0, "ECG/Imaging": 4.0, "Clinical Reasoning": 4.0,
            "Procedures": 3.5, "Guidelines & Evidence": 4.0, "Research/Lit": 3.0,
            "Communication/Empathy": 4.0
        },
        "keywords": {
            "Cardiac Physiology": ["cardiac output", "preload", "afterload"],
            "ECG/Imaging": ["ecg", "echo", "stress test", "angiography"],
            "Clinical Reasoning": ["acs", "heart failure", "arrhythmia"],
            "Procedures": ["catheter", "pacing", "cardioversion"],
            "Guidelines & Evidence": ["acc/aha", "esc", "guideline"],
            "Research/Lit": ["pubmed", "cohort", "trial"],
            "Communication/Empathy": ["counsel", "risk discussion"]
        },
        "resources": {
            "Core": [
                ("ACC/AHA Guidelines", "https://www.acc.org/Guidelines"),
                ("ESC Guidelines", "https://www.escardio.org/Guidelines")
            ],
            "ECG": [
                ("Life in the Fast Lane ECG Library", "https://litfl.com/ecg-library/")
            ]
        }
    },

    "Sports Physiotherapist":
    {
        "skills": {
            "Assessment/Screening": 4.0, "Diagnosis & Planning": 4.0,
            "Manual Therapy": 3.5, "Rehab Programming": 4.0,
            "Return-to-Play": 4.0, "Load Management": 3.5, "Communication": 4.0
        },
        "keywords": {
            "Assessment/Screening": ["fms", "screen", "aslr", "hop test"],
            "Diagnosis & Planning": ["dx", "plan", "soap", "goal"],
            "Manual Therapy": ["soft tissue", "mobilization"],
            "Rehab Programming": ["eccentric", "isometric", "protocol"],
            "Return-to-Play": ["rtp", "criteria", "functional"],
            "Load Management": ["acute:chronic", "rpe", "gps"],
            "Communication": ["coach", "athlete", "stakeholder"]
        },
        "resources": {
            "Core": [
                ("BJSM Blog", "https://blogs.bmj.com/bjsm/"),
                ("Clinical practice guidelines (PT)", "https://www.apta.org/patient-care/evidence-based-practice-resources")
            ],
            "Programming": [
                ("ExRx", "https://exrx.net/")
            ]
        }
    },
}

# ---------------------- Sidebar (Navigation) ----------------------
st.sidebar.title("🧭 Career Gap Mapper")
page = st.sidebar.radio("Go to", ["Home", "Assess", "Roadmap", "Resources", "Tracker", "Coach Bot"])

st.sidebar.markdown("---")
st.sidebar.caption("Your data stays in your browser session. No upload to servers.")

# Persist user selections
if "state" not in st.session_state:
    st.session_state.state = {
        "role": "Data Science (Entry)",
        "hours_per_week": 6,
        "resume_text": "",
        "self_scores": {},   # per skill 0..5
        "gaps": [],
        "plan": []
    }

S = st.session_state.state

# ---------------------- Home ----------------------
if page == "Home":
    st.markdown("## 🌟 Map your gap. Build your plan.")
    st.write(dedent("""
    Welcome to **Career Gap Mapper** — a simple, structured way to see where you stand
    and build a focused 12-week plan to reach your next role or performance level.
    """))

    col1, col2 = st.columns([1,1])
    with col1:
        st.selectbox("Choose a domain/role", list(ROLE_LIBRARY.keys()),
                     index=list(ROLE_LIBRARY.keys()).index(S["role"]), key="role_home")
    with col2:
        S["hours_per_week"] = st.slider("Hours you can invest each week", 2, 30, S["hours_per_week"], 1)

    S["role"] = st.session_state.get("role_home", S["role"])
    role = ROLE_LIBRARY[S["role"]]
    st.info(f"**Selected Role:** {S['role']}  \n"
            f"Target skill levels shown on the next page. You can paste your resume to auto-estimate current levels and then refine with sliders.")

    st.markdown("### What you’ll do")
    st.markdown("""
    1. **Assess** – Let the app read your resume (optional) and self-rate your skills.
    2. **Roadmap** – Get a 12-week plan that allocates your weekly hours to the biggest gaps.
    3. **Resources** – Explore curated links matched to your gaps.
    4. **Tracker** – Mark tasks done each week and keep going!
    """)

# ---------------------- Assess ----------------------
if page == "Assess":
    st.header("🧪 Assess your current level")
    role = ROLE_LIBRARY[S["role"]]
    targets = role["skills"]
    skills = list(targets.keys())

    st.subheader("1) Optional: paste your resume / profile")
    S["resume_text"] = st.text_area("Paste text (resume, profile, bio, achievements)…",
                                    value=S["resume_text"], height=180,
                                    placeholder="Paste here to auto-estimate skill levels")

    auto_scores = {}
    if st.button("🔍 Auto-estimate from text"):
        auto_scores = parse_resume(S["resume_text"], role["keywords"])
        st.success("Estimated from text. You can fine-tune with sliders below.")
        S["self_scores"].update(auto_scores)

    st.subheader("2) Self-rate each skill (0 = newbie, 5 = strong)")
    grid_cols = st.columns(2)
    cur_scores = {}
    for i, skill in enumerate(skills):
        with grid_cols[i % 2]:
            default = S["self_scores"].get(skill, 0.0)
            cur_scores[skill] = st.slider(f"{skill}", 0.0, 5.0, float(default), 0.5)
    S["self_scores"] = cur_scores

    st.subheader("Gap radar")
    cur = [norm(S["self_scores"][s]) for s in skills]
    tgt = [norm(targets[s]) for s in skills]
    fig = radar_chart(skills, cur, tgt)
    st.plotly_chart(fig, use_container_width=True)

    gaps = []
    # Default recommendations per broad role family
    default_reco = {
        "Data Science (Entry)": "do a focused project + share insights",
        "Software Engineering (Entry)": "implement mini-projects with tests",
        "Full-stack Software Engineer": "ship a small full-stack app with CI, tests, and deploy",
        "Medicine (Student/Resident)": "case logs + OSCE drills",
        "Cardiology Resident": "case logs + ECG/echo practice with guideline mapping",
        "Business / Entrepreneur": "customer interviews + MVP iterations",
        "Product Manager": "customer interviews + PRDs + lightweight experiments",
        "Cybersecurity Analyst (Blue Team)": "blue-team labs + incident writeups",
        "Sports (Athlete)": "structured drills + recovery routine",
        "Sports Physiotherapist": "evidence-based protocols + athlete communication drills"
    }

    for s in skills:
        c = norm(S["self_scores"][s]); t = norm(targets[s])
        gap = max(0.0, t - c)
        if gap < 0.25:
            priority = "Low"
        elif gap < 1.0:
            priority = "Med"
        else:
            priority = "High"
        gaps.append({
            "skill": s, "current": c, "target": t, "gap": gap,
            "priority": priority,
            "recommendation": default_reco.get(S["role"], "practice + feedback loops")
        })

    S["gaps"] = sorted(gaps, key=lambda x: x["gap"], reverse=True)

    st.markdown("#### Gap table")
    df = pd.DataFrame(S["gaps"])
    st.dataframe(df, use_container_width=True)

    st.success("Go to **Roadmap** to create a 12-week plan from your gaps.")

# ---------------------- Roadmap ----------------------
if page == "Roadmap":
    st.header("🗺️ Your 12-week roadmap")
    st.write(f"Role: **{S['role']}** | Hours/week: **{S['hours_per_week']}**")

    if not S["gaps"]:
        st.warning("No gaps yet. Visit **Assess** first.")
    else:
        meaningful = [g for g in S["gaps"] if g["gap"] >= 0.25]
        if not meaningful:
            st.info("You are already close to target across the board 🎉")
        else:
            S["plan"] = make_12_week_plan(meaningful[:6], S["hours_per_week"])  # top 6 gaps

            for wk in S["plan"]:
                with st.expander(f"Week {wk['week']} plan"):
                    dfw = pd.DataFrame(wk["tasks"])
                    st.dataframe(dfw, use_container_width=True)

            role = ROLE_LIBRARY[S["role"]]
            md = export_markdown(
                {"name": S["role"], "hours_per_week": S["hours_per_week"]},
                S["gaps"], S["plan"], role["resources"]
            )
            st.download_button("⬇️ Download report (Markdown)", md, file_name="career_gap_report.md")

# ---------------------- Resources ----------------------
if page == "Resources":
    st.header("📚 Curated resources")
    role = ROLE_LIBRARY[S["role"]]
    st.write(f"For **{S['role']}**, here are helpful links grouped by category. High-priority gaps are highlighted.")

    top_gaps = [g["skill"] for g in (S["gaps"][:5] if S["gaps"] else [])]
    for cat, links in role["resources"].items():
        badge = " 🔥" if any(s.lower() in cat.lower() for s in top_gaps) else ""
        st.subheader(cat + badge)
        for title, url in links:
            st.markdown(f"- [{title}]({url})")

# ---------------------- Tracker ----------------------
if page == "Tracker":
    st.header("✅ Weekly tracker")
    if not S["plan"]:
        st.warning("Create a plan in **Roadmap** first.")
    else:
        if "done" not in S:
            S["done"] = {}  # key: (week, skill, focus) -> bool

        total = 0
        completed = 0
        for wk in S["plan"]:
            st.markdown(f"### Week {wk['week']}")
            cols = st.columns(2)
            for i, task in enumerate(wk["tasks"]):
                key = (wk["week"], task["skill"], task["focus"])
                done_key = f"done_{wk['week']}_{i}"
                prev = S["done"].get(key, False)
                with cols[i % 2]:
                    checked = st.checkbox(
                        f"**{task['skill']}** — {task['focus']} _(~{task['hours']} h)_",
                        value=prev, key=done_key
                    )
                S["done"][key] = checked
                total += 1
                completed += int(checked)

        prog = 0 if total == 0 else int(100 * completed / total)
        st.progress(prog)
        st.info(f"Completed {completed} / {total} tasks ({prog}%). Keep going!")

# ---------------------- Coach Bot ----------------------
if page == "Coach Bot":
    st.header("🤖 Coach Bot")
    st.caption("A tiny rule-based assistant for quick tips.")

    def coach_reply(msg):
        m = msg.lower()
        if "motivat" in m:
            return "Momentum > motivation. Schedule tiny daily reps (15–20 min) and track streaks."
        if "resume" in m or "cv" in m:
            return "Write impact bullets: action verb + metric + outcome. e.g., 'Built X that reduced Y by Z%'."
        if "interview" in m:
            return "Use STAR: Situation, Task, Action, Result. Rehearse aloud with a timer."
        if "burnout" in m or "tired" in m:
            return "Deload week: 50–60% volume, keep the habit alive, sleep, hydrate, light walks."
        if "focus" in m or "procrast" in m:
            return "Set a 25-min focus sprint (no notifications), then 5-min break. Repeat x4."
        return "Try asking about resume bullets, interviews, motivation, focus, or burnout."

    if "chat" not in S:
        S["chat"] = [{"role": "assistant", "content": "Hi! I'm your coach. Ask me for concise, practical tips."}]

    for m in S["chat"]:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    user_msg = st.chat_input("Type here…")
    if user_msg:
        S["chat"].append({"role": "user", "content": user_msg})
        with st.chat_message("user"): st.write(user_msg)
        reply = coach_reply(user_msg)
        S["chat"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.write(reply)

# ---------------------- Footer ----------------------
st.markdown("---")
st.caption("Built with ❤️ to help you bridge the gap. This tool gives guidance, not guarantees. Always adapt to your context.")
