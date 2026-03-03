from flask import Blueprint, redirect, render_template, request, session, url_for

from app.models.database import save_student_profile
from app.services.career_service import (
    CAREER_CLUSTERS,
    build_roadmap,
    build_suggestions,
    normalize_skills,
    recommend_career,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def profile_input():
    if request.method == "POST":
        profile = {
            "name": request.form["name"].strip(),
            "department": request.form["department"].strip(),
            "cgpa": float(request.form["cgpa"]),
            "skills": request.form["skills"].strip(),
            "interests": request.form["interests"].strip(),
            "career_preference": request.form.get("career_preference", "").strip(),
        }

        student_id = save_student_profile(profile)
        result = recommend_career(profile)

        session["student_id"] = student_id
        session["profile"] = profile
        session["recommendation"] = {
            "recommended_career": result.recommended_career,
            "match_percentage": result.match_percentage,
            "justification": result.justification,
            "scores": result.scores,
            "missing_skills": result.missing_skills,
        }

        return redirect(url_for("main.recommendation"))

    return render_template(
        "profile_input.html",
        career_options=list(CAREER_CLUSTERS.keys()),
        current_step=1,
        page_theme="theme-profile",
    )


@main_bp.route("/recommendation")
def recommendation():
    recommendation_data = session.get("recommendation")
    if not recommendation_data:
        return redirect(url_for("main.profile_input"))

    return render_template(
        "recommendation.html",
        recommendation=recommendation_data,
        current_step=2,
        page_theme="theme-recommendation",
    )


@main_bp.route("/skill-gap")
def skill_gap():
    profile = session.get("profile")
    recommendation_data = session.get("recommendation")
    if not profile or not recommendation_data:
        return redirect(url_for("main.profile_input"))

    career = recommendation_data["recommended_career"]
    required = sorted(CAREER_CLUSTERS[career]["skills"])
    user_skills = normalize_skills(profile["skills"])
    missing = recommendation_data["missing_skills"]

    return render_template(
        "skill_gap.html",
        career=career,
        required_skills=required,
        user_skills=user_skills,
        missing_skills=missing,
        current_step=3,
        page_theme="theme-skill-gap",
    )


@main_bp.route("/suggestions")
def suggestions():
    recommendation_data = session.get("recommendation")
    if not recommendation_data:
        return redirect(url_for("main.profile_input"))

    career = recommendation_data["recommended_career"]
    missing = recommendation_data["missing_skills"]
    suggestion_data = build_suggestions(career, missing)

    return render_template(
        "suggestions.html",
        career=career,
        missing_skills=missing,
        suggestions=suggestion_data,
        current_step=4,
        page_theme="theme-suggestions",
    )


@main_bp.route("/roadmap")
def roadmap():
    recommendation_data = session.get("recommendation")
    if not recommendation_data:
        return redirect(url_for("main.profile_input"))

    career = recommendation_data["recommended_career"]
    missing = recommendation_data["missing_skills"]
    roadmap_data = build_roadmap(missing, career)

    return render_template(
        "roadmap.html",
        career=career,
        roadmap=roadmap_data,
        current_step=5,
        page_theme="theme-roadmap",
    )
