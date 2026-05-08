from flask import Blueprint, jsonify, request
from models import db, PolicyGenerated, BuilderQuestion

builder_bp = Blueprint("builder", __name__)


# Map philosophy values to T/C/E dimensions independently
# Question 1 (Educational Alignment)  T tier
T_MAP = {
    "Minimal Intervention": "T0",
    "Bounded Use": "T3",
    "Open Use": "T5",
}

# Question 2 (Compliance & Accountability)  C level
C_MAP = {
    "Minimal Intervention": "C0",
    "With Documentation": "C3",
    "Open Use": "C1",
}

# Question 3 (Enforcement & Consequences)  E level
E_MAP = {
    "Minimal Intervention": "E2",
    "Bounded Use": "E2",
    "Open Use": "E0",
}

# Policy templates for each philosophy
POLICY_TEMPLATES = {
    "Minimal Intervention": (
        "The use of generative AI tools is prohibited in this course. "
        "All submitted work must be your own. Violations will be treated as academic dishonesty."
    ),
    "Bounded Use": (
        "Generative AI may be used for brainstorming, outlining, and editing only. "
        "Students must describe how AI was used in a brief disclosure statement. "
        "Submitting AI-generated text as your own work is prohibited and will result in academic consequences."
    ),
    "With Documentation": (
        "Generative AI is permitted with full documentation. "
        "Students must provide a log of all prompts used and explain how AI output was modified. "
        "Undisclosed AI use is a violation of academic integrity policy."
    ),
    "Open Use": (
        "Generative AI tools are permitted and encouraged in this course as part of learning. "
        "Students should note when AI is used but there is no formal restriction on how or when."
    ),
}


@builder_bp.route("/questions", methods=["GET"])
def get_questions():
    """Fetch all builder questions in order."""
    questions = BuilderQuestion.query.order_by(BuilderQuestion.step_number).all()

    # Deduplicate by step_number in case the DB contains duplicate rows
    seen = set()
    unique_questions = []
    for q in questions:
        if q.step_number in seen:
            continue
        seen.add(q.step_number)
        unique_questions.append(q)
    
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
    } for q in unique_questions]
    
    return jsonify(questions_data), 200


@builder_bp.route("/generate", methods=["POST"])
def generate_policy():
    """
    Receives 3 quiz answers and returns T/C/E levels independently mapped from each answer.
    
    Expected JSON (new format):
    {
        "answer_1": "philosophy value from question 1",
        "answer_2": "philosophy value from question 2",
        "answer_3": "philosophy value from question 3"
    }
    """
    data = request.get_json()
    print(f"DEBUG: Received data: {data}")  # DEBUG LOG
    
    # Get the 3 answers from the quiz
    answer_1 = data.get("answer_1", "").strip()  # Question 1: Educational Alignment
    answer_2 = data.get("answer_2", "").strip()  # Question 2: Compliance & Accountability
    answer_3 = data.get("answer_3", "").strip()  # Question 3: Enforcement & Consequences
    
    print(f"DEBUG: answer_1={answer_1}, answer_2={answer_2}, answer_3={answer_3}")  # DEBUG LOG
    
    # Validate all answers are present
    if not answer_1 or not answer_2 or not answer_3:
        print(f"DEBUG: Missing answers - aborting")  # DEBUG LOG
        return jsonify({"error": "All three questions must be answered."}), 400
    
    # Validate all answers are in the respective maps
    if answer_1 not in T_MAP:
        return jsonify({"error": f"Invalid answer for question 1: {answer_1}"}), 400
    if answer_2 not in C_MAP:
        return jsonify({"error": f"Invalid answer for question 2: {answer_2}"}), 400
    if answer_3 not in E_MAP:
        return jsonify({"error": f"Invalid answer for question 3: {answer_3}"}), 400
    
    # Map each answer independently to its T/C/E level
    tier = T_MAP[answer_1]
    compliance = C_MAP[answer_2]
    enforcement = E_MAP[answer_3]
    
    # Get policy template from first answer's philosophy
    policy_text = POLICY_TEMPLATES.get(answer_1, "")
    
    # Save to database
    '''
    try:
        new_policy = PolicyGenerated(
            course_name="Generated",
            policy_text=policy_text,
            tier_id=tier,
            compliance_id=compliance,
            enforcement_id=enforcement,
        )
        db.session.add(new_policy)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    '''

    return jsonify({
        "policy_text": policy_text,
        "tier_id": tier,
        "compliance_id": compliance,
        "enforcement_id": enforcement,
    }), 200
