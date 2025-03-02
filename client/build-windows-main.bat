@echo off

cd /d "%~dp0"

pyinstaller --clean ^
 --contents-directory="tam" --hidden-import="PIL._tkinter_finder" ^
 --icon="icon.ico" --add-data="icon.png;." ^
 main.py

move dist\main\main.exe dist\main\tam-client.exe