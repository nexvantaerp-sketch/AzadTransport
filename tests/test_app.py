import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from datetime import date
from utils import auth, db

PASS, FAIL = [], []
def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("✅ " if cond else "❌ ") + name + (f"  → {extra}" if extra and not cond else ""))

# ───────── 1. Login flow through the real app.py (st.navigation) ─────────
reset()
at = AppTest.from_file(os.path.join(BASE, "app.py"), default_timeout=60).run()
check("login screen renders without exception", not at.exception, at.exception)
check("admin auto-created on first run", len(FAKE.tables.get("app_users", [])) == 1)
check("stored hash is salted pbkdf2", FAKE.tables["app_users"][0]["password_hash"].startswith("pbkdf2$"))
at.text_input[0].set_value("admin"); at.text_input[1].set_value("wrong"); at.button[0].click(); at.run()
check("wrong password rejected", any("Invalid" in e.value for e in at.error))
at.text_input[0].set_value("admin"); at.text_input[1].set_value("admin123"); at.button[0].click(); at.run()
check("login succeeds → main app, no exception", not at.exception and at.session_state["logged_in"], at.exception)
check("dashboard renders after login (default-password warning shown)", any("default password" in w.value for w in at.warning))

# placeholder-hash self-heal
reset(); FAKE.tables["app_users"] = [{"id": "x", "username": "admin", "password_hash": "pbkdf2:sha256:600000$azad$e3b0", "status": "Active"}]
auth.ensure_admin()
check("broken placeholder admin replaced", len(FAKE.tables["app_users"]) == 1 and FAKE.tables["app_users"][0]["password_hash"].startswith("pbkdf2$"))

# ───────── 2. Entity pages: add records through the real forms ─────────
def fill_and_submit(at, form_idx_button_label, values: dict):
    pass

reset()
# vehicles
at = view_test("vehicles"); check("vehicles page (empty) renders", not at.exception, errs(at))
at.text_input(key="n_vehicles_0_vehicle_number").set_value("tkr-1234")
at.button[[b.label for b in at.button].index("💾 Save Vehicle")].click(); at.run()
check("vehicle saved (upper-cased)", FAKE.tables.get("vehicles") and FAKE.tables["vehicles"][0]["vehicle_number"] == "TKR-1234", errs(at))
at = view_test("vehicles"); check("vehicles list renders with data", not at.exception, errs(at))

# duplicate
at.text_input(key="n_vehicles_0_vehicle_number").set_value("TKR-1234")
at.button[[b.label for b in at.button].index("💾 Save Vehicle")].click(); at.run()
check("duplicate vehicle shows friendly error", any("already exists" in e.value for e in at.error), errs(at))

# drivers (two with blank CNIC must not collide)
for n in ("Ali", "Bilal"):
    at = view_test("drivers")
    at.text_input(key="n_drivers_0_name").set_value(n)
    at.button[[b.label for b in at.button].index("💾 Save Driver")].click(); at.run()
check("two drivers with empty CNIC saved", len(FAKE.tables.get("drivers", [])) == 2, errs(at))
at = view_test("drivers"); at.text_input(key="n_drivers_0_name").set_value("Bad"); at.text_input(key="n_drivers_0_cnic").set_value("123")
at.button[[b.label for b in at.button].index("💾 Save Driver")].click(); at.run()
check("bad CNIC rejected", any("CNIC" in e.value for e in at.error), errs(at))

# customers
at = view_test("customers"); at.text_input(key="n_customers_0_name").set_value("Habib Sugar Mills")
at.number_input(key="n_customers_0_rate_per_ton").set_value(2500.0)
at.button[[b.label for b in at.button].index("💾 Save Customer")].click(); at.run()
check("customer saved", len(FAKE.tables.get("customers", [])) == 1, errs(at))

# trips
at = view_test("trips"); check("trips form renders (fk selects)", not at.exception, errs(at))
at.number_input(key="n_trips_0_loading_weight").set_value(30.0)
at.number_input(key="n_trips_0_unloading_weight").set_value(29.5)
at.selectbox(key="n_trips_0_status").set_value("Delivered")
at.button[[b.label for b in at.button].index("💾 Save Trip")].click(); at.run()
tr = FAKE.tables.get("trips", [{}])[0]
check("trip saved; rate defaulted from customer", tr.get("rate_per_ton") == 2500.0, errs(at) or tr)
check("trip freight = 30T × 2500", tr.get("total_freight") == 75000.0, tr)
check("trip shortage computed 0.5", tr.get("weight_difference") == 0.5, tr)
at = view_test("trips"); check("trips list renders", not at.exception, errs(at))

