#!/bin/sh

echo "Setting up DB"
python -c "from src.server.db import setup_db; setup_db()"

echo "Running flask devserver"
flask run --host=0.0.0.0 --port=8000
