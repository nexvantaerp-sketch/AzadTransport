from datetime import date, timedelta
import pandas as pd
import streamlit as st
from utils import db
from utils.auth import can_edit
from utils.billing import invoice_html
from utils.crud import fk_map, flash, _delete_dialog
from utils.db import DBError
from utils.helpers import STRETCH, num, pkr, fmt_date, status_text, to_date, download_excel
from utils.styles import page_header, section, kpi_row, empty_state


def eff_status(inv: dict) -> str:
    d = to_date(inv.get("due_date"))
    if inv.get("status") != "Paid" and num(inv.get("balance")) > 0.5 and d and d < date.today():
        return "Overdue"
    return inv.get("status", "Pending")


def _next_invoice_no() -> str:
    prefix = f"INV-{date.today():%Y%m%d}-"
    n = sum(1 for i in db.fetch("invoices") if str(i.get("invoice_number", "")).startswith(prefix))
    return f"{prefix}{n + 1:02d}"


# ───────────────────────── list ─────────────────────────
def _list_tab(customers: dict):
    invoices = db.fetch("invoices", "invoice_date")
    if not invoices:
        empty_state("No invoices yet — create the first one from the “Create Invoice” tab.", "🧾")
        return
    for i in invoices:
        i["_status"] = eff_status(i)
    tot = sum(num(i.get("net_amount")) for i in invoices)
    paid = sum(num(i.get("paid_amount")) for i in invoices)
    due = sum(num(i.get("balance")) for i in invoices)
    over = sum(num(i.get("balance")) for i in invoices if i["_status"] == "Overdue")
    kpi_row([("Total Invoiced", pkr(tot), f"{len(invoices)} invoices", "🧾", "navy"),
             ("Received", pkr(paid), "against invoices", "✅", "green"),
             ("Outstanding", pkr(due), "balance due", "⏳", "gold"),
             ("Overdue", pkr(over), "past due date", "⚠️", "red")])

    c1, c2 = st.columns([2.4, 1.2])
    q = c1.text_input("Search", placeholder="🔍 Search invoice no / customer…", label_visibility="collapsed", key="inv_q")
    stf = c2.selectbox("Status", ["All statuses", "Pending", "Partial", "Paid", "Overdue"],
                       label_visibility="collapsed", key="inv_st")
    rows = []
    for i in invoices:
        rows.append({"_id": i["id"], "Invoice": i["invoice_number"], "Date": fmt_date(i.get("invoice_date")),
                     "Customer": customers.get(i.get("customer_id"), "—"), "Net Amount": pkr(i.get("net_amount")),
                     "Received": pkr(i.get("paid_amount")), "Balance": pkr(i.get("balance")),
                     "Due": fmt_date(i.get("due_date")), "Status": status_text(i["_status"]), "_s": i["_status"]})
    df = pd.DataFrame(rows)
    if stf != "All statuses":
        df = df[df["_s"] == stf]
    if q:
        ql = q.lower()
        df = df[df[["Invoice", "Customer"]].apply(lambda s: s.str.lower().str.contains(ql, regex=False)).any(axis=1)]
    df = df.reset_index(drop=True)
    if df.empty:
        empty_state("No invoices match.", "🔎")
        return
    shown = df.drop(columns=["_id", "_s"])
    h1, h2 = st.columns([5, 1])
    h1.caption(f"{len(df)} invoice(s) — select a row to view details")
    with h2:
        download_excel("⬇ Excel", {"Invoices": shown}, "invoices.xlsx", key="inv_xl")
    ev = st.dataframe(shown, hide_index=True, on_select="rerun", selection_mode="single-row", key="inv_tbl",
                      height=min(440, 38 + 35 * len(shown)), **STRETCH)
    sel = ev.selection.rows if ev and ev.selection else []
    if not sel or sel[0] >= len(df):
        return
    inv = next((i for i in invoices if i["id"] == df.loc[sel[0], "_id"]), None)
    if inv:
        _detail(inv, customers)


