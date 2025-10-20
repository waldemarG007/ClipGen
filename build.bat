@echo off
echo Building ClipGen...

pyinstaller --onefile --windowed --name ClipGen --icon=ClipGen.ico --add-data "libs;libs" ClipGen.py

echo Build complete.
explorer "dist"