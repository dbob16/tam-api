from fastapi import APIRouter, Request, HTTPException
from db import *

router = APIRouter()

@router.get("/combined/{prefix}/")
def combined_all(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `baskets` b
    INNER JOIN `tickets` t
    ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
    WHERE b.prefix = \"{prefix}\"
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

@router.get("/combined/{prefix}/{basket_id}/")
def combined_single(request:Request, prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `baskets` b
    INNER JOIN `tickets` t
    ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
    WHERE b.prefix = \"{prefix}\" AND basket_id = {basket_id}
    ORDER BY b.basket_id""")
    r = cur.fetchone()
    conn.close()
    if r:
        r_d = {"basket_id": r[0], "description": r[1], "donors": r[2], "winning_ticket": r[3], "first_name": r[4], "last_name": r[5], "phone_number": r[6], "preference": r[7]}
        return r_d
    else:
        return []

@router.get("/combined/{prefix}/{id_from}/{id_to}/")
def combined_range(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute(f"""SELECT b.basket_id, b.description, b.donors, b.winning_ticket, t.first_name, t.last_name, t.phone_number, t.preference
    FROM `baskets` b
    INNER JOIN `tickets` t
    ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
    WHERE b.prefix = \"{prefix}\" AND basket_id BETWEEN {id_from} AND {id_to}
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