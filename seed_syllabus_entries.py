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
            with open('syllabus.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                added = 0
                
                for row in reader:
                    # Skip empty rows
                    if not row.get('Institution') or not row.get('Policy in the Syllabus'):
                        continue
                    
                    entry = SyllabusEntry(
                        course=row.get('Course &', '').strip() or None,
                        institution=row.get('Institution', '').strip(),
                        discipline=row.get('Discipline', '').strip() or None,
                        policy_text=row.get('Policy in the Syllabus', '').strip(),
                        contributor=row.get('Contributor', '').strip() or None,
                        rights=row.get('Rights for Reuse', '').strip() or None,
                        tier_id=row.get('Tier', 'T2').strip(),
                        compliance_id=row.get('Compliance', 'C0').strip(),
                        enforcement_id=row.get('Enforcement', 'E0').strip(),
                        notes=row.get('Notes', '').strip() or None,
                        school_level=row.get('School Level', '').strip() or None,
                        institution_type=row.get('Institution Type', '').strip() or None,
                        state_region=row.get('State/Region', '').strip() or None,
                        country=row.get('Country', '').strip() or None,
                        link=row.get('Link to Institution', '').strip() or None,
                        status='verified',
                    )
                    db.session.add(entry)
                    added += 1
                
                db.session.commit()
                print(f"✓ Seeded {added} syllabus entries from CSV.")
        
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
