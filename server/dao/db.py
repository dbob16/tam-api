import os
from sqlite3 import connect as l_connect
from mysql.connector import connect as m_connect

DB_TYPE = os.getenv("DB_TYPE", "LOCAL")

def rand():
    if DB_TYPE == "LOCAL":
        return "random()"
    elif DB_TYPE == "MARIADB":
        return "rand()"

def session():
    if DB_TYPE == "LOCAL":
        conn = l_connect("data.db")
        cur = conn.cursor()
        return conn, cur
    elif DB_TYPE == "MARIADB":
        MARIADB_HOST = os.getenv("MARIADB_HOST", "db")
        MARIADB_PORT = os.getenv("MARIADB_PORT", 3306)
        MARIADB_USER = os.getenv("MARIADB_USER", "tam")
        MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "password")
        MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "tam")
        try:
            MARIADB_PORT = int(MARIADB_PORT)
        except:
            print("Port number needs to be a whole number.")
        conn = m_connect(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DATABASE
        )
        cur = conn.cursor()
        return conn, cur