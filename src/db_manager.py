import sqlite3
import json
import datetime
import csv
import io
from aia_core import AlgorithmicImpactAssessment

DATABASE_NAME = "aia_register.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Main table for AI Systems / Use Cases — aligned to DTA Policy v2.0
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_systems (
        system_id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_name TEXT NOT NULL,
        agency_name TEXT,
        aia_status TEXT DEFAULT 'Draft',
        risk_category TEXT DEFAULT 'Low',
        total_score INTEGER DEFAULT 0,
        pia_status TEXT DEFAULT 'Not Started',
        security_assessment_status TEXT DEFAULT 'Not Started',
        human_rights_assessment_status TEXT DEFAULT 'Not Started',
        creation_date TEXT,
        last_modified_date TEXT,
        aia_data TEXT,
        -- v2.0 columns
        policy_version TEXT DEFAULT '2.0',
        usage_pattern TEXT DEFAULT '',
        inherent_risk_rating TEXT DEFAULT 'Not Assessed',
        residual_risk_rating TEXT DEFAULT 'Not Assessed',
        is_in_scope INTEGER DEFAULT NULL,
        accountable_owner_name TEXT DEFAULT '',
        accountable_owner_email TEXT DEFAULT '',
        ai_technology_type TEXT DEFAULT '',
        last_assessment_date TEXT DEFAULT '',
        dta_notified INTEGER DEFAULT 0,
        reference_id TEXT DEFAULT ''
    )
    """)

    # Run migration for existing databases
    _migrate_v2_columns(cursor)

    conn.commit()
    conn.close()
    print("Database initialized.")


def _migrate_v2_columns(cursor):
    """Adds v2.0 columns to existing databases that don't have them."""
    # Get existing columns
    cursor.execute("PRAGMA table_info(ai_systems)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    v2_columns = [
        ("policy_version", "TEXT DEFAULT '2.0'"),
        ("usage_pattern", "TEXT DEFAULT ''"),
        ("inherent_risk_rating", "TEXT DEFAULT 'Not Assessed'"),
        ("residual_risk_rating", "TEXT DEFAULT 'Not Assessed'"),
        ("is_in_scope", "INTEGER DEFAULT NULL"),
        ("accountable_owner_name", "TEXT DEFAULT ''"),
        ("accountable_owner_email", "TEXT DEFAULT ''"),
        ("ai_technology_type", "TEXT DEFAULT ''"),
        ("last_assessment_date", "TEXT DEFAULT ''"),
        ("dta_notified", "INTEGER DEFAULT 0"),
        ("reference_id", "TEXT DEFAULT ''"),
    ]

    for col_name, col_def in v2_columns:
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE ai_systems ADD COLUMN {col_name} {col_def}")
            print(f"Migration: Added column '{col_name}' to ai_systems.")


def add_system(system_name, agency_name):
    """Adds a new system entry with default values."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    default_aia = AlgorithmicImpactAssessment(system_name=system_name, agency_name=agency_name)
    default_aia.creation_date = now
    default_aia.last_modified_date = now
    aia_json = json.dumps(default_aia.__dict__, ensure_ascii=False)

    cursor.execute("""
    INSERT INTO ai_systems (system_name, agency_name, creation_date, last_modified_date, aia_data,
                           policy_version, inherent_risk_rating, residual_risk_rating)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (system_name, agency_name, now, now, aia_json,
          default_aia.policy_version, default_aia.inherent_risk_rating,
          default_aia.residual_risk_rating))
    system_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Added system '{system_name}' with ID: {system_id}")
    return system_id


def get_system_list(filters=None):
    """Retrieves a list of systems, potentially filtered."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    query = """SELECT system_id, system_name, agency_name, aia_status, risk_category,
                      total_score, last_modified_date, usage_pattern, inherent_risk_rating,
                      residual_risk_rating, is_in_scope, accountable_owner_name,
                      ai_technology_type, dta_notified, reference_id
               FROM ai_systems"""
    params = []
    if filters:
        conditions = []
        filterable = ['aia_status', 'risk_category', 'agency_name', 'inherent_risk_rating',
                      'residual_risk_rating', 'is_in_scope', 'usage_pattern']
        for key, value in filters.items():
            if key in filterable:
                conditions.append(f"{key} = ?")
                params.append(value)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY last_modified_date DESC"
    cursor.execute(query, params)
    systems = cursor.fetchall()
    conn.close()

    columns = ["system_id", "system_name", "agency_name", "aia_status", "risk_category",
               "total_score", "last_modified_date", "usage_pattern", "inherent_risk_rating",
               "residual_risk_rating", "is_in_scope", "accountable_owner_name",
               "ai_technology_type", "dta_notified", "reference_id"]
    return [dict(zip(columns, row)) for row in systems]


def get_aia_object(system_id) -> AlgorithmicImpactAssessment | None:
    """Retrieves the full AIA object for a given system ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT aia_data FROM ai_systems WHERE system_id = ?", (system_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        try:
            aia_data = json.loads(result[0])
            aia_obj = AlgorithmicImpactAssessment(
                system_name=aia_data.get('system_name', '[Unknown]'),
                agency_name=aia_data.get('agency_name', '[Unknown]')
            )
            aia_obj.__dict__.update(aia_data)
            aia_obj.system_id = system_id
            return aia_obj
        except json.JSONDecodeError:
            print(f"Error decoding JSON data for system_id {system_id}")
            return None
        except Exception as e:
            print(f"Error instantiating AIA object for system_id {system_id}: {e}")
            return None
    return None


