#!/bin/bash
# Render build script

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Seeding builder questions..."
python seed_builder_questions.py

echo "Seeding syllabus entries from CSV..."
python seed_syllabus_entries.py

echo "Build complete!"
