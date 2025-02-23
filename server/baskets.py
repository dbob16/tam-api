from fastapi import APIRouter, Request, HTTPException
from db import *
from models import Basket

router = APIRouter()

@router.get("/baskets/{prefix}/")
def get_all_baskets(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/baskets/{prefix}/{basket_id}/")
def get_single_basket(request:Request, prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.get("/baskets/{prefix}/{id_from}/{id_to}/")
def get_range_baskets(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
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

@router.post("/basket/{prefix}/")
def post_basket(request:Request, prefix:str, b:Basket, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    try:
        conn, cur = session()
        cur.execute(f"REPLACE INTO `{prefix}_baskets` (basket_id, description, donors, winning_ticket) VALUES ({b.basket_id}, \"{b.description}\", \"{b.donors}\", {b.winning_ticket})")
        conn.commit()
        conn.close()
        return {"success": True, "posted_basket": f"Prefix: {prefix} Details: {b.basket_id} {b.description} {b.donors} {b.winning_ticket}"}
    except Exception as e:
        return {"success": False, "exception": e}