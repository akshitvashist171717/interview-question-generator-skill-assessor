"""utils/gemini_client.py — Gemini 2.0 Flash for question gen + answer evaluation."""
import os, json, re

# ── Fallback question bank ────────────────────────────────────────────────────
FALLBACK_BANK = {
    "Python": [
        {"q": "Explain the difference between a list, tuple, and set in Python.", "diff": "Easy",   "type": "Conceptual"},
        {"q": "What are Python decorators and how would you implement one from scratch?", "diff": "Medium", "type": "Conceptual"},
        {"q": "Describe Python's GIL and how it affects multithreaded programs.", "diff": "Hard",   "type": "Conceptual"},
        {"q": "Write a function to find all duplicates in a list in O(n) time.", "diff": "Medium",  "type": "Coding"},
        {"q": "Explain generators vs regular functions. When would you prefer a generator?", "diff": "Medium", "type": "Conceptual"},
    ],
    "Machine Learning": [
        {"q": "What is the bias-variance tradeoff and why does it matter?", "diff": "Medium", "type": "Conceptual"},
        {"q": "Explain the difference between L1 and L2 regularization.", "diff": "Medium", "type": "Conceptual"},
        {"q": "How would you handle severe class imbalance in a classification problem?", "diff": "Medium", "type": "Scenario"},
        {"q": "Explain how Random Forest reduces overfitting compared to a single Decision Tree.", "diff": "Medium", "type": "Conceptual"},
        {"q": "Walk me through your approach to feature selection for a predictive model.", "diff": "Hard", "type": "Scenario"},
    ],
    "SQL": [
        {"q": "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?", "diff": "Easy",   "type": "Conceptual"},
        {"q": "Write a query to find the second highest salary in an employee table.", "diff": "Medium", "type": "Coding"},
        {"q": "Explain window functions with a real-world use case.", "diff": "Hard",   "type": "Conceptual"},
        {"q": "How do database indexes work and when should you avoid them?", "diff": "Medium", "type": "Conceptual"},
    ],
    "System Design": [
        {"q": "Design a URL shortener service like bit.ly. Walk through your architecture.", "diff": "Hard", "type": "Design"},
        {"q": "How would you design a notification system handling 1M messages/day?", "diff": "Hard", "type": "Design"},
        {"q": "Explain the CAP theorem and its practical implications.", "diff": "Hard", "type": "Conceptual"},
        {"q": "What is the difference between horizontal and vertical scaling?", "diff": "Easy", "type": "Conceptual"},
    ],
    "JavaScript": [
        {"q": "Explain event delegation and why it's useful.", "diff": "Medium", "type": "Conceptual"},
        {"q": "What is the difference between == and === in JavaScript?", "diff": "Easy", "type": "Conceptual"},
        {"q": "Explain closures with a practical example.", "diff": "Medium", "type": "Conceptual"},
        {"q": "What is the event loop and how does async/await work under the hood?", "diff": "Hard", "type": "Conceptual"},
    ],
    "Docker": [
        {"q": "What is the difference between a Docker image and a container?", "diff": "Easy", "type": "Conceptual"},
        {"q": "Explain multi-stage Docker builds and their advantages.", "diff": "Hard", "type": "Conceptual"},
        {"q": "How does Docker networking work? Explain bridge and overlay networks.", "diff": "Hard", "type": "Conceptual"},
    ],
    "AWS": [
        {"q": "Explain the difference between EC2, ECS, and Lambda.", "diff": "Medium", "type": "Conceptual"},
        {"q": "How would you design a fault-tolerant web application on AWS?", "diff": "Hard", "type": "Design"},
        {"q": "What is IAM and how do you manage permissions securely?", "diff": "Medium", "type": "Conceptual"},
    ],
    "React": [
        {"q": "Explain the difference between props and state in React.", "diff": "Easy",   "type": "Conceptual"},
        {"q": "What are React hooks? Explain useState and useEffect with examples.", "diff": "Medium", "type": "Conceptual"},
        {"q": "Explain the Context API and when you'd use it over Redux.", "diff": "Hard",  "type": "Conceptual"},
    ],
    "CI/CD": [
        {"q": "What is the difference between Continuous Integration, Delivery, and Deployment?", "diff": "Easy", "type": "Conceptual"},
        {"q": "Describe how you would set up a CI/CD pipeline from scratch for a microservice.", "diff": "Hard", "type": "Scenario"},
    ],
    "Kubernetes": [
        {"q": "Explain the difference between a Pod, Deployment, and Service in Kubernetes.", "diff": "Medium", "type": "Conceptual"},
        {"q": "How does Kubernetes handle auto-scaling? Explain HPA and VPA.", "diff": "Hard", "type": "Conceptual"},
    ],
}