def update_aia(aia_object: AlgorithmicImpactAssessment):
    """Updates the database record for the given AIA object."""
    if not aia_object.system_id:
        raise ValueError("AIA object must have a system_id to be updated.")

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    aia_object._update_risk_assessment()
    aia_object.last_modified_date = datetime.datetime.now().isoformat()
    aia_json = json.dumps(aia_object.__dict__, ensure_ascii=False)

    # Extract key fields for indexed columns
    risk_category = aia_object.risk_category.get('category', 'Low') if isinstance(aia_object.risk_category, dict) else aia_object.risk_category
    total_score = aia_object.total_score
    aia_status = aia_object.aia_status
    pia_status = aia_object.related_assessment_statuses.get('PIA', 'Not Started')
    sec_status = aia_object.related_assessment_statuses.get('Security Assessment', 'Not Started')
    hr_status = aia_object.related_assessment_statuses.get('Human Rights Assessment', 'Not Started')

    # v2.0 fields
    inherent_risk = getattr(aia_object, 'inherent_risk_rating', 'Not Assessed')
    residual_risk = getattr(aia_object, 'residual_risk_rating', 'Not Assessed')
    usage_pattern = getattr(aia_object, 'usage_pattern', '')
    is_in_scope = 1 if getattr(aia_object, 'is_in_scope', None) else (0 if getattr(aia_object, 'is_in_scope', None) is False else None)
    owner = getattr(aia_object, 'accountable_use_case_owner', {})
    owner_name = owner.get('name', '') if isinstance(owner, dict) else ''
    owner_email = owner.get('email', '') if isinstance(owner, dict) else ''
    ai_tech_type = getattr(aia_object, 'ai_technology_type', '')
    last_assess = getattr(aia_object, 'last_assessment_date', '')
    dta_notified = 1 if getattr(aia_object, 'dta_notified', False) else 0
    reference_id = getattr(aia_object, 'reference_id', '')

    cursor.execute("""
    UPDATE ai_systems
    SET system_name = ?, agency_name = ?, aia_status = ?, risk_category = ?, total_score = ?,
        pia_status = ?, security_assessment_status = ?, human_rights_assessment_status = ?,
        last_modified_date = ?, aia_data = ?,
        inherent_risk_rating = ?, residual_risk_rating = ?, usage_pattern = ?,
        is_in_scope = ?, accountable_owner_name = ?, accountable_owner_email = ?,
        ai_technology_type = ?, last_assessment_date = ?, dta_notified = ?, reference_id = ?
    WHERE system_id = ?
    """, (
        aia_object.system_name, aia_object.agency_name, aia_status, risk_category, total_score,
        pia_status, sec_status, hr_status,
        aia_object.last_modified_date, aia_json,
        inherent_risk, residual_risk, usage_pattern,
        is_in_scope, owner_name, owner_email,
        ai_tech_type, last_assess, dta_notified, reference_id,
        aia_object.system_id
    ))
    conn.commit()

    if conn.total_changes == 0:
        print(f"Warning: No rows updated for system_id {aia_object.system_id}. Does it exist?")
    else:
        print(f"Updated system_id {aia_object.system_id}")

    conn.close()


