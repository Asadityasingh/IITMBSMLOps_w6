#!/bin/bash
set -e

echo "🚀 Starting Iris Classification API..."
echo "📊 Working directory: $(pwd)"
echo "📁 Files in /app: $(ls -la)"
echo "📊 Loading model from: /app/deploy/iris-model.pkl"

# Verify Flask app file exists
if [ ! -f "/app/app.py" ]; then
    echo "❌ Flask app not found at /app/app.py"
    echo "📁 Current files: $(ls -la /app/)"
    exit 1
fi

echo "✅ Flask app found!"
echo "🌐 Starting Gunicorn..."

# Run Gunicorn
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --worker-class gthread \
    --threads 4 \
    --timeout 60 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
