#!/bin/bash

echo "Building ClipGen..."

# Determine the correct separator for --add-data
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    SEPARATOR=";"
else
    SEPARATOR=":"
fi

pyinstaller --onefile --windowed --name ClipGen --icon=ClipGen.ico --add-data "libs${SEPARATOR}libs" ClipGen.py

echo "Build complete."

# Open the output directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    open dist
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open dist
fi