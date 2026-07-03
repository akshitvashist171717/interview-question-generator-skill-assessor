"""app_views/settings_page.py — API Key & Configuration"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st


def render():
    st.markdown("<div class='section-header'>Settings &amp; Configuration</div>", unsafe_allow_html=True)

    st.markdown("##### Gemini API key")
    st.markdown("""
    <p style='color:var(--muted);'>Required for AI-powered question generation and answer evaluation.
    Get your free key at <a href='https://aistudio.google.com/app/apikey' target='_blank'
    style='color:var(--accent); font-weight:600;'>Google AI Studio →</a></p>
    """, unsafe_allow_html=True)

    current_key = st.session_state.get("gemini_api_key", "")
    new_key = st.text_input("Gemini API Key", value='Ab8RN6KkBsKioi6uDewT33BSzof8yXLOGKkzRfX48IqcGUm92w', type="password",
                            placeholder="AIza...",
                            help="Stored only in session memory and sent only to Google's API.")

    col_save, col_clear = st.columns([1, 1])
    with col_save:
        if st.button("Save Key", type="primary"):
            st.session_state.gemini_api_key = new_key.strip()
            os.environ["GEMINI_API_KEY"] = new_key.strip()
            st.success("API key saved for this session.") if new_key.strip() else st.info("Key cleared.")
    with col_clear:
        if st.button("Clear Key"):
            st.session_state.gemini_api_key = ""
            os.environ.pop("GEMINI_API_KEY", None)
            st.info("Key cleared.")

    if st.session_state.get("gemini_api_key"):
        st.markdown("""
        <div style='background:var(--success-bg); border-radius:10px; padding:12px 18px;
                    border:1px solid var(--border); color:var(--success); margin-top:8px; font-weight:500;'>
            Gemini API key is active — AI features enabled
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:var(--danger-bg); border-radius:10px; padding:12px 18px;
                    border:1px solid var(--border); color:var(--danger); margin-top:8px; font-weight:500;'>
            No API key — running in fallback mode (local question bank + heuristic scoring)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("##### Appearance")
    st.markdown("<p style='color:var(--muted);'>Choose a colour theme from the sidebar under "
                "<b>COLOUR THEME</b> — it applies instantly across every page.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Reset pipeline")
    st.markdown("<p style='color:var(--muted);'>Clear all session data and start fresh.</p>", unsafe_allow_html=True)

    if st.button("Reset All Session Data", type="secondary"):
        for k in ["resume_text","resume_meta","candidate_skills","ml_prediction","jd_text",
                 "jd_analysis","match_result","questions"]:
            st.session_state[k] = None
        st.session_state.evaluations = {}
        st.session_state.answers = {}
        st.success("Session reset.")
        st.session_state.page = "home"
        st.rerun()

    st.markdown("---")
    st.markdown("##### About InterviewAI")
    st.markdown("""
    <div class='card'>
        <b style='color:var(--ink);'>InterviewAI</b> <span style='color:var(--muted);'>v3.1.0</span><br><br>
        <span style='color:var(--muted);'>An end-to-end ML-powered hiring assistant trained on real
        resume data, with Gemini-powered interview question generation and answer evaluation.</span><br><br>
        <b style='color:var(--ink);'>Tech Stack:</b>
        <span style='color:var(--muted);'>Python · Streamlit · Scikit-learn · Plotly · Google Gemini · pdfplumber</span><br>
        <b style='color:var(--ink);'>ML Model:</b>
        <span style='color:var(--muted);'>TF-IDF (1-3 grams, 12,000 features) + Logistic Regression · 10 roles · 5-fold CV · ~93% accuracy</span><br>
        <b style='color:var(--ink);'>Datasets:</b>
        <span style='color:var(--muted);'>final_merged_dataset2.csv (8,167 resumes) · job_title_des.csv (2,277 JDs) · IT_Job_Roles_Skills.csv (493 roles)</span>
    </div>
    """, unsafe_allow_html=True)
