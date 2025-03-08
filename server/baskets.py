from fastapi import APIRouter, Request, HTTPException
from db import *
from dao import Basket, BasketRepo, BasketAddWinner

router = APIRouter()

@router.get("/baskets/{prefix}/")
def get_all_baskets(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    return repo.get_all(prefix)

@router.get("/baskets/{prefix}/{basket_id}/")
def get_single_basket(request:Request, prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    return repo.get_one(prefix, basket_id)

@router.get("/baskets/{prefix}/{id_from}/{id_to}/")
def get_range_baskets(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    return repo.get_range(prefix, id_from, id_to)

@router.post("/basket/")
def post_basket(request:Request, b:Basket, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    message = repo.add(b)
    return {"success": True, "message": message}

@router.post("/baskets/")
def post_basket(request:Request, baskets:list[Basket], api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    for b in baskets:
        repo.add(b)
    return {"success": True, "message": "Batch of baskets added successfully"}

@router.post("/basket/winner/")
def post_basket(request:Request, b:BasketAddWinner, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = BasketRepo()
    message = repo.add_winner(b.prefix, b.basket_id, b.winning_ticket)
    return {"success": True, "message": message}