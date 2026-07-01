"""
utils/skill_extractor.py
Extracts skills from resume text using the real IT_Job_Roles_Skills.csv vocabulary.
Builds a master skill set from all 493 IT role definitions.
"""
import re #Used to build dynamic regex patterns for each skill alias and scan the resume text.
import sys, os # Used to add the parent directory to Python's path so the local data_loader module can be found. 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))   
from data_loader import _load_skill_df, _parse_skills # loads IT_Job_Roles_Skills.csv into a Pandas DataFrame/splits raw comma/semicolon-separated skill strings from that CSV into clean individual skill names
from functools import lru_cache


# ── Additional common aliases not in dataset ──────────────────────────────
EXTRA_ALIASES = {
    "Python":         ["python", "python3", "py"],
    "JavaScript":     ["javascript", "js", "es6", "ecmascript"],
    "TypeScript":     ["typescript", "ts"],
    "React":          ["react", "reactjs", "react.js", "nextjs", "next.js"],
    "Node.js":        ["node.js", "nodejs", "node js"],
    "Vue.js":         ["vue", "vuejs", "vue.js"],
    "Angular":        ["angular", "angularjs"],
    "Django":         ["django", "drf"],
    "FastAPI":        ["fastapi", "fast api"],
    "Flask":          ["flask"],
    "Spring Boot":    ["spring boot", "spring"],
    "TensorFlow":     ["tensorflow", "tf", "keras"],
    "PyTorch":        ["pytorch", "torch"],
    "Scikit-learn":   ["scikit-learn", "sklearn"],
    "Pandas":         ["pandas"],
    "NumPy":          ["numpy"],
    "Machine Learning": ["machine learning", "ml model"],
    "Deep Learning":  ["deep learning", "neural network", "cnn", "rnn", "lstm"],
    "NLP":            ["nlp", "natural language processing", "bert", "transformers"],
    "AWS":            ["aws", "amazon web services", "ec2", "s3", "lambda", "sagemaker"],
    "Azure":          ["azure", "microsoft azure"],
    "GCP":            ["gcp", "google cloud", "bigquery"],
    "Docker":         ["docker", "dockerfile", "containerization"],
    "Kubernetes":     ["kubernetes", "k8s", "kubectl", "helm"],
    "CI/CD":          ["ci/cd", "github actions", "jenkins", "gitlab ci", "circleci"],
    "Terraform":      ["terraform", "iac", "infrastructure as code"],
    "Linux":          ["linux", "ubuntu", "centos", "unix", "bash"],
    "SQL":            ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "MongoDB":        ["mongodb", "mongo"],
    "Redis":          ["redis"],
    "Git":            ["git", "github", "gitlab", "bitbucket"],
    "REST API":       ["rest api", "restful", "rest"],
    "GraphQL":        ["graphql"],
    "Microservices":  ["microservices", "microservice"],
    "Agile/Scrum":    ["agile", "scrum", "kanban", "sprint"],
    "System Design":  ["system design", "distributed systems", "architecture"],
    "XGBoost":        ["xgboost", "lightgbm", "gradient boosting"],
    "Apache Spark":   ["apache spark", "pyspark", "spark"],
    "Kafka":          ["kafka", "apache kafka"],
    "Tableau":        ["tableau"],
    "Power BI":       ["power bi", "powerbi"],
    "Flutter":        ["flutter", "dart"],
    "Swift":          ["swift", "swiftui"],
    "Kotlin":         ["kotlin"],
    "Android":        ["android", "android sdk"],
    "iOS":            ["ios", "xcode"],
    "Cybersecurity":  ["cybersecurity", "infosec", "security", "penetration testing"],
}

_SKILL_SECTION = re.compile(
    r"\b(skills|technical skills|core competencies|technologies|tools|expertise|proficiencies)\b",
    re.IGNORECASE,
)
_EXP_SECTION = re.compile(
    r"\b(experience|work history|employment|projects|internship)\b",
    re.IGNORECASE,
)


