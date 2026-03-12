#!/bin/bash
set -e

echo "Installing dependencies..."

export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
export PATH="$BUN_INSTALL/bin:$PATH"

is_command_installed() {
  command -v "$1" >/dev/null 2>&1
}

echo "Installing Bun..."
if ! is_command_installed bun; then
    curl -fsSL https://bun.sh/install | bash
    export PATH="$BUN_INSTALL/bin:$PATH"
else
  echo "Bun is already installed."
fi

echo "Installing Node.js CLI tools..."
if ! is_command_installed kilocode; then
  bun add -g @kilocode/cli
else
  echo "KiloCode CLI is already installed."
fi

echo "Installing OpenCode..."
if ! is_command_installed opencode; then
  curl -fsSL https://opencode.ai/install | bash
else
  echo "OpenCode is already installed."
fi

echo "Creating database directory..."
mkdir -p attendence-system/database
if [ ! -f attendence-system/database/attendance.db ]; then
  touch attendence-system/database/attendance.db
fi

echo "Installing system dependencies..."
MISSING_APT_PACKAGES=()
for package in libgl1 libglib2.0-0; do
  if ! dpkg -s "$package" >/dev/null 2>&1; then
    MISSING_APT_PACKAGES+=("$package")
  fi
done

if [ "${#MISSING_APT_PACKAGES[@]}" -gt 0 ]; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends "${MISSING_APT_PACKAGES[@]}"
else
  echo "System dependencies are already installed."
fi

echo "Creating .env file..."
cd dashboard
if [ ! -f .env ]; then
    cp .env.example .env
else
  echo ".env already exists."
fi
cd ..

echo "Creating Python virtual environment..."
cd attendence-system
if [ ! -d .venv ]; then
  python3 -m venv .venv
else
  echo "Virtual environment already exists."
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python dependencies..."
python -m pip install --upgrade pip

MISSING_PY_REQUIREMENTS=()
while IFS= read -r requirement || [ -n "$requirement" ]; do
  requirement="${requirement%%#*}"
  requirement="$(echo "$requirement" | xargs)"

  if [ -z "$requirement" ]; then
    continue
  fi

  package_name="${requirement%%[<>=!~]*}"
  if ! python -m pip show "$package_name" >/dev/null 2>&1; then
    MISSING_PY_REQUIREMENTS+=("$requirement")
  fi
done < requirements.txt

if [ "${#MISSING_PY_REQUIREMENTS[@]}" -gt 0 ]; then
  python -m pip install "${MISSING_PY_REQUIREMENTS[@]}"
else
  echo "Requirements from requirements.txt are already installed."
fi

for package in fastapi uvicorn; do
  if ! python -m pip show "$package" >/dev/null 2>&1; then
    python -m pip install "$package"
  else
    echo "Python package '$package' is already installed."
  fi
done

echo "Installing face_recognition_models..."
if ! python -m pip show face_recognition_models >/dev/null 2>&1; then
  python -m pip install git+https://github.com/ageitgey/face_recognition_models
else
  echo "face_recognition_models is already installed."
fi

echo "Installing Node.js dependencies..."
cd ../dashboard
if [ ! -d node_modules ]; then
  bun install
else
  echo "Node.js dependencies are already installed."
fi

echo "Creating lib/utils.ts..."
mkdir -p src/lib
if [ ! -f src/lib/utils.ts ]; then
cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF
else
  echo "src/lib/utils.ts already exists."
fi

echo "Installation complete!"
