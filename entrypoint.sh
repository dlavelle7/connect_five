#!/bin/sh

echo "Setting up DB"
python -c "from src.server.db import setup_db; setup_db()"

# run gunicorn wsgi server with 2 worker processes on port 8000 in container
echo "Starting gunicorn wsgi server."
gunicorn src.server.app:app -w 2 -b :8000
