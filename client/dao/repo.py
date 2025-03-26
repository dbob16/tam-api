import httpx
from .models import *
from .db import session

class Repository:
    """Base class for all repos"""
    def __init__(self, BASE_URL:str="", api_key:str=""):
        self.BASE_URL = BASE_URL
        self.api_key = api_key
        self.conn, self.cur = session()
        self.params = {"api_key": api_key}

class PrefixRepo(Repository):
    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS prefixes (prefix TEXT PRIMARY KEY, bootstyle TEXT, sort_order INTEGER)")
        self.conn.commit()
    def get_one(self, prefix:str):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}prefixes/{prefix}/", params={"api_key": self.api_key}, verify=False)
            if response.status_code == 200:
                body = response.json()
                return Prefix(**body)
        stmt = "SELECT * FROM prefixes WHERE prefix = ?"
        data = (prefix,)
        self.cur.execute(stmt, data)
        l_r = self.cur.fetchone()
        return Prefix(*l_r)
    def get_all(self):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}prefixes/", params={"api_key": self.api_key}, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Prefix(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM prefixes"
        self.cur.execute(stmt)
        l_r = self.cur.fetchall()
        l_r = [Prefix(*r) for r in l_r]
        return l_r
    def add_prefix(self, prefix:Prefix):
        stmt = "REPLACE INTO prefixes VALUES (?, ?, ?)"
        data = (prefix.prefix, prefix.bootstyle, prefix.sort_order)
        self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            httpx.post(f"{self.BASE_URL}prefix/", json=prefix.__dict__, params={"api_key": self.api_key}, verify=False)
    def del_prefix(self, prefix:str):
        stmt = "DELETE FROM prefixes WHERE prefix = ?"
        data = (prefix,)
        self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            httpx.delete(f"{self.BASE_URL}delprefix/", params={"api_key": self.api_key, "prefix": prefix}, verify=False)
    def pull(self):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}prefixes/", params={"api_key": self.api_key}, verify=False)
            if response.status_code == 200:
                body = response.json()
                stmt = "REPLACE INTO prefixes VALUES (?, ?, ?)"
                for prefix in body:
                    data = (prefix["prefix"], prefix["bootstyle"], prefix["sort_order"])
                    self.cur.execute(stmt, data)
        self.conn.commit()
    def push(self):
        stmt = "SELECT * FROM prefixes"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        if len(self.BASE_URL) > 0:
            for r in results:
                cur_item = Prefix(prefix=r[0], bootstyle=r[1], sort_order=r[2])
                httpx.post(f"{self.BASE_URL}prefix/", json=cur_item.__dict__, params={"api_key": self.api_key}, verify=False)
    def sync(self):
        self.push()
        self.pull()

