import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from utils import db
ok = []
def check(n, c, x=""):
    ok.append(c); print(("✅ " if c else "❌ ") + n + (f" → {x}" if x and not c else ""))

reset()
v = db.insert("vehicles", {"vehicle_number": "AAA-1", "status": "Active", "vehicle_type": "Tanker"})
d = db.insert("drivers", {"name": "Ali", "status": "Active"})
c = db.insert("customers", {"name": "Mill A", "rate_per_ton": 2000, "payment_terms": 30, "status": "Active"})
t = db.insert("trips", {"trip_number": "T1", "trip_date": "2026-10-01", "vehicle_id": v["id"], "driver_id": d["id"],
                        "customer_id": c["id"], "loading_weight": 30, "unloading_weight": 0, "rate_per_ton": 2000,
                        "total_freight": 60000, "status": "Pending", "freight_basis": "Loading Weight"})

def run_dialog(kind, table_module, rec, extra=""):
    code = f"""
import sys; sys.path.insert(0, {BASE!r}); sys.path.insert(0, {os.path.join(BASE,'tests')!r})
import streamlit as st, harness
from utils import crud, db
from views import {table_module} as m
st.session_state.setdefault('user', {{'id':'u','role':'admin','username':'a'}})
fk = {{f['key']: crud.fk_map(f['ref']) for f in m.CFG['fields'] if f.get('kind')=='fk'}}
rec = db.where(m.CFG['table'], 'id', {rec['id']!r})[0]
crud._{kind}_dialog(m.CFG, rec, fk) if {kind!r}=='edit' else crud._delete_dialog(m.CFG, rec)
"""
    return AppTest.from_string(code, default_timeout=60).run()

at = run_dialog("edit", "trips", t)
check("edit dialog renders", not at.exception, errs(at))
labels = [b.label for b in at.button]
check("edit dialog has Save button", "💾 Save changes" in labels, labels)
# change loading weight & unloading basis
ks = [n.key for n in at.number_input]
lw = next(k for k in ks if k.endswith("_loading_weight"))
at.number_input(key=lw).set_value(32.0)
at.button[labels.index("💾 Save changes")].click(); at.run()
row = FAKE.tables["trips"][0]
check("edit trip recalculates freight (32×2000)", row["total_freight"] == 64000.0, row)

at = run_dialog("delete", "vehicles", v)
check("delete dialog renders", not at.exception, errs(at))
labels = [b.label for b in at.button]
at.button[labels.index("Yes, delete")].click(); at.run()
check("vehicle with trips → friendly FK error, row kept", any("linked" in e.value for e in at.error) and len(FAKE.tables["vehicles"]) == 1, errs(at))

e = db.insert("vehicles", {"vehicle_number": "ZZZ-9", "status": "Active"})
at = run_dialog("delete", "vehicles", e)
at.button[[b.label for b in at.button].index("Yes, delete")].click(); at.run()
check("unlinked vehicle deleted", len(FAKE.tables["vehicles"]) == 1)

# billed trip lock
db.update("trips", t["id"], {"status": "Billed"})
at = run_dialog("edit", "trips", t)
lw = next(n.key for n in at.number_input if n.key.endswith("_loading_weight"))
at.number_input(key=lw).set_value(10.0)
at.button[[b.label for b in at.button].index("💾 Save changes")].click(); at.run()
check("billed trip edit blocked", any("billed" in e.value.lower() for e in at.error) and FAKE.tables["trips"][0]["loading_weight"] == 32.0, errs(at))

print(f"\n{sum(ok)}/{len(ok)} passed"); sys.exit(0 if all(ok) else 1)
