"""app_views/home.py — Landing page"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import get_dataset_stats


def render():
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1.2rem 0;'>
        <span class='dataset-badge'>◈ Trained on real-world hiring data</span>
        <h1 class='hero-title' style='margin-top:16px;'>InterviewAI</h1>
        <p class='hero-sub' style= 'width:100%;
        max-width:1400px;
        text-align:center;
        margin:10px auto;'>
            An end-to-end ML platform that classifies resumes, matches candidates to job
            descriptions, and generates tailored interview questions — powered by a
            classifier trained on <b>8,167 real resumes</b> across 10 technical roles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>How the pipeline works</div>", unsafe_allow_html=True)
    steps = [
        ("⤒", "Resume\nUpload"), ("◐", "ML\nClassifier"), ("◆", "Predicted\nRole"),
        ("◉", "Skill\nExtraction"), ("☰", "JD\nAnalysis"), ("⇄", "Skill\nMatching"),
        ("✦", "Question\nGeneration"), ("✎", "Answer\nEvaluation"), ("◫", "Dashboard"),
    ]
    cols = st.columns(9)
    for col, (icon, label) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class='pipe-step'>
                <div class='pipe-icon'>{icon}</div>
                <div class='pipe-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    stats = get_dataset_stats()
    st.markdown("<div class='section-header'>Powered by real hiring data</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    metric_data = [
        (c1, f"{stats['total_resume_records']:,}", "Real Resumes (Training)"),
        (c2, f"{stats['unique_resume_roles']}",      "Classified Job Roles"),
        (c3, f"{stats['total_jd_records']:,}",        "Job Description Records"),
        (c4, f"{stats['total_skill_records']:,}",     "IT Role-Skill Profiles"),
    ]
    for col, val, label in metric_data:
        with col:
            st.markdown(f"""
            <div class='card' style='text-align:center;'>
                <div style='font-family:var(--heading-font); font-weight:600;
                            font-size:1.9rem; color:var(--accent);'>{val}</div>
                <div style='color:var(--muted); font-size:0.84rem; margin-top:4px;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Key features</div>", unsafe_allow_html=True)
    features = [
        ("◐", "ML Resume Classifier",
         "TF-IDF + Logistic Regression trained on 8,167 real resumes across 10 roles, achieving 93%+ cross-validated accuracy."),
        ("⇄", "Skill Matching Engine",
         "Weighted scoring (70% required / 30% preferred) compares candidate skills against JD requirements using a real skill taxonomy."),
        ("✦", "Gemini Question Generation",
         "Google Gemini generates tailored interview questions from matched skills, gaps, and the exact job description."),
        ("✎", "AI Answer Evaluation",
         "Gemini scores candidate answers 0–10 with detailed feedback, strengths, and improvement areas."),
        ("◫", "Analytics Dashboard",
         "Interactive visualisations: match radar, skill gap charts, score timelines, and exportable reports."),
        ("◈", "Dataset Insights",
         "Explore the underlying training data — role distributions, skill frequency, and model performance."),
    ]
    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, features[i:i+3]):
            with col:
                st.markdown(f"""
                <div class='card card-hover' style='min-height:160px;'>
                    <div style='font-size:1.3rem; color:var(--accent);'>{icon}</div>
                    <div style='font-family:var(--heading-font); font-weight:600;
                                font-size:1.05rem; color:var(--ink); margin:8px 0 6px 0;'>{title}</div>
                    <div style='color:var(--ink-soft); font-size:0.87rem; line-height:1.5;'>{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Technology stack</div>", unsafe_allow_html=True)
    stack = [("Python 3.11",""), ("Streamlit",""), ("Scikit-learn",""), ("Gemini API",""), ("Plotly","")]
    tc = st.columns(5)
    for col, (name, _) in zip(tc, stack):
        with col:
            st.markdown(f"""
            <div class='card' style='text-align:center; padding:14px;'>
                <div style='color:var(--ink-soft); font-size:0.84rem; font-weight:500;'>{name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("Start Analysing Resume →", type="primary", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
