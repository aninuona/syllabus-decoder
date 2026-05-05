#!/usr/bin/env python3
"""
Seed or update builder questions.
Usage:
  python seed_builder_questions.py          # Seed if empty, skip if exists
  python seed_builder_questions.py --reset  # Delete all and reseed
  python seed_builder_questions.py --update # Update existing questions
"""

import sys
from app import create_app
from models import db, BuilderQuestion

QUESTIONS = [
    {
        "step_number": 1,
        "category": "Educational Alignment",
        "question": "Which statement best reflects your philosophy on student use of generative AI?",
        "option_a_title": "It's not helpful",
        "option_a_desc": "I believe students learn better without AI intervention.",
        "option_a_value": "Minimal Intervention",
        "option_b_title": "It's an extra pair of hands",
        "option_b_desc": "I see AI as an assistant, not a high-level thinker.",
        "option_b_value": "Bounded Use",
        "option_c_title": "It is the future",
        "option_c_desc": "I want my students to master these tools as professional competencies.",
        "option_c_value": "Open Use",
    },
    {
        "step_number": 2,
        "category": "Compliance & Accountability",
        "question": "How do you want students to document their AI use?",
        "option_a_title": "Don't use it",
        "option_a_desc": "No AI tools allowed in this course.",
        "option_a_value": "Minimal Intervention",
        "option_b_title": "Disclose & Document",
        "option_b_desc": "Full logs of prompts and AI contributions required.",
        "option_b_value": "With Documentation",
        "option_c_title": "Just mention it",
        "option_c_desc": "A brief note is fine; no formal log needed.",
        "option_c_value": "Open Use",
    },
    {
        "step_number": 3,
        "category": "Enforcement & Consequences",
        "question": "What happens if a student violates your AI policy?",
        "option_a_title": "Zero tolerance",
        "option_a_desc": "Violations are treated as academic dishonesty.",
        "option_a_value": "Minimal Intervention",
        "option_b_title": "Grade penalty",
        "option_b_desc": "The assignment loses points but isn't automatic failure.",
        "option_b_value": "Bounded Use",
        "option_c_title": "Discussion",
        "option_c_desc": "We talk about it; not a punitive approach.",
        "option_c_value": "Open Use",
    },
]

app = create_app()

def seed():
    """Add questions if table is empty."""
    with app.app_context():
        count = BuilderQuestion.query.count()
        if count > 0:
            print(f"✓ Builder questions already exist ({count} questions). Use --reset or --update to change them.")
            return
        
        for q_data in QUESTIONS:
            q = BuilderQuestion(**q_data)
            db.session.add(q)
        db.session.commit()
        print(f"✓ Seeded {len(QUESTIONS)} builder questions.")

def reset():
    """Delete all questions and reseed"""
    with app.app_context():
        count = BuilderQuestion.query.count()
        if count > 0:
            BuilderQuestion.query.delete()
            db.session.commit()
            print(f"✓ Deleted {count} existing questions.")
        
        for q_data in QUESTIONS:
            q = BuilderQuestion(**q_data)
            db.session.add(q)
        db.session.commit()
        print(f"✓ Reseeded {len(QUESTIONS)} builder questions.")

def update():
    """Update existing questions (by step_number)"""
    with app.app_context():
        count = BuilderQuestion.query.count()
        if count == 0:
            print("✗ No questions exist. Run without arguments to seed first.")
            return
        
        for q_data in QUESTIONS:
            step = q_data["step_number"]
            q = BuilderQuestion.query.filter_by(step_number=step).first()
            if q:
                for key, value in q_data.items():
                    setattr(q, key, value)
                print(f"✓ Updated question {step}: {q_data['category']}")
            else:
                print(f"✗ Question {step} not found, skipping.")
        
        db.session.commit()
        print("✓ All questions updated.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            reset()
        elif sys.argv[1] == "--update":
            update()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python seed_builder_questions.py [--reset|--update]")
    else:
        seed()