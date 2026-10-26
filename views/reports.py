from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils import db
from utils.db import DBError
from utils.helpers import STRETCH, num, to_date, download_excel
from utils.styles import page_header, section, kpi_row, empty_state
from views.dashboard import _style, _chart, NAVY, GOLD, GREEN, RED, PALETTE

MONEY = "{:,.0f}"


def _show(df: pd.DataFrame, name: str, fmts: dict, key: str):
    st.dataframe(df.style.format(fmts), hide_index=True, **STRETCH)
    download_excel("⬇ Download Excel", {name: df}, f"{name.lower().replace(' ', '_')}.xlsx", key=key)


def _in_range(rows, key, a, b):
    return [r for r in rows if (d := to_date(r.get(key))) and a <= d <= b]


def render():
    page_header("Reports", "Profit & loss, receivables, expenses and driver analysis / رپورٹیں", "📈")
    try:
        today = date.today()
        c1, c2, _ = st.columns([1, 1, 2])
        a = c1.date_input("From", value=today.replace(month=1, day=1), format="DD/MM/YYYY", key="rp_a")
        b = c2.date_input("To", value=today, format="DD/MM/YYYY", key="rp_b")
        if a > b:
            st.error("“From” date must be before “To” date.")
            return
        vehicles = {v["id"]: v["vehicle_number"] for v in db.fetch("vehicles")}
        drivers = {d["id"]: d["name"] for d in db.fetch("drivers")}
        customers = {c["id"]: c["name"] for c in db.fetch("customers")}
        trips = [t for t in _in_range(db.fetch("trips"), "trip_date", a, b) if t.get("status") != "Cancelled"]
        exps = _in_range(db.fetch("expenses"), "expense_date", a, b)
        invoices = db.fetch("invoices")
        payments = [p for p in db.fetch("payments") if p.get("status") != "Bounced"]
        advances = _in_range(db.fetch("driver_advances"), "advance_date", a, b)
    except DBError as e:
        st.error(f"⚠️ {e}")
        return

    rev, spend = sum(num(t.get("total_freight")) for t in trips), sum(num(e.get("amount")) for e in exps)
    kpi_row([("Revenue", f"{rev:,.0f}", "PKR", "💰", "gold"), ("Expenses", f"{spend:,.0f}", "PKR", "💸", "red"),
             ("Net Profit", f"{rev - spend:,.0f}", f"{(rev - spend) / rev * 100 if rev else 0:.1f}% margin", "📈",
              "green" if rev >= spend else "red"),
             ("Tons", f"{sum(num(t.get('loading_weight')) for t in trips):,.0f}", f"{len(trips)} trips", "⚖️", "navy")])

    t1, t2, t3, t4, t5 = st.tabs(["🚛 Vehicle P&L", "🏭 Customers", "⏳ Receivables Ageing", "💸 Expenses", "👤 Drivers"])

    with t1:
        rows = []
        for vid, vn in vehicles.items():
            vt = [t for t in trips if t.get("vehicle_id") == vid]
            r = sum(num(t.get("total_freight")) for t in vt)
            tn = sum(num(t.get("loading_weight")) for t in vt)
            e = sum(num(x.get("amount")) for x in exps if x.get("vehicle_id") == vid)
            rows.append({"Vehicle": vn, "Trips": len(vt), "Tons": tn, "Revenue": r, "Expenses": e, "Profit": r - e,
                         "Margin %": (r - e) / r * 100 if r else 0, "Profit / Ton": (r - e) / tn if tn else 0})
        un = sum(num(x.get("amount")) for x in exps if not x.get("vehicle_id"))
        if un:
            rows.append({"Vehicle": "(Unassigned expenses)", "Trips": 0, "Tons": 0, "Revenue": 0, "Expenses": un,
                         "Profit": -un, "Margin %": 0, "Profit / Ton": 0})
        df = pd.DataFrame(rows)
        if df.empty or (df["Revenue"].sum() == 0 and df["Expenses"].sum() == 0):
            empty_state("No data in this period", "🚛")
        else:
            df = df.sort_values("Profit", ascending=False)
            with st.container(border=True):
                fig = go.Figure(go.Bar(x=df["Vehicle"], y=df["Profit"], marker_color=[GREEN if x >= 0 else RED for x in df["Profit"]]))
                _chart(_style(fig, 280))
            _show(df, "Vehicle PnL", {"Tons": "{:,.1f}", "Revenue": MONEY, "Expenses": MONEY, "Profit": MONEY,
                                      "Margin %": "{:.1f}", "Profit / Ton": MONEY}, "rp_v")

    with t2:
        rows = []
        for cid, cn in customers.items():
            ct = [t for t in trips if t.get("customer_id") == cid]
            inv_p = [i for i in _in_range(invoices, "invoice_date", a, b) if i.get("customer_id") == cid]
            rc = sum(num(p.get("amount")) for p in _in_range(payments, "payment_date", a, b) if p.get("customer_id") == cid)
            rows.append({"Customer": cn, "Trips": len(ct), "Tons": sum(num(t.get("loading_weight")) for t in ct),
                         "Freight": sum(num(t.get("total_freight")) for t in ct),
                         "Invoiced": sum(num(i.get("net_amount")) for i in inv_p), "Received": rc,
                         "Outstanding (all time)": sum(num(i.get("balance")) for i in invoices if i.get("customer_id") == cid)})
        df = pd.DataFrame(rows)
        if df.empty:
            empty_state("No customers yet", "🏭")
        else:
            _show(df.sort_values("Freight", ascending=False), "Customers",
                  {"Tons": "{:,.1f}", "Freight": MONEY, "Invoiced": MONEY, "Received": MONEY, "Outstanding (all time)": MONEY}, "rp_c")

    with t3:
        buckets = ["Not due", "1-30", "31-60", "61-90", "90+"]
        agg: dict[str, dict] = {}
        for i in invoices:
            bal = num(i.get("balance"))
            if bal <= 0.5:
                continue
            d = to_date(i.get("due_date"))
            late = (today - d).days if d else 0
            bk = buckets[0] if late <= 0 else buckets[1] if late <= 30 else buckets[2] if late <= 60 else buckets[3] if late <= 90 else buckets[4]
            row = agg.setdefault(customers.get(i.get("customer_id"), "—"), {k: 0.0 for k in buckets})
            row[bk] += bal
        if not agg:
            empty_state("No outstanding invoices 🎉", "✅")
        else:
            df = pd.DataFrame([{"Customer": k, **v, "Total": sum(v.values())} for k, v in agg.items()]).sort_values("Total", ascending=False)
            _show(df, "Receivables Ageing", {k: MONEY for k in [*buckets, "Total"]}, "rp_ag")

    with t4:
        if not exps:
            empty_state("No expenses in this period", "💸")
        else:
            df = pd.DataFrame(exps)
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            l, r = st.columns([1, 1.3])
            with l.container(border=True):
                _chart(_style(go.Figure(go.Pie(labels=cat.index, values=cat.values, hole=.55, marker=dict(colors=PALETTE))), 300))
            with r:
                _show(cat.reset_index().rename(columns={"category": "Category", "amount": "Amount"}), "Expense by Category",
                      {"Amount": MONEY}, "rp_ec")
            section("Expense register")
            reg = pd.DataFrame([{"Date": e.get("expense_date"), "Category": e.get("category"), "Amount": num(e.get("amount")),
                                 "Vehicle": vehicles.get(e.get("vehicle_id"), ""), "Driver": drivers.get(e.get("driver_id"), ""),
                                 "Description": e.get("description") or ""} for e in exps]).sort_values("Date", ascending=False)
            _show(reg, "Expense Register", {"Amount": MONEY}, "rp_er")

    with t5:
        rows = []
        for did, dn in drivers.items():
            dt = [t for t in trips if t.get("driver_id") == did]
            adv = sum(num(x.get("amount")) for x in advances if x.get("driver_id") == did and x.get("status") == "Given")
            rows.append({"Driver": dn, "Trips": len(dt), "Tons": sum(num(t.get("loading_weight")) for t in dt),
                         "Freight": sum(num(t.get("total_freight")) for t in dt), "Advances (Given)": adv})
        df = pd.DataFrame(rows)
        if df.empty:
            empty_state("No drivers yet", "👤")
        else:
            _show(df.sort_values("Trips", ascending=False), "Drivers", {"Tons": "{:,.1f}", "Freight": MONEY, "Advances (Given)": MONEY}, "rp_d")