class TicketRepo(Repository):
    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS tickets (
        prefix TEXT,
        ticket_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        preference TEXT,
        PRIMARY KEY (prefix, ticket_id))""")
        self.conn.commit()
    def get_one(self, prefix:str, ticket_id:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}tickets/{prefix}/{ticket_id}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = Ticket(**body)
                return r_r
            return Ticket(prefix, ticket_id)
        stmt = "SELECT * FROM tickets WHERE prefix = ? AND ticket_id = ?"
        data = (prefix, ticket_id)
        self.cur.execute(stmt, data)
        result = self.cur.fetchone()
        if not result:
            return Ticket(prefix, ticket_id)
        l_r = Ticket(*result)
        return l_r
    def get_range(self, prefix:str, id_from:int, id_to:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}tickets/{prefix}/{id_from}/{id_to}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Ticket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM tickets WHERE prefix = ? AND ticket_id BETWEEN ? and ?"
        data = (prefix, id_from, id_to)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [Ticket(*r) for r in results]
        return l_r
    def get_all(self, prefix:str):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}tickets/{prefix}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Ticket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM tickets WHERE prefix = ?"
        data = (prefix,)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [Ticket(*r) for r in results]
        return l_r
    def get_random(self, prefix:str):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}random/tickets/{prefix}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                return Ticket(**body)
        stmt = "SELECT * FROM tickets WHERE prefix = ? ORDER BY random() LIMIT 1"
        data = (prefix,)
        self.cur.execute(stmt, data)
        result = self.cur.fetchone()
        if not result:
            return Ticket(prefix, 0)
        l_r = Ticket(*result)
        return l_r
    def get_all_prefixes(self):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}tickets/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Ticket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM tickets"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        l_r = [Ticket(*r) for r in results]
        return l_r
    def add(self, t:Ticket):
        stmt = "REPLACE INTO tickets VALUES (?, ?, ?, ?, ?, ?)"
        data = (t.prefix, t.ticket_id, t.first_name, t.last_name, t.phone_number, t.preference)
        self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            httpx.post(f"{self.BASE_URL}ticket/", json=t.__dict__, params=self.params, verify=False)
    def add_list(self, l:list[Ticket]):
        stmt = "REPLACE INTO tickets VALUES (?, ?, ?, ?, ?, ?)"
        for i in l:
            data = (i.prefix, i.ticket_id, i.first_name, i.last_name, i.phone_number, i.preference)
            self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            out_list = [r.__dict__ for r in l]
            httpx.post(f"{self.BASE_URL}tickets/", json=out_list, params=self.params, verify=False)
    def push(self):
        stmt = "SELECT * FROM tickets"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        l_r = [Ticket(*r) for r in results]
        if len(self.BASE_URL) > 0:
            out_list = [r.__dict__ for r in l_r]
            httpx.post(f"{self.BASE_URL}tickets/", json=out_list, params=self.params, verify=False)

class BasketRepo(Repository):
    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS baskets (
        prefix TEXT,
        basket_id INTEGER,
        description TEXT,
        donors TEXT,
        winning_ticket INTEGER,
        PRIMARY KEY (prefix, basket_id))""")
        self.conn.commit()
    def get_one(self, prefix:str, basket_id:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}baskets/{prefix}/{basket_id}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = Basket(**body)
                return r_r
            return Basket(prefix, basket_id)
        stmt = "SELECT * FROM baskets WHERE prefix = ? AND basket_id = ?"
        data = (prefix, basket_id)
        self.cur.execute(stmt, data)
        result = self.cur.fetchone()
        if not result:
            return Basket(prefix, basket_id)
        l_r = Basket(*result)
        return l_r
    def get_range(self, prefix:str, id_from:int, id_to:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}baskets/{prefix}/{id_from}/{id_to}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Basket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM baskets WHERE prefix = ? AND basket_id BETWEEN ? AND ?"
        data = (prefix, id_from, id_to)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [Basket(*r) for r in results]
        return l_r
    def get_all(self, prefix:str):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}baskets/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Basket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM baskets WHERE prefix = ?"
        data = (prefix,)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [Basket(*r) for r in results]
        return l_r
    def get_all_prefixes(self):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}baskets/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [Basket(**r) for r in body]
                return r_r
            return []
        stmt = "SELECT * FROM baskets"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        l_r = [Basket(*r) for r in results]
        return l_r
    def add(self, b:Basket):
        stmt = "REPLACE INTO baskets VALUES (?, ?, ?, ?, ?)"
        data = (b.prefix, b.basket_id, b.description, b.donors, b.winning_ticket)
        self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            httpx.post(f"{self.BASE_URL}basket/", json=b.__dict__, params=self.params, verify=False)
    def add_list(self, l:list[Basket]):
        stmt = "REPLACE INTO baskets VALUES (?, ?, ?, ?, ?)"
        for i in l:
            data = (i.prefix, i.basket_id, i.description, i.donors, i.winning_ticket)
            self.cur.execute(stmt, data)
        self.conn.commit()
        if len(self.BASE_URL) > 0:
            out_list = [r.__dict__ for r in l]
            httpx.post(f"{self.BASE_URL}baskets/", json=out_list, params=self.params, verify=False)
    def update_winner(self, prefix:str, basket_id:int, winning_ticket:int):
        existing = self.get_one(prefix, basket_id)
        existing.winning_ticket = winning_ticket
        self.add(existing)
    def push(self):
        stmt = "SELECT * FROM baskets"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        l_r = [Basket(*r) for r in results]
        if len(self.BASE_URL) > 0:
            out_list = [r.__dict__ for r in l_r]
            httpx.post(f"{self.BASE_URL}baskets/", json=out_list, params=self.params, verify=False)

