from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils import db
from utils.auth import current_user
from utils.config import EXPIRY_WARN_DAYS
from utils.db import DBError
from utils.helpers import STRETCH, num, pkr, pkr_short, fmt_date, to_date, status_text
from utils.styles import page_header, section, kpi_row, empty_state, alert_rows

NAVY, GOLD, GREEN, RED, BLUE = "#0F2A5C", "#C9A227", "#16A34A", "#DC2626", "#2563EB"
PALETTE = [NAVY, GOLD, BLUE, GREEN, "#7C3AED", RED, "#0891B2", "#64748B"]


def _frame(rows, date_col, nums):
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[date_col, *nums])
    for c in nums:
        df[c] = pd.to_numeric(df.get(c), errors="coerce").fillna(0) if c in df else 0.0
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce") if date_col in df else pd.NaT
    return df


def _style(fig, h=320):
    fig.update_layout(template="plotly_white", height=h, margin=dict(l=8, r=8, t=28, b=8),
                      font=dict(family="Inter, sans-serif", color="#334155"),
                      legend=dict(orientation="h", y=1.14, x=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    return fig


def _chart(fig):
    st.plotly_chart(fig, config={"displayModeBar": False}, **STRETCH)


def _period(label: str):
    today = date.today()
    if label == "This month":
        return today.replace(day=1), today
    if label == "Last 30 days":
        return today - timedelta(days=30), today
    if label == "This year":
        return today.replace(month=1, day=1), today
    return None, None


def render():
    page_header("Dashboard", f"Business overview · {date.today():%A, %d %B %Y} / کاروبار کا جائزہ", "📊")
    try:
        vehicles, drivers = db.fetch("vehicles"), db.fetch("drivers")
        customers = {c["id"]: c["name"] for c in db.fetch("customers")}
        trips_all, exp_all = db.fetch("trips", "trip_date"), db.fetch("expenses", "expense_date")
        pays_all, invoices = db.fetch("payments", "payment_date"), db.fetch("invoices", "invoice_date")
    except DBError as e:
        st.error(f"⚠️ {e}")
        return

    if current_user().get("using_default_password"):
        st.warning("🔐 You are using the default password. Go to **Settings → My Account** and change it now.")

    choice = st.segmented_control("Period", ["This month", "Last 30 days", "This year", "All time"],
                                  default="This year", label_visibility="collapsed", key="dash_period") or "All time"
    start, end = _period(choice)

    trips = _frame([t for t in trips_all if t.get("status") != "Cancelled"], "trip_date", ["total_freight", "loading_weight"])
    exp = _frame(exp_all, "expense_date", ["amount"])
    pays = _frame([p for p in pays_all if p.get("status") != "Bounced"], "payment_date", ["amount"])
    if start:
        a, b = pd.Timestamp(start), pd.Timestamp(end)
        trips = trips[(trips["trip_date"] >= a) & (trips["trip_date"] <= b)]
        exp = exp[(exp["expense_date"] >= a) & (exp["expense_date"] <= b)]
        pays = pays[(pays["payment_date"] >= a) & (pays["payment_date"] <= b)]

    revenue, spend = trips["total_freight"].sum(), exp["amount"].sum()
    profit = revenue - spend
    margin = (profit / revenue * 100) if revenue else 0
    outstanding = sum(num(i.get("balance")) for i in invoices)
    overdue = sum(num(i.get("balance")) for i in invoices
                  if num(i.get("balance")) > 0.5 and (d := to_date(i.get("due_date"))) and d < date.today())
    unbilled = sum(num(t.get("total_freight")) for t in trips_all if t.get("status") == "Delivered")
    active_v = sum(1 for v in vehicles if v.get("status") == "Active")

    kpi_row([("Revenue", pkr_short(revenue), pkr(revenue), "💰", "gold"),
             ("Expenses", pkr_short(spend), pkr(spend), "💸", "red"),
             ("Net Profit", pkr_short(profit), f"{margin:.1f}% margin", "📈", "green" if profit >= 0 else "red"),
             ("Tons Moved", f"{trips['loading_weight'].sum():,.0f}", f"{len(trips)} trips", "⚖️", "navy")])
    kpi_row([("Receivable", pkr_short(outstanding), "outstanding invoices", "⏳", "gold"),
             ("Overdue", pkr_short(overdue), "past due date", "⚠️", "red"),
             ("Delivered, Not Billed", pkr_short(unbilled), "create invoices for these", "🧾", "blue"),
             ("Collected", pkr_short(pays["amount"].sum()), "in selected period", "✅", "green"),
             ("Fleet", f"{active_v}/{len(vehicles)}", f"active · {len(drivers)} drivers", "🚛", "navy")])

    if trips.empty and exp.empty:
        empty_state("No activity in this period. Add trips and expenses to see analytics.", "🗺️")
    else:
        monthly = pd.concat([
            trips.groupby(trips["trip_date"].dt.to_period("M"))["total_freight"].sum().rename("Revenue"),
            exp.groupby(exp["expense_date"].dt.to_period("M"))["amount"].sum().rename("Expenses")], axis=1).fillna(0).sort_index()
        monthly["Profit"] = monthly["Revenue"] - monthly["Expenses"]
        monthly.index = monthly.index.astype(str)
        c1, c2 = st.columns([3, 2])
        with c1.container(border=True):
            section("Revenue vs Expenses")
            fig = go.Figure()
            fig.add_bar(x=monthly.index, y=monthly["Revenue"], name="Revenue", marker_color=NAVY)
            fig.add_bar(x=monthly.index, y=monthly["Expenses"], name="Expenses", marker_color=GOLD)
            fig.add_scatter(x=monthly.index, y=monthly["Profit"], name="Profit", mode="lines+markers",
                            line=dict(color=GREEN, width=3))
            fig.update_layout(barmode="group")
            _chart(_style(fig))
        with c2.container(border=True):
            section("Top Customers")
            tc = trips.assign(c=trips.get("customer_id").map(customers).fillna("Unknown")) if "customer_id" in trips else trips.assign(c="Unknown")
            tc = tc.groupby("c")["total_freight"].sum().nlargest(6).sort_values()
            fig = go.Figure(go.Bar(x=tc.values, y=tc.index, orientation="h", marker_color=GOLD))
            _chart(_style(fig))
        c3, c4, c5 = st.columns(3)
        with c3.container(border=True):
            section("Expense Breakdown")
            if exp.empty:
                st.caption("No expenses")
            else:
                ec = exp.groupby("category")["amount"].sum()
                _chart(_style(go.Figure(go.Pie(labels=ec.index, values=ec.values, hole=.55,
                                               marker=dict(colors=PALETTE))), 290))
        with c4.container(border=True):
            section("Trip Status")
            if trips.empty:
                st.caption("No trips")
            else:
                sv = trips["status"].value_counts()
                _chart(_style(go.Figure(go.Pie(labels=sv.index, values=sv.values, hole=.55,
                                               marker=dict(colors=PALETTE))), 290))
        with c5.container(border=True):
            section("Profit by Vehicle")
            vm = {v["id"]: v["vehicle_number"] for v in vehicles}
            rv = trips.groupby("vehicle_id")["total_freight"].sum() if "vehicle_id" in trips else pd.Series(dtype=float)
            ev = exp[exp["vehicle_id"].notna()].groupby("vehicle_id")["amount"].sum() if "vehicle_id" in exp else pd.Series(dtype=float)
            vp = (rv.sub(ev, fill_value=0)).rename(index=vm).sort_values().tail(6)
            if vp.empty:
                st.caption("No data")
            else:
                _chart(_style(go.Figure(go.Bar(x=vp.values, y=vp.index, orientation="h",
                                               marker_color=[GREEN if x >= 0 else RED for x in vp.values])), 290))

    # alerts
    today, horizon = date.today(), date.today() + timedelta(days=EXPIRY_WARN_DAYS)
    alerts = []
    for v in vehicles:
        if v.get("status") == "Inactive":
            continue
        for key, lab in (("registration_expiry", "Registration"), ("insurance_expiry", "Insurance"), ("fitness_expiry", "Fitness")):
            d = to_date(v.get(key))
            if d and d <= horizon:
                alerts.append((f"🚛 {v['vehicle_number']} — {lab} " + ("expired" if d < today else "expires"), fmt_date(d), d < today))
    for d_ in drivers:
        d = to_date(d_.get("license_expiry"))
        if d and d <= horizon and d_.get("status") != "Inactive":
            alerts.append((f"👤 {d_['name']} — Licence " + ("expired" if d < today else "expires"), fmt_date(d), d < today))
    for i in invoices:
        d = to_date(i.get("due_date"))
        if num(i.get("balance")) > 0.5 and d and d < today:
            alerts.append((f"🧾 {i['invoice_number']} overdue — {customers.get(i.get('customer_id'), '')}", pkr(i.get("balance")), True))
    alerts.sort(key=lambda a: (not a[2], a[1]))
    l, r = st.columns([1, 1.6])
    with l.container(border=True):
        section(f"Alerts ({len(alerts)})")
        if alerts:
            alert_rows(alerts[:10])
            if len(alerts) > 10:
                st.caption(f"+ {len(alerts) - 10} more")
        else:
            st.success("All documents are valid and no invoices are overdue.")
    with r.container(border=True):
        section("Recent Trips")
        vm = {v["id"]: v["vehicle_number"] for v in vehicles}
        recent = [{"Trip": t.get("trip_number"), "Date": fmt_date(t.get("trip_date")), "Vehicle": vm.get(t.get("vehicle_id"), "—"),
                   "Customer": customers.get(t.get("customer_id"), "—"), "Tons": f"{num(t.get('loading_weight')):,.1f}",
                   "Freight": pkr(t.get("total_freight")), "Status": status_text(t.get("status"))} for t in trips_all[:8]]
        if recent:
            st.dataframe(pd.DataFrame(recent), hide_index=True, **STRETCH)
        else:
            st.caption("No trips yet.")
