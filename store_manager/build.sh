#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Dependencies
# Render caches dependencies by default, so this will be fast on subsequent builds.
pip install -r requirements.txt

# 2. Collect Static Files
# This command gathers all static files (CSS, JS, images) into a single directory.
python manage.py collectstatic --no-input

# 3. Apply Database Migrations
# This ensures your database schema is up-to-date with your models.
python manage.py migrate