_NOISE_SKILLS = {
    "analytics", "execution", "innovation", "analysis", "automation",
    "administrative support", "account management", "budgeting",
    "business acumen", "communication", "leadership", "collaboration",
    "problem solving", "problem-solving", "teamwork", "creativity",
    "strategy", "planning", "reporting", "documentation", "presentation",
    "negotiation", "customer service", "time management", "adaptability",
    "critical thinking", "decision making", "mentoring", "training",
    "support", "monitoring", "optimization", "integration", "design",
    "development", "management", "implementation", "maintenance",
}


@lru_cache(maxsize=1)
def _build_master_vocab() -> dict[str, list[str]]:
    """Build unified skill vocabulary from dataset + extra aliases, filtering generic noise words."""
    vocab = {}
    skill_df = _load_skill_df()

    # Collect all unique skills from the dataset
    all_dataset_skills = set()
    for raw in skill_df["skills"].dropna():
        for s in _parse_skills(raw):
            all_dataset_skills.add(s.strip())

    # Build a normalised lookup of EXTRA_ALIASES canonical names (singular, lowercase)
    # so near-duplicate dataset skills (e.g. "REST APIs" vs "REST API") don't double up.
    def _norm(s: str) -> str:
        s = s.lower().strip()
        return s[:-1] if s.endswith("s") and not s.endswith("ss") else s

    extra_norm_names = {_norm(c) for c in EXTRA_ALIASES}

    # For each dataset skill, create a simple alias entry (skip generic noise terms
    # and skip anything that collides with a curated EXTRA_ALIASES entry)
    for skill in all_dataset_skills:
        if len(skill) < 2:
            continue
        if skill.lower().strip() in _NOISE_SKILLS:
            continue
        if _norm(skill) in extra_norm_names:
            continue
        vocab[skill] = [skill.lower()]

    # Overlay our extra aliases (they take precedence for common skills)
    for canonical, aliases in EXTRA_ALIASES.items():
        vocab[canonical] = aliases

    return vocab


def extract_skills(text: str) -> list[dict]:
    """
    Extracts skills from resume text using dataset vocabulary.
    Returns list of dicts: {skill, confidence, in_skills_section, years_exp}
    """
    lower    = text.lower()
    lines    = text.splitlines()
    vocab    = _build_master_vocab()

    # Identify skills-section lines
    skill_lines = set()
    current = None
    for i, line in enumerate(lines):
        if _SKILL_SECTION.search(line):
            current = "skills"
        elif _EXP_SECTION.search(line):
            current = "exp"
        if current == "skills":
            skill_lines.add(i)

    found: dict[str, dict] = {}

    for canonical, aliases in vocab.items():
        best_conf  = 0.0
        in_sec     = False

        for alias in aliases:
            pattern = r"(?<![a-z0-9\-/])" + re.escape(alias) + r"(?![a-z0-9\-/])"
            for m in re.finditer(pattern, lower):
                line_idx = lower[:m.start()].count("\n")
                in_s     = line_idx in skill_lines
                conf     = 0.75 + (0.20 if in_s else 0.0)
                conf     = min(conf, 1.0)
                if conf > best_conf:
                    best_conf = conf
                    in_sec    = in_s

        if best_conf > 0:
            found[canonical] = {
                "skill":             canonical,
                "confidence":        round(best_conf, 2),
                "in_skills_section": in_sec,
                "years_exp":         _years(canonical, text),
            }

    return sorted(found.values(), key=lambda x: (-x["confidence"], x["skill"]))


def _years(skill: str, text: str) -> int | None:
    "3 years of Python experience  → pattern 1 matches → returns 3
"Python (5+ years)             → pattern 2 matches → returns 5""
    
    patterns = [
        rf"(\d+)\+?\s+years?\s+(?:of\s+)?(?:experience\s+(?:in|with)\s+)?{re.escape(skill.lower())}",
        rf"{re.escape(skill.lower())}\s+(?:\w+\s+){{0,3}}(\d+)\+?\s+years?",
    ]
    lower = text.lower()
    for p in patterns:
        m = re.search(p, lower)
        if m:
            return int(m.group(1))
    return None
