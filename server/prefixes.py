from fastapi import APIRouter, Request, HTTPException
from db import *
from dao import Prefix, PrefixRepo

router = APIRouter()

@router.get("/prefixes/")
def list_prefixes(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = PrefixRepo()
    return repo.get_all()

@router.get("/prefixes/{prefix}/")
def get_prefix(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = PrefixRepo()
    return repo.get_one(prefix)

@router.post("/prefix/")
def post_prefix(request:Request, prefix:Prefix, api_key:str=None):
    prefix.prefix = prefix.prefix.lower()
    prefix.bootstyle = prefix.bootstyle.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = PrefixRepo()
    message = repo.add(prefix)
    return {"message": message}

@router.delete("/delprefix/")
def delete_prefix(request:Request, prefix:str, api_key:str=None):
    prefix = prefix.lower()
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    repo = PrefixRepo()
    message = repo.delete(prefix)
    return {"success": True, "message": message}