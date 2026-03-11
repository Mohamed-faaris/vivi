#!/bin/bash
set -e

echo "Installing dependencies..."

echo "Installing Bun..."
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
fi

echo "Creating database directory..."
mkdir -p attendence-system/database
touch attendence-system/database/attendance.db

echo "Installing system dependencies..."
sudo apt-get install -y --no-install-recommends libgl1 libglib2.0-0

echo "Creating .env file..."
cd dashboard
if [ ! -f .env ]; then
    cp .env.example .env
fi
cd ..

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
bun add clsx tailwind-merge

echo "Creating lib/utils.ts..."
mkdir -p src/lib
cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

echo "Installation complete!"