BEHAVIORAL = [
    {"q": "Tell me about yourself and your motivation for this role.", "diff": "Easy", "type": "Behavioral", "skill": "General"},
    {"q": "Describe the most challenging project you've worked on and how you handled obstacles.", "diff": "Medium", "type": "Behavioral", "skill": "General"},
    {"q": "Where do you see yourself in 3–5 years?", "diff": "Easy", "type": "Behavioral", "skill": "General"},
    {"q": "How do you stay current with developments in your field?", "diff": "Easy", "type": "Behavioral", "skill": "General"},
    {"q": "Describe a time you failed at something and what you learned.", "diff": "Medium", "type": "Behavioral", "skill": "General"},
]


def _client():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=key)
    except Exception:
        return None


def _call(prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str | None:
    c = _client()
    if not c:
        return None
    try:
        from google.genai import types
        r = c.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens, temperature=temperature),
        )
        return r.text
    except Exception as e:
        print(f"[Gemini] {e}")
        return None


def generate_questions(role: str, matched_skills: list[str], missing_skills: list[str],
                       jd_text: str, n: int = 10) -> list[dict]:
    if _client():
        qs = _gemini_questions(role, matched_skills, missing_skills, jd_text, n)
        if qs:
            return qs
    return _fallback_questions(matched_skills, n)


def _gemini_questions(role, matched, missing, jd_text, n) -> list[dict] | None:
    skills_str  = ", ".join(matched[:12]) if matched else "general software skills"
    missing_str = ", ".join(missing[:5])  if missing else "none"
    jd_snip     = jd_text[:500].strip()

    easy = max(1, round(n * 0.2))
    hard = max(1, round(n * 0.3))
    medium = max(1, n - easy - hard)
    import time
    seed = time.time_ns() % 1000000

    prompt = f"""You are a senior technical recruiter generating interview questions for a {role} candidate.
[Request Seed: {seed}]

Candidate matched skills: {skills_str}
Candidate skill gaps: {missing_str}
Job description excerpt: {jd_snip}

Generate exactly {n} interview questions.
Mix: Easy({easy}), Medium({medium}), Hard({hard}). Types: Conceptual, Coding, Scenario, Design, Behavioral.
Include 1-2 questions on gap skills. Make questions specific and role-relevant.
Ensure the questions are unique, creative, and cover different facets of the skills. Do not repeat the same questions.

Return ONLY valid JSON array, no markdown:
[{{"q":"<question>","diff":"Easy|Medium|Hard","type":"Conceptual|Coding|Scenario|Design|Behavioral","skill":"<primary skill>"}}]"""

    raw = _call(prompt, temperature=0.85)
    if not raw:
        return None
    return _parse_list(raw)


def generate_questions_from_jd_resume(role: str, jd_text: str, resume_text: str,
                                      matched_skills: list[str] | None = None,
                                      n: int = 10) -> list[dict]:
    """Generate questions directly from JD + resume text (no skill-matching step).
    Falls back to the same skill-based fallback bank if Gemini is unavailable."""
    if _client():
        qs = _gemini_questions_from_jd_resume(role, jd_text, resume_text, n)
        if qs:
            return qs
    return _fallback_questions(matched_skills or [], n)


