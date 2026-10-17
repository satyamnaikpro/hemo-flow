#!/bin/bash
set -e

echo "Creating isolated virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing requirements inside venv..."
pip install -r requirements.txt

echo "Collecting static assets into staticfiles_build/static..."
python manage.py collectstatic --noinput --clear

echo "Static assets successfully collected:"
ls -la staticfiles_build/static/

echo "Build finished successfully!"
