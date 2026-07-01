"""
theme.py — Defines 4 selectable colour palettes for InterviewAI and renders
the CSS custom-property block for the currently active theme.

Each palette supplies every CSS variable consumed across app.py and
app_views/*.py so swapping themes recolours the entire app instantly.
"""

THEMES = {
    "claude": {
        "label": "Claude Warm",
        "swatch": ["#F9F8F6", "#C96442", "#2D2A26"],
        "google_fonts": "Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500",
        "heading_font": "'Source Serif 4', Georgia, serif",
        "body_font":    "'Inter', -apple-system, sans-serif",
        "vars": {
            "bg":          "#F9F8F6",
            "surface":     "#FFFFFF",
            "sidebar":     "#F4F3EE",
            "ink":         "#2D2A26",
            "ink-soft":    "#44413C",
            "muted":       "#87837C",
            "accent":      "#C96442",
            "accent-hov":  "#B5532F",
            "accent-soft": "#F3E3DA",
            "border":      "#E8E5DD",
            "border-soft": "#EFEDE6",
            "success":     "#5F8D52",
            "success-bg":  "#EBF2E7",
            "warning":     "#B8932A",
            "warning-bg":  "#FAF3E1",
            "danger":      "#BC4B3C",
            "danger-bg":   "#FBEAE6",
            "sidebar-hover":   "#EAE7DD",
            "sidebar-active-border": "#E8C9B8",
            "chip-cyan-bg":    "#E8F0F1",
            "chip-cyan-text":  "#3D7A82",
            "chip-cyan-border":"#C9DEE0",
        },
    },
    "midnight": {
        "label": "Midnight Blue",
        "swatch": ["#0F1420", "#5B8DEF", "#E8ECF4"],
        "google_fonts": "Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500",
        "heading_font": "'Plus Jakarta Sans', sans-serif",
        "body_font":    "'Inter', -apple-system, sans-serif",
        "vars": {
            "bg":          "#0F1420",
            "surface":     "#171D2D",
            "sidebar":     "#0B0F18",
            "ink":         "#E8ECF4",
            "ink-soft":    "#C2C9D6",
            "muted":       "#8A92A6",
            "accent":      "#5B8DEF",
            "accent-hov":  "#7AA3F2",
            "accent-soft": "#1C2A4A",
            "border":      "#262D40",
            "border-soft": "#1E2536",
            "success":     "#4ADE80",
            "success-bg":  "#0F2A1C",
            "warning":     "#FBBF24",
            "warning-bg":  "#2E2410",
            "danger":      "#F87171",
            "danger-bg":   "#2E1416",
            "sidebar-hover":   "#1A2236",
            "sidebar-active-border": "#3A5BA0",
            "chip-cyan-bg":    "#10293A",
            "chip-cyan-text":  "#67D7E8",
            "chip-cyan-border":"#1E4A5E",
        },
    },
    "sage": {
        "label": "Sage Garden",
        "swatch": ["#F6F8F4", "#5A8A6B", "#23302A"],
        "google_fonts": "Lora:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500",
        "heading_font": "'Lora', Georgia, serif",
        "body_font":    "'Inter', -apple-system, sans-serif",
        "vars": {
            "bg":          "#F6F8F4",
            "surface":     "#FFFFFF",
            "sidebar":     "#EEF3EA",
            "ink":         "#23302A",
            "ink-soft":    "#3C4A41",
            "muted":       "#7A887E",
            "accent":      "#5A8A6B",
            "accent-hov":  "#487057",
            "accent-soft": "#E1ECE3",
            "border":      "#DEE7DA",
            "border-soft": "#E8F0E5",
            "success":     "#4C8C5A",
            "success-bg":  "#E6F2E8",
            "warning":     "#B98A2C",
            "warning-bg":  "#F8F0DC",
            "danger":      "#B5503F",
            "danger-bg":   "#F7E6E2",
            "sidebar-hover":   "#E2EBDD",
            "sidebar-active-border": "#B8D4BE",
            "chip-cyan-bg":    "#E2EFEE",
            "chip-cyan-text":  "#347A78",
            "chip-cyan-border":"#C2DEDB",
        },
    },
    "violet": {
        "label": "Violet Ink",
        "swatch": ["#FAF8FC", "#7C5CC4", "#2A2438"],
        "google_fonts": "Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500",
        "heading_font": "'Fraunces', Georgia, serif",
        "body_font":    "'Inter', -apple-system, sans-serif",
        "vars": {
            "bg":          "#FAF8FC",
            "surface":     "#FFFFFF",
            "sidebar":     "#F1ECF8",
            "ink":         "#2A2438",
            "ink-soft":    "#473F58",
            "muted":       "#8B82A0",
            "accent":      "#7C5CC4",
            "accent-hov":  "#6747AE",
            "accent-soft": "#EAE2F6",
            "border":      "#E5DEF0",
            "border-soft": "#EFE9F7",
            "success":     "#5E9C6F",
            "success-bg":  "#E7F2E9",
            "warning":     "#BD8F2E",
            "warning-bg":  "#F9F1DD",
            "danger":      "#C1564C",
            "danger-bg":   "#F8E6E4",
            "sidebar-hover":   "#E6DEF2",
            "sidebar-active-border": "#C9B5E6",
            "chip-cyan-bg":    "#E7EBFA",
            "chip-cyan-text":  "#4C5FA8",
            "chip-cyan-border":"#CCD4F2",
        },
    },
}

