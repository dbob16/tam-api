from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import dotenv
import os

dotenv.load_dotenv()
DB_TYPE = os.getenv("DB_TYPE", "LOCAL")

if DB_TYPE == "LOCAL":
    from sqlite3 import connect

def session():
    if DB_TYPE == "LOCAL":
        conn = connect('data.db')
        cur = conn.cursor()
        return conn, cur

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

templates = Jinja2Templates(directory="templates")

conn, cur = session()
cur.execute("CREATE TABLE IF NOT EXISTS prefixes (prefix VARCHAR(150) PRIMARY KEY, bootstyle VARCHAR(150) NOT NULL, sort_order INT DEFAULT 1)")
conn.commit()
conn.close()

app = FastAPI()

@app.get("/")
def index():
    return {"whoami": "TAM-Server"}

@app.get("/prefixes/")
def list_prefixes():
    conn, cur = session()
    cur.execute("SELECT * FROM prefixes ORDER BY sort_order, prefix")
    results = cur.fetchall()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"prefix": r[0], "bootstyle": r[1], "sort_order": r[2]}
            r_l.append(r_d)
        return r_l

@app.get("/prefixes/{prefix}/")
def get_prefix(prefix:str):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM prefixes WHERE prefix = '{prefix}'")
    r = cur.fetchone()
    if not r:
        return {}
    else:
        r_d = {"prefix": r[0], "bootstyle": r[1], "sort_order": r[2]}
        return r_d

@app.post("/prefix/")
def post_prefix(prefix:Prefix):
    prefix.prefix = prefix.prefix.lower()
    prefix.bootstyle = prefix.bootstyle.lower()
    try:
        conn, cur = session()
        cur.execute(f"CREATE TABLE IF NOT EXISTS '{prefix.prefix}_tickets' (ticket_id INT PRIMARY KEY, first_name VARCHAR(200), last_name VARCHAR(200), phone_number VARCHAR(200), preference VARCHAR(100))")
        cur.execute(f"CREATE TABLE IF NOT EXISTS '{prefix.prefix}_baskets' (basket_id INT PRIMARY KEY, description VARCHAR(255), donors VARCHAR(255), winning_ticket INT)")
        cur.execute(f"INSERT INTO prefixes (prefix, bootstyle, sort_order) VALUES ('{prefix.prefix}', '{prefix.bootstyle}', {prefix.sort_order})")
        conn.commit()
        return {"success": True, "created_prefix": f"{prefix.prefix} | {prefix.bootstyle} | {prefix.sort_order}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.get("/tickets/{prefix}/")
def get_all_tickets(prefix:str):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_tickets' ORDER BY ticket_id")
    results = cur.fetchall()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
            r_l.append(r_d)
        return r_l

@app.get("/tickets/{prefix}/{ticket_id}/")
def get_single_ticket(prefix:str, ticket_id:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_tickets' WHERE ticket_id={ticket_id}")
    r = cur.fetchone()
    if not r:
        return {}
    else:
        r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
        return r_d

@app.get("/tickets/{prefix}/{id_from}/{id_to}/")
def get_range_tickets(prefix:str, id_from:int, id_to:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_tickets' WHERE ticket_id BETWEEN {id_from} AND {id_to}")
    results = cur.fetchall()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}
            r_l.append(r_d)
        return r_l

@app.post("/ticket/{prefix}/")
def post_ticket(prefix:str, t:Ticket):
    prefix = prefix.lower()
    try:
        conn, cur = session()
        cur.execute(f"INSERT OR REPLACE INTO '{prefix}_tickets' (ticket_id, first_name, last_name, phone_number, preference) VALUES ({t.ticket_id}, \"{t.first_name}\", \"{t.last_name}\", \"{t.phone_number}\", \"{t.preference}\")")
        conn.commit()
        return {"success": True, "posted_ticket": f"Prefix: {prefix} Details: {t.ticket_id} {t.first_name} {t.last_name} {t.phone_number} {t.preference}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.get("/baskets/{prefix}/")
def get_all_baskets(prefix:str):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_baskets' ORDER BY basket_id")
    results = cur.fetchall()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
            r_l.append(r_d)
        return r_l

@app.get("/baskets/{prefix}/{basket_id}/")
def get_single_basket(prefix:str, basket_id:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_baskets' WHERE basket_id = {basket_id}")
    r = cur.fetchone()
    if not r:
        return {}
    else:
        r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
        return r_d

@app.get("/baskets/{prefix}/{id_from}/{id_to}/")
def get_range_baskets(prefix:str, id_from:int, id_to:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"SELECT * FROM '{prefix}_baskets' WHERE basket_id BETWEEN {id_from} AND {id_to} ORDER BY basket_id")
    results = cur.fetchall()
    if not results:
        return []
    else:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3]}
            r_l.append(r_d)
        return r_l

@app.post("/basket/{prefix}/")
def post_basket(prefix:str, b:Basket):
    prefix = prefix.lower()
    try:
        conn, cur = session()
        cur.execute(f"INSERT OR REPLACE INTO '{prefix}_baskets' (basket_id, description, donors, winning_ticket) VALUES ({b.basket_id}, \"{b.description}\", \"{b.donors}\", {b.winning_ticket})")
        conn.commit()
        return {"success": True, "posted_basket": f"Prefix: {prefix} Details: {b.basket_id} {b.description} {b.donors} {b.winning_ticket}"}
    except Exception as e:
        return {"success": False, "exception": e}

@app.get("/combined/{prefix}/")
def combined_all(prefix:str):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM '{prefix}_baskets' b
    INNER JOIN '{prefix}_tickets' t
    ON b.winning_ticket = t.ticket_id
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    if results:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
            r_l.append(r_d)
        return r_l
    else:
        return []

@app.get("/combined/{prefix}/{basket_id}/")
def combined_single(prefix:str, basket_id:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM '{prefix}_baskets' b
    INNER JOIN '{prefix}_tickets' t
    ON b.winning_ticket = t.ticket_id
    WHERE basket_id = {basket_id}
    ORDER BY b.basket_id""")
    r = cur.fetchone()
    if r:
        r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
        return r_d
    else:
        return []

@app.get("/combined/{prefix}/{id_from}/{id_to}/")
def combined_range(prefix:str, id_from:int, id_to:int):
    prefix = prefix.lower()
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM '{prefix}_baskets' b
    INNER JOIN '{prefix}_tickets' t
    ON b.winning_ticket = t.ticket_id
    WHERE basket_id BETWEEN {id_from} AND {id_to}
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    if results:
        r_l = []
        for r in results:
            r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
            r_l.append(r_d)
        return r_l
    else:
        return []

@app.get("/reports/byname/{prefix}/", response_class=HTMLResponse)
def report_byname(request:Request, prefix:str, filter:str=None):
    prefix = prefix.lower()
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
    FROM '{prefix}_baskets' b INNER JOIN '{prefix}_tickets' t ON b.winning_ticket = t.ticket_id
    {filter_line}
    ORDER BY last_first, t.phone_number, b.basket_id""")
    results = cur.fetchall()
    headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
    return templates.TemplateResponse(request=request, name="byname.html", context={"title": select_title, "headers": headers, "records": results})