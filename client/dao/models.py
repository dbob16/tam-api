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
    first_name:str = ""
    last_name:str = ""
    phone_number:str = ""
    preference:str = ""

@dataclass
class Basket:
    prefix:str
    basket_id:int
    description:str = ""
    donors:str = ""
    winning_ticket:int = 0

@dataclass
class BasketWinner:
    prefix:str
    basket_id:int
    description:str = ""
    donors:str = ""
    winning_ticket:int = 0
    winner_name:str = ""
    phone_number:str = ""
    preference:str = ""