from fastapi import Request
import os
import dotenv
import string
import random

dotenv.load_dotenv('.env')
dotenv.load_dotenv('.env.secret')
DB_TYPE = os.getenv("DB_TYPE", "LOCAL")
API_PW = os.getenv("API_PW", None)
SS_MODE = os.getenv("SS_MODE", "off")

if DB_TYPE == "LOCAL":
    from sqlite3 import connect

if DB_TYPE == "MYSQL":
    from mysql.connector import connect
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mariadb")
    MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
    MYSQL_USER = os.getenv("MYSQL_USER", "tam")
    MYSQL_PASSWD = os.getenv("MYSQL_PASSWD", "password")
    MYSQL_DB = os.getenv("MYSQL_DB", "tam")

def session():
    if DB_TYPE == "LOCAL":
        conn = connect('data.db')
        cur = conn.cursor()
        return conn, cur
    elif DB_TYPE == "MYSQL":
        conn = connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWD,
            database=MYSQL_DB
        )
        cur = conn.cursor()
        return conn, cur


def rand():
    if DB_TYPE == "LOCAL":
        return "random()"
    elif DB_TYPE == "MYSQL":
        return "rand()"

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