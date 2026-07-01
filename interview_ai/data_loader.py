"""
data_loader.py
Loads, cleans, and preprocesses THREE real datasets:

  1. final_merged_dataset2.csv  — 8,234 real RESUMES labelled by category
                                   -> PRIMARY source for ML classifier training
  2. job_title_des.csv          — 2,277 real job description postings, 15 roles
                                   -> source for realistic sample JDs
  3. IT_Job_Roles_Skills.csv    — 493 IT role -> skills/certifications mapping
                                   -> source for the skill vocabulary + certs

Exposes:(function available for other files)
  - get_training_corpus()      -> (texts, labels) for ML classifier (resumes)
  - get_all_roles()            -> sorted list of all known roles
  - get_skills_for_role()      -> list[str] skills for a given role(it gives skills for the particular role)
  - get_certifications_for_role() -> certifications for a role 
  - get_jd_sample()            -> realistic sample JD text for a role
  - get_dataset_stats()        -> stats across all 3 datasets for dashboard
"""

import os ##used for folders , files and paths(opearting system)
import re ##used for text cleaning(regular expression) egPython!!!@@@ SQL###123 -> Python SQL
import pandas as pd
from functools import lru_cache ##lru->least recently used A decorator that stores function results in memory to avoid redundant calculations
from collections import Counter ##used to find most common skill through their occurrence

DATA_DIR    = os.path.join(os.path.dirname(__file__), "data") ##Look at the folder where this data_loader.py file is currently sitting, and dynamically glue the word data onto the end of it.
RESUME_CSV  = os.path.join(DATA_DIR, "final_merged_dataset2.csv")##Take the folder path we just saved in DATA_DIR, and glue the file name "final_merged_dataset2.csv" right onto the end of it.
JD_CSV      = os.path.join(DATA_DIR, "job_title_des.csv")
SKILL_CSV   = os.path.join(DATA_DIR, "IT_Job_Roles_Skills.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Role normalisation — maps raw labels from BOTH datasets onto one shared
# taxonomy of roles, so the resume classifier and JD/skill lookups agree.
# ─────────────────────────────────────────────────────────────────────────────
## created dictionary for the normalization purpose 
RESUME_ROLE_NORMALISE = {
    "python_developer":        "Python Developer",
    "java_developer":          "Java Developer",
    "web_developer":           "Web Developer",
    "database_administrator":  "Database Administrator",
    "security_analyst":        "Security Analyst",
    "systems_administrator":   "Systems Administrator",
    "project_manager":         "Project Manager",
    "front_end_developer":     "Front End Developer",
    "network_administrator":   "Network Administrator",
    "software_developer":      "Software Developer",
}

JD_ROLE_NORMALISE = {
    "machine learning":         "Machine Learning Engineer",
    "flutter developer":        "Flutter / Mobile Developer",
    "django developer":         "Python Developer",
    "ios developer":            "iOS Developer",
    "full stack developer":     "Full Stack Developer",
    "java developer":           "Java Developer",
    "javascript developer":     "Web Developer",
    "devops engineer":          "DevOps Engineer",
    "software engineer":        "Software Developer",
    "database administrator":   "Database Administrator",
    "wordpress developer":      "Web Developer",
    "php developer":            "Software Developer",
    "backend developer":        "Software Developer",
    "network administrator":    "Network Administrator",
    "node js developer":        "Web Developer",
}

ROLE_CATEGORY = {
    "Python Developer":        "Backend",
    "Java Developer":          "Backend",
    "Web Developer":           "Web Dev",
    "Database Administrator":  "Database",
    "Security Analyst":        "Security",
    "Systems Administrator":   "Infrastructure",
    "Project Manager":         "Management",
    "Front End Developer":     "Frontend",
    "Network Administrator":   "Networking",
    "Software Developer":      "Engineering",
    "Machine Learning Engineer": "AI / ML",
    "Flutter / Mobile Developer": "Mobile",
    "iOS Developer":           "Mobile",
    "Full Stack Developer":    "Web Dev",
    "DevOps Engineer":         "DevOps",
}


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)##decorator A decorator modifies the behavior of a function. maxsize means only one result
def _load_resume_df() -> pd.DataFrame: ##internal function for training corpus (__load_resume_df) -> means it will return pd.dataframe
    """Loads the 8,234-row real resume corpus — PRIMARY ML training source."""
    df = pd.read_csv(RESUME_CSV, encoding="utf-8") ##utf-8 is a standard without é ü
    df.columns = ["resume_text", "category"]
    df = df.dropna(subset=["resume_text", "category"])## it removes missing values 
    df["resume_text"] = df["resume_text"].astype(str).str.strip()## text processing requires strings and it is also doing extra space removal 
    df = df[df["resume_text"].str.len() > 30]## removing very small resumes 
    df["label"] = df["category"].str.lower().str.strip().map(RESUME_ROLE_NORMALISE)## it uses the normalize dictionary from above 
    df = df.dropna(subset=["label"])## removes missing values from label 
    df = df.drop_duplicates(subset=["resume_text"])## remove duplicate resume and not making the model overfitting and biased
    return df.reset_index(drop=True) ##reseting the index after cleaning and drop=true means old index is discarded


@lru_cache(maxsize=1)
def _load_jd_df() -> pd.DataFrame:
    """Loads job_title_des.csv — used for realistic sample JD text."""
    df = pd.read_csv(JD_CSV, encoding="latin1")
    df.columns = ["idx", "job_title", "description"]
    df["job_title"] = df["job_title"].str.strip()
    df["label"] = df["job_title"].str.lower().str.strip().map(JD_ROLE_NORMALISE)
    df = df.dropna(subset=["label"])
    df["description"] = df["description"].fillna("").str.strip()##fillna replace missing values with empty string 
    return df


