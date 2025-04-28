import sqlite3
import json
import datetime
from aia_core import AlgorithmicImpactAssessment # Import class for type hinting/instantiation

DATABASE_NAME = "aia_register.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Main table for AI Systems / Use Cases
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
        aia_data TEXT  -- Store the full AIA object as JSON
    )
    """)
    # Add more columns to ai_systems if other fields are frequently needed for filtering/dashboarding

    conn.commit()
    conn.close()
    print("Database initialized.")

def add_system(system_name, agency_name):
    """Adds a new system entry with default values."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    # Create a default AIA object to store its initial JSON state
    default_aia = AlgorithmicImpactAssessment(system_name=system_name, agency_name=agency_name)
    default_aia.creation_date = now # Set creation date on object too if needed
    default_aia.last_modified_date = now
    aia_json = json.dumps(default_aia.__dict__, ensure_ascii=False)

    cursor.execute("""
    INSERT INTO ai_systems (system_name, agency_name, creation_date, last_modified_date, aia_data)
    VALUES (?, ?, ?, ?, ?)
    """, (system_name, agency_name, now, now, aia_json))
    system_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Added system '{system_name}' with ID: {system_id}")
    return system_id

def get_system_list(filters=None):
    """Retrieves a list of systems, potentially filtered."""
    # Filters could be a dict like {'aia_status': 'Approved', 'risk_category': 'High'}
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    query = "SELECT system_id, system_name, agency_name, aia_status, risk_category, total_score, last_modified_date FROM ai_systems"
    params = []
    if filters:
        conditions = []
        for key, value in filters.items():
            # Basic filtering - adjust security/complexity as needed
            if key in ['aia_status', 'risk_category', 'agency_name']: # Example filterable fields
                 conditions.append(f"{key} = ?")
                 params.append(value)
        if conditions:
             query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY last_modified_date DESC" # Show most recent first
    cursor.execute(query, params)
    systems = cursor.fetchall()
    conn.close()
    # Return as list of dicts for easier use in Streamlit
    columns = ["system_id", "system_name", "agency_name", "aia_status", "risk_category", "total_score", "last_modified_date"]
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
            aia_obj.__dict__.update(aia_data) # Populate object
            aia_obj.system_id = system_id # Ensure system_id is set on the object
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

    # Ensure calculations and timestamps are current
    aia_object._update_risk_assessment()
    aia_object.last_modified_date = datetime.datetime.now().isoformat()
    aia_json = json.dumps(aia_object.__dict__, ensure_ascii=False)

    # Extract key fields for indexed columns
    risk_category = aia_object.risk_category['category']
    total_score = aia_object.total_score
    aia_status = aia_object.aia_status
    pia_status = aia_object.related_assessment_statuses.get('PIA', 'Not Started')
    sec_status = aia_object.related_assessment_statuses.get('Security Assessment', 'Not Started')
    hr_status = aia_object.related_assessment_statuses.get('Human Rights Assessment', 'Not Started')
    # Add others as needed

    cursor.execute("""
    UPDATE ai_systems
    SET system_name = ?, agency_name = ?, aia_status = ?, risk_category = ?, total_score = ?,
        pia_status = ?, security_assessment_status = ?, human_rights_assessment_status = ?,
        last_modified_date = ?, aia_data = ?
    WHERE system_id = ?
    """, (
        aia_object.system_name, aia_object.agency_name, aia_status, risk_category, total_score,
        pia_status, sec_status, hr_status,
        aia_object.last_modified_date, aia_json,
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
    conn.row_factory = sqlite3.Row # Return rows as dict-like objects
    cursor = conn.cursor()

    try:
        # Example aggregations - add more as needed
        systems_by_status = cursor.execute("SELECT aia_status, COUNT(*) as count FROM ai_systems GROUP BY aia_status").fetchall()
        systems_by_risk = cursor.execute("SELECT risk_category, COUNT(*) as count FROM ai_systems GROUP BY risk_category").fetchall()
        systems_by_pia_status = cursor.execute("SELECT pia_status, COUNT(*) as count FROM ai_systems GROUP BY pia_status").fetchall()
        systems_by_sec_status = cursor.execute("SELECT security_assessment_status, COUNT(*) as count FROM ai_systems GROUP BY security_assessment_status").fetchall()
        total_systems = cursor.execute("SELECT COUNT(*) as count FROM ai_systems").fetchone()['count']

        # Convert results to simple dicts for easier processing
        dashboard_data = {
            "total_systems": total_systems,
            "by_status": {row['aia_status']: row['count'] for row in systems_by_status},
            "by_risk": {row['risk_category']: row['count'] for row in systems_by_risk},
            "by_pia_status": {row['pia_status']: row['count'] for row in systems_by_pia_status},
            "by_security_status": {row['security_assessment_status']: row['count'] for row in systems_by_sec_status},
            # Add more aggregated data here
        }
        return dashboard_data
    except Exception as e:
         print(f"Error fetching dashboard data: {e}")
         return None # Or return default structure
    finally:
         conn.close()


# Initialize the database when this module is imported
init_db()