def _gemini_questions_from_jd_resume(role, jd_text, resume_text, n) -> list[dict] | None:
    jd_snip     = (jd_text or "")[:1500].strip()
    resume_snip = (resume_text or "")[:1500].strip()

    easy = max(1, round(n * 0.2))
    hard = max(1, round(n * 0.3))
    medium = max(1, n - easy - hard)
    import time
    seed = time.time_ns() % 1000000

    prompt = f"""You are a senior technical recruiter generating interview questions by
comparing a candidate's resume against a job description for a {role} role.
[Request Seed: {seed}]

Job Description:
{jd_snip}

Candidate Resume:
{resume_snip}

Generate exactly {n} interview questions tailored to this specific candidate and this
specific job description. Base the questions on:
- Skills, tools, and responsibilities mentioned in the JD
- Projects, experience, and skills mentioned in the resume
- Gaps between the resume and the JD (probe these areas)
- Specific claims in the resume worth verifying in depth

Mix: Easy({easy}), Medium({medium}), Hard({hard}). Types: Conceptual, Coding, Scenario, Design, Behavioral.
Ensure the questions are unique, creative, and cover different facets of the skills. Do not repeat the same questions.

Return ONLY valid JSON array, no markdown:
[{{"q":"<question>","diff":"Easy|Medium|Hard","type":"Conceptual|Coding|Scenario|Design|Behavioral","skill":"<primary skill or topic>"}}]"""

    raw = _call(prompt, temperature=0.85)
    if not raw:
        return None
    return _parse_list(raw)


def generate_questions_from_resume_only(role: str, resume_text: str,
                                        matched_skills: list[str] | None = None,
                                        n: int = 10) -> list[dict]:
    """Generate questions based solely on the candidate's resume (no JD used).
    Falls back to the skill-based fallback bank if Gemini is unavailable."""
    if _client():
        qs = _gemini_questions_from_resume_only(role, resume_text, n)
        if qs:
            return qs
    return _fallback_questions(matched_skills or [], n)


def _gemini_questions_from_resume_only(role, resume_text, n) -> list[dict] | None:
    resume_snip = (resume_text or "")[:2000].strip()
    if not resume_snip:
        return None

    easy = max(1, round(n * 0.2))
    hard = max(1, round(n * 0.3))
    medium = max(1, n - easy - hard)
    import time
    seed = time.time_ns() % 1000000

    prompt = f"""You are a senior technical recruiter generating interview questions based
ONLY on a candidate's resume for a {role} role. Do not assume or reference any specific
job description — base every question purely on what appears in the resume below.
[Request Seed: {seed}]

Candidate Resume:
{resume_snip}

Generate exactly {n} interview questions that probe the candidate's own claimed skills,
projects, tools, and experience as described in the resume. Dig into specifics (e.g. ask
them to elaborate on a listed project or technology) rather than asking generic questions.

Mix: Easy({easy}), Medium({medium}), Hard({hard}). Types: Conceptual, Coding, Scenario, Design, Behavioral.
Ensure the questions are unique, creative, and cover different facets of the skills. Do not repeat the same questions.

Return ONLY valid JSON array, no markdown:
[{{"q":"<question>","diff":"Easy|Medium|Hard","type":"Conceptual|Coding|Scenario|Design|Behavioral","skill":"<primary skill or topic>"}}]"""

    raw = _call(prompt, temperature=0.85)
    if not raw:
        return None
    return _parse_list(raw)


def generate_questions_from_jd_only(role: str, jd_text: str,
                                    matched_skills: list[str] | None = None,
                                    n: int = 10) -> list[dict]:
    """Generate questions based solely on the job description (no resume used).
    Falls back to the skill-based fallback bank if Gemini is unavailable."""
    if _client():
        qs = _gemini_questions_from_jd_only(role, jd_text, n)
        if qs:
            return qs
    return _fallback_questions(matched_skills or [], n)


def _gemini_questions_from_jd_only(role, jd_text, n) -> list[dict] | None:
    jd_snip = (jd_text or "")[:2000].strip()
    if not jd_snip:
        return None

    easy = max(1, round(n * 0.2))
    hard = max(1, round(n * 0.3))
    medium = max(1, n - easy - hard)
    import time
    seed = time.time_ns() % 1000000

    prompt = f"""You are a senior technical recruiter generating interview questions based
ONLY on a job description for a {role} role. Do not assume or reference any specific
candidate resume — base every question purely on the requirements below.
[Request Seed: {seed}]

Job Description:
{jd_snip}

Generate exactly {n} interview questions that probe the skills, tools, responsibilities,
and requirements called out in this job description, so that any qualified candidate for
this role could be assessed fairly against it.

Mix: Easy({easy}), Medium({medium}), Hard({hard}). Types: Conceptual, Coding, Scenario, Design, Behavioral.
Ensure the questions are unique, creative, and cover different facets of the requirements. Do not repeat the same questions.

Return ONLY valid JSON array, no markdown:
[{{"q":"<question>","diff":"Easy|Medium|Hard","type":"Conceptual|Coding|Scenario|Design|Behavioral","skill":"<primary skill or topic>"}}]"""

    raw = _call(prompt, temperature=0.85)
    if not raw:
        return None
    return _parse_list(raw)


