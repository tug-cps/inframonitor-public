#!/bin/bash

python -u -m $service_name.run &
PID=$!

trap 'kill -SIGTERM $PID; exit 0' SIGTERM
wait $PID
