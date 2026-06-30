"""utils/jd_analyzer.py — Extracts required/preferred skills from JD text."""
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.skill_extractor import extract_skills, _build_master_vocab

_REQ = re.compile(
    r"\b(require[ds]?|must have|mandatory|essential|minimum|need[s]?|"
    r"strong (background|knowledge|experience) in|you (must|should) have)\b",
    re.IGNORECASE,
)
_PREF = re.compile(
    r"\b(prefer(?:red)?|nice[- ]to[- ]have|bonus|plus|advantage|desirable|"
    r"familiarity with|knowledge of|exposure to|good to have|experience with)\b",
    re.IGNORECASE,
)
_SENIORITY = {
    "Senior":    re.compile(r"\b(senior|sr\.|lead|principal|staff)\b", re.IGNORECASE),
    "Mid-Level": re.compile(r"\b(mid[- ]?level|intermediate)\b",        re.IGNORECASE),
    "Junior":    re.compile(r"\b(junior|jr\.|entry[- ]?level|fresher)\b", re.IGNORECASE),
    "Intern":    re.compile(r"\b(intern|internship|trainee)\b",           re.IGNORECASE),
}


def analyze_jd(jd_text: str) -> dict:
    lower = jd_text.lower()
    lines = jd_text.splitlines()

    required:  set[str] = set()
    preferred: set[str] = set()

    # Segment-aware extraction
    segments = _segment(lines)
    for seg_type, seg_text in segments:
        matched = _match_skills_from_text(seg_text)
        if seg_type == "required":
            required.update(matched)
        elif seg_type == "preferred":
            preferred.update(matched)
        else:
            for skill in matched:
                ctx = _context(skill, seg_text)
                if ctx == "preferred":
                    preferred.add(skill)
                else:
                    required.add(skill)

    preferred -= required

    return {
        "required_skills":  sorted(required),
        "preferred_skills": sorted(preferred),
        "all_skills":       sorted(required | preferred),
        "seniority":        _seniority(jd_text),
        "years_required":   _years(jd_text),
        "responsibilities": _responsibilities(lines),
    }


def _segment(lines):
    segs, cur_type, cur = [], "body", []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        # Only treat short, header-like lines as section switches
        is_header_like = len(s) < 60 and (s.endswith(":") or s.istitle() or s.isupper())

        if _REQ.search(s) and (is_header_like or len(s) < 50):
            if cur: segs.append((cur_type, " ".join(cur)))
            cur_type, cur = "required", [s]
        elif _PREF.search(s) and (is_header_like or len(s) < 50):
            if cur: segs.append((cur_type, " ".join(cur)))
            cur_type, cur = "preferred", [s]
        else:
            cur.append(s)
    if cur:
        segs.append((cur_type, " ".join(cur)))
    return segs


def _match_skills_from_text(text: str) -> list[str]:
    lower  = text.lower()
    vocab  = _build_master_vocab()
    found  = []
    for canonical, aliases in vocab.items():
        for alias in aliases:
            pat = r"(?<![a-z0-9\-/])" + re.escape(alias) + r"(?![a-z0-9\-/])"
            if re.search(pat, lower):
                found.append(canonical)
                break
    return found


def _context(skill: str, text: str) -> str:
    lower = text.lower()
    vocab = _build_master_vocab()
    for alias in vocab.get(skill, [skill.lower()]):
        m = re.search(re.escape(alias), lower)
        if m:
            # Narrow window: only the immediate ~40 chars before the skill mention
            window = lower[max(0, m.start()-40): m.start()]
            if _PREF.search(window):
                return "preferred"
            if _REQ.search(window):
                return "required"
    return "neutral"


def _seniority(text):
    for label, pat in _SENIORITY.items():
        if pat.search(text):
            return label
    return "Mid-Level"


def _years(text):
    for p in [r"(\d+)\+?\s+years?\s+of\s+(?:relevant\s+)?experience",
              r"minimum\s+(?:of\s+)?(\d+)\+?\s+years?",
              r"at\s+least\s+(\d+)\+?\s+years?"]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def _responsibilities(lines):
    bullets = []
    for line in lines:
        s = line.strip()
        if s.startswith(("•", "-", "*", "–", "·")):
            clean = re.sub(r"^[•\-*–·]\s*", "", s).strip()
            if 10 < len(clean) < 200:
                bullets.append(clean)
    return bullets[:6]
