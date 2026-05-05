from flask import Blueprint, jsonify, request, session
from models import db, User, PolicyGenerated, SyllabusEntry, BuilderQuestion

admin_bp = Blueprint("admin", __name__)


def require_admin():
    # Returns an error response if the caller is not a logged-in admin
    if session.get("role") != "admin":
        return jsonify({"error": "Admin access required."}), 403
    return None


@admin_bp.route("/stats", methods=["GET"])
def stats():
    # Summary for the dashboard
    denied = require_admin()
    if denied: return denied

    return jsonify({
        "entries":   SyllabusEntry.query.count(),
        "users":     User.query.count(),
        "policies":  PolicyGenerated.query.count(),
        "fragments": SyllabusEntry.query.count(),
    }), 200


@admin_bp.route("/entries", methods=["GET"])
def list_entries():
    # Returns all syllabus entries, newest first
    denied = require_admin()
    if denied: return denied

    entries = SyllabusEntry.query.order_by(SyllabusEntry.id.desc()).all()
    return jsonify([e.to_dict() for e in entries]), 200


@admin_bp.route("/entries", methods=["POST"])
def add_entry():
    # Creates a new syllabus entry from the upload form
    denied = require_admin()
    if denied: return denied

    data  = request.get_json()
    entry = SyllabusEntry(
        institution    = data.get("institution", "").strip(),
        discipline     = data.get("discipline", "").strip(),
        policy_text    = data.get("policy_text", "").strip(),
        tier_id        = data.get("tier_id", "T2"),
        compliance_id  = data.get("compliance_id", "C0"),
        enforcement_id = data.get("enforcement_id", "E0"),
        status         = "pending",
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Entry added.", "id": entry.id}), 201


@admin_bp.route("/entries/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    # Updates an existing entry with new values from the edit 
    denied = require_admin()
    if denied: return denied

    entry = SyllabusEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    data = request.get_json()
    entry.institution    = data.get("institution",    entry.institution)
    entry.discipline     = data.get("discipline",     entry.discipline)
    entry.policy_text    = data.get("policy_text",    entry.policy_text)
    entry.tier_id        = data.get("tier_id",        entry.tier_id)
    entry.compliance_id  = data.get("compliance_id",  entry.compliance_id)
    entry.enforcement_id = data.get("enforcement_id", entry.enforcement_id)

    db.session.commit()
    return jsonify({"message": "Entry updated."}), 200


@admin_bp.route("/entries/<int:entry_id>/status", methods=["PATCH"])
def update_status(entry_id):
    # Toggles an entry between pending, verified, and flagged
    denied = require_admin()
    if denied: return denied

    entry = SyllabusEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    new_status = request.get_json().get("status", "pending")
    if new_status not in ("pending", "verified", "flagged"):
        return jsonify({"error": "Invalid status value."}), 400

    entry.status = new_status
    db.session.commit()
    return jsonify({"message": "Status updated.", "status": entry.status}), 200
