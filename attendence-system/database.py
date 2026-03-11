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
        photo TEXT
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

    conn.commit()
    conn.close()
