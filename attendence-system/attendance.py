import datetime
from database import get_connection


def mark_attendance(user_id, photo_path, status_override=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT status FROM attendance
    WHERE user_id = ?
    ORDER BY id DESC LIMIT 1
    """, (user_id,))

    last = cursor.fetchone()

    if status_override is not None:
        status = status_override
        if last and last[0] == status:
            conn.close()
            return None, None
    elif last and last[0] == "IN":
        status = "OUT"
    else:
        status = "IN"

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO attendance(user_id,timestamp,status,photo)
    VALUES(?,?,?,?)
    """, (user_id, time, status, photo_path))

    conn.commit()
    conn.close()

    return status, time
