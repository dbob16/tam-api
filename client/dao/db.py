import sqlite3
import os

if os.path.exists("data.db"):
    db_file_path = "data.db"
elif os.name == "nt":
    home_path = os.getenv("APPDATA")
    if not os.path.exists(f"{home_path}\\TAM"):
        os.mkdir(f"{home_path}\\TAM")
    db_file_path = f"{home_path}\\TAM\\data.db"
else:
    home_path = os.path.expanduser("~")
    if not os.path.exists(f"{home_path}/.config/TAM"):
        os.mkdir(f"{home_path}/.config/TAM")
    db_file_path = f"{home_path}/.config/TAM/data.db"

def session():
    conn = sqlite3.connect(db_file_path)
    cur = conn.cursor()
    return conn, cur