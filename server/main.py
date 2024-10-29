from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import string
import dotenv
import os

dotenv.load_dotenv('.env')
dotenv.load_dotenv('.env.secret')
DB_TYPE = os.getenv("DB_TYPE", "LOCAL")
API_PW = os.getenv("API_PW", None)

if DB_TYPE == "LOCAL":
    from sqlite3 import connect

if DB_TYPE == "MYSQL":
    from mysql.connector import connect
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mariadb")
    MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
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

class Prefix(BaseModel):
    prefix: str
    bootstyle: str
    sort_order: int

class Ticket(BaseModel):
    ticket_id: int
    first_name: str
    last_name: str
    phone_number: str
    preference: str

class Basket(BaseModel):
    basket_id: int
    description: str
    donors: str
    winning_ticket: int

class ApiRequest(BaseModel):
    inp_pw: str
    pc_name: str

templates = Jinja2Templates(directory="templates")

def create_api_key():
    rnd_str = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(rnd_str) for i in range(0, 16))

def check_api_key(in_key:str):
    conn, cur = session()
    cur.execute(f"SELECT api_key from api_keys WHERE api_key = \"{in_key}\"")
    result = cur.fetchone()
    if result:
        return True
    else:
        return False

conn, cur = session()
cur.execute("CREATE TABLE IF NOT EXISTS prefixes (prefix VARCHAR(150) PRIMARY KEY, bootstyle VARCHAR(150) NOT NULL, sort_order INT DEFAULT 1)")
cur.execute("CREATE TABLE IF NOT EXISTS api_keys (api_key VARCHAR(255) PRIMARY KEY, pc_name VARCHAR(255))")
conn.commit()
conn.close()

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/")
def index(api_key:str=None):
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return {"whoami": "TAM-Server"}

@app.get("/health/")
def health_check():
    return {"status": "healthy"}

@app.get("/api_keys/")
def get_api_keys(api_key:str=None):
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute("SELECT * FROM api_keys ORDER BY pc_name")
    conn.close()
    results = cur.fetchall()
    if not results:
        return []
    r_l = []
    for r in results:
        r_d = {"api_key": r[0], "pc_name": r[1]}
        r_l.append(r_d)
    return r_l

@app.post("/genapi/")
def gen_api(in_req:ApiRequest):
    if API_PW and API_PW != in_req.inp_pw:
        raise HTTPException(status_code=401, detail="Password is not correct")
    rtn_key = create_api_key()
    conn, cur = session()
    cur.execute(f"INSERT INTO api_keys (api_key, pc_name) VALUES (\"{rtn_key}\", \"{in_req.pc_name}\")")
    conn.commit()
    conn.close()
    return {"api_key": rtn_key}

@app.delete("/delapi/")
def del_api(auth_key:str=None, api_key:str=None, pc_name:str=None):
    if API_PW and not check_api_key(auth_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if api_key and pc_name:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE api_key = \"{api_key}\" AND pc_name = \"{pc_name}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {api_key} and {pc_name}"}
    elif api_key:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE api_key = \"{api_key}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {api_key}"}
    elif pc_name:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE pc_name = \"{pc_name}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {pc_name}"}
    else:
        return {"success": False, "response": "Nothing provided, can't act"}

@app.get("/prefixes/")
def list_prefixes(api_key:str=None):
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute("SELECT * FROM prefixes ORDER BY sort_order, prefix")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"prefix": r[0], "bootstyle": r[1], "sort_order": r[2]}
            r_l.append(r_d)
        return r_l