def _fallback_questions(matched: list[str], n: int) -> list[dict]:
    qs, seen = [], set()
    for skill in matched:
        if skill in FALLBACK_BANK:
            for q in FALLBACK_BANK[skill]:
                if q["q"] not in seen:
                    qs.append({**q, "skill": skill})
                    seen.add(q["q"])
    for q in BEHAVIORAL:
        if q["q"] not in seen:
            qs.append(q)
            seen.add(q["q"])
    
    # Pad with other skills if we have fewer than n questions
    if len(qs) < n:
        for skill, questions in FALLBACK_BANK.items():
            if skill not in matched:
                for q in questions:
                    if q["q"] not in seen:
                        qs.append({**q, "skill": skill})
                        seen.add(q["q"])
                    if len(qs) >= n:
                        break
            if len(qs) >= n:
                break
    
    import random
    random.shuffle(qs)
    return qs[:n]


def evaluate_answer(question: str, answer: str, skill: str, difficulty: str, role: str) -> dict:
    if _client() and answer.strip():
        r = _gemini_eval(question, answer, skill, difficulty, role)
        if r:
            return r
    return _heuristic_eval(answer)


def _gemini_eval(question, answer, skill, difficulty, role) -> dict | None:
    prompt = f"""You are an expert technical interviewer evaluating a {role} candidate.

Question ({difficulty} | {skill}): {question}

Candidate Answer: {answer}

Evaluate on 0-10 scale. Return ONLY valid JSON, no markdown:
{{"score":<0-10>,"grade":"A|B|C|D|F","feedback":"<2-3 sentence assessment>","strengths":["<s1>","<s2>"],"improvements":["<i1>","<i2>"],"keywords_hit":["<kw1>","<kw2>"]}}

Rubric: 9-10=A(exceptional), 7-8=B(strong), 5-6=C(adequate), 3-4=D(weak), 0-2=F(incorrect)"""

    raw = _call(prompt, 600, temperature=0.2)
    if not raw:
        return None
    result = _parse_dict(raw)
    if result:
        s = result.get("score", 0)
        if not result.get("grade"):
            result["grade"] = "A" if s>=9 else "B" if s>=7 else "C" if s>=5 else "D" if s>=3 else "F"
    return result


def _heuristic_eval(answer: str) -> dict:
    if not answer or len(answer.strip()) < 10:
        return {"score": 0, "grade": "F", "feedback": "No answer provided.",
                "strengths": [], "improvements": ["Please provide a detailed answer."], "keywords_hit": []}
    words = len(answer.split())
    score = min(int(words / 20 * 5) + 2, 7)
    grade = "A" if score>=9 else "B" if score>=7 else "C" if score>=5 else "D" if score>=3 else "F"
    return {
        "score": score, "grade": grade,
        "feedback": "Basic evaluation (no Gemini key). Add API key in Settings for AI feedback.",
        "strengths": ["Answer provided"] if score > 2 else [],
        "improvements": ["Add Gemini API key in Settings for detailed AI evaluation."],
        "keywords_hit": [],
    }


def _parse_list(raw: str) -> list[dict] | None:
    try:
        clean = re.sub(r"```(?:json)?", "", raw).strip()
        s, e  = clean.find("["), clean.rfind("]") + 1
        return json.loads(clean[s:e]) if s != -1 and e > 0 else None
    except Exception:
        return None


def _parse_dict(raw: str) -> dict | None:
    try:
        clean = re.sub(r"```(?:json)?", "", raw).strip()
        s, e  = clean.find("{"), clean.rfind("}") + 1
        return json.loads(clean[s:e]) if s != -1 and e > 0 else None
    except Exception:
        return None
