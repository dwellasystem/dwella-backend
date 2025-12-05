#!/bin/bash

echo "🛑 Stopping Django server..."
pkill -f "manage.py runserver"

echo "🛑 Stopping Celery worker..."
pkill -f "celery -A api worker"

echo "🛑 Stopping Celery beat..."
pkill -f "celery -A api beat"

echo "✅ All dev services stopped."