def _detail(inv: dict, customers: dict):
    items = db.where("invoice_items", "invoice_id", inv["id"])
    trips = {t["id"]: t for t in db.fetch("trips")}
    vehicles = fk_map(("vehicles", "vehicle_number"))
    cust = next((c for c in db.fetch("customers") if c["id"] == inv.get("customer_id")), {})
    payments = db.where("payments", "invoice_id", inv["id"])
    with st.container(border=True):
        section(f"Invoice {inv['invoice_number']} — {customers.get(inv.get('customer_id'), '—')}")
        a, b, c, d = st.columns(4)
        a.metric("Subtotal", pkr(inv.get("total_amount")))
        b.metric("Tax / WHT", pkr(inv.get("tax_amount")))
        c.metric("Net payable", pkr(inv.get("net_amount")))
        d.metric("Balance due", pkr(inv.get("balance")))
        idf = pd.DataFrame([{
            "Description": it.get("description"), "Vehicle": vehicles.get(trips.get(it.get("trip_id"), {}).get("vehicle_id"), "—"),
            "Qty (T)": num(it.get("quantity")), "Rate": num(it.get("rate")), "Amount": num(it.get("amount"))} for it in items])
        if not idf.empty:
            st.dataframe(idf.style.format({"Qty (T)": "{:,.2f}", "Rate": "{:,.0f}", "Amount": "{:,.0f}"}),
                         hide_index=True, **STRETCH)
        if payments:
            st.caption("Payments received")
            pdf = pd.DataFrame([{"Date": fmt_date(p.get("payment_date")), "Amount": num(p.get("amount")),
                                 "Method": p.get("payment_method"), "Reference": p.get("reference_number"),
                                 "Status": p.get("status")} for p in payments])
            st.dataframe(pdf.style.format({"Amount": "{:,.0f}"}), hide_index=True, **STRETCH)
        if inv.get("notes"):
            st.info(inv["notes"])
        x, y, _ = st.columns([1.3, 1, 3])
        x.download_button("🖨️ Print / Download Invoice", invoice_html(inv, cust, items, trips, vehicles),
                          file_name=f"{inv['invoice_number']}.html", mime="text/html", key=f"dl_{inv['id']}", **STRETCH)
        if can_edit() and y.button("🗑️ Delete", key=f"delinv_{inv['id']}", **STRETCH):
            _delete_dialog(DELETE_CFG, inv)


def _before_delete(inv):
    if db.where("payments", "invoice_id", inv["id"]):
        raise DBError("This invoice has payments recorded against it. Delete those payments first.")
    inv["_trip_ids"] = [i["trip_id"] for i in db.where("invoice_items", "invoice_id", inv["id"]) if i.get("trip_id")]


def _after_delete(inv):
    for tid in inv.get("_trip_ids", []):
        db.update("trips", tid, {"status": "Delivered"})


DELETE_CFG = dict(table="invoices", noun="Invoice", label=lambda r: r["invoice_number"],
                  before_delete=_before_delete, after_delete=_after_delete)


