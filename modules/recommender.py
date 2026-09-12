"""
UniPathAi — Recommendation / Matching Engine
==============================================
Hassan's module. Scores and ranks universities against a student
profile from app.py's "Applicant profile" form.

Fix: field/level/country/scholarship are treated as *soft* factors
first. We only apply them as hard filters if doing so still leaves
at least one result — otherwise we progressively relax filters so
the student never sees "no eligible universities" purely because
the dataset is thin for their exact combination.
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


def _field_level_score(row, profile) -> float:
    score = 100.0
    if profile.get("field") and row.get("field") != profile["field"]:
        score -= 40
    if profile.get("level") and row.get("level") != profile["level"]:
        score -= 40
    return max(0.0, score)


def _apply_hard_filters(df: pd.DataFrame, profile: Dict[str, Any],
                         use_field: bool, use_level: bool,
                         use_country: bool, use_scholarship: bool) -> pd.DataFrame:
    view = df.copy()
    if use_field and profile.get("field"):
        view = view[view["field"] == profile["field"]]
    if use_level and profile.get("level"):
        view = view[view["level"] == profile["level"]]
    if use_country and profile.get("preferred_countries"):
        view = view[view["country"].isin(profile["preferred_countries"])]
    if use_scholarship and profile.get("needs_scholarship"):
        view = view[view["scholarship_available"] == "Yes"]
    return view


def recommend_universities(profile: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    attempts = [
        dict(use_field=True, use_level=True, use_country=True, use_scholarship=True),
        dict(use_field=True, use_level=True, use_country=True, use_scholarship=False),
        dict(use_field=True, use_level=True, use_country=False, use_scholarship=False),
        dict(use_field=True, use_level=False, use_country=False, use_scholarship=False),
        dict(use_field=False, use_level=False, use_country=False, use_scholarship=False),
    ]

    view = df.iloc[0:0]
    relaxed_note = None
    for i, flags in enumerate(attempts):
        candidate = _apply_hard_filters(df, profile, **flags)
        if not candidate.empty:
            view = candidate
            if i > 0:
                relaxed_note = (
                    "Showing close alternatives — no exact match for every "
                    "preference, so some filters were relaxed."
                )
            break

    if view.empty:
        empty = df.iloc[0:0].copy()
        empty["match_score"] = []
        empty["match_reasons"] = []
        return empty

    scores = []
    reasons_list = []
    for _, row in view.iterrows():
        budget_s = _budget_score(row.get("tuition_usd_yearly"), profile.get("budget_usd", 0))
        cgpa_s = _cgpa_score(row.get("min_cgpa"), profile.get("cgpa", 0))
        ielts_s = _ielts_score(row.get("ielts_min"), profile.get("ielts", 0))
        fl_s = _field_level_score(row, profile)
        total = round(budget_s * 0.3 + cgpa_s * 0.3 + ielts_s * 0.15 + fl_s * 0.25)
        scores.append(int(total))

        reasons = []
        if relaxed_note and (row.get("field") != profile.get("field")
                              or row.get("level") != profile.get("level")):
            reasons.append(
                f"Closest available match ({row.get('field')}, {row.get('level')}) "
                f"for your requested {profile.get('field')} / {profile.get('level')}"
            )
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
