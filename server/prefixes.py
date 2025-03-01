from fastapi import APIRouter, Request, HTTPException
from models import Prefix
from db import *

router = APIRouter()

@router.get("/prefixes/")
def list_prefixes(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/prefixes/{prefix}/")
def get_prefix(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.post("/prefix/")
def post_prefix(request:Request, prefix:Prefix, api_key:str=None):
    prefix.prefix = prefix.prefix.lower()
    prefix.bootstyle = prefix.bootstyle.lower()
    if API_PW and not check_api_key(api_key, request):
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
        return HTTPException(status_code=500, detail={"success": False, "exception": e})

@router.delete("/delprefix/")
def delete_prefix(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"DELETE FROM prefixes WHERE prefix = \"{prefix}\"")
    conn.commit()
    conn.close()
    return {"success": True, "result": f"Deleted {prefix} from the prefixes table"}