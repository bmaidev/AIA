"""
Canberra Charities Database Manager
Manages SQLite database for 350+ ACT charities and not-for-profits.
Supporting Hands Across Canberra x Black Mountain AI strategic partnership.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "canberra_charities.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS charities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            abn TEXT,
            acnc_registered INTEGER DEFAULT 1,
            registration_status TEXT DEFAULT 'Registered',
            charity_size TEXT DEFAULT 'Unknown',
            established_date TEXT,

            -- Sector and purpose
            sector TEXT,
            sub_sector TEXT,
            acnc_subtype TEXT,
            purpose TEXT,
            mission_statement TEXT,
            clients_served TEXT,
            service_area TEXT DEFAULT 'ACT',

            -- Contact
            website TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            suburb TEXT,
            postcode TEXT,

            -- Leadership
            ceo_name TEXT,
            ceo_title TEXT DEFAULT 'CEO',
            ceo_email TEXT,
            ceo_linkedin TEXT,

            -- Board
            board_chair TEXT,
            board_members TEXT,  -- JSON array
            board_size INTEGER,
            board_last_verified TEXT,

            -- Membership
            membership_count INTEGER,
            membership_type TEXT,
            staff_count INTEGER,
            volunteer_count INTEGER,

            -- Technology
            technology_systems TEXT,  -- JSON object
            website_platform TEXT,
            crm_system TEXT,
            accounting_system TEXT,
            case_management_system TEXT,
            email_platform TEXT,
            social_media TEXT,  -- JSON object

            -- Functions
            core_functions TEXT,  -- JSON array
            service_types TEXT,  -- JSON array
            funding_sources TEXT,  -- JSON array

            -- Hands Across Canberra
            hac_member INTEGER DEFAULT 0,
            hac_grant_recipient INTEGER DEFAULT 0,

            -- Data quality
            data_completeness REAL DEFAULT 0.0,
            last_verified TEXT,
            data_sources TEXT,  -- JSON array
            notes TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS board_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            charity_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'Director',
            title TEXT,
            bio TEXT,
            linkedin TEXT,
            current INTEGER DEFAULT 1,
            start_date TEXT,
            end_date TEXT,
            verified_date TEXT,
            FOREIGN KEY (charity_id) REFERENCES charities(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS charity_functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            charity_id INTEGER NOT NULL,
            function_category TEXT NOT NULL,
            function_name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (charity_id) REFERENCES charities(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            parent_sector TEXT,
            charity_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS function_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            shared_innovation_potential TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_charities_sector ON charities(sector);
        CREATE INDEX IF NOT EXISTS idx_charities_name ON charities(name);
        CREATE INDEX IF NOT EXISTS idx_charities_suburb ON charities(suburb);
        CREATE INDEX IF NOT EXISTS idx_charities_hac ON charities(hac_member);
        CREATE INDEX IF NOT EXISTS idx_board_charity ON board_members(charity_id);
        CREATE INDEX IF NOT EXISTS idx_functions_charity ON charity_functions(charity_id);
    """)

    conn.commit()
    conn.close()


def add_charity(data):
    """Add a charity to the database. data is a dict matching column names."""
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate data completeness
    fields_to_check = ['name', 'abn', 'sector', 'purpose', 'website', 'email',
                       'phone', 'address', 'ceo_name', 'board_chair']
    filled = sum(1 for f in fields_to_check if data.get(f))
    data['data_completeness'] = filled / len(fields_to_check)
    data['updated_at'] = datetime.now().isoformat()

    # JSON encode list/dict fields
    json_fields = ['board_members', 'technology_systems', 'social_media',
                   'core_functions', 'service_types', 'funding_sources', 'data_sources']
    for field in json_fields:
        if field in data and isinstance(data[field], (list, dict)):
            data[field] = json.dumps(data[field])

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    values = list(data.values())

    cursor.execute(f"INSERT INTO charities ({columns}) VALUES ({placeholders})", values)
    charity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return charity_id


