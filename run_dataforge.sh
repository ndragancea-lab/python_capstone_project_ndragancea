#!/bin/bash
# DataForge Runner Script
# Automatically activates venv and runs dataforge

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run dataforge with all passed arguments
python -m dataforge "$@"

# Deactivate is automatic when script ends