@app.get("/prefixes/{prefix}/")
def get_prefix(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM prefixes WHERE prefix = '{prefix}'")
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    else:
        r_d = {"prefix": r[0], "bootstyle": r[1], "sort_order": r[2]}
        return r_d

@app.post("/prefix/")
def post_prefix(prefix:Prefix, api_key:str=None):
    prefix.prefix = prefix.prefix.lower()
    prefix.bootstyle = prefix.bootstyle.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        cur.execute(f"CREATE TABLE IF NOT EXISTS `{prefix.prefix}_tickets` (ticket_id INT PRIMARY KEY, first_name VARCHAR(200), last_name VARCHAR(200), phone_number VARCHAR(200), preference VARCHAR(100))")
        cur.execute(f"CREATE TABLE IF NOT EXISTS `{prefix.prefix}_baskets` (basket_id INT PRIMARY KEY, description VARCHAR(255), donors VARCHAR(255), winning_ticket INT)")
        cur.execute(f"REPLACE INTO prefixes (prefix, bootstyle, sort_order) VALUES ('{prefix.prefix}', '{prefix.bootstyle}', {prefix.sort_order})")
        conn.commit()
        conn.close()
        return {"success": True, "created_prefix": f"{prefix.prefix} | {prefix.bootstyle} | {prefix.sort_order}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.delete("/delprefix/")
def delete_prefix(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"DELETE FROM prefixes WHERE prefix = \"{prefix}\"")
    conn.commit()
    conn.close()
    return {"success": True, "result": f"Deleted {prefix} from the prefixes table"}

@app.get("/tickets/{prefix}/")
def get_all_tickets(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_tickets` ORDER BY ticket_id")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
            r_l.append(r_d)
        return r_l

@app.get("/tickets/{prefix}/{ticket_id}/")
def get_single_ticket(prefix:str, ticket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_tickets` WHERE ticket_id={ticket_id}")
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    else:
        r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
        return r_d

@app.get("/tickets/{prefix}/{id_from}/{id_to}/")
def get_range_tickets(prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_tickets` WHERE ticket_id BETWEEN {id_from} AND {id_to}")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
            r_l.append(r_d)
        return r_l

@app.get("/random/tickets/{prefix}/")
def get_random_ticket(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_tickets` ORDER BY {rand()} LIMIT 1")
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    else:
        return {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}

@app.post("/ticket/{prefix}/")
def post_ticket(prefix:str, t:Ticket, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        cur.execute(f"REPLACE INTO `{prefix}_tickets` (ticket_id, first_name, last_name, phone_number, preference) VALUES ({t.ticket_id}, \"{t.first_name}\", \"{t.last_name}\", \"{t.phone_number}\", \"{t.preference}\")")
        conn.commit()
        conn.close()
        return {"success": True, "posted_ticket": f"Prefix: {prefix} Details: {t.ticket_id} {t.first_name} {t.last_name} {t.phone_number} {t.preference}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.get("/baskets/{prefix}/")
def get_all_baskets(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_baskets` ORDER BY basket_id")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
            r_l.append(r_d)
        return r_l

@app.get("/baskets/{prefix}/{basket_id}/")
def get_single_basket(prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_baskets` WHERE basket_id = {basket_id}")
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    else:
        r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
        return r_d

@app.get("/baskets/{prefix}/{id_from}/{id_to}/")
def get_range_baskets(prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_baskets` WHERE basket_id BETWEEN {id_from} AND {id_to} ORDER BY basket_id")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
            r_l.append(r_d)
        return r_l

@app.post("/basket/{prefix}/")
def post_basket(prefix:str, b:Basket, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        cur.execute(f"REPLACE INTO `{prefix}_baskets` (basket_id, description, donors, winning_ticket) VALUES ({b.basket_id}, \"{b.description}\", \"{b.donors}\", {b.winning_ticket})")
        conn.commit()
        conn.close()
        return {"success": True, "posted_basket": f"Prefix: {prefix} Details: {b.basket_id} {b.description} {b.donors} {b.winning_ticket}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.get("/combined/{prefix}/")
def combined_all(prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `{prefix}_baskets` b
    INNER JOIN `{prefix}_tickets` t
    ON b.winning_ticket = t.ticket_id
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    conn.close()
    if results:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
            r_l.append(r_d)
        return r_l
    else:
        return []

@app.get("/combined/{prefix}/{basket_id}/")
def combined_single(prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `{prefix}_baskets` b
    INNER JOIN `{prefix}_tickets` t
    ON b.winning_ticket = t.ticket_id
    WHERE basket_id = {basket_id}
    ORDER BY b.basket_id""")
    r = cur.fetchone()
    conn.close()
    if r:
        r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
        return r_d
    else:
        return []

@app.get("/combined/{prefix}/{id_from}/{id_to}/")
def combined_range(prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `{prefix}_baskets` b
    INNER JOIN `{prefix}_tickets` t
    ON b.winning_ticket = t.ticket_id
    WHERE basket_id BETWEEN {id_from} AND {id_to}
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    conn.close()
    if results:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
            r_l.append(r_d)
        return r_l
    else:
        return []

@app.get("/reports/byname/{prefix}/", response_class=HTMLResponse)
def report_byname(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    if filter == None:
        select_title = "Winners - All Preferences"
        filter_line = ""
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        filter_line = "WHERE t.preference = \"CALL\""
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        filter_line = "WHERE t.preference = \"TEXT\""
    cur.execute(f"""SELECT CONCAT(t.last_name, \", \", t.first_name) as last_first, t.phone_number, b.basket_id, b.winning_ticket, b.description
    FROM `{prefix}_baskets` b INNER JOIN `{prefix}_tickets` t ON b.winning_ticket = t.ticket_id
    {filter_line}
    ORDER BY last_first, t.phone_number, b.basket_id""")
    results = cur.fetchall()
    conn.close()
    headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
    return templates.TemplateResponse(request=request, name="byname.html", context={"prefix": prefix.capitalize(), "title": select_title, "headers": headers, "records": results})

@app.get("/reports/bybasket/{prefix}/", response_class=HTMLResponse)
def report_bybasket(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    if filter == None:
        select_title = "Winners - All Preferences"
        filter_line = ""
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        filter_line = "WHERE t.preference = \"CALL\""
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        filter_line = "WHERE t.preference = \"TEXT\""
    cur.execute(f"""SELECT b.basket_id, b.description, b.winning_ticket, CONCAT(t.last_name, \", \", t.first_name) AS last_first, t.phone_number
    FROM `{prefix}_baskets` b INNER JOIN `{prefix}_tickets` t ON b.winning_ticket = t.ticket_id
    {filter_line}
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    conn.close()
    headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
    return templates.TemplateResponse(request=request, name="bybasket.html", context={"prefix": prefix.capitalize(), "title": select_title, "headers": headers, "records": results})

@app.get("/reports/counts/", response_class=HTMLResponse)
def get_counts(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    conn, cur = session()
    cur.execute("SELECT prefix FROM prefixes ORDER BY sort_order")
    prefixes = [[v[0]] for v in cur.fetchall()]
    for l in prefixes:
        cur.execute(f"SELECT COUNT(*) FROM `{l[0]}_tickets`")
        l.append(cur.fetchone()[0])
        cur.execute(f"SELECT COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) FROM `{l[0]}_tickets`")
        l.append(cur.fetchone()[0])
        l[0] = l[0].capitalize()
    headers = ("Prefix", "All Ticket Lines", "Unique Buyers")
    return templates.TemplateResponse(request=request, name="counts.html", context={"headers": headers, "records": prefixes})