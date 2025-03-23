from fastapi import APIRouter, Request, HTTPException
from typing import List
from dao import *

router = APIRouter()

@router.get("/tickets/")
def get_all_ticket_prefixes(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    results = repo.get_all_prefixes()
    return results

@router.get("/tickets/{prefix}/")
def get_all_tickets(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    results = repo.get_all(prefix)
    return results

@router.get("/tickets/{prefix}/{ticket_id}/")
def get_single_ticket(request:Request, prefix:str, ticket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    results = repo.get_one(prefix, ticket_id)
    return results

@router.get("/tickets/{prefix}/{id_from}/{id_to}/")
def get_range_tickets(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    results = repo.get_range(prefix, id_from, id_to)
    return results

@router.get("/random/tickets/{prefix}/")
def get_random_ticket(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    return repo.get_random(prefix)

@router.post("/ticket/")
def post_ticket(request:Request, t:Ticket, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    try:
        result = repo.add(t)
        return {"success": True, "message": result}
    except:
        raise HTTPException(status_code=500, detail="Something went wrong, check server logs")

@router.post("/tickets/")
def post_tickets(request:Request, tickets:list[Ticket], api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = TicketRepo()
    try:
        for t in tickets:
            repo.add(t)
        return {"success": True, "message": "Batch of tickets added/updated successfully."}
    except:
        raise HTTPException(status_code=500, detail="Something went wrong, check server logs")