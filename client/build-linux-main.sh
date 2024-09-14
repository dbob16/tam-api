#!/bin/bash

cd "$(dirname "$0")"
pyinstaller --noconsole --onefile --hidden-import='PIL._tkinter_finder' main.py