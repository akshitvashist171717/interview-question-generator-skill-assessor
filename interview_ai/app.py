"""
app.py — InterviewAI: Smart Hiring Platform
Run: streamlit run app.py
"""
import streamlit as st
from theme import THEMES, DEFAULT_THEME, render_theme_css

st.set_page_config(
    page_title="InterviewAI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ────────────────────────────────────────────────────────────
DEFAULTS = {
    "page": "home", "resume_text": None, "resume_meta": None,
    "candidate_skills": None, "ml_prediction": None, "jd_text": None,
    "jd_analysis": None, "match_result": None, "questions": None,
    "evaluations": {}, "answers": {}, "gemini_api_key": "",
    "theme": DEFAULT_THEME,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Inject the active theme's CSS (must run before any other markup) ─────────
st.markdown(render_theme_css(st.session_state.theme), unsafe_allow_html=True)

PAGES = {
    "home":       ("⌂", "Home"),
    "upload":     ("⤒", "Resume Upload"),
    "jd":         ("☰", "Job Description"),
    "questions":  ("?", "Interview Questions"),
    "assessment": ("✎", "Skill Assessment"),
    "dashboard":  ("◫", "Dashboard"),
    "insights":   ("◈", "Dataset Insights"),
    "settings":   ("⚙", "Settings"),
}

with st.sidebar:
    st.markdown("""
    <div style='padding:6px 4px 16px 4px;'>
        <div style='font-family:var(--heading-font); font-weight:600;
                    font-size:1.35rem; color:var(--ink);'>✦ InterviewAI</div>
        <div style='color:var(--muted); font-size:0.8rem; margin-top:2px;'>
            ML-Powered Hiring Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    for key, (icon, label) in PAGES.items():
        active = st.session_state.page == key
        if st.button(f"{icon}   {label}", key=f"nav_{key}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    st.markdown("<div style='color:var(--muted); font-size:0.74rem; font-weight:600; "
                "letter-spacing:0.04em;'>PIPELINE PROGRESS</div>", unsafe_allow_html=True)
    steps = [
        ("Resume Upload",       st.session_state.resume_text is not None),
        ("ML Classification",   st.session_state.ml_prediction is not None),
        ("Skill Extraction",    st.session_state.candidate_skills is not None),
        ("JD Analysis",         st.session_state.jd_analysis is not None),
        ("Skill Matching",      st.session_state.match_result is not None),
        ("Question Generation", st.session_state.questions is not None),
        ("Assessment",          len(st.session_state.evaluations) > 0),
    ]
    for label, done in steps:
        c = "var(--success)" if done else "var(--muted)"
        dot = "●" if done else "○"
        st.markdown(f"<div style='font-size:0.83rem; color:{c}; margin:3px 0;'>"
                     f"{dot}&nbsp;&nbsp;{label}</div>", unsafe_allow_html=True)

    

   


page = st.session_state.page
if page == "home":
    from app_views import home; home.render()
elif page == "upload":
    from app_views import upload; upload.render()
elif page == "jd":
    from app_views import jd_page; jd_page.render()
elif page == "questions":
    from app_views import questions_page; questions_page.render()
elif page == "assessment":
    from app_views import assessment_page; assessment_page.render()
elif page == "dashboard":
    from app_views import dashboard; dashboard.render()
elif page == "insights":
    from app_views import insights_page; insights_page.render()
elif page == "settings":
    from app_views import settings_page; settings_page.render()
