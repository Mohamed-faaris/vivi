#!/bin/bash
set -e

echo "Starting Vivi Attendance System..."

export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

echo "Starting FastAPI server on port 8080..."
cd attendence-system
source .venv/bin/activate
python api.py &
API_PID=$!

echo "Starting Streamlit on port 8501..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

echo "Starting Next.js dashboard on port 3000..."
cd ../dashboard
bun run dev --hostname 0.0.0.0 &
NEXT_PID=$!

echo ""
echo "All services started:"
echo "- FastAPI Control Panel: http://<your-ip>:8080"
echo "- Streamlit App: http://<your-ip>:8501"
echo "- Next.js Dashboard: http://<your-ip>:3000"
echo ""
echo "Press Ctrl+C to stop all services"

cleanup() {
    echo "Stopping services..."
    kill $API_PID $STREAMLIT_PID $NEXT_PID 2>/dev/null || true
}
trap cleanup SIGINT SIGTERM

wait
