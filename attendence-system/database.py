import sqlite3

DB_PATH = "database/attendance.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll TEXT,
        encoding BLOB,
        photo TEXT,
        force_out INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT,
        status TEXT,
        photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS toggle_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        force_out INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_user_force_out(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT force_out FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def set_user_force_out(user_id, force_out):
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET force_out = ? WHERE id = ?", (force_out, user_id))
    cursor.execute(
        "INSERT INTO toggle_log(user_id, force_out, timestamp) VALUES(?, ?, ?)",
        (user_id, force_out, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_toggle_log(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, u.name, t.force_out, t.timestamp
        FROM toggle_log t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.timestamp DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results
