#!/bin/sh
# simple-http-server.sh - a wrapper to run python's http.server

# Configuration
PORT=8000
PUBLIC_DIR="/var/www/waterplant"
PYTHON_EXEC="/home/clawd/WaterPlant/server/.venv/bin/python3"

echo "Starting HTTP server on port $PORT, serving from $PUBLIC_DIR"

cd $PUBLIC_DIR
exec $PYTHON_EXEC -m http.server $PORT