# ───────────────────────── create ─────────────────────────
def _create_tab(customers: dict):
    if not customers:
        st.warning("⚠️ Please add a customer first.")
        return
    ver = st.session_state.setdefault("inv_ver", 0)
    with st.container(border=True):
        section("1 · Customer & dates")
        c1, c2, c3 = st.columns(3)
        cid = c1.selectbox("Customer", list(customers), format_func=lambda x: customers[x], key=f"ic_{ver}")
        inv_date = c2.date_input("Invoice date", value=date.today(), key=f"id_{ver}", format="DD/MM/YYYY")
        cust = next((c for c in db.fetch("customers") if c["id"] == cid), {})
        terms = int(num(cust.get("payment_terms"), 30))
        due = c3.date_input("Due date", value=inv_date + timedelta(days=terms), key=f"idue_{ver}_{cid}_{inv_date}",
                            format="DD/MM/YYYY")

        section("2 · Select trips to bill")
        pool = [t for t in db.fetch("trips", "trip_date") if t.get("customer_id") == cid and t.get("status") != "Billed"
                and t.get("status") != "Cancelled"]
        incl = st.toggle("Include Pending / In-Transit trips (default: Delivered only)", key=f"ii_{ver}")
        pool = [t for t in pool if incl or t.get("status") == "Delivered"]
        vehicles = fk_map(("vehicles", "vehicle_number"))
        lab = {t["id"]: f"{t['trip_number']} · {fmt_date(t.get('trip_date'))} · {vehicles.get(t.get('vehicle_id'), '—')} · "
                        f"{num(t.get('loading_weight')):,.1f}T · {pkr(t.get('total_freight'))}" for t in pool}
        picked = st.multiselect("Trips", list(lab), default=list(lab), format_func=lambda x: lab[x],
                                key=f"it_{ver}_{cid}_{incl}", placeholder="No billable trips for this customer")
        if not pool:
            st.caption("No unbilled trips for this customer. Mark trips as **Delivered** in the Trips page first.")

        section("3 · Charges & tax")
        d1, d2, d3 = st.columns(3)
        extra = d1.number_input("Additional charges (PKR)", min_value=0.0, step=500.0, key=f"ie_{ver}")
        extra_desc = d2.text_input("Additional charges description", key=f"ied_{ver}", placeholder="Detention, loading…")
        tax_pct = d3.number_input("Withholding tax %", min_value=0.0, max_value=100.0, step=0.5, key=f"itx_{ver}")
        e1, e2 = st.columns([1, 2])
        inv_no = e1.text_input("Invoice number", value=_next_invoice_no(), key=f"in_{ver}")
        notes = e2.text_input("Notes", key=f"inn_{ver}")

    chosen = [t for t in pool if t["id"] in picked]
    sub = sum(num(t.get("total_freight")) for t in chosen) + extra
    tax = round(sub * tax_pct / 100, 2)
    net = round(sub - tax, 2)
    kpi_row([("Trips", len(chosen), "selected", "🗺️", "navy"), ("Subtotal", pkr(sub), "", "🧮", "gold"),
             ("Tax / WHT", pkr(tax), f"{tax_pct:g}%", "🏛️", "red"), ("Net Payable", pkr(net), "", "💰", "green")])

    if st.button("🧾 Generate Invoice", type="primary", key=f"igen_{ver}"):
        if not inv_no.strip():
            st.error("Invoice number is required.")
            return
        if sub <= 0:
            st.error("Select at least one trip or add an additional charge.")
            return
        try:
            inv = db.insert("invoices", {
                "invoice_number": inv_no.strip(), "invoice_date": inv_date.isoformat(), "customer_id": cid,
                "total_amount": sub, "tax_amount": tax, "net_amount": net, "paid_amount": 0, "balance": net,
                "due_date": due.isoformat(), "status": "Pending", "notes": notes or None})
            try:
                items = []
                for t in chosen:
                    fr, rate = num(t.get("total_freight")), num(t.get("rate_per_ton"))
                    qty = round(fr / rate, 2) if rate else num(t.get("loading_weight"))
                    items.append({"invoice_id": inv["id"], "trip_id": t["id"], "quantity": qty, "rate": rate, "amount": fr,
                                  "description": f"{t['trip_number']} · {fmt_date(t.get('trip_date'))} · "
                                                 f"{t.get('loading_point') or '—'} → {t.get('unloading_point') or '—'}"})
                if extra > 0:
                    items.append({"invoice_id": inv["id"], "trip_id": None, "quantity": 1, "rate": extra,
                                  "amount": extra, "description": extra_desc or "Additional charges"})
                db.insert_many("invoice_items", items)
                for t in chosen:
                    db.update("trips", t["id"], {"status": "Billed"})
            except DBError:
                db.delete("invoices", inv["id"])          # roll back the half-created invoice
                raise
        except DBError as e:
            st.error(str(e))
            return
        st.session_state["inv_ver"] = ver + 1
        flash(f"Invoice {inv_no} created for {pkr(net)}", "🧾")
        st.rerun()


def render():
    page_header("Freight & Billing", "Generate invoices from delivered trips & track dues / بلنگ اور انوائس", "🧾")
    try:
        customers = fk_map(("customers", "name"))
        if not can_edit():
            _list_tab(customers)
            return
        t1, t2 = st.tabs(["📋 Invoices", "➕ Create Invoice"])
        with t1:
            _list_tab(customers)
        with t2:
            _create_tab(customers)
    except DBError as e:
        st.error(f"⚠️ {e}")
