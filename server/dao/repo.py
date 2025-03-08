from .models import *
from .db import session, DB_TYPE
from .exceptions import ItemNotFound

class Repository[I]:
    """Container for all other repository items"""

class PrefixRepo(Repository[Prefix]):
    def get_one(self, prefix:str) -> Prefix:
        conn, cur = session()
        stmt = "SELECT * FROM prefixes WHERE prefix = ?"
        if DB_TYPE != "LOCAL":
            stmt = stmt.replace("?", "%s")
        data = (prefix,)
        cur.execute(stmt, data)
        r = cur.fetchone()
        conn.close()
        if not r:
            return {}
        return Prefix(prefix=r[0], bootstyle=r[1], sort_order=r[2])
    def get_all(self) -> list[Prefix]:
        conn, cur = session()
        stmt = "SELECT * FROM prefixes"
        cur.execute(stmt)
        results = cur.fetchall()
        if not results:
            return []
        l = [Prefix(prefix=r[0], bootstyle=r[1], sort_order=r[2]) for r in results]
        return l
    def add(self, p:Prefix) -> str:
        conn, cur = session()
        stmt_insert = "INSERT INTO prefixes (bootstyle, sort_order, prefix) VALUES (?, ?, ?)"
        stmt_update = "UPDATE prefixes SET bootstyle = ?, sort_order = ? WHERE prefix = ?"
        data = (p.bootstyle, p.sort_order, p.prefix)
        if DB_TYPE != "LOCAL":
            stmt_insert = stmt_insert.replace("?", "%s")
            stmt_update = stmt_update.replace("?", "%s")
        try:
            cur.execute(stmt_insert, data)
            conn.commit()
        except Exception as e:
            print(e)
            cur.execute(stmt_update, data)
            conn.commit()
        conn.close()
        return f"Prefix {p.prefix} added/updated successfully"
    def delete(self, prefix:str) -> str:
        conn, cur = session()
        try:
            self.get_one(prefix)
            stmt = "DELETE FROM prefixes WHERE prefix = ?"
            data = (prefix,)
            if DB_TYPE != "LOCAL":
                stmt = stmt.replace("?", "%s")
            cur.execute(stmt, data)
            conn.commit()
            conn.close()
        except:
            return f"Prefix {prefix} was not found to delete, maybe it has already been deleted."
        return f"Prefix {prefix} was found and deleted."

class TicketRepo(Repository[Ticket]):
    def get_one(self, prefix:str, id:int) -> Ticket:
        conn, cur = session()
        stmt = "SELECT * FROM tickets WHERE prefix = ? AND ticket_id = ?"
        data = (prefix, id)
        if DB_TYPE != "LOCAL":
            stmt = stmt.replace("?", "%s")
        cur.execute(stmt, data)
        r = cur.fetchone()
        if not r:
            return {}
        return Ticket(prefix=r[0], ticket_id=r[1], first_name=r[2], last_name=r[3], phone_number=r[4], preference=r[5])
    def get_range(self, prefix:str, id_from:int, id_to:int) -> list[Ticket]:
        conn, cur = session()
        stmt = "SELECT * FROM tickets WHERE prefix = ? AND ticket_id BETWEEN ? AND ?"
        data = (prefix, id_from, id_to)
        if DB_TYPE != "LOCAL":
            stmt = stmt.replace("?", "%s")
        cur.execute(stmt, data)
        results = cur.fetchall()
        conn.close()
        if not results:
            return []
        l = [Ticket(prefix=r[0], ticket_id=r[1], first_name=r[2], last_name=r[3], phone_number=r[4], preference=r[5]) for r in results]
        return l
    def get_all(self, prefix:str) -> list[Ticket]:
        conn, cur = session()
        stmt = "SELECT * FROM tickets WHERE prefix = ?"
        data = (prefix,)
        if DB_TYPE != "LOCAL":
            stmt = stmt.replace("?", "%s")
        cur.execute(stmt, data)
        results = cur.fetchall()
        if not results:
            return []
        l = [Ticket(prefix=r[0], ticket_id=r[1], first_name=r[2], last_name=r[3], phone_number=r[4], preference=r[5]) for r in results]
        return l
    def add(self, t:Ticket) -> str:
        conn, cur = session()
        stmt_insert = "INSERT INTO tickets (first_name, last_name, phone_number, preference, prefix, ticket_id) VALUES (?, ?, ?, ?, ?, ?)"
        stmt_update = "UPDATE tickets SET first_name = ?, last_name = ?, phone_number = ?, preference = ? WHERE prefix = ? AND ticket_id = ?"
        data = (t.first_name, t.last_name, t.phone_number, t.preference, t.prefix, t.ticket_id) 
        if DB_TYPE != "LOCAL":
            stmt_insert = stmt_insert.replace("?", "%s")
            stmt_update = stmt_update.replace("?", "%s")
        try:
            cur.execute(stmt_insert, data)
            conn.commit()
        except:
            cur.execute(stmt_update, data)
            conn.commit()
        conn.close()
        return f"Ticket {t.prefix} {t.ticket_id} added/updated successfully"