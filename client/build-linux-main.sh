#!/bin/bash

cd "$(dirname "$0")"
pyinstaller --clean --noconsole \
 --contents-directory='tam' --hidden-import='PIL._tkinter_finder' \
 --icon='icon.ico' --add-data='icon.png:.' --add-data='templates:.' \
  main.py

mv dist/main/main dist/main/tam-client