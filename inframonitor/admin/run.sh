#!/bin/bash

gunicorn --workers=2 \
  --bind=":80" \
  --access-logfile '-' \
  "admin.wsgi:app" &

PID=$!

trap 'kill -SIGTERM $PID; exit 0' SIGTERM
wait $PID
