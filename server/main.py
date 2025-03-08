from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from db import *
from models import *
from api_keys import router as api_router
from prefixes import router as prefixes_router
from tickets import router as tickets_router
from baskets import router as baskets_router
from combined import router as combined_router
from reports import router as reports_router
import random
import string
import dotenv
import os
import time

while True:
    try:
        db_init()
        break
    except Exception as e:
        print(e)
        print("DB Connection Failed. Trying again in 3 seconds")
        time.sleep(3)

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/")
def index(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return {"whoami": "TAM-Server"}

@app.get("/health/")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router)

app.include_router(prefixes_router)

app.include_router(tickets_router)

app.include_router(baskets_router)

app.include_router(combined_router)

app.include_router(reports_router)