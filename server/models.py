from pydantic import BaseModel

class Prefix(BaseModel):
    prefix: str
    bootstyle: str
    sort_order: int

class Ticket(BaseModel):
    ticket_id: int
    first_name: str
    last_name: str
    phone_number: str
    preference: str

class Basket(BaseModel):
    basket_id: int
    description: str
    donors: str
    winning_ticket: int

class ApiRequest(BaseModel):
    inp_pw: str
    pc_name: str