import random
from flask import Blueprint, jsonify, request
from models import db, SyllabusEntry

game_bp = Blueprint("game", __name__)


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
    # Scores the three guesses against the real tagged values in the DB
    data        = request.get_json()
    entry_id    = data.get("fragment_id")
    user_t      = data.get("user_t", "").strip()
    user_c      = data.get("user_c", "").strip()
    user_e      = data.get("user_e", "").strip()

    entry = SyllabusEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    correct = 0
    if user_t == entry.tier_id:        correct += 1
    if user_c == entry.compliance_id:  correct += 1
    if user_e == entry.enforcement_id: correct += 1

    return jsonify({
        "score":     correct,
        "out_of":    3,
        "accuracy":  round((correct / 3) * 100),
        "correct_t": entry.tier_id,
        "correct_c": entry.compliance_id,
        "correct_e": entry.enforcement_id,
    }), 200
