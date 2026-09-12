"""
UniPathAi — Recommendation / Matching Engine
==============================================
Hassan's module. Scores and ranks universities against a student
profile from app.py's "Applicant profile" form.

recommend_universities(profile, df) -> pd.DataFrame
    Same columns as `df`, filtered to the profile's field/level
    (and country/scholarship if requested), plus two new columns:
      - match_score:   int 0-100
      - match_reasons: list[str] (human-readable, shown in the UI)
"""

from typing import Any, Dict

import pandas as pd


def _budget_score(tuition, budget) -> float:
    try:
        tuition = float(tuition)
        budget = float(budget)
    except (TypeError, ValueError):
        return 50.0
    if budget <= 0:
        return 50.0
    if tuition <= budget:
        return 100.0
    over_ratio = (tuition - budget) / budget
    return max(0.0, 100.0 - over_ratio * 100)


def _cgpa_score(min_cgpa, cgpa) -> float:
    try:
        min_cgpa = float(min_cgpa)
        cgpa = float(cgpa)
    except (TypeError, ValueError):
        return 70.0
    if cgpa >= min_cgpa:
        return 100.0
    gap = min_cgpa - cgpa
    return max(0.0, 100.0 - gap * 100)


def _ielts_score(ielts_min, ielts) -> float:
    try:
        ielts_min = float(ielts_min)
    except (TypeError, ValueError):
        return 100.0
    if ielts_min <= 0:
        return 100.0
    try:
        ielts = float(ielts)
    except (TypeError, ValueError):
        ielts = 0.0
    if ielts >= ielts_min:
        return 100.0
    return max(0.0, 100.0 - (ielts_min - ielts) * 20)


def recommend_universities(profile: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    view = df.copy()

    if profile.get("field"):
        view = view[view["field"] == profile["field"]]
    if profile.get("level"):
        view = view[view["level"] == profile["level"]]
    if profile.get("preferred_countries"):
        view = view[view["country"].isin(profile["preferred_countries"])]
    if profile.get("needs_scholarship"):
        view = view[view["scholarship_available"] == "Yes"]

    if view.empty:
        empty = view.copy()
        empty["match_score"] = []
        empty["match_reasons"] = []
        return empty

    scores = []
    reasons_list = []
    for _, row in view.iterrows():
        budget_s = _budget_score(row.get("tuition_usd_yearly"), profile.get("budget_usd", 0))
        cgpa_s = _cgpa_score(row.get("min_cgpa"), profile.get("cgpa", 0))
        ielts_s = _ielts_score(row.get("ielts_min"), profile.get("ielts", 0))
        total = round(budget_s * 0.4 + cgpa_s * 0.4 + ielts_s * 0.2)
        scores.append(int(total))

        reasons = []
        try:
            tuition = float(row.get("tuition_usd_yearly", 0))
            budget = float(profile.get("budget_usd", 0))
            if tuition <= budget:
                reasons.append(f"Tuition (${int(tuition):,}/yr) fits your budget")
            else:
                reasons.append(f"Tuition (${int(tuition):,}/yr) is above your stated budget")
        except (TypeError, ValueError):
            pass

        try:
            min_cgpa = float(row.get("min_cgpa"))
            cgpa = float(profile.get("cgpa", 0))
            if cgpa >= min_cgpa:
                reasons.append(f"Your CGPA ({cgpa}) meets the {min_cgpa} requirement")
            else:
                reasons.append(f"Your CGPA ({cgpa}) is below the {min_cgpa} requirement")
        except (TypeError, ValueError):
            pass

        if row.get("scholarship_available") == "Yes":
            reasons.append("Scholarship opportunities available")
        if profile.get("preferred_countries") and row.get("country") in profile["preferred_countries"]:
            reasons.append(f"Located in your preferred country: {row['country']}")

        reasons_list.append(reasons)

    view = view.assign(match_score=scores, match_reasons=reasons_list)
    view = view.sort_values("match_score", ascending=False).reset_index(drop=True)
    return view