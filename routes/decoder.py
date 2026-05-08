from flask import Blueprint, jsonify, request
from models import SyllabusEntry
import re

decoder_bp = Blueprint("decoder", __name__)


def classify_policy(text: str) -> dict:
    """Lightweight NLP-style classifier with brief explanations for each category.

    scores keyword groups and returns
    the best matching code plus short reason snippets explaining matches.
    """
    text_lower = (text or "").lower()

    # Helper to find matches and return sample matches
    def find_matches(patterns):
        matches = []
        for p in patterns:
            if p in text_lower:
                matches.append(p)
        return matches

    # T-Tier scoring
    t_map = [
        ("T0", ["prohibited", "not permitted", "strictly forbidden", "no use of ai", "no ai", "ban"]),
        ("T1", ["strongly discouraged", "avoid", "refrain", "prefer you not"]),
        ("T2", ["prior approval", "ask permission", "instructor approval", "permission before"]),
        ("T3", ["brainstorm", "outline only", "limited use", "specific tasks only", "bounded"]),
        ("T4", ["with documentation", "cite ai", "citation required", "must cite", "document your use"]),
        ("T5", ["encouraged", "welcome to use", "open use", "freely permitted"]),
    ]

    best_t, best_t_matches = None, []
    for code, pats in t_map:
        matches = find_matches(pats)
        if matches and not best_t:  # prefer first group that matches specificity order
            best_t = code
            best_t_matches = matches
    if not best_t:
        best_t = "T2"

    # C-Level scoring
    c_map = [
        ("C3", ["full log", "step-by-step", "transcript", "every prompt", "prompt log"]),
        ("C2", ["describe how", "explain your use", "how you used", "what you used it for", "modified the output"]),
        ("C1", ["note if", "mention if", "indicate if", "acknowledge", "disclose", "note that ai"]),
    ]
    best_c, best_c_matches = None, []
    for code, pats in c_map:
        matches = find_matches(pats)
        if matches and not best_c:
            best_c = code
            best_c_matches = matches
    if not best_c:
        best_c = "C0"

    # E-Level scoring
    e_map = [
        ("E3", ["expulsion", "automatic failure", "automatic zero", "academic dismissal"]),
        ("E2", ["will result in", "grade reduction", "fail the assignment", "zero on", "penalty", "violation"]),
        ("E1", ["may result", "could affect", "at risk", "possible consequences"]),
    ]
    best_e, best_e_matches = None, []
    for code, pats in e_map:
        matches = find_matches(pats)
        if matches and not best_e:
            best_e = code
            best_e_matches = matches
    if not best_e:
        best_e = "E0"

    # Build short explanations: include sample matched phrases or a fallback sentence
    def explain(code, matches, fallback):
        if matches:
            sample = ", ".join(matches[:3])
            return f"Matches found: {sample}."
        return fallback

    t_reason = explain(best_t, best_t_matches, "No strong permissiveness/ban language detected.")
    c_reason = explain(best_c, best_c_matches, "No disclosure or logging requirements detected.")
    e_reason = explain(best_e, best_e_matches, "No explicit enforcement language detected.")

    return {
        "t_tier": best_t,
        "t_reason": t_reason,
        "c_level": best_c,
        "c_reason": c_reason,
        "e_level": best_e,
        "e_reason": e_reason,
    }


@decoder_bp.route("/entries", methods=["GET"])
def get_entries():
    # Returns all verified syllabus entries for public data visualization
    entries = SyllabusEntry.query.filter_by(status="verified").order_by(SyllabusEntry.id.desc()).all()
    return jsonify([e.to_dict() for e in entries]), 200


@decoder_bp.route("/classify", methods=["POST"])
def classify():
    # Accepts raw syllabus text and returns the three classification codes + explanations
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No syllabus text provided."}), 400

    result = classify_policy(text)
    return jsonify(result), 200
