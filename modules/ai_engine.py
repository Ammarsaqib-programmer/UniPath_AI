"""
UniPathAi — AI Counsellor Bridge
==================================
Connects app.py to Azmatullah's RAG/Agentic AI module (main.UniPathAI).

If that backend (main.py + agents/ + rag/ + llm/ + prompts/ +
config.py + knowledge_base/) is present in the project root, it is
used for real, grounded answers. If it isn't available yet (e.g.
not merged into this folder), these functions fall back to a
simple templated response so the UI never crashes while the team
finishes integration.
"""

from typing import Any, Dict

_ai_instance = None
_ai_available = True
_import_error = None

try:
    from main import UniPathAI
except Exception as e:
    _ai_available = False
    _import_error = f"import error: {e}"
    print(f"[ai_engine] Failed to import UniPathAI: {e}")


def _get_ai():
    global _ai_instance, _import_error
    if _ai_instance is None and _ai_available:
        try:
            _ai_instance = UniPathAI()
        except Exception as e:
            _ai_instance = None
            _import_error = f"init error: {e}"
            print(f"[ai_engine] Failed to initialize UniPathAI: {e}")
    return _ai_instance


def _map_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Translate app.py's profile shape into Azmatullah's expected schema."""
    countries = profile.get("preferred_countries") or []
    return {
        "cgpa": profile.get("cgpa"),
        "field_of_study": profile.get("field"),
        "preferred_country": countries[0] if countries else None,
        "budget_usd": profile.get("budget_usd"),
        "ielts_score": profile.get("ielts"),
        "interested_in_part_time_work": True,
    }


def generate_explanation(profile: Dict[str, Any], university: Dict[str, Any]) -> str:
    """Used by the 'Ask the AI counsellor about this one' button on each card."""
    ai = _get_ai()
    if ai:
        try:
            context = (
                f"University: {university.get('university')}\n"
                f"Program: {university.get('program')}\n"
                f"Country: {university.get('country')}\n"
                f"City: {university.get('city')}\n"
                f"Tuition (USD/year): {university.get('tuition_usd_yearly')}\n"
                f"Minimum CGPA required: {university.get('min_cgpa')}\n"
                f"Minimum IELTS required: {university.get('ielts_min')}\n"
                f"Scholarship available: {university.get('scholarship_available')}\n"
                f"Scholarship details: {university.get('scholarship_details')}\n"
                f"Application deadline: {university.get('application_deadline')}\n"
                f"Accommodation available: {university.get('accommodation_available')}\n"
                f"Part-time work allowed: {university.get('part_time_work')}\n"
                f"Match score for this student: {university.get('match_score')}\n"
            )
            profile_map = _map_profile(profile)
            profile_text = "\n".join(
                f"- {k}: {v}" for k, v in profile_map.items() if v not in (None, "", [])
            )
            system_prompt = (
                "You are UniPathAi's admissions counsellor. Answer using ONLY the "
                "UNIVERSITY DATA given below as ground truth — do not say the "
                "information is unavailable, since it is provided directly here."
            )
            user_prompt = (
                f"STUDENT PROFILE:\n{profile_text or '(not provided)'}\n\n"
                f"UNIVERSITY DATA:\n{context}\n\n"
                "Briefly explain why this university/program is a good match for "
                "this student. Mention eligibility (CGPA/IELTS), scholarship, "
                "budget fit, and the application deadline."
            )
            # Call the LLM directly (bypassing ai.chat()'s RAG-only grounding)
            # since we already have the exact row data — no retrieval needed.
            answer = ai.llm.chat(system_prompt, user_prompt)
            return answer
        except Exception as e:
            return f"(AI counsellor hit an error, showing a basic summary instead: {e})"

    reasons = university.get("match_reasons") or []
    return (
        f"{university.get('university')} is a {university.get('match_score')}% match "
        f"based on your CGPA, budget and preferences. " + " ".join(reasons)
    )


def chat_with_advisor(profile: Dict[str, Any], query: str) -> str:
    """Used by the free-form 'AI counsellor' chat page."""
    ai = _get_ai()
    if ai:
        try:
            result = ai.chat(query, _map_profile(profile))
            return result["answer"]
        except Exception as e:
            return f"Sorry, the AI counsellor hit an error: {e}"

    return (
        "The AI counsellor backend isn't connected in this environment yet — "
        "once Azmatullah's RAG module is merged into this project, I'll answer "
        "this using the verified knowledge base."
        + (f"\n\n(debug: {_import_error})" if _import_error else "")
    )
