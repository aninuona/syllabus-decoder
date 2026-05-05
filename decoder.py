from flask import Blueprint, jsonify, request

decoder_bp = Blueprint("decoder", __name__)

# TODO: replace keyword-based method with NLP/LLM

def classify_policy(text: str) -> dict:
    # Keyword-based classification, checks for the most specific match first
    text_lower = text.lower()

    # T-Tier: how permissive the policy is toward AI use
    if any(w in text_lower for w in ["prohibited", "not permitted", "strictly forbidden", "no use of ai", "no ai", "ban"]):
        t_tier = "T0"
    elif any(w in text_lower for w in ["strongly discouraged", "avoid", "refrain", "prefer you not"]):
        t_tier = "T1"
    elif any(w in text_lower for w in ["prior approval", "ask permission", "instructor approval", "permission before"]):
        t_tier = "T2"
    elif any(w in text_lower for w in ["brainstorm", "outline only", "limited use", "specific tasks only", "bounded"]):
        t_tier = "T3"
    elif any(w in text_lower for w in ["with documentation", "cite ai", "citation required", "must cite", "document your use"]):
        t_tier = "T4"
    elif any(w in text_lower for w in ["encouraged", "welcome to use", "open use", "freely permitted"]):
        t_tier = "T5"
    else:
        t_tier = "T2"

    # C-Level: what disclosure or logging is required
    if any(w in text_lower for w in ["full log", "step-by-step", "transcript", "every prompt"]):
        c_level = "C3"
    elif any(w in text_lower for w in ["describe how", "explain your use", "how you used", "what you used it for"]):
        c_level = "C2"
    elif any(w in text_lower for w in ["note if", "mention if", "indicate if", "acknowledge", "disclose"]):
        c_level = "C1"
    else:
        c_level = "C0"

    # E-Level: severity of consequences for violating the policy
    if any(w in text_lower for w in ["expulsion", "automatic failure", "automatic zero", "dismissed", "academic dismissal"]):
        e_level = "E3"
    elif any(w in text_lower for w in ["will result in", "grade reduction", "fail the assignment", "zero on", "penalty", "violation"]):
        e_level = "E2"
    elif any(w in text_lower for w in ["may result", "could affect", "at risk", "possible consequences"]):
        e_level = "E1"
    else:
        e_level = "E0"

    return {"t_tier": t_tier, "c_level": c_level, "e_level": e_level}


@decoder_bp.route("/classify", methods=["POST"])
def classify():
    # Accepts raw syllabus text and returns the three classification codes
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No syllabus text provided."}), 400

    result = classify_policy(text)
    return jsonify(result), 200
