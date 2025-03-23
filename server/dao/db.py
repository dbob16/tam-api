import os
import string
import random
from fastapi import Request
from sqlite3 import connect as l_connect
from mysql.connector import connect as m_connect

DB_TYPE = os.getenv("DB_TYPE", "LOCAL")
API_PW = os.getenv("API_PW", None)
SS_MODE = os.getenv("SS_MODE", "off")

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

def create_api_key():
    rnd_str = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(rnd_str) for i in range(0, 16))

def check_api_key(in_key:str, request:Request):
    if 'x-real-ip' in request.headers:
        client_ip = request.headers['x-real-ip']
    else:
        client_ip = request.client.host
    conn, cur = session()
    if SS_MODE != "off":
        cur.execute(f"SELECT api_key from api_keys WHERE api_key = \"{in_key}\" AND ip_addr = \"{client_ip}\"")
    else:
        cur.execute(f"SELECT api_key from api_keys WHERE api_key = \"{in_key}\"")
    result = cur.fetchone()
    if result:
        return True
    else:
        return False

def db_init():
    with open('schema.sql', 'r') as f:
        contents = f.read()
        db_schema = contents.split(';')
    conn, cur = session()
    for stmt in db_schema:
        cur.execute(stmt)
    conn.commit()
    conn.close()