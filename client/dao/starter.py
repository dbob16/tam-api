from .repo import *

def init_local_db(BASE_URL:str="", api_key:str=""):
    conn_d = {
        "BASE_URL": BASE_URL,
        "api_key": api_key
    }
    PrefixRepo(**conn_d).create_table()
    TicketRepo(**conn_d).create_table()
    BasketRepo(**conn_d).create_table()
    WinnerRepo(**conn_d).create_view()
    CountsRepo(**conn_d).create_view()
