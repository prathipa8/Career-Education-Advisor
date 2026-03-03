from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CareerResult:
    recommended_career: str
    match_percentage: int
    justification: str
    scores: Dict[str, int]
    missing_skills: List[str]


# Distinct skill groups avoid heavy overlap and default-cluster bias.
CAREER_CLUSTERS = {
    "Data Analyst": {
        "skills": {
            "sql",
            "excel",
            "tableau",
            "power bi",
            "statistics",
            "data visualization",
            "python",
            "data cleaning",
        },
        "internship_domain": "Data Analytics Intern",
    },
    "Software Developer": {
        "skills": {
            "java",
            "c++",
            "javascript",
            "flask",
            "django",
            "api",
            "git",
            "problem solving",
        },
        "internship_domain": "Software Development Intern",
    },
    "UI/UX Designer": {
        "skills": {
            "figma",
            "wireframing",
            "prototyping",
            "user research",
            "design systems",
            "typography",
            "color theory",
            "usability testing",
        },
        "internship_domain": "UI/UX Design Intern",
    },
    "Digital Marketer": {
        "skills": {
            "seo",
            "content strategy",
            "social media marketing",
            "google analytics",
            "email marketing",
            "ppc",
            "brand storytelling",
            "marketing funnel",
        },
        "internship_domain": "Digital Marketing Intern",
    },
}


def normalize_skills(raw_skills: str) -> List[str]:
    return [skill.strip().lower() for skill in raw_skills.split(",") if skill.strip()]


def _interest_bonus(interests: str, career: str) -> float:
    interest_map = {
        "Data Analyst": ["analysis", "numbers", "insights", "data"],
        "Software Developer": ["coding", "building", "software", "development"],
        "UI/UX Designer": ["design", "creativity", "user experience", "interface"],
        "Digital Marketer": ["marketing", "branding", "campaigns", "growth"],
    }
    text = interests.lower()
    hits = sum(1 for keyword in interest_map[career] if keyword in text)
    return min(hits * 0.05, 0.15)


def recommend_career(profile: dict) -> CareerResult:
    user_skills = set(normalize_skills(profile["skills"]))
    preference = (profile.get("career_preference") or "").strip()
    interests = profile.get("interests", "")

    scores: Dict[str, int] = {}

    for career, data in CAREER_CLUSTERS.items():
        required_skills = data["skills"]
        overlap = len(user_skills & required_skills)

        # Normalized core score: share of required skills matched.
        normalized_score = overlap / len(required_skills)

        # Controlled bonus terms keep scoring balanced across careers.
        cgpa_bonus = min(max((float(profile["cgpa"]) - 6.0) / 4.0, 0), 0.08)
        preference_bonus = 0.08 if preference == career else 0
        interest_bonus = _interest_bonus(interests, career)

        total = min(normalized_score + cgpa_bonus + preference_bonus + interest_bonus, 1.0)
        scores[career] = int(round(total * 100))

    recommended_career = max(scores, key=scores.get)
    match_percentage = scores[recommended_career]
    missing_skills = sorted(CAREER_CLUSTERS[recommended_career]["skills"] - user_skills)

    justification = (
        f"Based on your skills and interests, you are best suited for {recommended_career}."
    )

    return CareerResult(
        recommended_career=recommended_career,
        match_percentage=match_percentage,
        justification=justification,
        scores=scores,
        missing_skills=missing_skills,
    )


def build_suggestions(career: str, missing_skills: List[str]) -> dict:
    focus_topics = missing_skills[:4] if missing_skills else ["portfolio projects"]
    topic_phrase = ", ".join(focus_topics)

    return {
        "coursera": [
            f"Google Career Certificate: Foundations in {career}",
            f"Hands-on {career} Specialization",
            f"Practical Skills Bootcamp: {topic_phrase}",
        ],
        "nptel": [
            f"NPTEL: Core Concepts for {career}",
            f"NPTEL: Applied Learning in {topic_phrase}",
            "NPTEL: Soft Skills and Professional Communication",
        ],
        "youtube": [
            f"Beginner to Advanced tutorials on {topic_phrase}",
            f"Case studies and mini projects for {career}",
            "Interview preparation and resume walkthroughs",
        ],
        "internships": [
            CAREER_CLUSTERS[career]["internship_domain"],
            f"Project-based {career} Trainee",
            "Campus Ambassador / Live Client Project Roles",
        ],
    }


def build_roadmap(missing_skills: List[str], career: str) -> List[dict]:
    fundamentals = ", ".join(missing_skills[:5]) if missing_skills else "advanced practice areas"

    return [
        {
            "month": "Month 1",
            "title": "Learn Missing Fundamentals",
            "description": f"Focus on {fundamentals}. Complete short assessments weekly and build notes.",
        },
        {
            "month": "Month 2",
            "title": "Build 1-2 Projects",
            "description": f"Create 1 mini and 1 capstone project aligned with {career}, then publish your work on GitHub/portfolio.",
        },
        {
            "month": "Month 3",
            "title": "Apply for Internships + Resume Improvement",
            "description": "Refine resume, add measurable project impact, practice interviews, and apply to targeted internships every week.",
        },
    ]
