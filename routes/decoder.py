from flask import Blueprint, jsonify, request
from models import SyllabusEntry
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

decoder_bp = Blueprint("decoder", __name__)


def classify_policy(text: str) -> dict:
    """Lightweight NLP-style classifier with brief explanations for each category.

    It scores keyword groups and returns
    the best matching code plus short reason snippets explaining matches.
    """
    text_lower = (text or "").lower()

    # --- TF-IDF based classifier setup ---
    # Create example documents for each class using the existing keyword maps.
    examples = {}
    examples.update({
        'T0': 'total prohibition banned no use of ai not permitted',
        'T1': 'default prohibited exceptions only avoid refrain',
        'T2': 'prior approval ask permission instructor approval',
        'T3': 'brainstorm outline limited use bounded support proofreading',
        'T4': 'with documentation cite ai citation required disclose',
        'T5': 'encouraged welcome freely permitted open use',
    })
    examples.update({
        'C0': 'no disclosure none',
        'C1': 'mention acknowledge note if indicate if',
        'C2': 'describe how explain your use formal citation apa mla',
        'C3': 'full audit prompt logs transcript every prompt submission',
    })
    examples.update({
        'E0': 'trust based integrity no monitoring',
        'E1': 'may result could affect warn about risks instructive',
        'E2': 'will result penalty grade reduction detectors investigative',
        'E3': 'expulsion automatic failure conduct office zero tolerance',
    })

    # Vectorize examples + incoming text
    vectorizer = TfidfVectorizer().fit(list(examples.values()) + [text_lower])
    doc_vecs = vectorizer.transform(list(examples.values()) + [text_lower])
    text_vec = doc_vecs[-1]
    example_vecs = doc_vecs[:-1]

    sims = cosine_similarity(text_vec, example_vecs).flatten()
    # Map similarity scores back to codes
    codes = list(examples.keys())
    sim_map = {codes[i]: float(sims[i]) for i in range(len(codes))}

    # Choose best for each dimension by highest similarity among its codes
    def best_in(prefix):
        best_code, best_score = None, -1.0
        for k, v in sim_map.items():
            if k.startswith(prefix) and v > best_score:
                best_code, best_score = k, v
        return best_code, best_score

    tf_t, tf_t_score = best_in('T')
    tf_c, tf_c_score = best_in('C')
    tf_e, tf_e_score = best_in('E')

    # Threshold: require some minimal similarity to trust TF-IDF; otherwise fall back to rule map
    TF_THRESHOLD = 0.12

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
        if matches and not best_t:
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

    # Build short explanations: include sample matched phrases or a fallback sentence
    t_reason = explain(best_t, best_t_matches, "No strong permissiveness/ban language detected.")
    c_reason = explain(best_c, best_c_matches, "No disclosure or logging requirements detected.")
    e_reason = explain(best_e, best_e_matches, "No explicit enforcement language detected.")

    # If TF-IDF produced confident predictions, use them with explanatory confidence
    if tf_t_score >= TF_THRESHOLD:
        best_t = tf_t
        t_reason = f"{t_reason}"
    if tf_c_score >= TF_THRESHOLD:
        best_c = tf_c
        c_reason = f"{c_reason}"
    if tf_e_score >= TF_THRESHOLD:
        best_e = tf_e
        e_reason = f"{e_reason}"

    return {
        "t_tier": best_t,
        "t_reason": t_reason,
        "c_level": best_c,
        "c_reason": c_reason,
        "e_level": best_e,
        "e_reason": e_reason,
        "tf_scores": sim_map,
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
