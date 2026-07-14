"""app_views/dashboard.py — Analytics Dashboard"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from theme import get_active_colors


def render():
    st.markdown("<div class='section-header'>Analytics Dashboard</div>", unsafe_allow_html=True)

    if not st.session_state.resume_text:
        st.warning("Complete the pipeline first — start with Resume Upload.")
        if st.button("Start Pipeline"):
            st.session_state.page = "upload"; st.rerun()
        return

    C = get_active_colors()
    PLOT_FONT = dict(family="Inter, sans-serif", color=C["ink"])

    ml = st.session_state.ml_prediction
    skills = st.session_state.candidate_skills or []
    match = st.session_state.match_result
    jd = st.session_state.jd_analysis
    qs = st.session_state.questions or []
    evals = st.session_state.evaluations
    meta = st.session_state.resume_meta or {}

    name = meta.get("name") or "Candidate"
    role = ml["role"] if ml else "Unknown"
    conf = f"{round(ml['confidence']*100, 1)}%" if ml else "—"
    now = datetime.now().strftime("%d %b %Y, %H:%M")

    st.markdown(f"""
    <div style='background:var(--ink); border-radius:14px; padding:24px 30px; margin-bottom:20px;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <div style='font-family:var(--heading-font); font-weight:600;
                            font-size:1.6rem; color:var(--bg);'>{name}</div>
                <div style='color:var(--border); font-size:0.9rem; margin-top:4px;'>
                    Predicted Role: <b style='color:{C["accent"]};'>{role}</b> &nbsp;·&nbsp;
                    Model Confidence: <b style='color:{C["success"]};'>{conf}</b>
                </div>
            </div>
            <div style='text-align:right; color:var(--border); font-size:0.8rem;'>
                Report generated<br>{now}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Skills Extracted", len(skills))
    k2.metric("Match Score", f"{match['overall_score']}%" if match else "—")
    k3.metric("Questions Generated", len(qs))
    k4.metric("Answers Evaluated", len(evals))
    if evals:
        scores = [evals[i]["score"] for i in evals]
        avg = round(sum(scores)/len(scores), 1)
        k5.metric("Avg Answer Score", f"{avg}/10")
    else:
        k5.metric("Avg Answer Score", "—")
    st.markdown("---")

    col_ml, col_match = st.columns(2)
    with col_ml:
        st.markdown("##### ML role prediction")
        if ml:
            top3 = ml["top3"]
            fig = go.Figure(go.Bar(
                x=[r["probability"]*100 for r in top3], y=[r["role"] for r in top3],
                orientation="h", marker=dict(color=[C["accent"], C["accent_soft"], C["border"]]),
                text=[f"{r['probability']*100:.1f}%" for r in top3], textposition="outside",
                textfont=dict(color=C["ink"]),
            ))
            fig.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                              xaxis=dict(range=[0,100], title="Probability (%)", gridcolor=C["border"]),
                              yaxis=dict(title=""), height=210, margin=dict(l=20,r=60,t=20,b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ML prediction available.")

    with col_match:
        st.markdown("##### Skill match overview")
        if match:
            sc = C["success"] if match["overall_score"]>=70 else C["warning"] if match["overall_score"]>=45 else C["danger"]
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=match["overall_score"],
                number={"suffix":"%","font":{"color":sc,"size":34}},
                delta={"reference":60,"increasing":{"color":C["success"]},"decreasing":{"color":C["danger"]}},
                title={"text":match["verdict"],"font":{"color":C["muted"],"size":14}},
                gauge={"axis":{"range":[0,100],"tickcolor":C["muted"]},
                      "bar":{"color":sc,"thickness":0.25}, "bgcolor":C["surface"],"bordercolor":C["border"],
                      "steps":[{"range":[0,40],"color":C["danger_bg"]},{"range":[40,70],"color":C["warning_bg"]},
                               {"range":[70,100],"color":C["success_bg"]}]},
            ))
            fig2.update_layout(paper_bgcolor=C["surface"], height=210, margin=dict(l=20,r=20,t=50,b=20))
            st.plotly_chart(fig2, use_container_width=True)
            r_col, p_col = st.columns(2)
            r_col.metric("Required Match", f"{match['required_score']}%")
            p_col.metric("Preferred Match", f"{match['preferred_score']}%")
        else:
            st.info("No match result available.")

    st.markdown("---")
    col_radar, col_skills = st.columns(2)
    with col_radar:
        st.markdown("##### Skill coverage radar")
        if match and jd:
            _radar(match, jd, C)
        else:
            st.info("Complete JD analysis to see the radar chart.")

    with col_skills:
        st.markdown("##### Top candidate skills")
        if skills:
            top = sorted(skills, key=lambda x: -x["confidence"])[:12]
            df_sk = pd.DataFrame({"Skill":[s["skill"] for s in top],
                                  "Confidence":[s["confidence"] for s in top]})
            fig_sk = px.bar(df_sk, x="Confidence", y="Skill", orientation="h",
                            color="Confidence", color_continuous_scale=[[0,C["accent_soft"]],[1,C["accent"]]],
                            range_color=[0.5,1.0])
            fig_sk.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                                 coloraxis_showscale=False,
                                 xaxis=dict(range=[0,1.1], tickformat=".0%", gridcolor=C["border"]),
                                 yaxis=dict(title=""), height=330, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_sk, use_container_width=True)
        else:
            st.info("No skills extracted yet.")

    st.markdown("---")

    if evals:
        st.markdown("##### Assessment score breakdown")
        scores = [evals[i]["score"] for i in sorted(evals.keys())]
        q_labels = [f"Q{i+1}" for i in sorted(evals.keys())]
        grades = [evals[i]["grade"] for i in sorted(evals.keys())]
        bar_colors = [C["success"] if s>=8 else C["success"] if s>=7 else C["warning"] if s>=5
                     else C["warning"] if s>=3 else C["danger"] for s in scores]

        fig_sc = go.Figure(go.Bar(x=q_labels, y=scores, marker_color=bar_colors,
                                   text=[f"{s}/10 ({g})" for s,g in zip(scores,grades)],
                                   textposition="outside", textfont=dict(color=C["ink"])))
        fig_sc.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                             xaxis=dict(title="Question", gridcolor=C["border"]),
                             yaxis=dict(range=[0,12], title="Score", gridcolor=C["border"]),
                             height=290, margin=dict(l=10,r=10,t=30,b=30))
        st.plotly_chart(fig_sc, use_container_width=True)

        grade_counts = {}
        for g in grades: grade_counts[g] = grade_counts.get(g,0)+1
        cols = st.columns(5)
        grade_palette = [("A",C["success"]),("B",C["success"]),("C",C["warning"]),
                         ("D",C["warning"]),("F",C["danger"])]
        for col,(grade,color) in zip(cols, grade_palette):
            col.markdown(f"""
            <div class='card' style='text-align:center; border-color:{color}40;'>
                <div style='font-family:var(--heading-font); font-weight:600;
                            font-size:1.5rem; color:{color};'>{grade_counts.get(grade,0)}</div>
                <div style='font-size:0.8rem; color:{color};'>Grade {grade}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### Question-by-question evaluation")
        rows = []
        for i in sorted(evals.keys()):
            q, ev = (qs[i] if i<len(qs) else {}), evals[i]
            rows.append({"#": i+1, "Question": q.get("q","")[:60]+"...", "Skill": q.get("skill","—"),
                        "Difficulty": q.get("diff","—"), "Score": f"{ev['score']}/10",
                        "Grade": ev["grade"], "Feedback": ev.get("feedback","")[:80]+"..."})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown("---")

    if match:
        st.markdown("##### Recommendations")
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("**Skill gaps to address**")
            missing = match["missing_required"][:6]
            if missing:
                for s in missing:
                    st.markdown(f"<div style='background:{C['danger_bg']}; border-radius:8px; padding:8px 12px;"
                               f"border-left:3px solid {C['danger']}; margin:4px 0; color:{C['ink']}; "
                               f"font-size:0.9rem;'>{s}</div>", unsafe_allow_html=True)
            else:
                st.success("No critical skill gaps.")
        with rc2:
            st.markdown("**Candidate strengths**")
            for s in match["matched_required"][:6]:
                st.markdown(f"<div style='background:{C['success_bg']}; border-radius:8px; padding:8px 12px;"
                           f"border-left:3px solid {C['success']}; margin:4px 0; color:{C['ink']}; "
                           f"font-size:0.9rem;'>{s}</div>", unsafe_allow_html=True)

    st.markdown("---")
    _export(meta, ml, match, skills, qs, evals)


def _radar(match, jd, C):
    req = jd["required_skills"][:8]
    if not req:
        st.info("No required skills extracted from JD.")
        return
    cand_set = {s["skill"] for s in st.session_state.candidate_skills}
    cand_vals = [1.0 if s in cand_set else 0.0 for s in req]

    accent_rgb = _hex_to_rgb(C["accent"])
    success_rgb = _hex_to_rgb(C["success"])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[1.0]*len(req)+[1.0], theta=req+[req[0]], fill="toself",
                                  name="JD Requirement", line_color=C["accent"],
                                  fillcolor=f"rgba({accent_rgb[0]},{accent_rgb[1]},{accent_rgb[2]},0.08)"))
    fig.add_trace(go.Scatterpolar(r=cand_vals+[cand_vals[0]], theta=req+[req[0]], fill="toself",
                                  name="Candidate", line_color=C["success"],
                                  fillcolor=f"rgba({success_rgb[0]},{success_rgb[1]},{success_rgb[2]},0.18)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0,1.2]),
                  angularaxis=dict(color=C["ink_soft"]), bgcolor=C["surface"]),
        paper_bgcolor=C["surface"], font=dict(color=C["ink"], size=11),
        legend=dict(font=dict(size=11)), height=330, margin=dict(l=40,r=40,t=30,b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _export(meta, ml, match, skills, qs, evals):
    lines = ["="*60, "        INTERVIEWAI — CANDIDATE ASSESSMENT REPORT", "="*60,
             f"Candidate:     {meta.get('name') or 'N/A'}",
             f"Email:         {meta.get('email') or 'N/A'}",
             f"Generated:     {datetime.now().strftime('%d %b %Y %H:%M')}", "",
             "── ML CLASSIFICATION ─────────────────────────────────────",
             f"Predicted Role: {ml['role'] if ml else 'N/A'}",
             f"Confidence:     {round(ml['confidence']*100,1)}%" if ml else "N/A", "",
             "── SKILL MATCH ───────────────────────────────────────────"]
    if match:
        lines += [f"Overall Score:  {match['overall_score']}%", f"Verdict:        {match['verdict']}",
                  f"Required Score: {match['required_score']}%",
                  f"Preferred Score:{match['preferred_score']}%",
                  f"Matched Required Skills: {', '.join(match['matched_required'])}",
                  f"Missing Required Skills: {', '.join(match['missing_required'])}"]
    lines += ["", "── CANDIDATE SKILLS ──────────────────────────────────────",
              ", ".join(s["skill"] for s in skills)]
    if evals:
        lines += ["", "── ASSESSMENT SCORES ─────────────────────────────────────"]
        sc = [evals[i]["score"] for i in sorted(evals.keys())]
        lines.append(f"Average Score: {sum(sc)/len(sc):.1f}/10")
        for i in sorted(evals.keys()):
            q, ev = (qs[i] if i<len(qs) else {}), evals[i]
            lines.append(f"  Q{i+1} [{q.get('diff','?')}]: {ev['score']}/10 (Grade {ev['grade']}) — "
                        f"{q.get('q','')[:50]}...")
    lines += ["", "="*60, "End of Report"]

    st.download_button("Download Full Report (.txt)", data="\n".join(lines),
                       file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                       mime="text/plain", type="primary")
