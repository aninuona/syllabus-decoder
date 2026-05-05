from flask import Blueprint, jsonify, request, session
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/check-email", methods=["POST"])
def check_email():
    # checks if the email exists in the pre-approved admin list
    data  = request.get_json()
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # email not in the database = not an authorized admin
        return jsonify({"error": "This email is not authorized for admin access."}), 403

    if user.password_hash is None or user.password_hash == "UNSET":
        # email exists but no password set yet, prompt them to create one
        return jsonify({"status": "no_password"}), 200

    # Email exists and has a password, prompt enter it
    return jsonify({"status": "has_password"}), 200


@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    # called when an authorized admin logs in for the first time and sets their password
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Email not authorized."}), 403

    if user.password_hash is not None and user.password_hash != "UNSET":
        return jsonify({"error": "Password already set. Use the login form."}), 400

    user.password_hash = generate_password_hash(password)
    db.session.commit()

    session["user_id"] = user.id
    session["role"]    = user.role

    return jsonify({"message": "Password set. Logged in.", "role": user.role}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    # verifies the password for an admin who already has one
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or user.password_hash is None or user.password_hash == "UNSET":
        return jsonify({"error": "Invalid email or password."}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"] = user.id
    session["role"]    = user.role

    return jsonify({"message": "Logged in.", "role": user.role}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # clears the session
    session.clear()
    return jsonify({"message": "Logged out."}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    # returns current session user, used by admin page to verify access on load
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"id": user.id, "email": user.email, "role": user.role}), 200