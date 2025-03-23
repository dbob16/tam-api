from pydantic import BaseModel, Field

class Prefix(BaseModel):
    prefix:str
    bootstyle:str
    sort_order:int

class Ticket(BaseModel):
    prefix:str
    ticket_id:int
    first_name:str | None
    last_name:str | None
    phone_number:str | None
    preference:str | None

class Basket(BaseModel):
    prefix:str
    basket_id:int
    description:str | None
    donors:str | None
    winning_ticket:int | None

class BasketAddWinner(BaseModel):
    prefix:str
    basket_id:int
    winning_ticket:int

class Counts(BaseModel):
    prefix:str
    total:int
    unique:int

class BasketWinner(BaseModel):
    prefix:str
    basket_id:int
    description:str | None
    donors:str | None
    winning_ticket:int | None
    winner_name:str | None
    phone_number:str | None
    preference:str | None

class ApiKey(BaseModel):
    api_key:str
    pc_name:str
    ip_addr:str

class ApiRequest(BaseModel):
    inp_pw:str
    pc_name:str