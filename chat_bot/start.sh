#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8080}

echo "Starting application on port $PORT"
echo "Environment variables:"
echo "PORT: $PORT"
echo "FLASK_ENV: $FLASK_ENV"
echo "PYTHONPATH: $PYTHONPATH"

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    ls -la
    exit 1
fi

# Check if requirements are installed
python -c "import flask, openai, gunicorn" 2>/dev/null || {
    echo "ERROR: Required packages not installed!"
    pip list
    exit 1
}

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app
