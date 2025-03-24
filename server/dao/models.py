from pydantic.dataclasses import dataclass

@dataclass
class Prefix:
    prefix:str
    bootstyle:str
    sort_order:int

@dataclass
class Ticket:
    prefix:str
    ticket_id:int
    first_name:str | None = ""
    last_name:str | None = ""
    phone_number:str | None = ""
    preference:str | None = ""

@dataclass
class Basket:
    prefix:str
    basket_id:int
    description:str | None = ""
    donors:str | None = ""
    winning_ticket:int | None = 0

@dataclass
class Counts:
    prefix:str
    total:int
    unique:int

@dataclass
class BasketWinner:
    prefix:str
    basket_id:int
    description:str | None = ""
    donors:str | None = ""
    winning_ticket:int | None = 0
    winner_name:str | None = ""
    phone_number:str | None = ""
    preference:str | None = ""

@dataclass
class ApiKey:
    api_key:str
    pc_name:str
    ip_addr:str | None = ""

@dataclass
class ApiRequest:
    inp_pw:str
    pc_name:str | None = ""