DEFAULT_THEME = "claude"


def get_theme(theme_key: str) -> dict:
    return THEMES.get(theme_key, THEMES[DEFAULT_THEME])


def get_active_colors() -> dict:
    """
    Returns the hex values for the currently active theme, for use in Python-side
    contexts that can't read CSS variables (Plotly figures, inline-styled HTML).
    Reads st.session_state.theme; falls back to the default theme if unset.
    """
    import streamlit as st
    theme_key = st.session_state.get("theme", DEFAULT_THEME)
    t = get_theme(theme_key)
    v = t["vars"]
    return {
        "bg":          v["bg"],
        "surface":     v["surface"],
        "ink":         v["ink"],
        "ink_soft":    v["ink-soft"],
        "muted":       v["muted"],
        "accent":      v["accent"],
        "accent_hov":  v["accent-hov"],
        "accent_soft": v["accent-soft"],
        "border":      v["border"],
        "success":     v["success"],
        "success_bg":  v["success-bg"],
        "warning":     v["warning"],
        "warning_bg":  v["warning-bg"],
        "danger":      v["danger"],
        "danger_bg":   v["danger-bg"],
        "cyan":        v["chip-cyan-text"],
        "cyan_bg":     v["chip-cyan-bg"],
        "heading_font_css": t["heading_font"],
    }


def render_theme_css(theme_key: str) -> str:
    """Returns the full <link> + <style> block for the given theme, ready for st.markdown()."""
    t = get_theme(theme_key)
    v = t["vars"]

    css_vars = "\n".join(f"    --{k}: {val};" for k, val in v.items())

    return f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={t['google_fonts']}&display=swap" rel="stylesheet">

<style>
:root {{
{css_vars}
    --heading-font: {t['heading_font']};
    --body-font: {t['body_font']};
}}

html, body, [class*="css"] {{ font-family: var(--body-font); }}
h1, h2, h3, h4, .serif {{ font-family: var(--heading-font) !important; }}
code, .mono {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ── App shell ── */
[data-testid="stAppViewContainer"] {{ background: var(--bg); }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 1100px; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: var(--sidebar);
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] * {{ color: var(--ink-soft) !important; }}
[data-testid="stSidebar"] .stButton button {{
    background: transparent;
    border: 1px solid transparent;
    color: var(--ink-soft) !important;
    text-align: left;
    font-weight: 500;
    font-size: 0.93rem;
    border-radius: 8px;
    box-shadow: none;
    transition: background .15s ease;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: var(--sidebar-hover);
    border-color: transparent;
}}
[data-testid="stSidebar"] .stButton button[kind="primary"] {{
    background: var(--accent-soft) !important;
    color: var(--accent-hov) !important;
    font-weight: 600;
    border: 1px solid var(--sidebar-active-border);
    box-shadow: none;
}}
[data-testid="stSidebar"] hr {{ border-color: var(--border); }}

/* ── Buttons ── */
.stButton button[kind="primary"] {{
    background: var(--accent);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: var(--body-font);
    padding: 0.55rem 1.3rem;
    box-shadow: none;
    transition: background .15s ease;
}}
.stButton button[kind="primary"]:hover {{ background: var(--accent-hov); }}
.stButton button[kind="secondary"] {{
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--surface);
    font-weight: 500;
    color: var(--ink-soft);
    box-shadow: none;
}}
.stButton button[kind="secondary"]:hover {{ border-color: var(--accent); color: var(--accent); }}