@lru_cache(maxsize=1)
def _load_skill_df() -> pd.DataFrame:
    """Loads IT_Job_Roles_Skills.csv — used for skill vocabulary + certifications."""
    df = pd.read_csv(SKILL_CSV, encoding="latin1")
    df.columns = ["job_title", "description", "skills", "certifications"]
    df["job_title"]      = df["job_title"].str.strip()
    df["skills"]         = df["skills"].fillna("")
    df["certifications"] = df["certifications"].fillna("")
    df["description"]    = df["description"].fillna("")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_training_corpus() -> tuple[list[str], list[str]]: ##corpus meaning is collection of text documents
    """
    Returns (texts, labels) for ML classifier training.
    PRIMARY SOURCE: final_merged_dataset2.csv — 8,234 real resumes, 10 roles.
    """
    df = _load_resume_df()
    return df["resume_text"].tolist(), df["label"].tolist()## it converts pdseries to list because every model input x needs correct answer y with it 


def get_all_roles() -> list[str]:
    """Returns sorted list of all roles the resume classifier can predict."""
    df = _load_resume_df()
    return sorted(df["label"].unique().tolist())


def get_role_category(role: str) -> str:
    return ROLE_CATEGORY.get(role, "Engineering")##.get() to access the dictionary , it will not crash the system will return engineering as the default value  


def get_skills_for_role(role: str) -> list[str]: ##the function expects a string 
    """Returns reference skill list for a role from IT_Job_Roles_Skills.csv (fuzzy matched)."""
    skill_df = _load_skill_df()
    role_lower = role.lower()

    for _, row in skill_df.iterrows():
        if row["job_title"].lower() == role_lower:
            return _parse_skills(row["skills"])

    best_row, best_score = None, 0
    role_words = set(role_lower.replace("/", " ").split())
    for _, row in skill_df.iterrows():
        title_words = set(row["job_title"].lower().split())
        score = len(role_words & title_words) / max(len(role_words | title_words), 1)
        if score > best_score:
            best_score, best_row = score, row

    if best_row is not None and best_score > 0.2:
        return _parse_skills(best_row["skills"])
    return []


def get_certifications_for_role(role: str) -> list[str]:
    """Returns recommended certifications for a role (fuzzy matched)."""
    skill_df = _load_skill_df()
    role_lower = role.lower()

    for _, row in skill_df.iterrows():
        if row["job_title"].lower() == role_lower:
            return [c for c in _parse_skills(row["certifications"]) if len(c) > 3][:5]

    best_row, best_score = None, 0
    role_words = set(role_lower.replace("/", " ").split())
    for _, row in skill_df.iterrows():
        title_words = set(row["job_title"].lower().split())
        score = len(role_words & title_words) / max(len(role_words | title_words), 1)
        if score > best_score:
            best_score, best_row = score, row

    if best_row is not None and best_score > 0.2:
        return [c for c in _parse_skills(best_row["certifications"]) if len(c) > 3][:5]
    return []


def get_jd_sample(role: str) -> str:
    """Returns a representative, medium-length sample JD for a role (fuzzy matched)."""
    df = _load_jd_df()
    rows = df[df["label"] == role].copy()

    if rows.empty:
        role_words = set(role.lower().replace("/", " ").split())
        best_label, best_score = None, 0
        for lbl in df["label"].unique():
            lbl_words = set(lbl.lower().replace("/", " ").split())
            score = len(role_words & lbl_words) / max(len(role_words | lbl_words), 1)
            if score > best_score:
                best_score, best_label = score, lbl
        if best_label and best_score > 0.15:
            rows = df[df["label"] == best_label].copy()

    if rows.empty:
        return ""

    rows["len"] = rows["description"].str.len()
    mid = rows[(rows["len"] >= 600) & (rows["len"] <= 2800)]
    if mid.empty:
        mid = rows
    median_len = mid["len"].median()
    idx = (mid["len"] - median_len).abs().idxmin()
    return _clean_encoding(mid.loc[idx, "description"])


def _clean_encoding(text: str) -> str:
    """Fixes common mis-decoded bullet/quote characters from latin-1 JD source data."""
    replacements = {
        "â¢": "•", "â€™": "'", "â€œ": '"', "â€\x9d": '"',
        "â€“": "–", "â€”": "—", "Â": "", "â": "•",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.strip()


def get_dataset_stats() -> dict:
    """Returns statistics across all three datasets for the Insights dashboard."""
    resume_df = _load_resume_df()
    jd_df     = _load_jd_df()
    skill_df  = _load_skill_df()

    all_skills = []
    for s in skill_df["skills"]:
        all_skills.extend(_parse_skills(s))
    skill_counts = Counter(all_skills)

    return {
        "total_resume_records": len(resume_df),
        "unique_resume_roles":  resume_df["label"].nunique(),
        "total_jd_records":     len(jd_df),
        "unique_roles_jd":      jd_df["label"].nunique(),
        "total_skill_records":  len(skill_df),
        "unique_it_roles":      skill_df["job_title"].nunique(),
        "top_skills":           skill_counts.most_common(15),
        "role_distribution":    resume_df["label"].value_counts().to_dict(),
        "avg_resume_length":    int(resume_df["resume_text"].str.len().mean()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_skills(raw: str) -> list[str]:
    if not raw or pd.isna(raw):
        return []
    skills = [s.strip() for s in str(raw).split(",") if s.strip()]
    skills = [re.sub(r"â.*", "", s).strip() for s in skills]
    return [s for s in skills if len(s) > 1]
