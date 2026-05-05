import os
import sys
import random
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from config import config
from models import db


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get("FLASK_ENV", "development")

    # Flask auto-finds /templates and /static when no custom folders are given
    app = Flask(__name__)
    app.config.from_object(config[env])

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:5173",
    ])

    db.init_app(app)

    # Register API blueprints
    from routes.auth    import auth_bp
    from routes.decoder import decoder_bp
    from routes.builder import builder_bp
    from routes.game    import game_bp
    from routes.admin   import admin_bp

    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(decoder_bp, url_prefix="/api/decoder")
    app.register_blueprint(builder_bp, url_prefix="/api/builder")
    app.register_blueprint(game_bp,    url_prefix="/api/game")
    app.register_blueprint(admin_bp,   url_prefix="/api/admin")

    # Page routes

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/decoder", methods=["GET"])
    def decoder_page():
        #Empty on first load
        return render_template("decoder.html", t_tier=None, c_level=None, e_level=None, pasted_text="")

    @app.route("/decode", methods=["POST"])
    def decode():
        # Calls the classifier in routes/decoder.py and renders results
        from routes.decoder import classify_policy

        syllabus_text = request.form.get("syllabus_text", "").strip()

        if not syllabus_text:
            return render_template("decoder.html", t_tier=None, c_level=None, e_level=None,
                                   pasted_text="", error="Please paste some policy text first.")

        result = classify_policy(syllabus_text)

        return render_template(
            "decoder.html",
            pasted_text = syllabus_text,
            t_tier      = result["t_tier"],
            c_level     = result["c_level"],
            e_level     = result["e_level"],
        )

    @app.route("/buildsyllabus", methods=["GET"])
    def builder_page():
        # Loads builder questions from DB and renders the wizard
        from models import BuilderQuestion
        questions = BuilderQuestion.query.order_by(BuilderQuestion.step_number).all()
        
        # Convert to dict for JSON serialization
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
        
        return render_template("build_syllabus.html", questions=questions_data)

    @app.route("/submit-policy", methods=["POST"])
    def submit_policy():
        #Passes form answers to the builder route logic and renders the result
        from routes.builder import TIER_MAP
        from models import BuilderQuestion, PolicyGenerated

        philosophy  = request.form.get("philosophy", "").strip()
        course_name = request.form.get("course_name", "this course").strip()
        questions   = BuilderQuestion.query.all()

        if philosophy not in TIER_MAP:
            return render_template("build_syllabus.html", questions=questions,
                                   error="Please select an option before submitting.")

        tier, compliance, enforcement, template = TIER_MAP[philosophy]
        policy_text = template.replace("this course", course_name) if course_name else template

        new_policy = PolicyGenerated(
            course_name   = course_name,
            policy_text   = policy_text,
            tier_id       = tier,
            compliance_id = compliance,
        )
        db.session.add(new_policy)
        db.session.commit()

        return render_template(
            "build_syllabus.html",
            questions      = questions,
            generated_text = policy_text,
            tier           = tier,
            compliance     = compliance,
            enforcement    = enforcement,
        )

    @app.route("/traininggame", methods=["GET"])
    def game_page():
        # Picks a random syllabus entry for the quiz
        from models import SyllabusEntry

        entry = None
        try:
            count = SyllabusEntry.query.filter_by(status="verified").count()
            if count > 0:
                entry = SyllabusEntry.query.filter_by(status="verified") \
                                           .offset(random.randint(0, count - 1)) \
                                           .first()
        except Exception:
            pass

        return render_template(
            "training_game.html",
            policy_text = entry.policy_text if entry else "No entries in database yet.",
            fragment_id = entry.id          if entry else 0,
            accuracy    = None,
        )

    @app.route("/check-answer", methods=["POST"])
    def check_answer():
        # Scores guess, loads the next random entry
        from models import SyllabusEntry

        entry_id = request.form.get("fragment_id", type=int)
        user_t   = request.form.get("user_t", "")
        user_c   = request.form.get("user_c", "")
        user_e   = request.form.get("user_e", "")

        entry   = SyllabusEntry.query.get(entry_id)
        correct = 0

        if entry:
            if user_t == entry.tier_id:        correct += 1
            if user_c == entry.compliance_id:  correct += 1
            if user_e == entry.enforcement_id: correct += 1

        accuracy = round((correct / 3) * 100)

        next_entry = None
        try:
            count = SyllabusEntry.query.filter_by(status="verified").count()
            if count > 0:
                next_entry = SyllabusEntry.query.filter_by(status="verified") \
                                                .offset(random.randint(0, count - 1)) \
                                                .first()
        except Exception:
            pass

        return render_template(
            "training_game.html",
            policy_text = next_entry.policy_text if next_entry else "No more entries.",
            fragment_id = next_entry.id          if next_entry else 0,
            accuracy    = accuracy,
        )

    @app.route("/admin")
    def admin_page():
        if session.get("role") != "admin":
            return redirect("/login")
        return render_template("admin.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")


# UTILITY
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Syllabus Decoder API is running."}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error."}), 500

    # Auto-create any missing tables on first run
    with app.app_context():
        try:
            db.create_all()
        except Exception as ex:
            print(f"WARNING: Could not auto-create tables: {ex}")

    return app


# Create app instance at module level (for gunicorn to find it)
app = create_app()

# Entry point for local development
if __name__ == "__main__":
    app.run(debug=True)