/* ── Cards ── */
.card {{
    background: var(--surface);
    border-radius: 14px;
    padding: 22px 24px;
    border: 1px solid var(--border);
}}
.card-hover {{ transition: all .18s ease; }}
.card-hover:hover {{ border-color: var(--accent-soft); box-shadow: 0 2px 10px rgba(0,0,0,0.06); }}

/* ── Hero ── */
.hero-title {{
    font-family: var(--heading-font);
    font-weight: 600;
    font-size: 2.9rem;
    color: var(--ink);
    line-height: 1.15;
    letter-spacing: -0.01em;
}}
.hero-sub {{
    color: var(--muted);
    font-size: 1.08rem;
    max-width: 660px;
    margin: 0 auto;
    line-height: 1.65;
}}

/* ── Pipeline step ── */
.pipe-step {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 8px;
    text-align: center;
}}
.pipe-icon {{ font-size: 1.5rem; }}
.pipe-label {{
    font-size: 0.7rem; color: var(--muted); font-weight: 600;
    margin-top: 6px; line-height: 1.3; letter-spacing: 0.01em;
}}

/* ── Section header ── */
.section-header {{
    font-family: var(--heading-font);
    font-size: 1.45rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0.3rem 0 1rem 0;
}}

/* ── Skill chips ── */
.chip {{
    display: inline-block;
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 0.79rem;
    font-weight: 500;
    margin: 3px;
    border: 1px solid transparent;
}}
.chip-success {{ background: var(--success-bg); color: var(--success); border-color: var(--border); }}
.chip-danger  {{ background: var(--danger-bg);  color: var(--danger);  border-color: var(--border); }}
.chip-primary {{ background: var(--accent-soft); color: var(--accent-hov); border-color: var(--sidebar-active-border); }}
.chip-cyan    {{ background: var(--chip-cyan-bg); color: var(--chip-cyan-text); border-color: var(--chip-cyan-border); }}
.chip-warning {{ background: var(--warning-bg); color: var(--warning); border-color: var(--border); }}
.chip-neutral {{ background: var(--border-soft); color: var(--muted); border-color: var(--border); }}

/* ── Score display ── */
.score-circle {{
    text-align: center;
    background: var(--surface);
    border-radius: 16px;
    padding: 28px;
    border: 1.5px solid var(--border);
}}
.score-num {{ font-family: var(--heading-font); font-weight: 600; font-size: 3.4rem; }}
.score-label {{ color: var(--muted); font-size: 0.92rem; }}

/* ── Metric override ── */
div[data-testid="stMetric"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
}}
div[data-testid="stMetricLabel"] {{ color: var(--muted) !important; font-weight: 500; }}
div[data-testid="stMetricValue"] {{ color: var(--ink) !important; font-family: var(--heading-font); }}

/* ── Expander ── */
.streamlit-expanderHeader {{ background: var(--surface); border-radius: 10px; font-weight: 500; color: var(--ink); }}
div[data-testid="stExpander"] {{
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--surface);
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px 8px 0 0; font-weight: 500; color: var(--muted); }}
.stTabs [aria-selected="true"] {{ color: var(--accent) !important; background: var(--accent-soft); }}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {{
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface);
    border: 1.5px dashed var(--border);
    border-radius: 12px;
}}

/* ── Body text ── */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span:not(.chip),
[data-testid="stAppViewContainer"] li {{ color: var(--ink-soft); }}
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3 {{ color: var(--ink); }}
[data-testid="stAppViewContainer"] strong {{ color: var(--ink); }}

/* ── Dataset badge ── */
.dataset-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--ink-soft);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 500;
}}

/* ── Divider ── */
hr {{ border-color: var(--border) !important; margin: 1.4rem 0; }}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{ border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}

/* ── Checkbox / radio labels ── */
[data-testid="stAppViewContainer"] label {{ color: var(--ink-soft); }}

/* ── Theme swatch picker ── */
.theme-swatch-row {{ display: flex; gap: 6px; margin-bottom: 2px; }}
.theme-swatch {{
    width: 16px; height: 16px; border-radius: 50%;
    border: 1px solid rgba(0,0,0,0.12);
    display: inline-block;
}}
</style>
"""
