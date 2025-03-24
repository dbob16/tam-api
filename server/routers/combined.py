from fastapi import APIRouter, Request, HTTPException
from dao import *

router = APIRouter()

@router.get("/combined/{prefix}/")
def combined_all(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = WinnerRepo()
    results = repo.get_all(prefix)
    return results
    
@router.get("/combined/{prefix}/{basket_id}/")
def combined_single(request:Request, prefix:str, basket_id:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = WinnerRepo()
    results = repo.get_basket_one(prefix, basket_id)
    return results

@router.get("/combined/{prefix}/{id_from}/{id_to}/")
def combined_range(request:Request, prefix:str, id_from:int, id_to:int, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = WinnerRepo()
    results = repo.get_basket_range(prefix, id_from, id_to)
    return results