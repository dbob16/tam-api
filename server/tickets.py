from fastapi import APIRouter, Request, HTTPException
from db import *
from models import Ticket

router = APIRouter()

@router.get("/tickets/{prefix}/")
def get_all_tickets(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/tickets/{prefix}/{ticket_id}/")
def get_single_ticket(request:Request, prefix:str, ticket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/tickets/{prefix}/{id_from}/{id_to}/")
def get_range_tickets(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/random/tickets/{prefix}/")
def get_random_ticket(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"SELECT * FROM `{prefix}_tickets` ORDER BY {rand()} LIMIT 1")
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    else:
        return {"ticket_id": r[0], "first_name": r[1], "last_name": r[2], "phone_number": r[3], "preference": r[4]}

@router.post("/ticket/{prefix}/")
def post_ticket(request:Request, prefix:str, t:Ticket, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        cur.execute(f"REPLACE INTO `{prefix}_tickets` (ticket_id, first_name, last_name, phone_number, preference) VALUES ({t.ticket_id}, \"{t.first_name}\", \"{t.last_name}\", \"{t.phone_number}\", \"{t.preference}\")")
        conn.commit()
        conn.close()
        return {"success": True, "posted_ticket": f"Prefix: {prefix} Details: {t.ticket_id} {t.first_name} {t.last_name} {t.phone_number} {t.preference}"}
    except Exception as e:
        return {"success": False, "exception": e}

@router.post("/tickets/{prefix}/")
def post_tickets(request:Request, prefix:str, tickets:list[Ticket], api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        for t in tickets:
            cur.execute(f"REPLACE INTO `{prefix}_tickets` (ticket_id, first_name, last_name, phone_number, preference) VALUES ({t.ticket_id}, \"{t.first_name}\", \"{t.last_name}\", \"{t.phone_number}\", \"{t.preference}\")")
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return HTTPException(status_code=500, detail={"success": False, "exception": e})