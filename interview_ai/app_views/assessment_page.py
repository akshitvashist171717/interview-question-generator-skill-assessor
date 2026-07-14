"""app_views/assessment_page.py — Answer Input → Gemini Evaluation"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
from utils.gemini_client import evaluate_answer
from theme import get_active_colors


def _grade_colors(C):
    return {"A": C["success"], "B": C["success"], "C": C["warning"], "D": C["warning"], "F": C["danger"]}


def render():
    st.markdown("<div class='section-header'>Skill Assessment — Answer Evaluation</div>", unsafe_allow_html=True)

    if not st.session_state.questions:
        st.warning("Please generate interview questions first.")
        if st.button("Go to Questions"):
            st.session_state.page = "questions"; st.rerun()
        return

    questions = st.session_state.questions
    role = st.session_state.ml_prediction["role"]
    api_key = st.session_state.get("gemini_api_key", "")
    if api_key: os.environ["GEMINI_API_KEY"] = api_key

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Questions", len(questions))
    col_b.metric("Answered", len(st.session_state.answers))
    col_c.metric("Evaluated", len(st.session_state.evaluations))

    if not api_key:
        st.info("Add your Gemini API key in Settings for detailed AI evaluation. "
                "Currently using heuristic scoring.")
    st.markdown("---")

    st.markdown("##### Answer the questions below")
    st.caption("Type your answer and click 'Evaluate' for instant AI feedback.")

    for i, q in enumerate(questions):
        diff, qtype, skill = q.get("diff","Medium"), q.get("type","Conceptual"), q.get("skill","General")
        ev = st.session_state.evaluations.get(i)
        ans_key = f"answer_{i}"

        with st.expander(f"Q{i+1}  [{diff} · {qtype}]  {q['q'][:70]}{'...' if len(q['q'])>70 else ''}",
                         expanded=(ev is None)):
            st.markdown(f"""
            <div class='card'>
                <span class='chip chip-cyan'>{skill}</span>
                <span class='chip chip-primary'>{qtype}</span>
                <span class='chip chip-neutral'>{diff}</span>
                <p style='color:var(--ink); margin-top:10px; font-size:1rem; font-weight:600;'>{q['q']}</p>
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_area("Your Answer", value=st.session_state.answers.get(i, ""),
                                  height=120, key=ans_key, placeholder="Type your answer here...",
                                  label_visibility="collapsed")

            col_btn, col_clear = st.columns([2, 1])
            with col_btn:
                eval_clicked = st.button("Evaluate Answer", key=f"eval_{i}", type="primary")
            with col_clear:
                if st.button("Clear", key=f"clear_{i}"):
                    st.session_state.answers.pop(i, None)
                    st.session_state.evaluations.pop(i, None)
                    st.rerun()

            if eval_clicked:
                if not answer.strip():
                    st.warning("Please type an answer before evaluating.")
                else:
                    st.session_state.answers[i] = answer
                    with st.spinner("Gemini is evaluating your answer..."):
                        result = evaluate_answer(question=q["q"], answer=answer, skill=skill,
                                                 difficulty=diff, role=role)
                    st.session_state.evaluations[i] = result
                    st.rerun()

            if ev:
                _render_eval(ev)

    st.markdown("---")
    n_eval = len(st.session_state.evaluations)
    if n_eval > 0:
        C = get_active_colors()
        scores = [st.session_state.evaluations[i]["score"] for i in range(len(questions))
                  if i in st.session_state.evaluations]
        avg = sum(scores) / len(scores)

        st.markdown("##### Assessment progress")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Answered", f"{n_eval}/{len(questions)}")
        c2.metric("Average Score", f"{avg:.1f}/10")
        c3.metric("Best Score", f"{max(scores)}/10")
        c4.metric("Grade", _avg_grade(avg))

        fig = go.Figure(go.Scatter(
            x=[f"Q{i+1}" for i in range(len(scores))], y=scores, mode="lines+markers",
            line=dict(color=C["accent"], width=2),
            marker=dict(size=10, color=scores,
                       colorscale=[[0,C["danger"]],[0.5,C["warning"]],[1,C["success"]]], cmin=0, cmax=10),
        ))
        fig.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"],
                          font=dict(family="Inter, sans-serif", color=C["ink"]),
                          xaxis=dict(gridcolor=C["border"]),
                          yaxis=dict(range=[0,11], gridcolor=C["border"], title="Score"),
                          height=230, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)

        if n_eval == len(questions):
            st.success("All questions answered. View the full dashboard.")
            if st.button("View Dashboard →", type="primary"):
                st.session_state.page = "dashboard"; st.rerun()
        else:
            if st.button("View Partial Dashboard →", type="secondary"):
                st.session_state.page = "dashboard"; st.rerun()


def _render_eval(ev):
    C = get_active_colors()
    GRADE_COLOR = _grade_colors(C)
    score, grade = ev.get("score", 0), ev.get("grade", "—")
    g_col = GRADE_COLOR.get(grade, C["muted"])
    s_col = C["success"] if score>=8 else C["warning"] if score>=5 else C["danger"]

    st.markdown(f"""
    <div style='background:var(--bg); border-radius:12px; padding:16px;
                border:1px solid {s_col}40; margin-top:10px;'>
        <div style='display:flex; align-items:center; gap:18px; margin-bottom:10px;'>
            <div style='text-align:center;'>
                <div style='font-size:0.75rem; color:var(--muted);'>Score</div>
                <div style='font-family:var(--heading-font); font-weight:600;
                            font-size:1.6rem; color:{s_col};'>{score}/10</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:0.75rem; color:var(--muted);'>Grade</div>
                <div style='font-family:var(--heading-font); font-weight:600;
                            font-size:1.6rem; color:{g_col};'>{grade}</div>
            </div>
            <div style='flex:1; color:var(--ink-soft); font-size:0.87rem;'>{ev.get("feedback","")}</div>
        </div>
    """, unsafe_allow_html=True)

    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown("**Strengths**")
        for s in ev.get("strengths", []): st.markdown(f"- {s}")
    with col_i:
        st.markdown("**Areas to improve**")
        for imp in ev.get("improvements", []): st.markdown(f"- {imp}")

    kw = ev.get("keywords_hit", [])
    if kw:
        st.markdown("**Keywords detected:**")
        st.markdown("".join(f"<span class='chip chip-cyan'>{k}</span>" for k in kw), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _avg_grade(avg):
    return "A" if avg>=9 else "B" if avg>=7 else "C" if avg>=5 else "D" if avg>=3 else "F"
