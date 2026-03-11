from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from database import init_db, get_connection, get_user_force_out, set_user_force_out, get_toggle_log
from attendance import mark_attendance

app = FastAPI()

DB_PATH = "database/attendance.db"
REGISTERED_FACES_DIR = "registered_faces"
PHOTOS_DIR = "photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll, photo, force_out FROM users")
    users = cursor.fetchall()
    conn.close()

    users_data = []
    for u in users:
        users_data.append({
            "id": u[0],
            "name": u[1],
            "roll": u[2],
            "photo": u[3],
            "force_out": u[4]
        })

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connection Control Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            body {{ background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ text-align: center; margin-bottom: 30px; color: #333; }}
            .user-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .user-photo {{ width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #ddd; }}
            .user-info {{ flex: 1; }}
            .user-name {{ font-size: 18px; font-weight: 600; color: #333; }}
            .user-roll {{ color: #666; font-size: 14px; }}
            .user-status {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
            .status-on {{ background: #d4edda; color: #155724; }}
            .status-off {{ background: #f8d7da; color: #721c24; }}
            .mark-out-btn {{ padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background 0.2s; }}
            .mark-out-btn.connect {{ background: #28a745; }}
            .mark-out-btn.connect:hover {{ background: #218838; }}
            .no-users {{ text-align: center; color: #666; padding: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Connection Control Panel</h1>
    """

    if not users_data:
        html += '<div class="no-users">No registered users</div>'
    else:
        for user in users_data:
            photo_path = user["photo"] if user["photo"] and os.path.exists(user["photo"]) else None
            photo_url = f"/photos/{os.path.basename(photo_path)}" if photo_path else "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Ccircle cx='40' cy='40' r='40' fill='%23ddd'/%3E%3Ctext x='40' y='45' text-anchor='middle' fill='%23999' font-size='30'%3E%3F%3C/text%3E%3C/svg%3E"
            
            connection_active = user["force_out"] == 0
            status_class = "status-on" if connection_active else "status-off"
            status_text = "Connected" if connection_active else "Disconnected"
            
            html += f"""
            <div class="user-card">
                <img src="{photo_url}" alt="{user['name']}" class="user-photo">
                <div class="user-info">
                    <div class="user-name">{user['name']}</div>
                    <div class="user-roll">{user['roll']}</div>
                    <span class="user-status {status_class}">{status_text}</span>
                </div>
                <button class="mark-out-btn {'connect' if connection_active else ''}" onclick="toggleConnection({user['id']}, {str(connection_active).lower()})">{ 'Disconnect' if connection_active else 'Connect' }</button>
            </div>
            """

    html += """
        </div>
        
        <div class="container" style="margin-top: 40px;">
            <h2>Connection History</h2>
            <table class="log-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
    """

    toggle_logs = get_toggle_log(20)
    for log in toggle_logs:
        status_text = "Connected" if log[2] == 0 else "Disconnected"
        status_class = "status-on" if log[2] == 0 else "status-off"
        html += f"""
            <tr>
                <td>{log[1]}</td>
                <td><span class="user-status {status_class}">{status_text}</span></td>
                <td>{log[3]}</td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
        
        <style>
            .log-table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; border-radius: 12px; overflow: hidden; }
            .log-table th, .log-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
            .log-table th { background: #f8f9fa; font-weight: 600; color: #333; }
            .log-table tr:hover { background: #f8f9fa; }
        </style>
        
        <script>
            async function toggleConnection(userId, currentlyConnected) {
                await fetch(`/toggle/${userId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({force_out: currentlyConnected ? 1 : 0})
                });
                location.reload();
            }

            async function markOut(userId) {
                await fetch(`/mark_out/${userId}`, {
                    method: 'POST'
                });
                alert('Marked OUT successfully!');
            }
        </script>
    </body>
    </html>
    """

    return html


@app.post("/toggle/{user_id}")
async def toggle_force_out(user_id: int, request: Request):
    data = await request.json()
    force_out = data.get("force_out", 0)
    set_user_force_out(user_id, force_out)
    return {"success": True}


@app.post("/mark_out/{user_id}")
async def mark_out(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        photo_path = os.path.join(PHOTOS_DIR, f"{user[0]}_out.jpg")
        mark_attendance(user_id, photo_path, "OUT")
    
    return {"success": True}


@app.get("/status")
async def get_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll, force_out FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return {
        "users": [
            {"id": u[0], "name": u[1], "roll": u[2], "force_out": bool(u[3])}
            for u in users
        ]
    }


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8080)
