"""app_views/upload.py — Resume Upload → ML Classifier → Skill Extraction"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.resume_parser   import extract_text, extract_metadata
from utils.skill_extractor import extract_skills
from theme import get_active_colors


def render():
    st.markdown("<div class='section-header'>Resume Upload &amp; Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--muted);'>Upload a PDF or DOCX resume. The ML classifier — "
                "trained on 8,167 real resumes — will predict the candidate's role and "
                "extract technical skills automatically.</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Drop your resume here", type=["pdf", "docx"])
    use_demo = st.checkbox("Use a sample resume for demo", value=False)

    if use_demo:
        _process_resume(_demo_resume(), "demo_resume.pdf")
        return

    if uploaded:
        file_bytes = uploaded.read()
        with st.spinner("Parsing resume..."):
            try:
                text = extract_text(file_bytes, uploaded.name)
            except Exception as e:
                st.error(f"Failed to parse file: {e}")
                return
        _process_resume(text, uploaded.name)


def _process_resume(text: str, filename: str):
    if not text or len(text.strip()) < 50:
        st.error("Resume appears to be empty or unreadable. Please try a different file.")
        return

    C = get_active_colors()

    st.session_state.resume_text = text
    meta = extract_metadata(text)
    st.session_state.resume_meta = meta

    with st.spinner("Running ML classifier (trained on real resumes)..."):
        from ml.resume_classifier import predict
        prediction = predict(text)
        st.session_state.ml_prediction = prediction

    with st.spinner("Extracting skills..."):
        skills = extract_skills(text)
        st.session_state.candidate_skills = skills

    st.success("Resume processed successfully.")
    st.markdown("---")

    col_info, col_ml = st.columns([1, 1])
    with col_info:
        st.markdown("##### Candidate information")
        st.markdown(f"""
        <div class='card'>
            <b style='color:var(--ink);'>Name:</b> <span>{meta.get('name') or '—'}</span><br>
            <b style='color:var(--ink);'>Email:</b> <span>{meta.get('email') or '—'}</span><br>
            <b style='color:var(--ink);'>Phone:</b> <span>{meta.get('phone') or '—'}</span><br>
            <b style='color:var(--ink);'>LinkedIn:</b> <span>{meta.get('linkedin') or '—'}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--muted); font-size:0.85rem; margin-top:8px;'>"
                     f"Words: <b>{len(text.split()):,}</b> &nbsp;·&nbsp; "
                     f"Characters: <b>{len(text):,}</b></p>", unsafe_allow_html=True)

    with col_ml:
        st.markdown("##### ML role prediction")
        role = prediction["role"]
        conf_pct = round(prediction["confidence"] * 100, 1)
        color = C["success"] if conf_pct >= 70 else C["warning"] if conf_pct >= 45 else C["danger"]
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div style='color:var(--muted); font-size:0.85rem;'>Predicted Role</div>
            <div style='font-family:var(--heading-font); font-weight:600;
                        font-size:1.45rem; color:var(--accent); margin:6px 0;'>{role}</div>
            <div style='color:var(--muted); font-size:0.85rem;'>Model Confidence</div>
            <div style='font-family:var(--heading-font); font-weight:600;
                        font-size:1.9rem; color:{color};'>{conf_pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Role probability distribution (top 3)")
    top3 = prediction["top3"]
    fig = go.Figure(go.Bar(
        x=[r["probability"] * 100 for r in top3],
        y=[r["role"] for r in top3],
        orientation="h",
        marker=dict(color=[C["accent"], C["accent_soft"], C["border"]]),
        text=[f"{r['probability']*100:.1f}%" for r in top3],
        textposition="outside",
        textfont=dict(color=C["ink"]),
    ))
    fig.update_layout(
        paper_bgcolor=C["surface"], plot_bgcolor=C["surface"],
        font=dict(family="Inter, sans-serif", color=C["ink"]),
        xaxis=dict(range=[0, 100], title="Probability (%)", gridcolor=C["border"]),
        yaxis=dict(title=""), height=210, margin=dict(l=20, r=60, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(f"##### Extracted skills · `{len(skills)} found`")

    if not skills:
        st.warning("No skills detected. Try a more detailed resume.")
        return

    in_sec  = [s for s in skills if s["in_skills_section"]]
    not_sec = [s for s in skills if not s["in_skills_section"]]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**From Skills Section**")
        _chips(in_sec, "chip-primary")
    with c2:
        st.markdown("**From Experience / Other Sections**")
        _chips(not_sec, "chip-cyan")

    st.markdown("##### Skill details")
    df = pd.DataFrame([{
        "Skill": s["skill"],
        "Confidence": f"{int(s['confidence']*100)}%",
        "In Skills Section": "Yes" if s["in_skills_section"] else "—",
        "Years Exp.": str(s["years_exp"]) if s["years_exp"] else "—",
    } for s in skills])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button("Next: Analyse Job Description →", type="primary"):
        st.session_state.page = "jd"
        st.rerun()


def _chips(skills, cls):
    if not skills:
        st.markdown('<span style="color:var(--muted);">None detected</span>', unsafe_allow_html=True)
        return
    st.markdown("".join(f"<span class='chip {cls}'>{s['skill']}</span>" for s in skills),
                unsafe_allow_html=True)


def _demo_resume() -> str:
    return """
Priya Mehta
priya.mehta@gmail.com | +91-9123456789 | linkedin.com/in/priyamehta

SUMMARY
Experienced Python Developer with 4+ years building backend systems, REST APIs,
and data pipelines for e-commerce and healthcare. Strong Django, Flask, and SQL background.

TECHNICAL SKILLS
Python, Django, Flask, REST API, SQL, PostgreSQL, Docker, AWS, Git, Linux,
Data Pipelines, ETL, Microservices, CI/CD, Agile/Scrum

EXPERIENCE
Senior Python Developer — Amazon (2022–Present)
- Built backend services in Django and Flask serving 1M+ requests/day
- Designed REST APIs consumed by 10+ internal teams
- Deployed services to AWS using Docker, with CI/CD pipelines via GitHub Actions
- Built ETL pipelines processing 80GB of daily transactional data

Python Developer — Practo (2020–2022)
- Built patient management backend using Django REST Framework
- Wrote complex SQL queries and optimised PostgreSQL schemas
- Implemented automated testing achieving 85% code coverage

EDUCATION
B.Tech, Computer Science — NIT Surat (2014–2018)

PROJECTS
- Inventory Management API: Django REST Framework + PostgreSQL, deployed on AWS
- Real-time Chat Service: Python WebSockets + Redis pub/sub

CERTIFICATIONS
AWS Certified Developer – Associate | PCAP (Certified Associate in Python Programming)
"""
