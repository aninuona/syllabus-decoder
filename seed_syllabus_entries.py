#!/usr/bin/env python3
"""
Seed syllabus entries from CSV file into database.
Usage:
  python seed_syllabus_entries.py          # Seed if empty, skip if exists
  python seed_syllabus_entries.py --reset  # Delete all and reseed
"""

import sys
import csv
from app import create_app
from models import db, SyllabusEntry

app = create_app()


def seed():
    """Add entries from CSV if table is empty."""
    with app.app_context():
        count = SyllabusEntry.query.count()
        if count > 0:
            print(f"✓ Syllabus entries already exist ({count} entries). Use --reset to replace them.")
            return
        
        try:
            # safely truncate long strings
            def safe_str(val, max_len):
                s = (val or '').strip()
                return s[:max_len] if s and len(s) > max_len else (s or None)

            #  encoding  'utf-8-sig' to handle BOM characters from Excel exports
            with open('syllabus.csv', 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                added = 0
                skipped = 0
                
                for row in reader:
                    # extract requirements
                    institution = row.get('Institution', '').strip()
                    policy_text = row.get('Policy in the Syllabus', '').strip()

                    # Skip empty rows based on variable checks
                    if not institution or not policy_text:
                        skipped += 1
                        continue
                    
                    # Truncating variables to match SQLAlchemy limits in models.py
                    entry = SyllabusEntry(
                        course=safe_str(row.get('Course &'), 1000),
                        institution=safe_str(row.get('Institution'), 1000),
                        discipline=safe_str(row.get('Discipline'), 500),
                        policy_text=policy_text,
                        contributor=safe_str(row.get('Contributor'), 1000),
                        rights=safe_str(row.get('Rights for Reuse'), 1000),
                        tier_id=safe_str(row.get('Tier', 'T2'), 5),
                        compliance_id=safe_str(row.get('Compliance', 'C0'), 5),
                        enforcement_id=safe_str(row.get('Enforcement', 'E0'), 5),
                        notes=row.get('Notes', '').strip() or None,
                        school_level=safe_str(row.get('School Level'), 100),
                        institution_type=safe_str(row.get('Institution Type'), 100),
                        state_region=safe_str(row.get('State/Region'), 100),
                        country=safe_str(row.get('Country'), 100),
                        link=safe_str(row.get('Link to Institution'), 500),
                        status='verified',
                    )
                    db.session.add(entry)
                    added += 1
                
                db.session.commit()
                print(f"✓ Seeded {added} syllabus entries from CSV. Skipped {skipped} empty rows.")
        
        except FileNotFoundError:
            print("✗ syllabus.csv not found.")
        except Exception as ex:
            print(f"✗ Error seeding entries: {ex}")
            db.session.rollback()


def reset():
    """Delete all entries and reseed from CSV"""
    with app.app_context():
        count = SyllabusEntry.query.count()
        if count > 0:
            SyllabusEntry.query.delete()
            db.session.commit()
            print(f"✓ Deleted {count} existing entries.")
        
        seed()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            reset()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python seed_syllabus_entries.py [--reset]")
    else:
        seed()
