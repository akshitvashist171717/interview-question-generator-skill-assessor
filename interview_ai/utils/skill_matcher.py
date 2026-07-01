"""utils/skill_matcher.py — Weighted skill matching engine (70% required / 30% preferred)."""


def compute_match(candidate_skills: list[dict], jd_required: list[str], jd_preferred: list[str]) -> dict:
    cand_map  = {s["skill"]: s["confidence"] for s in candidate_skills}
    cand_names = set(cand_map)

    matched_req  = [s for s in jd_required  if s in cand_names]
    missing_req  = [s for s in jd_required  if s not in cand_names]
    matched_pref = [s for s in jd_preferred if s in cand_names]
    missing_pref = [s for s in jd_preferred if s not in cand_names]

    req_score  = round((sum(cand_map.get(s, 0) for s in matched_req)  / max(len(jd_required),  1)) * 100, 1)
    pref_score = round((sum(cand_map.get(s, 0) for s in matched_pref) / max(len(jd_preferred), 1)) * 100, 1)

    if jd_required and jd_preferred:
        overall = round(0.70 * req_score + 0.30 * pref_score, 1)
    elif jd_required:
        overall = req_score
    else:
        overall = pref_score
    overall = min(overall, 100.0)

    miss_ratio = len(missing_req) / max(len(jd_required), 1)
    if overall >= 80 and miss_ratio <= 0.15:
        verdict = "Strong Match"
        verdict_emoji = "✅"
    elif overall >= 60 and miss_ratio <= 0.35:
        verdict = "Good Match"
        verdict_emoji = "🟢"
    elif overall >= 40 and miss_ratio <= 0.55:
        verdict = "Partial Match"
        verdict_emoji = "🟡"
    elif overall >= 20:
        verdict = "Weak Match"
        verdict_emoji = "🟠"
    else:
        verdict = "Poor Match"
        verdict_emoji = "🔴"

    all_jd = set(jd_required) | set(jd_preferred)
    breakdown = (
        [{"skill": s, "category": "Required",  "matched": s in cand_names, "confidence": cand_map.get(s, 0)} for s in jd_required] +
        [{"skill": s, "category": "Preferred", "matched": s in cand_names, "confidence": cand_map.get(s, 0)} for s in jd_preferred]
    )

    return {
        "overall_score":     overall,
        "required_score":    req_score,
        "preferred_score":   pref_score,
        "matched_required":  matched_req,
        "missing_required":  missing_req,
        "matched_preferred": matched_pref,
        "missing_preferred": missing_pref,
        "candidate_extra":   sorted(cand_names - all_jd),
        "verdict":           verdict,
        "verdict_emoji":     verdict_emoji,
        "breakdown":         breakdown,
    }