def delete_system(system_id):
    """Deletes a system record from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ai_systems WHERE system_id = ?", (system_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    if changes > 0:
        print(f"Deleted system_id {system_id}")
        return True
    else:
        print(f"Warning: No system found with ID {system_id} to delete.")
        return False


def get_dashboard_data():
    """Fetches aggregated data for the dashboard."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        systems_by_status = cursor.execute(
            "SELECT aia_status, COUNT(*) as count FROM ai_systems GROUP BY aia_status").fetchall()
        systems_by_risk = cursor.execute(
            "SELECT risk_category, COUNT(*) as count FROM ai_systems GROUP BY risk_category").fetchall()
        systems_by_inherent_risk = cursor.execute(
            "SELECT inherent_risk_rating, COUNT(*) as count FROM ai_systems GROUP BY inherent_risk_rating").fetchall()
        systems_by_residual_risk = cursor.execute(
            "SELECT residual_risk_rating, COUNT(*) as count FROM ai_systems GROUP BY residual_risk_rating").fetchall()
        systems_by_pia_status = cursor.execute(
            "SELECT pia_status, COUNT(*) as count FROM ai_systems GROUP BY pia_status").fetchall()
        systems_by_sec_status = cursor.execute(
            "SELECT security_assessment_status, COUNT(*) as count FROM ai_systems GROUP BY security_assessment_status").fetchall()
        total_systems = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems").fetchone()['count']
        in_scope_count = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems WHERE is_in_scope = 1").fetchone()['count']
        out_scope_count = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems WHERE is_in_scope = 0").fetchone()['count']
        not_screened_count = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems WHERE is_in_scope IS NULL").fetchone()['count']
        dta_notified_count = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems WHERE dta_notified = 1").fetchone()['count']
        high_risk_count = cursor.execute(
            "SELECT COUNT(*) as count FROM ai_systems WHERE inherent_risk_rating = 'High'").fetchone()['count']

        dashboard_data = {
            "total_systems": total_systems,
            "by_status": {row['aia_status']: row['count'] for row in systems_by_status},
            "by_risk": {row['risk_category']: row['count'] for row in systems_by_risk},
            "by_inherent_risk": {row['inherent_risk_rating']: row['count'] for row in systems_by_inherent_risk},
            "by_residual_risk": {row['residual_risk_rating']: row['count'] for row in systems_by_residual_risk},
            "by_pia_status": {row['pia_status']: row['count'] for row in systems_by_pia_status},
            "by_security_status": {row['security_assessment_status']: row['count'] for row in systems_by_sec_status},
            "in_scope_count": in_scope_count,
            "out_scope_count": out_scope_count,
            "not_screened_count": not_screened_count,
            "dta_notified_count": dta_notified_count,
            "high_risk_count": high_risk_count,
        }
        return dashboard_data
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return None
    finally:
        conn.close()


def get_dta_export():
    """Generates a CSV export of the AI register for DTA 6-monthly reporting."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT system_id, system_name, agency_name, reference_id, usage_pattern,
           ai_technology_type, aia_status, inherent_risk_rating, residual_risk_rating,
           is_in_scope, accountable_owner_name, accountable_owner_email,
           last_assessment_date, dta_notified, last_modified_date, creation_date
    FROM ai_systems
    WHERE is_in_scope = 1 OR is_in_scope IS NULL
    ORDER BY system_name
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "System ID", "Use Case Name", "Agency", "Reference ID", "Usage Pattern",
        "AI Technology Type", "Assessment Status", "Inherent Risk Rating",
        "Residual Risk Rating", "In Scope", "Accountable Owner Name",
        "Accountable Owner Email", "Last Assessment Date", "DTA Notified",
        "Last Modified", "Created"
    ])
    for row in rows:
        scope_val = "Yes" if row['is_in_scope'] == 1 else ("No" if row['is_in_scope'] == 0 else "Not Screened")
        dta_val = "Yes" if row['dta_notified'] else "No"
        writer.writerow([
            row['system_id'], row['system_name'], row['agency_name'],
            row['reference_id'], row['usage_pattern'], row['ai_technology_type'],
            row['aia_status'], row['inherent_risk_rating'], row['residual_risk_rating'],
            scope_val, row['accountable_owner_name'], row['accountable_owner_email'],
            row['last_assessment_date'], dta_val, row['last_modified_date'],
            row['creation_date']
        ])

    return output.getvalue()


def get_high_risk_systems():
    """Returns systems with high inherent risk that haven't been reported to DTA."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT system_id, system_name, agency_name, inherent_risk_rating, dta_notified
    FROM ai_systems
    WHERE inherent_risk_rating = 'High' AND dta_notified = 0
    ORDER BY system_name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_overdue_reviews():
    """Returns systems with reviews overdue (>12 months since last assessment)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    twelve_months_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat()
    cursor.execute("""
    SELECT system_id, system_name, agency_name, last_modified_date
    FROM ai_systems
    WHERE aia_status = 'Approved'
    AND (last_assessment_date < ? OR last_assessment_date = '' OR last_assessment_date IS NULL)
    ORDER BY last_modified_date ASC
    """, (twelve_months_ago,))
    rows = cursor.fetchall()
    conn.close()
    columns = ["system_id", "system_name", "agency_name", "last_modified_date"]
    return [dict(zip(columns, row)) for row in rows]


# Initialize the database when this module is imported
init_db()
