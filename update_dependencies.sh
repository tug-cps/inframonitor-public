#!/bin/bash

echo "Upgrading pip..."
pip install --upgrade pip

if [ ! "$(which pip-compile)" ]; then
  echo "Pip compile not found, installing..."
  pip install pip-tools
fi

echo "Collecting dependencies..."

rm "requirements.in"

for d in inframonitor/*/; do
  if [ -f "$d/requirements.in" ]; then
    { echo "### $d" ; cat "$d/requirements.in"; echo ""; } >> requirements.in
  fi
done

echo "Upgrading dependency files..."

echo "  requirements.in -> requirements.txt"
pip-compile --upgrade -q

echo "  test-requirements.in -> test-requirements.txt"
pip-compile --upgrade -q test-requirements.in

for d in inframonitor/*/; do
  if [ -f "$d/requirements.in" ]; then
    echo "  ${d}requirements.in -> ${d}requirements.txt"
    pip-compile --upgrade -q "$d/requirements.in" --output-file="$d/requirements.txt"
  fi
done

echo "Syncing dependencies..."
pip-sync requirements.txt test-requirements.txt

echo "Done."
