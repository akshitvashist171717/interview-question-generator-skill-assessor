"""app_views/jd_page.py — JD Input → Analysis → Skill Matching"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.jd_analyzer    import analyze_jd
from utils.skill_matcher  import compute_match
from data_loader          import get_jd_sample
from theme import get_active_colors


def render():
    st.markdown("<div class='section-header'>Job Description Analysis &amp; Skill Matching</div>",
                unsafe_allow_html=True)

    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
        if st.button("Go to Resume Upload"):
            st.session_state.page = "upload"; st.rerun()
        return

    st.markdown("##### Paste the job description")
    col_jd, col_opts = st.columns([3, 1])

    with col_opts:
        use_demo = st.checkbox("Use demo JD", value=False)
        if use_demo and st.session_state.ml_prediction:
            predicted_role = st.session_state.ml_prediction["role"]
            sample = get_jd_sample(predicted_role)
        else:
            sample = None

    with col_jd:
        default_val = sample if (use_demo and sample) else (st.session_state.jd_text or "")
        jd_text = st.text_area("Job Description", value=default_val, height=280,
                                placeholder="Paste the full job description here...",
                                label_visibility="collapsed")

    if st.button("Analyse JD &amp; Match Skills", type="primary"):
        if len(jd_text.strip()) < 30:
            st.error("Please enter a job description (at least 30 characters).")
            return
        st.session_state.jd_text = jd_text
        with st.spinner("Analysing job description..."):
            jd_analysis = analyze_jd(jd_text)
            st.session_state.jd_analysis = jd_analysis
        with st.spinner("Running skill matching engine..."):
            match_result = compute_match(
                candidate_skills=st.session_state.candidate_skills,
                jd_required=jd_analysis["required_skills"],
                jd_preferred=jd_analysis["preferred_skills"],
            )
            st.session_state.match_result = match_result

    if st.session_state.jd_analysis and st.session_state.match_result:
        _display(st.session_state.jd_analysis, st.session_state.match_result)


def _display(jd, match):
    C = get_active_colors()

    st.success("JD analysed and skills matched.")
    st.markdown("---")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Seniority", jd["seniority"])
    m2.metric("Years Required", f"{jd['years_required']}+" if jd["years_required"] else "—")
    m3.metric("Required Skills", len(jd["required_skills"]))
    m4.metric("Preferred Skills", len(jd["preferred_skills"]))
    st.markdown("---")

    score = match["overall_score"]
    color = C["success"] if score >= 70 else C["warning"] if score >= 45 else C["danger"]
    st.markdown(f"""
    <div class='score-circle' style='border-color:{color};'>
        <div class='score-label'>Overall Match Score</div>
        <div class='score-num' style='color:{color};'>{score}%</div>
        <div style='font-size:1.1rem; font-weight:600; color:{color};'>
            {match["verdict_emoji"]} {match["verdict"]}
        </div>
        <div style='color:var(--muted); font-size:0.85rem; margin-top:8px;'>
            Required: {match["required_score"]}% &nbsp;|&nbsp; Preferred: {match["preferred_score"]}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_req, col_pref = st.columns(2)
    with col_req:  _gauge("Required Skills Match", match["required_score"], C)
    with col_pref: _gauge("Preferred Skills Match", match["preferred_score"], C)
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("###### Matched required skills")
        _chips(match["matched_required"], "chip-success")
        st.markdown("###### Missing required skills")
        _chips(match["missing_required"], "chip-danger")
    with col_b:
        st.markdown("###### Matched preferred skills")
        _chips(match["matched_preferred"], "chip-success")
        st.markdown("###### Bonus skills (beyond JD)")
        _chips(match["candidate_extra"][:12], "chip-cyan")

    st.markdown("---")
    st.markdown("##### Per-skill breakdown")
    df = pd.DataFrame([{
        "Skill": r["skill"], "Category": r["category"],
        "Matched": "Yes" if r["matched"] else "No",
        "Confidence": f"{int(r['confidence']*100)}%" if r["matched"] else "—",
    } for r in match["breakdown"]])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("##### Required skills — candidate coverage")
    req_names   = jd["required_skills"]
    cand_skills = {s["skill"] for s in st.session_state.candidate_skills}
    if req_names:
        colors = [C["success"] if s in cand_skills else C["danger"] for s in req_names]
        fig = go.Figure(go.Bar(
            x=req_names, y=[1]*len(req_names), marker_color=colors,
            text=["Match" if s in cand_skills else "Gap" for s in req_names],
            textposition="outside", textfont=dict(color=C["ink"]),
        ))
        fig.update_layout(
            paper_bgcolor=C["surface"], plot_bgcolor=C["surface"],
            font=dict(family="Inter, sans-serif", color=C["ink"]),
            yaxis=dict(visible=False), xaxis=dict(tickangle=-30, gridcolor=C["border"]),
            height=270, margin=dict(l=10, r=10, t=30, b=80), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    if st.button("Next: Generate Interview Questions →", type="primary"):
        st.session_state.page = "questions"; st.rerun()


def _gauge(title, value, C):
    color = C["success"] if value >= 70 else C["warning"] if value >= 45 else C["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        number={"suffix": "%", "font": {"color": color, "size": 26}},
        title={"text": title, "font": {"color": C["muted"], "size": 13}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": C["muted"]},
            "bar": {"color": color},
            "bgcolor": C["surface"], "bordercolor": C["border"],
            "steps": [
                {"range": [0, 40], "color": C["danger_bg"]},
                {"range": [40, 70], "color": C["warning_bg"]},
                {"range": [70, 100], "color": C["success_bg"]},
            ],
            "threshold": {"line": {"color": C["ink"], "width": 2}, "thickness": 0.75, "value": value},
        },
    ))
    fig.update_layout(paper_bgcolor=C["surface"], height=190, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)


def _chips(skills, cls):
    if not skills:
        st.markdown('<span style="color:var(--muted); font-size:0.85rem;">None</span>', unsafe_allow_html=True)
        return
    st.markdown("".join(f"<span class='chip {cls}'>{s}</span>" for s in skills), unsafe_allow_html=True)
