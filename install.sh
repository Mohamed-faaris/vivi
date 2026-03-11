#!/bin/bash
set -e

echo "Installing dependencies..."

echo "Installing Bun..."
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
fi

echo "Creating Python virtual environment..."
cd attendence-system
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn

echo "Installing Node.js dependencies..."
cd ../dashboard
bun install

echo "Installation complete!"
