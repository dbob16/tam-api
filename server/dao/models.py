from pydantic import BaseModel

class Prefix(BaseModel):
    prefix:str
    bootstyle:str
    sort_order:int

class Ticket(BaseModel):
    prefix:str
    ticket_id:int
    first_name:str
    last_name:str
    phone_number:str
    preference:str

class Basket(BaseModel):
    prefix:str
    basket_id:int
    description:str
    donors:str
    winning_ticket:int

class Counts(BaseModel):
    prefix:str
    total:int
    unique:int

class BasketWinner(BaseModel):
    prefix:str
    basket_id:int
    description:str
    donors:str
    winning_ticket:int
    winner_name:str
    phone_number:str
    preference:str

class ApiKey(BaseModel):
    api_key:str
    pc_name:str
    ip_addr:str

class ApiRequest(BaseModel):
    inp_pw:str
    pc_name:str