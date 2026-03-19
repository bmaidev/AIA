"""
Populate the Canberra Charities Database with seed data.
Run this script to initialize the database with 350+ charities.

Usage: python populate_charities.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import charity_db as cdb
from seed_data import SEED_CHARITIES


def populate():
    """Populate the database with seed data."""
    print("Initializing database...")
    cdb.init_db()

    existing = cdb.get_all_charities()
    if existing:
        print(f"Database already has {len(existing)} charities.")
        response = input("Do you want to clear and re-populate? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            return
        # Clear existing data
        conn = cdb.get_connection()
        conn.execute("DELETE FROM charity_functions")
        conn.execute("DELETE FROM board_members")
        conn.execute("DELETE FROM charities")
        conn.commit()
        conn.close()
        print("Cleared existing data.")

    print(f"Populating with {len(SEED_CHARITIES)} charities...")

    for i, charity_data in enumerate(SEED_CHARITIES):
        try:
            charity_id = cdb.add_charity(charity_data)

            # Add standard functions for each charity
            functions = charity_data.get('core_functions', [])
            if isinstance(functions, list):
                for func in functions:
                    conn = cdb.get_connection()
                    conn.execute("""
                        INSERT INTO charity_functions (charity_id, function_category, function_name)
                        VALUES (?, ?, ?)
                    """, (charity_id, _categorize_function(func), func))
                    conn.commit()
                    conn.close()

            if (i + 1) % 50 == 0:
                print(f"  Added {i + 1}/{len(SEED_CHARITIES)} charities...")

        except Exception as e:
            print(f"  Error adding '{charity_data.get('name', 'Unknown')}': {e}")

    stats = cdb.get_statistics()
    print(f"\nDone! Database now contains:")
    print(f"  Total charities: {stats['total_charities']}")
    print(f"  With CEO identified: {stats['with_ceo']}")
    print(f"  With Board Chair: {stats['with_board']}")
    print(f"  With Website: {stats['with_website']}")
    print(f"  HAC Members: {stats['hac_members']}")
    print(f"  Avg Data Completeness: {stats['avg_completeness']:.0%}")
    print(f"\nSectors:")
    for sector, count in sorted(stats['by_sector'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {sector}: {count}")


def _categorize_function(func_name):
    """Map function names to categories."""
    categories = {
        'Governance': 'Governance & Leadership',
        'Service Delivery': 'Operations',
        'Fundraising': 'Revenue & Fundraising',
        'Advocacy': 'External Relations',
        'Volunteer Management': 'People & Culture',
        'Finance & Administration': 'Corporate Services',
        'Communications & Marketing': 'External Relations',
        'HR & People': 'People & Culture',
        'Compliance & Reporting': 'Corporate Services',
        'IT & Systems': 'Technology & Data',
        'Program Management': 'Operations',
        'Quality & Impact': 'Operations',
        'Research': 'Knowledge & Innovation',
        'Training & Education': 'Knowledge & Innovation',
        'Community Engagement': 'External Relations',
        'Policy & Research': 'External Relations',
        'Client Services': 'Operations',
        'Case Management': 'Operations',
        'Emergency Relief': 'Operations',
        'Housing Support': 'Operations',
        'Health Services': 'Operations',
        'Counselling': 'Operations',
        'Legal Services': 'Operations',
        'Cultural Programs': 'Operations',
        'Events Management': 'External Relations',
        'Retail Operations': 'Revenue & Fundraising',
    }
    return categories.get(func_name, 'General')


if __name__ == '__main__':
    populate()