# expenses
at = view_test("expenses"); at.number_input(key="n_expenses_0_amount").set_value(15000.0)
at.selectbox(key="n_expenses_0_trip_id").set_value(FAKE.tables["trips"][0]["id"])
at.button[[b.label for b in at.button].index("💾 Save Expense")].click(); at.run()
ex = FAKE.tables.get("expenses", [{}])[0]
check("expense saved, vehicle auto-filled from trip", ex.get("vehicle_id") == FAKE.tables["trips"][0]["vehicle_id"], errs(at) or ex)
at = view_test("expenses"); at.number_input(key="n_expenses_0_amount").set_value(0.0)
at.button[[b.label for b in at.button].index("💾 Save Expense")].click(); at.run()
check("zero expense rejected", any("greater than 0" in e.value for e in at.error), errs(at))

# advances
at = view_test("advances"); at.number_input(key="n_driver_advances_0_amount").set_value(5000.0)
at.button[[b.label for b in at.button].index("💾 Save Advance")].click(); at.run()
check("driver advance saved", len(FAKE.tables.get("driver_advances", [])) == 1, errs(at))

# ───────── 3. Billing flow ─────────
at = view_test("billing"); check("billing page renders", not at.exception, errs(at))
at.button[[b.label for b in at.button].index("🧾 Generate Invoice")].click(); at.run()
inv = FAKE.tables.get("invoices", [{}])[0]
check("invoice generated from delivered trip", inv.get("net_amount") == 75000.0, errs(at) or inv)
check("invoice items created", len(FAKE.tables.get("invoice_items", [])) == 1)
check("trip marked Billed", FAKE.tables["trips"][0]["status"] == "Billed")
at = view_test("billing"); check("invoice list + detail path renders", not at.exception, errs(at))

# ───────── 4. Payments update invoice ─────────
at = view_test("payments")
cust = FAKE.tables["customers"][0]["id"]
at.selectbox(key="n_payments_0_invoice_id").set_value(inv["id"])
at.number_input(key="n_payments_0_amount").set_value(25000.0)
at.button[[b.label for b in at.button].index("💾 Save Payment")].click(); at.run()
inv = FAKE.tables["invoices"][0]
check("partial payment → invoice Partial, balance 50000", inv["status"] == "Partial" and inv["balance"] == 50000.0, errs(at) or inv)
at = view_test("payments"); at.selectbox(key="n_payments_0_invoice_id").set_value(inv["id"]); at.number_input(key="n_payments_0_amount").set_value(90000.0)
at.button[[b.label for b in at.button].index("💾 Save Payment")].click(); at.run()
check("overpayment rejected", any("exceeds" in e.value for e in at.error), errs(at))
at = view_test("payments"); at.selectbox(key="n_payments_0_invoice_id").set_value(inv["id"]); at.number_input(key="n_payments_0_amount").set_value(50000.0)
at.button[[b.label for b in at.button].index("💾 Save Payment")].click(); at.run()
check("full payment → invoice Paid", FAKE.tables["invoices"][0]["status"] == "Paid" and FAKE.tables["invoices"][0]["balance"] == 0, errs(at))

# ───────── 5. Read-only pages with data ─────────
for m in ("dashboard", "reports", "settings", "advances", "payments", "billing", "expenses"):
    at = view_test(m); check(f"{m} renders with data", not at.exception, errs(at))
at = view_test("reports"); check("reports tabs rendered", len(at.tabs) >= 5)
at = view_test("settings"); 
at.button[[b.label for b in at.button].index("🔍 Run system check")].click() if any(b.label == "🔍 Run system check" for b in at.button) else None
at.run(); check("system check runs", not at.exception, errs(at))

# viewer role cannot see forms
at = view_test("trips", user={"id": "v", "username": "v", "role": "viewer"})
check("viewer: read-only (no Save button)", not any("Save Trip" in b.label for b in at.button), [b.label for b in at.button])

