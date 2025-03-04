from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import *

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/reports/byname/{prefix}/", response_class=HTMLResponse)
def report_byname(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    if filter == None:
        select_title = "Winners - All Preferences"
        filter_line = f"WHERE b.prefix = \"{prefix}\""
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        filter_line = f"WHERE b.prefix = \"{prefix}\" AND t.preference = \"CALL\""
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        filter_line = f"WHERE b.prefix = \"{prefix}\"t.preference = \"TEXT\""
    cur.execute(f"""SELECT CONCAT(t.last_name, \", \", t.first_name) as last_first, t.phone_number, b.basket_id, b.winning_ticket, b.description
    FROM `baskets` b INNER JOIN `tickets` t ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
    {filter_line}
    ORDER BY last_first, t.phone_number, b.basket_id""")
    results = cur.fetchall()
    conn.close()
    headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
    return templates.TemplateResponse(request=request, name="byname.html", context={"prefix": prefix.capitalize(), "title": select_title, "headers": headers, "records": results})

@router.get("/reports/bybasket/{prefix}/", response_class=HTMLResponse)
def report_bybasket(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    if filter == None:
        select_title = "Winners - All Preferences"
        filter_line = f"WHERE b.prefix = \"{prefix}\""
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        filter_line = f"WHERE b.prefix = \"{prefix}\" AND t.preference = \"CALL\""
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        filter_line = f"WHERE b.prefix = \"{prefix}\" AND t.preference = \"TEXT\""
    cur.execute(f"""SELECT b.basket_id, b.description, b.winning_ticket, CONCAT(t.last_name, \", \", t.first_name) AS last_first, t.phone_number
    FROM `baskets` b INNER JOIN `tickets` t ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
    {filter_line}
    ORDER BY b.basket_id""")
    results = cur.fetchall()
    conn.close()
    headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
    return templates.TemplateResponse(request=request, name="bybasket.html", context={"prefix": prefix.capitalize(), "title": select_title, "headers": headers, "records": results})

@router.get("/reports/counts/", response_class=HTMLResponse)
def get_counts(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    conn, cur = session()
    cur.execute("SELECT prefix FROM prefixes ORDER BY sort_order")
    prefixes = [[v[0]] for v in cur.fetchall()]
    total_count, unique_count = 0, 0
    for l in prefixes:
        cur.execute(f"SELECT COUNT(*) FROM `tickets` WHERE prefix = \"{l[0]}\"")
        row_count = cur.fetchone()[0]
        total_count += row_count
        l.append(row_count)
        cur.execute(f"SELECT COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) FROM `tickets` WHERE prefix = \"{prefix}\"")
        distinct_count = cur.fetchone()[0]
        unique_count += distinct_count
        l.append(distinct_count)
        l[0] = l[0].capitalize()
    prefixes.append(["Totals", total_count, unique_count])
    conn.close()
    headers = ("Prefix", "All Ticket Lines", "Unique Buyers")
    return templates.TemplateResponse(request=request, name="counts.html", context={"headers": headers, "records": prefixes})