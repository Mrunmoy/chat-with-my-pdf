#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Name of your venv folder
VENV_DIR="venv"

echo "🔍 Checking for virtual environment..."

# If venv doesn't exist, create it
if [ ! -d "$VENV_DIR" ]; then
  echo "No virtual environment found. Creating one..."
  python3 -m venv $VENV_DIR
fi

# Activate the venv
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source $VENV_DIR/bin/activate

echo "Virtual environment activated."

# Install requirements
if [ -f "requirements.txt" ]; then
  echo "Installing requirements from requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
  echo "All requirements installed."
else
  echo "No requirements.txt found. Skipping installation."
fi
