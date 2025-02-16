#!/bin/bash

cd "$(dirname "$0")"
pyinstaller --noconsole --contents-directory='tam' --hidden-import='PIL._tkinter_finder' --icon='icon.ico' main.py
pyinstaller --contents-directory='tam' --icon='icon.ico' backup_restore.py

cp icon.png dist/backup_restore/backup_restore dist/main/
mv dist/main/backup_restore dist/main/tam-backup-restore
mv dist/main/main dist/main/tam-client