#!/bin/bash

# Stop on errors
set -e

# -----------------------------
# Configuration
# -----------------------------
# Parses folder relative to script
PARSER_DIR="$(dirname "$0")/parser"

# Virtual environment path
VENV_DIR="$PARSER_DIR/.venv"

# Default flags (can override with command-line arguments)
COPY_FLAG=false
PRINT_FLAG=false

# -----------------------------
# Parse command-line arguments
# -----------------------------
for arg in "$@"; do
  case "$arg" in
    --should-copy) COPY_FLAG=true ;;
    --should-print) PRINT_FLAG=true ;;
    *)
      echo "Unknown option: $arg"
      echo "Usage $0 [--should-copy] [--should-print]"
      exit 1
      ;;
  esac
done

# -----------------------------
# Check parser folder
# -----------------------------
if [ ! -d "$PARSER_DIR" ]; then
  echo "Error: Parser directory not found in $PARSER_DIR"
  exit 1
fi

# -----------------------------
# Setup virtual environment
# -----------------------------
if [ -f "$VENV_DIR/bin/activate" ]; then
  echo "Activating existing virtual environment..."
else
  echo "Virtual environment not found. Creating ..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating venv ..."
source "$VENV_DIR/bin/activate"

echo "Updating pip ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip

echo "Installing dependencies ..."
"$VENV_DIR/bin/pip" install -r $PARSER_DIR/requirements.txt

# -----------------------------
# Run the Python script with selected flags
# -----------------------------
CMD="python $PARSER_DIR/main_get_all.py"
$COPY_FLAG && CMD="$CMD --should-copy"
$PRINT_FLAG && CMD="$CMD --should-print"

echo "Running command: $CMD"
$CMD

echo "Done."