from flask import Blueprint, jsonify, request
from models import db, PolicyGenerated, BuilderQuestion

builder_bp = Blueprint("builder", __name__)


# Tier mapping based on faculty answers
TIER_MAP = {
    "Minimal Intervention": ("T0", "C0", "E2",
        "The use of generative AI tools is prohibited in this course. "
        "All submitted work must be your own. Violations will be treated as academic dishonesty."),

    "Discouragement":       ("T1", "C0", "E1",
        "Students are strongly discouraged from using generative AI in this course. "
        "If used, it must be disclosed, though there is no formal penalty structure."),

    "Ask Permission":       ("T2", "C1", "E1",
        "Use of generative AI requires prior instructor approval. "
        "Students must note any AI use on submitted work."),

    "Bounded Use":          ("T3", "C2", "E2",
        "Generative AI may be used for brainstorming, outlining, and editing only. "
        "Students must describe how AI was used in a brief disclosure statement. "
        "Submitting AI-generated text as your own work is prohibited and will result in academic consequences."),

    "With Documentation":   ("T4", "C3", "E2",
        "Generative AI is permitted with full documentation. "
        "Students must provide a log of all prompts used and explain how AI output was modified. "
        "Undisclosed AI use is a violation of academic integrity policy."),

    "Open Use":             ("T5", "C1", "E0",
        "Generative AI tools are permitted and encouraged in this course as part of learning. "
        "Students should note when AI is used but there is no formal restriction on how or when."),
}


@builder_bp.route("/questions", methods=["GET"])
def get_questions():
    """Fetch all builder questions in order."""
    questions = BuilderQuestion.query.order_by(BuilderQuestion.step_number).all()
    
    questions_data = [{
        'step_number': q.step_number,
        'category': q.category,
        'question': q.question,
        'option_a_title': q.option_a_title,
        'option_a_desc': q.option_a_desc,
        'option_a_value': q.option_a_value,
        'option_b_title': q.option_b_title,
        'option_b_desc': q.option_b_desc,
        'option_b_value': q.option_b_value,
        'option_c_title': q.option_c_title,
        'option_c_desc': q.option_c_desc,
        'option_c_value': q.option_c_value,
    } for q in questions]
    
    return jsonify(questions_data), 200


@builder_bp.route("/generate", methods=["POST"])
def generate_policy():
    """Receives faculty quiz answers and returns a generated policy text fragment."""
    data       = request.get_json()
    philosophy = data.get("philosophy", "").strip()
    course     = data.get("course_name", "this course").strip()

    if philosophy not in TIER_MAP:
        return jsonify({"error": "Invalid answer selection."}), 400

    tier, compliance, enforcement, template = TIER_MAP[philosophy]

    # Personalize the text with the course name if provided
    policy_text = template.replace("this course", course) if course else template

    # Save to the database so admin can see all generated policies
    new_policy = PolicyGenerated(
        course_name   = course,
        policy_text   = policy_text,
        tier_id       = tier,
        compliance_id = compliance,
    )
    db.session.add(new_policy)
    db.session.commit()

    return jsonify({
        "policy_text":    policy_text,
        "tier_id":        tier,
        "compliance_id":  compliance,
        "enforcement_id": enforcement,
    }), 200
