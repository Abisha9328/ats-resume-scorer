import re

def extract_skills_from_text(text: str) -> set:
    # List of common tech skills (you can expand this list)
    known_skills = [
        "python", "java", "flask", "django", "sql", "mysql", "postgresql",
        "rest", "rest apis", "html", "css", "javascript", "react", "docker",
        "git", "aws", "azure", "linux", "bash", "kubernetes"
    ]

    text = text.lower()
    found_skills = set()

    for skill in known_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found_skills.add(skill)

    return found_skills


def get_skill_match_score(resume_skills: set, jd_skills: set) -> tuple:
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    score = len(matched) / len(jd_skills) * 100 if jd_skills else 0
    return round(score, 2), matched, missing