def update_charity(charity_id, data):
    """Update a charity record."""
    conn = get_connection()
    cursor = conn.cursor()

    data['updated_at'] = datetime.now().isoformat()

    json_fields = ['board_members', 'technology_systems', 'social_media',
                   'core_functions', 'service_types', 'funding_sources', 'data_sources']
    for field in json_fields:
        if field in data and isinstance(data[field], (list, dict)):
            data[field] = json.dumps(data[field])

    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [charity_id]

    cursor.execute(f"UPDATE charities SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_charity(charity_id):
    """Get a single charity by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM charities WHERE id = ?", (charity_id,)).fetchone()
    conn.close()
    if row:
        return _row_to_dict(row)
    return None


def get_all_charities():
    """Get all charities."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM charities ORDER BY name").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_charities(query=None, sector=None, suburb=None, hac_member=None,
                     has_ceo=None, has_board=None, min_completeness=None):
    """Search charities with filters."""
    conn = get_connection()
    conditions = []
    params = []

    if query:
        conditions.append("(name LIKE ? OR purpose LIKE ? OR clients_served LIKE ?)")
        q = f"%{query}%"
        params.extend([q, q, q])

    if sector:
        conditions.append("sector = ?")
        params.append(sector)

    if suburb:
        conditions.append("suburb = ?")
        params.append(suburb)

    if hac_member is not None:
        conditions.append("hac_member = ?")
        params.append(1 if hac_member else 0)

    if has_ceo:
        conditions.append("ceo_name IS NOT NULL AND ceo_name != ''")

    if has_board:
        conditions.append("board_chair IS NOT NULL AND board_chair != ''")

    if min_completeness is not None:
        conditions.append("data_completeness >= ?")
        params.append(min_completeness)

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM charities WHERE {where} ORDER BY name"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_sectors():
    """Get all unique sectors with counts."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT sector, COUNT(*) as count
        FROM charities
        WHERE sector IS NOT NULL AND sector != ''
        GROUP BY sector
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [(r['sector'], r['count']) for r in rows]


def get_statistics():
    """Get database statistics."""
    conn = get_connection()
    stats = {}

    stats['total_charities'] = conn.execute("SELECT COUNT(*) FROM charities").fetchone()[0]
    stats['with_ceo'] = conn.execute("SELECT COUNT(*) FROM charities WHERE ceo_name IS NOT NULL AND ceo_name != ''").fetchone()[0]
    stats['with_board'] = conn.execute("SELECT COUNT(*) FROM charities WHERE board_chair IS NOT NULL AND board_chair != ''").fetchone()[0]
    stats['with_website'] = conn.execute("SELECT COUNT(*) FROM charities WHERE website IS NOT NULL AND website != ''").fetchone()[0]
    stats['with_email'] = conn.execute("SELECT COUNT(*) FROM charities WHERE email IS NOT NULL AND email != ''").fetchone()[0]
    stats['hac_members'] = conn.execute("SELECT COUNT(*) FROM charities WHERE hac_member = 1").fetchone()[0]
    stats['avg_completeness'] = conn.execute("SELECT AVG(data_completeness) FROM charities").fetchone()[0] or 0

    # Sector breakdown
    rows = conn.execute("""
        SELECT sector, COUNT(*) as count
        FROM charities WHERE sector IS NOT NULL AND sector != ''
        GROUP BY sector ORDER BY count DESC
    """).fetchall()
    stats['by_sector'] = {r['sector']: r['count'] for r in rows}

    # Size breakdown
    rows = conn.execute("""
        SELECT charity_size, COUNT(*) as count
        FROM charities WHERE charity_size IS NOT NULL
        GROUP BY charity_size ORDER BY count DESC
    """).fetchall()
    stats['by_size'] = {r['charity_size']: r['count'] for r in rows}

    conn.close()
    return stats


def get_all_functions():
    """Get all unique functions across charities."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT function_category, function_name, COUNT(*) as charity_count
        FROM charity_functions
        GROUP BY function_category, function_name
        ORDER BY function_category, charity_count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_board_member(charity_id, name, role="Director", **kwargs):
    """Add a board member to a charity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO board_members (charity_id, name, role, title, bio, linkedin, verified_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (charity_id, name, role, kwargs.get('title'), kwargs.get('bio'),
          kwargs.get('linkedin'), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_board_members(charity_id):
    """Get board members for a charity."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM board_members
        WHERE charity_id = ? AND current = 1
        ORDER BY role, name
    """, (charity_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_charity(charity_id):
    """Delete a charity and related records."""
    conn = get_connection()
    conn.execute("DELETE FROM board_members WHERE charity_id = ?", (charity_id,))
    conn.execute("DELETE FROM charity_functions WHERE charity_id = ?", (charity_id,))
    conn.execute("DELETE FROM charities WHERE id = ?", (charity_id,))
    conn.commit()
    conn.close()


def _row_to_dict(row):
    """Convert a sqlite3.Row to a dict, parsing JSON fields."""
    d = dict(row)
    json_fields = ['board_members', 'technology_systems', 'social_media',
                   'core_functions', 'service_types', 'funding_sources', 'data_sources']
    for field in json_fields:
        if field in d and d[field] and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def export_to_dataframe():
    """Export all charities as a pandas DataFrame."""
    import pandas as pd
    charities = get_all_charities()
    if not charities:
        return pd.DataFrame()

    # Flatten JSON fields for spreadsheet
    rows = []
    for c in charities:
        row = {k: v for k, v in c.items()
               if not isinstance(v, (list, dict))}

        # Flatten core functions
        if isinstance(c.get('core_functions'), list):
            row['core_functions'] = '; '.join(c['core_functions'])
        if isinstance(c.get('service_types'), list):
            row['service_types'] = '; '.join(c['service_types'])
        if isinstance(c.get('funding_sources'), list):
            row['funding_sources'] = '; '.join(c['funding_sources'])
        if isinstance(c.get('data_sources'), list):
            row['data_sources'] = '; '.join(c['data_sources'])

        # Flatten technology
        if isinstance(c.get('technology_systems'), dict):
            for tk, tv in c['technology_systems'].items():
                row[f'tech_{tk}'] = tv

        # Flatten social media
        if isinstance(c.get('social_media'), dict):
            for sk, sv in c['social_media'].items():
                row[f'social_{sk}'] = sv

        # Flatten board members
        if isinstance(c.get('board_members'), list):
            row['board_members'] = '; '.join(c['board_members'])

        rows.append(row)

    df = pd.DataFrame(rows)
    return df
