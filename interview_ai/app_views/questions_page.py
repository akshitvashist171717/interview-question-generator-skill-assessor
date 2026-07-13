"""app_views/questions_page.py — Gemini Question Generation"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.gemini_client import (
    generate_questions_from_jd_resume,
    generate_questions_from_resume_only,
    generate_questions_from_jd_only,
)
from theme import get_active_colors


def _palettes(C):
    diff_color = {"Easy": C["success"], "Medium": C["warning"], "Hard": C["danger"]}
    type_color = {"Conceptual": C["accent"], "Coding": C["cyan"], "Scenario": C["warning"],
                  "Design": C["accent_hov"], "Behavioral": C["danger"]}
    return diff_color, type_color


def render():
    st.markdown("<div class='section-header'>Interview Question Generation</div>", unsafe_allow_html=True)

    if not st.session_state.match_result:
        st.warning("Please complete the resume upload and JD analysis first.")
        if st.button("Go Back"):
            st.session_state.page = "jd"; st.rerun()
        return

    match, jd = st.session_state.match_result, st.session_state.jd_analysis
    ml_pred = st.session_state.ml_prediction

    st.markdown("##### Question configuration")

    MODE_RESUME   = "Resume only"
    MODE_JD       = "JD only"
    MODE_COMBINED = "Combined (JD + Resume)"

    gen_mode = st.selectbox(
        "Generate questions based on",
        [MODE_RESUME, MODE_JD, MODE_COMBINED],
        index=2,
        help="**Resume only**: questions are generated purely from the candidate's resume — "
             "the job description is not used.\n\n"
             "**JD only**: questions are generated purely from the job description — "
             "the candidate's resume is not used.\n\n"
             "**Combined (JD + Resume)**: sends both the full job description and resume text "
             "to Gemini so questions are tailored to this exact JD and this exact candidate.",
    )

    has_resume = bool((st.session_state.resume_text or "").strip())
    has_jd = bool((st.session_state.jd_text or "").strip())

    col_n, col_focus, col_api = st.columns([1, 2, 1])
    with col_n:
        n_questions = st.slider("Number of questions", 5, 20, 10)
    with col_focus:
        focus_opts = ["All matched skills"] + match["matched_required"][:8] + match["matched_preferred"][:4]
        focus = st.multiselect("Focus on skills (optional)", options=focus_opts, default=[])
        st.caption("Steers question topics when possible, and is used as the skill pool for offline fallback questions.")
    with col_api:
        api_key = st.session_state.get("gemini_api_key", "")
        st.markdown("**Gemini API** ✓" if api_key else "**Gemini API** — *(fallback mode)*")
        if not api_key and st.button("Add Key"):
            st.session_state.page = "settings"; st.rerun()

    # Validate that the data required for the chosen mode is actually available.
    missing_data_msg = None
    if gen_mode == MODE_RESUME and not has_resume:
        missing_data_msg = "Resume text not found. Please complete the resume upload step first."
    elif gen_mode == MODE_JD and not has_jd:
        missing_data_msg = "Job description text not found. Please complete the JD analysis step first."
    elif gen_mode == MODE_COMBINED and not (has_resume and has_jd):
        missing_pieces = []
        if not has_resume: missing_pieces.append("resume")
        if not has_jd: missing_pieces.append("job description")
        missing_data_msg = f"Missing {' and '.join(missing_pieces)} text — please complete the earlier steps first."

    if missing_data_msg:
        st.warning(missing_data_msg)

    if st.button("Generate Questions with Gemini", type="primary", disabled=bool(missing_data_msg)):
        skills_to_use = focus if (focus and "All matched skills" not in focus) else \
                        (match["matched_required"] + match["matched_preferred"])
        with st.spinner("Gemini is crafting your questions..."):
            if api_key: os.environ["GEMINI_API_KEY"] = api_key
            if gen_mode == MODE_RESUME:
                questions = generate_questions_from_resume_only(
                    role=ml_pred["role"],
                    resume_text=st.session_state.resume_text or "",
                    matched_skills=skills_to_use,
                    n=n_questions,
                )
            elif gen_mode == MODE_JD:
                questions = generate_questions_from_jd_only(
                    role=ml_pred["role"],
                    jd_text=st.session_state.jd_text or "",
                    matched_skills=skills_to_use,
                    n=n_questions,
                )
            else:
                questions = generate_questions_from_jd_resume(
                    role=ml_pred["role"],
                    jd_text=st.session_state.jd_text or "",
                    resume_text=st.session_state.resume_text or "",
                    matched_skills=skills_to_use,
                    n=n_questions,
                )

            if not questions:
                st.error("No questions could be generated. Please check your Gemini API key or try again.")
            else:
                st.session_state.questions = questions
                st.session_state.evaluations = {}
                st.session_state.answers = {}

    if st.session_state.questions:
        _display(st.session_state.questions)


def _display(questions):
    C = get_active_colors()
    DIFF_COLOR, TYPE_COLOR = _palettes(C)
    PLOT_FONT = dict(family="Inter, sans-serif", color=C["ink"])

    st.success(f"{len(questions)} questions generated.")
    st.markdown("---")

    df_q = pd.DataFrame(questions)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**By Difficulty**")
        dc = df_q["diff"].value_counts().reset_index(); dc.columns = ["Difficulty", "Count"]
        fig = px.pie(dc, values="Count", names="Difficulty", color="Difficulty",
                     color_discrete_map=DIFF_COLOR, hole=0.55)
        fig.update_layout(paper_bgcolor=C["surface"], font=PLOT_FONT, margin=dict(l=0,r=0,t=0,b=0),
                           height=190, legend=dict(font=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**By Type**")
        tc = df_q["type"].value_counts().reset_index(); tc.columns = ["Type", "Count"]
        fig2 = px.bar(tc, x="Type", y="Count", color="Type", color_discrete_map=TYPE_COLOR)
        fig2.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                            showlegend=False, height=190, margin=dict(l=0,r=0,t=0,b=40),
                            xaxis=dict(tickangle=-25, gridcolor=C["border"]), yaxis=dict(gridcolor=C["border"]))
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown("**By Skill**")
        if "skill" in df_q.columns:
            sc = df_q["skill"].value_counts().head(6).reset_index(); sc.columns = ["Skill", "Count"]
            fig3 = px.bar(sc, x="Count", y="Skill", orientation="h",
                          color_discrete_sequence=[C["accent"]])
            fig3.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                               height=190, margin=dict(l=0,r=0,t=0,b=0),
                               xaxis=dict(gridcolor=C["border"]))
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown(f"##### Question bank · `{len(questions)} questions`")

    for i, q in enumerate(questions, 1):
        diff, qtype, skill = q.get("diff","Medium"), q.get("type","Conceptual"), q.get("skill","General")
        d_col, t_col = DIFF_COLOR.get(diff, C["muted"]), TYPE_COLOR.get(qtype, C["muted"])
        with st.expander(f"Q{i}. {q['q'][:80]}{'...' if len(q['q'])>80 else ''}"):
            st.markdown(f"""
            <div style='margin-bottom:8px;'>
                <span class='chip chip-cyan'>{skill}</span>
                <span style='background:{d_col}1A; color:{d_col}; border-radius:8px;
                             padding:4px 12px; font-size:0.78rem; margin:3px; font-weight:500;
                             display:inline-block;'>{diff}</span>
                <span style='background:{t_col}1A; color:{t_col}; border-radius:8px;
                             padding:4px 12px; font-size:0.78rem; margin:3px; font-weight:500;
                             display:inline-block;'>{qtype}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**{q['q']}**")

    st.markdown("---")
    csv_df = pd.DataFrame(questions)[["q", "diff", "type"]].rename(
        columns={"q": "Question", "diff": "Difficulty", "type": "Type"})
    if "skill" in pd.DataFrame(questions).columns:
        csv_df["Skill"] = pd.DataFrame(questions)["skill"]
    st.download_button("Download Questions as CSV", data=csv_df.to_csv(index=False),
                       file_name="interview_questions.csv", mime="text/csv")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Next: Answer &amp; Assessment →", type="primary"):
        st.session_state.page = "assessment"; st.rerun()
