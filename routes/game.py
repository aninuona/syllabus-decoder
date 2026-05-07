import random
from flask import Blueprint, jsonify, request
from models import db, SyllabusEntry

game_bp = Blueprint("game", __name__)


def explain_difference(category, user_answer, correct_answer, policy_text):
    """
    Generate a natural language explanation for why a classification might be confused.
    Based on keywords and patterns in the policy text.
    """
    text_lower = policy_text.lower()
    
    if category == "t_tier":
        explanations = {
            ("T0", "T1"): "This policy is restrictive but allows some exceptions. You may have missed language like 'except for' or 'only when' that permit use in specific cases.",
            ("T0", "T2"): "This policy prohibits AI by default but allows case-by-case approval. You may have overlooked permission-gating language.",
            ("T1", "T0"): "This policy allows exceptions, which is more permissive than a total ban. Look for conditional language permitting AI use.",
            ("T1", "T2"): "Both require permission, but T1 defaults to no unless stated. This policy may use softer language like 'ask first' rather than implied prohibition.",
            ("T1", "T3"): "This policy allows bounded uses (like brainstorming), not just exceptions. Phrases like 'for outlining' or 'to start your research' indicate T3.",
            ("T2", "T3"): "This policy allows specific bounded uses without requiring approval. You may have missed phrases like 'can be used for brainstorming' or 'limited support.'",
            ("T2", "T4"): "This policy allows AI if documented, not just with approval. Look for 'cite if used' or 'must disclose' language.",
            ("T3", "T4"): "This policy requires documentation/citation. You correctly identified it allows AI, but missed the documentation requirement moves it higher.",
            ("T4", "T5"): "This policy is permissive but not encouraged. T5 policies actively welcome or require AI use; T4 just allows it with disclosure.",
            ("T5", "T4"): "This policy encourages AI use. Look for words like 'encouraged,' 'welcomed,' or 'recommended'—more than just allowing with documentation.",
        }
        key = (user_answer, correct_answer)
        if key in explanations:
            return explanations[key]
        return f"You predicted {user_answer} but the database classifies this as {correct_answer}. Review the specific language in the policy to understand the permissiveness level."
    
    elif category == "c_level":
        explanations = {
            ("C0", "C1"): "This policy requires some mention of AI use. Look for phrases like 'note if used' or 'acknowledge AI assistance'—even if no specific citation format.",
            ("C0", "C2"): "This policy requires formal documentation or structured citation of AI use, not just a note.",
            ("C0", "C3"): "This policy requires detailed logs or transcripts of AI interactions, not just citation.",
            ("C1", "C0"): "You may have seen acknowledgment language, but this policy doesn't actually require disclosure. Check if the mention is optional or aspirational.",
            ("C1", "C2"): "This policy requires more formal documentation. Look for citation format language (APA, MLA) or specific attribution requirements.",
            ("C1", "C3"): "This policy requires comprehensive disclosure: transcripts, prompts, or step-by-step explanation—not just a mention.",
            ("C2", "C1"): "This policy mentions AI but doesn't mandate formal citation format. The requirement is less structured than you assessed.",
            ("C2", "C3"): "This policy requires full transparency: logs, drafts, or full audit trails—beyond just citation.",
            ("C3", "C2"): "This policy requires formal citation or structured disclosure, not full logs. You over-estimated the documentation burden.",
        }
        key = (user_answer, correct_answer)
        if key in explanations:
            return explanations[key]
        return f"You predicted {user_answer} but the database classifies this as {correct_answer}. Consider how much documentation/disclosure is explicitly required."
    
    elif category == "e_level":
        explanations = {
            ("E0", "E1"): "This policy mentions risks or consequences of AI use. You may have missed cautionary language about hallucinations or dishonesty.",
            ("E0", "E2"): "This policy threatens consequences like grade penalties or zero credit for violations.",
            ("E0", "E3"): "This policy has severe consequences (expulsion, dismissal). You may have minimized strong enforcement language.",
            ("E1", "E0"): "You may have over-read cautionary language. This policy warns about risks but doesn't explicitly threaten consequences.",
            ("E1", "E2"): "This policy explicitly threatens consequences (grade reduction, failing). You may have confused warning language with enforcement threats.",
            ("E1", "E3"): "This policy threatens severe consequences. Warnings are different from explicit penalties.",
            ("E2", "E1"): "This policy warns about consequences but doesn't threaten specific penalties. It's more educational than punitive.",
            ("E2", "E3"): "This policy has the harshest consequences (expulsion, automatic dismissal). You may have underestimated the severity.",
            ("E3", "E2"): "This policy implies consequences but doesn't explicitly mention automatic/extreme outcomes like expulsion. It's serious but not zero-tolerance.",
        }
        key = (user_answer, correct_answer)
        if key in explanations:
            return explanations[key]
        return f"You predicted {user_answer} but the database classifies this as {correct_answer}. Consider the severity of enforcement language."
    
    return "Review this classification to strengthen your understanding."


@game_bp.route("/fragment", methods=["GET"])
def get_fragment():
    # Pulls a random verified entry from the syllabus database for the quiz
    count = SyllabusEntry.query.filter_by(status="verified").count()

    if count == 0:
        return jsonify({"error": "No verified entries in the database yet."}), 404

    entry = SyllabusEntry.query.filter_by(status="verified") \
                               .offset(random.randint(0, count - 1)) \
                               .first()

    return jsonify({
        "id":   entry.id,
        "text": entry.policy_text,
    }), 200


@game_bp.route("/check", methods=["POST"])
def check_answer():
    # Compares user answers to database answers and provides explanations
    data        = request.get_json()
    entry_id    = data.get("fragment_id")
    user_t      = data.get("user_t", "").strip()
    user_c      = data.get("user_c", "").strip()
    user_e      = data.get("user_e", "").strip()

    entry = SyllabusEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    # Generate explanations for each category
    t_explanation = explain_difference("t_tier", user_t, entry.tier_id, entry.policy_text)
    c_explanation = explain_difference("c_level", user_c, entry.compliance_id, entry.policy_text)
    e_explanation = explain_difference("e_level", user_e, entry.enforcement_id, entry.policy_text)

    return jsonify({
        "user_t": user_t,
        "user_c": user_c,
        "user_e": user_e,
        "correct_t": entry.tier_id,
        "correct_c": entry.compliance_id,
        "correct_e": entry.enforcement_id,
        "t_match": user_t == entry.tier_id,
        "c_match": user_c == entry.compliance_id,
        "e_match": user_e == entry.enforcement_id,
        "t_explanation": t_explanation if user_t != entry.tier_id else "Correct! Great job identifying the permissiveness tier.",
        "c_explanation": c_explanation if user_c != entry.compliance_id else "Correct! You accurately assessed the documentation requirements.",
        "e_explanation": e_explanation if user_e != entry.enforcement_id else "Correct! You correctly identified the enforcement level.",
    }), 200
