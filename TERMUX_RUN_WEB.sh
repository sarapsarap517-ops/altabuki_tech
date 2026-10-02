#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
flet run --web main.py
