#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate virtual environment (adjust path if needed)
source venv/bin/activate

cd api

# Start Django server
echo "🚀 Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

# Start Celery worker
echo "⚙️  Starting Celery worker..."
celery -A api worker --loglevel=info &

# Start Celery beat scheduler
echo "⏰ Starting Celery beat..."
celery -A api beat --loglevel=info &

# Wait for all processes
wait
