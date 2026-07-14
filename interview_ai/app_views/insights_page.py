"""app_views/insights_page.py — Explore the real training datasets"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import get_dataset_stats, _load_resume_df, _load_jd_df, _load_skill_df
from ml.resume_classifier import train_and_save
from theme import get_active_colors


def _category_palette(C):
    """12-color categorical palette derived from the active theme's semantic colors."""
    return [
        C["accent"], C["cyan"], C["success"], C["warning"], C["accent_hov"], C["danger"],
        C["accent"], C["cyan"], C["success"], C["warning"], C["accent_hov"], C["danger"],
    ]


def render():
    C = get_active_colors()
    PLOT_FONT = dict(family="Inter, sans-serif", color=C["ink"])
    PALETTE = _category_palette(C)

    st.markdown("<div class='section-header'>Dataset Insights &amp; Model Performance</div>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:var(--muted);'>Full transparency into the three real-world datasets "
                "powering the ML classifier, JD analysis, and skill matching engine.</p>",
                unsafe_allow_html=True)

    stats = get_dataset_stats()
    resume_df = _load_resume_df()
    jd_df = _load_jd_df()
    skill_df = _load_skill_df()

    # ── Dataset overview cards ──────────────────────────────────────────
    st.markdown("##### Source datasets")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class='card card-hover'>
            <div style='font-family:var(--heading-font); font-weight:600;
                        font-size:1.02rem; color:var(--accent); margin-bottom:6px;'>final_merged_dataset2.csv</div>
            <div style='color:var(--muted); font-size:0.85rem;'>
                Real resumes labelled by job category — primary ML training source.
            </div>
            <div style='margin-top:12px;'>
                <span class='chip chip-primary'>{stats['total_resume_records']:,} resumes</span>
                <span class='chip chip-cyan'>{stats['unique_resume_roles']} roles</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='card card-hover'>
            <div style='font-family:var(--heading-font); font-weight:600;
                        font-size:1.02rem; color:var(--accent); margin-bottom:6px;'>job_title_des.csv</div>
            <div style='color:var(--muted); font-size:0.85rem;'>
                Real job description postings — used for realistic sample JDs.
            </div>
            <div style='margin-top:12px;'>
                <span class='chip chip-primary'>{stats['total_jd_records']:,} records</span>
                <span class='chip chip-cyan'>{stats['unique_roles_jd']} roles</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='card card-hover'>
            <div style='font-family:var(--heading-font); font-weight:600;
                        font-size:1.02rem; color:var(--accent); margin-bottom:6px;'>IT_Job_Roles_Skills.csv</div>
            <div style='color:var(--muted); font-size:0.85rem;'>
                Structured skill &amp; certification mapping per IT role.
            </div>
            <div style='margin-top:12px;'>
                <span class='chip chip-primary'>{stats['total_skill_records']:,} records</span>
                <span class='chip chip-cyan'>{stats['unique_it_roles']} unique roles</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Role distribution (resumes) ─────────────────────────────────────
    st.markdown("##### Resume role distribution (ML training data)")
    role_dist = stats["role_distribution"]
    df_roles = pd.DataFrame({"Role": list(role_dist.keys()), "Count": list(role_dist.values())})
    df_roles = df_roles.sort_values("Count", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_roles["Count"], y=df_roles["Role"], orientation="h",
        marker=dict(color=df_roles["Count"], colorscale=[[0,C["accent_soft"]],[1,C["accent"]]]),
        text=df_roles["Count"], textposition="outside", textfont=dict(color=C["ink"]),
    ))
    fig.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                      xaxis=dict(title="Number of Resumes", gridcolor=C["border"]),
                      yaxis=dict(title=""), height=400, margin=dict(l=10,r=40,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Top skills + role category split ────────────────────────────────
    col_sk, col_pie = st.columns([3, 2])
    with col_sk:
        st.markdown("##### Most in-demand skills (across 493 IT roles)")
        top_skills = stats["top_skills"]
        df_sk = pd.DataFrame(top_skills, columns=["Skill", "Frequency"]).sort_values("Frequency")
        fig2 = px.bar(df_sk, x="Frequency", y="Skill", orientation="h",
                     color="Frequency", color_continuous_scale=[[0,C["cyan_bg"]],[1,C["cyan"]]])
        fig2.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                           coloraxis_showscale=False, height=400,
                           xaxis=dict(title="Mentions across role profiles", gridcolor=C["border"]),
                           yaxis=dict(title=""), margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col_pie:
        st.markdown("##### Role category split")
        from data_loader import get_role_category
        cats = [get_role_category(r) for r in role_dist.keys() for _ in range(role_dist[r])]
        cat_counts = pd.Series(cats).value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig3 = px.pie(cat_counts, values="Count", names="Category", hole=0.5,
                     color_discrete_sequence=PALETTE)
        fig3.update_layout(paper_bgcolor=C["surface"], font=PLOT_FONT, height=400,
                           margin=dict(l=10,r=10,t=10,b=10), legend=dict(font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Resume length distribution ──────────────────────────────────────
    st.markdown("##### Resume length distribution")
    lengths = resume_df["resume_text"].str.len()
    fig4 = px.histogram(x=lengths, nbins=40, color_discrete_sequence=[C["accent"]])
    fig4.update_layout(paper_bgcolor=C["surface"], plot_bgcolor=C["surface"], font=PLOT_FONT,
                       xaxis=dict(title="Resume Length (characters)", gridcolor=C["border"]),
                       yaxis=dict(title="Count", gridcolor=C["border"]),
                       height=240, margin=dict(l=10,r=10,t=10,b=10), bargap=0.05)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption(f"Average resume length: {stats['avg_resume_length']:,} characters across "
              f"{stats['total_resume_records']:,} unique resumes.")

    st.markdown("---")

    # ── Sample data preview ─────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Resume Samples", "Job Description Samples", "Skills Mapping Samples"])
    with tab1:
        sample0 = resume_df[["label", "resume_text"]].sample(
            min(8, len(resume_df)), random_state=42
        ).reset_index(drop=True)
        sample0["resume_text"] = sample0["resume_text"].str.slice(0, 140) + "..."
        sample0.columns = ["Role", "Resume Preview"]
        st.dataframe(sample0, use_container_width=True, hide_index=True)

    with tab2:
        sample1 = jd_df[["job_title", "label", "description"]].sample(
            min(8, len(jd_df)), random_state=42
        ).reset_index(drop=True)
        sample1["description"] = sample1["description"].str.slice(0, 140) + "..."
        sample1.columns = ["Original Title", "Normalised Role", "Description Preview"]
        st.dataframe(sample1, use_container_width=True, hide_index=True)

    with tab3:
        sample2 = skill_df[["job_title", "skills", "certifications"]].sample(
            min(8, len(skill_df)), random_state=42
        ).reset_index(drop=True)
        sample2["skills"] = sample2["skills"].str.slice(0, 100) + "..."
        sample2.columns = ["Job Title", "Skills", "Certifications"]
        st.dataframe(sample2, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── ML Model performance ────────────────────────────────────────────
    st.markdown("##### ML model performance")
    with st.spinner("Loading model metrics..."):
        result = train_and_save()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cross-Val Accuracy", f"{round(result['cv_mean']*100,1)}%")
    c2.metric("Std Deviation", f"±{round(result['cv_std']*100,2)}%")
    c3.metric("Training Samples", f"{result['n_samples']:,}")
    c4.metric("Classes (Roles)", result["n_classes"])

    st.markdown(f"""
    <div class='card' style='margin-top:12px;'>
        <b style='color:var(--ink);'>Algorithm:</b> <span style='color:var(--muted);'>
            TF-IDF Vectorizer (1-3 grams, 12,000 features) + Logistic Regression
            (balanced class weights, L2 regularisation)
        </span><br>
        <b style='color:var(--ink);'>Validation:</b> <span style='color:var(--muted);'>
            5-Fold Stratified Cross-Validation
        </span><br>
        <b style='color:var(--ink);'>Training Data:</b> <span style='color:var(--muted);'>
            final_merged_dataset2.csv — {stats['total_resume_records']:,} real resumes
            across {stats['unique_resume_roles']} job categories
        </span><br>
        <b style='color:var(--ink);'>Supporting Data:</b> <span style='color:var(--muted);'>
            job_title_des.csv for realistic JD samples ·
            IT_Job_Roles_Skills.csv for skill taxonomy &amp; certifications
        </span>
    </div>
    """, unsafe_allow_html=True)
