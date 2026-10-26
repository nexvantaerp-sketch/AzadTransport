"""Tiny in-memory stand-in for the supabase-py client (enough for this app's queries)."""
import uuid
from datetime import datetime, timezone

UNIQUE = {"vehicles": ["vehicle_number"], "trips": ["trip_number"], "invoices": ["invoice_number"],
          "app_users": ["username"], "drivers": ["cnic"]}
FK_BLOCK = {  # parent table -> [(child table, child column)]
    "vehicles": [("trips", "vehicle_id"), ("expenses", "vehicle_id")],
    "drivers": [("trips", "driver_id")], "customers": [("trips", "customer_id"), ("invoices", "customer_id")],
    "trips": [("invoice_items", "trip_id"), ("expenses", "trip_id")], "invoices": [("payments", "invoice_id")],
}


class Res:
    def __init__(self, data, count=None):
        self.data, self.count = data, count


class Q:
    def __init__(self, db, table):
        self.db, self.t = db, table
        self.op, self.payload, self.filters, self.orders, self.rng, self.lim, self.cnt = "select", None, [], [], None, None, None

    def select(self, cols="*", count=None):
        self.op, self.cnt = "select", count
        return self

    def insert(self, payload):
        self.op, self.payload = "insert", payload
        return self

    def update(self, payload):
        self.op, self.payload = "update", payload
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, c, v):
        self.filters.append((c, v))
        return self

    def order(self, c, desc=False):
        self.orders.append((c, desc))
        return self

    def range(self, a, b):
        self.rng = (a, b)
        return self

    def limit(self, n):
        self.lim = n
        return self

    def _match(self, r):
        return all(r.get(c) == v for c, v in self.filters)

    def execute(self):
        rows = self.db.tables.setdefault(self.t, [])
        if self.op == "insert":
            items = self.payload if isinstance(self.payload, list) else [self.payload]
            out = []
            for it in items:
                for col in UNIQUE.get(self.t, []):
                    if it.get(col) is not None and any(r.get(col) == it[col] for r in rows):
                        raise Exception(f"{{'code': '23505', 'message': 'duplicate key value violates unique constraint'}}")
                row = {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), **it}
                rows.append(row)
                out.append(dict(row))
            return Res(out)
        if self.op == "update":
            hit = [r for r in rows if self._match(r)]
            for r in hit:
                r.update(self.payload)
            return Res([dict(r) for r in hit])
        if self.op == "delete":
            hit = [r for r in rows if self._match(r)]
            for r in hit:
                for ct, cc in FK_BLOCK.get(self.t, []):
                    if any(c.get(cc) == r["id"] for c in self.db.tables.get(ct, [])):
                        raise Exception("{'code': '23503', 'message': 'violates foreign key constraint'}")
            self.db.tables[self.t] = [r for r in rows if not self._match(r)]
            if self.t == "invoices":      # ON DELETE CASCADE
                ids = {r["id"] for r in hit}
                self.db.tables["invoice_items"] = [i for i in self.db.tables.get("invoice_items", []) if i.get("invoice_id") not in ids]
            return Res([dict(r) for r in hit])
        out = [dict(r) for r in rows if self._match(r)]
        for c, desc in reversed(self.orders):
            out.sort(key=lambda r: (r.get(c) is None, r.get(c) or ""), reverse=desc)
        total = len(out)
        if self.rng:
            out = out[self.rng[0]:self.rng[1] + 1]
        if self.lim:
            out = out[:self.lim]
        return Res(out, total if self.cnt else None)


class FakeSupabase:
    def __init__(self):
        self.tables = {}

    def table(self, name):
        return Q(self, name)
