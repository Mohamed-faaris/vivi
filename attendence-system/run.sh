#!/bin/bash
echo "Starting FastAPI server on port 8080..."
.venv/bin/python api.py &

echo "Starting Streamlit on port 8501..."
streamlit run app.py &

echo ""
echo "Servers running:"
echo "- FastAPI Control Panel: http://localhost:8080"
echo "- Streamlit App: http://localhost:8501"
