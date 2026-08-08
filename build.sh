#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Database schema migrations & static file asset collection
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Optional seed demo data on explicit environment request
if [ "$SEED_DEMO_DATA" = "true" ] || [ "$SEED_DEMO_DATA" = "1" ]; then
    python manage.py seed_data
fi
