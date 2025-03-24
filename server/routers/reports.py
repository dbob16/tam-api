from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dao import *

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/reports/byname/{prefix}/", response_class=HTMLResponse)
def report_byname(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = WinnerRepo()
    if filter == None:
        select_title = "Winners - All Preferences"
        results = repo.get_all_byname(prefix)
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        results = repo.get_all_byname(prefix, "CALL")
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        results = repo.get_all_byname(prefix, "TEXT")
    results = [(r.winner_name, r.phone_number, r.basket_id, r.winning_ticket, r.description) for r in results]
    headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
    return templates.TemplateResponse(request=request, name="report.html", context={
        "maintitle": f"{prefix.capitalize()} Basket Winners by Name",
        "title": select_title,
        "headers": headers,
        "records": results})

@router.get("/reports/bybasket/{prefix}/", response_class=HTMLResponse)
def report_bybasket(request:Request, prefix:str, filter:str=None, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = WinnerRepo()
    if filter == None:
        select_title = "Winners - All Preferences"
        results = repo.get_all(prefix)
    elif filter == "call":
        select_title = "Winners Preferring Calls"
        results = repo.get_all(prefix, "CALL")
    elif filter == "text":
        select_title = "Winners Preferring Texts"
        results = repo.get_all(prefix, "TEXT")
    results = [(r.basket_id, r.description, r.winning_ticket, r.winner_name, r.phone_number) for r in results]
    headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
    return templates.TemplateResponse(request=request, name="report.html", context={
        "maintitle": f"{prefix.capitalize} Basket Winners by Basket #",
        "title": select_title,
        "headers": headers,
        "records": results})

@router.get("/reports/counts/", response_class=HTMLResponse)
def get_counts(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    repo = CountsRepo()
    results = repo.get_counts()
    results = [(r.prefix, r.total, r.unique) for r in results]
    headers = ("Prefix", "All Ticket Lines", "Unique Buyers")
    return templates.TemplateResponse(request=request, name="report.html", context={
        "maintitle": "Ticket Counts",
        "title": "Lists ticket counts",
        "headers": headers,
        "records": results})