# delete flow block: billed trip
rec = FAKE.tables["trips"][0]
from views import trips as tv
try: tv._before_delete(rec); check("billed trip delete blocked", False)
except db.DBError: check("billed trip delete blocked", True)

# ───────── 6. Dropdown Lists (add / remove), quick add, invoice PDF ─────────
from utils import options
K, D = options.list_key("expenses", "category"), ["Diesel", "Toll Tax", "Other"]
check("defaults used when nothing customised", options.effective(K, D) == D)
options.add(K, "Parking Fee", D)
check("added option shows in list", options.effective(K, D) == D + ["Parking Fee"])
at = view_test("expenses")
check("added option appears in the form dropdown", "Parking Fee" in at.selectbox(key="n_expenses_0_category").options)
try: options.add(K, "parking fee", D); check("duplicate (any case) rejected", False)
except db.DBError: check("duplicate (any case) rejected", True)
options.remove(K, "Toll Tax", D)
check("built-in option can be removed", "Toll Tax" not in options.effective(K, D))
at = view_test("expenses")
check("removed option gone from form dropdown", "Toll Tax" not in at.selectbox(key="n_expenses_0_category").options)
check("removed built-in listed for restore", options.removed_defaults(K, D) == ["Toll Tax"])
options.restore(K, "Toll Tax")
check("removed option restored", "Toll Tax" in options.effective(K, D))
options.remove(K, "Parking Fee", D)
check("added option can be removed (row deleted)", "Parking Fee" not in options.effective(K, D))
try: options.remove(options.list_key("x", "y"), "A", ["A"]); check("last option cannot be removed", False)
except db.DBError: check("last option cannot be removed", True)
from utils import crud
check("status/freight_basis locked", not crud._allow_new({"key": "status"}) and not crud._allow_new({"key": "freight_basis"}) and crud._allow_new({"key": "category"}))

at = view_test("dropdowns"); check("Dropdown Lists page renders", not at.exception, errs(at))
check("list picker has every free dropdown", len(at.selectbox(key="dl_pick").options) >= 6, len(at.selectbox(key="dl_pick").options))
_sb = at.selectbox(key="dl_pick"); _sb.select_index(list(_sb.options).index("Expenses  →  Category")).run()
at.button(key="rm_expenses.category_0").click(); at.run()
check("Remove button on page removes the option", "Diesel" not in options.effective(K, D), errs(at))
# hide a vehicle from dropdowns (Inactive) — records stay
vid = FAKE.tables["vehicles"][0]["id"]
at = view_test("dropdowns"); at.segmented_control(key="dl_ent").set_value("🚛 Vehicles").run()
at.button(key=f"hd_{vid}").click(); at.run()
check("Hide sets vehicle Inactive", FAKE.tables["vehicles"][0]["status"] == "Inactive", errs(at))
at = view_test("expenses")
VN = FAKE.tables["vehicles"][0]["vehicle_number"]
check("hidden vehicle not offered in dropdown", VN not in at.selectbox(key="n_expenses_0_vehicle_id").options, at.selectbox(key="n_expenses_0_vehicle_id").options)
db.update("vehicles", vid, {"status": "Active"})
at = view_test("expenses")
check("vehicle back in dropdown after Show again", VN in at.selectbox(key="n_expenses_0_vehicle_id").options)

at = view_test("trips"); check("trips shows ➕ quick-add buttons", any("New Customer" in b.label for b in at.button) and any("New Vehicle" in b.label for b in at.button), [b.label for b in at.button])
at = view_test("dropdowns", user={"id": "v", "username": "v", "role": "viewer"}); check("viewer cannot edit lists", not at.exception and not any("Remove" in b.label for b in at.button))
from utils.billing import invoice_pdf
_inv = FAKE.tables["invoices"][0]
_items = db.where("invoice_items", "invoice_id", _inv["id"])
_pdf = invoice_pdf(_inv, FAKE.tables["customers"][0], _items, {t["id"]: t for t in FAKE.tables["trips"]}, {v["id"]: v["vehicle_number"] for v in FAKE.tables["vehicles"]})
check("invoice PDF generated", _pdf[:5] == b"%PDF-" and len(_pdf) > 1500)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
