# Vivi - Face Recognition Attendance System

A face recognition-based attendance system with a real-time webcam interface and dashboard.

## Features

- **Face Registration**: Register users with name and roll number via camera or photo upload
- **Face Attendance**: Mark attendance by scanning face
- **Real-time Attendance**: Live webcam-based attendance with automatic IN/OUT detection based on face position
- **Control Panel**: Web-based control panel to manage users and force OUT mode
- **Dashboard**: Next.js dashboard to view attendance analytics

## Requirements

- Python 3.9+
- Node.js 18+
- Bun (for Next.js)
- Webcam

## Installation

```bash
./install.sh
```

## Running

```bash
./run.sh
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Streamlit App | http://localhost:8501 | Main attendance UI |
| FastAPI Control Panel | http://localhost:8080 | User management |
| Next.js Dashboard | http://localhost:3000 | Attendance analytics |

## Project Structure

```
vivi/
├── attendence-system/    # Python attendance system
│   ├── app.py           # Streamlit app
│   ├── api.py           # FastAPI control panel
│   ├── database.py      # SQLite database
│   ├── face_utils.py    # Face recognition utilities
│   ├── attendance.py    # Attendance logic
│   └── requirements.txt # Python dependencies
├── dashboard/           # Next.js dashboard
│   ├── src/            # React components
│   └── package.json    # Node dependencies
├── install.sh          # Installation script
├── run.sh              # Run script
└── README.md           # This file
```

## Usage

1. Register users via the Streamlit app at http://localhost:8501
2. Take attendance using camera scan or real-time mode
3. View attendance records in the dashboard at http://localhost:3000
4. Manage users via the control panel at http://localhost:8080
