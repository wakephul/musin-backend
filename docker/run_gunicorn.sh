#!/bin/bash

# Start Gunicorn with the --reload option
gunicorn --timeout 2000 --bind 0.0.0.0:5000 --workers 1 --reload api.api:api &
pid=$!

# Start watchdog to monitor the application source files for changes
watchmedo auto-restart \
    --recursive \
    --pattern '*.py' \
    --directory ./ \
    --ignore-pattern='*/.*' \
    --ignore-pattern='venv/*' \
    --signal SIGTERM \
    --signal SIGHUP \
    -- python -m gunicorn --reload api.api:api

# Kill Gunicorn when watchdog exits
kill $pid