class WinnerRepo(Repository):
    def create_view(self):
        self.cur.execute("""CREATE VIEW IF NOT EXISTS basket_winners AS
        SELECT b.*, CONCAT(t.last_name, ", ", t.first_name) AS winner_name, t.phone_number, t.preference
        FROM baskets AS b
        LEFT JOIN tickets AS t
        ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
        ORDER BY b.prefix, b.basket_id""")
        self.conn.commit()
    def get_basket_one(self, prefix:str, basket_id:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}combined/{prefix}/{basket_id}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = BasketWinner(**body)
                return r_r
        stmt = "SELECT * FROM basket_winners WHERE prefix = ? AND basket_id = ?"
        data = (prefix, basket_id)
        self.cur.execute(stmt, data)
        results = self.cur.fetchone()
        if not results:
            return BasketWinner(prefix, basket_id)
        l_r = BasketWinner(*results)
        return l_r
    def get_basket_range(self, prefix:str, id_from:int, id_to:int):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}combined/{prefix}/{id_from}/{id_to}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [BasketWinner(**r) for r in body]
                return r_r
        stmt = "SELECT * FROM basket_winners WHERE prefix = ? AND basket_id BETWEEN ? AND ?"
        data = (prefix, id_from, id_to)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [BasketWinner(*r) for r in results]
        return l_r
    def get_all(self, prefix:str):
        if len(self.BASE_URL) > 0:
            response = httpx.get(f"{self.BASE_URL}combined/{prefix}/", params=self.params, verify=False)
            if response.status_code == 200:
                body = response.json()
            if body:
                r_r = [BasketWinner(**r) for r in body]
                return r_r
        stmt = "SELECT * FROM basket_winners WHERE prefix = ?"
        data = (prefix,)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [BasketWinner(*r) for r in results]
        return l_r
    def report_byname(self, prefix:str, preference:str=None):
        if preference:
            stmt = "SELECT * FROM basket_winners WHERE prefix = ? AND preference = ? ORDER BY winner_name, phone_number, winning_ticket"
            data = (prefix, preference)
        else:
            stmt = "SELECT * FROM basket_winners WHERE prefix = ? ORDER BY winner_name, phone_number, winning_ticket"
            data = (prefix,)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [BasketWinner(*r) for r in results]
        return l_r
    def report_bybasket(self, prefix:str, preference:str=None):
        if preference:
            stmt = "SELECT * FROM basket_winners WHERE prefix = ? AND preference = ?"
            data = (prefix, preference)
        else:
            stmt = "SELECT * FROM basket_winners WHERE prefix = ?"
            data = (prefix,)
        self.cur.execute(stmt, data)
        results = self.cur.fetchall()
        l_r = [BasketWinner(*r) for r in results]
        return l_r

class CountsRepo(Repository):
    def create_view(self):
        self.cur.execute("""CREATE VIEW IF NOT EXISTS ticket_counts AS
        SELECT prefix, COUNT(*) AS total_buys, COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) AS unique_buys
        FROM tickets
        GROUP BY prefix
        UNION ALL
        SELECT "totals", COUNT(*) AS total_buys, COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) AS unique_buys
        FROM tickets""")
        self.conn.commit()
    def get_counts(self):
        stmt = "SELECT * FROM ticket_counts"
        self.cur.execute(stmt)
        results = self.cur.fetchall()
        l_r = [Counts(*r) for r in results]
        return l_r