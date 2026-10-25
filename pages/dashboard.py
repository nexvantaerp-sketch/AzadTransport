"""Dashboard — Premium KPI Overview"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_supabase
from utils.styles import premium_header, gold_divider, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Dashboard", "Real-time overview / کاروبار کا جائزہ", "🏠")
    sb = get_supabase()
    try:
        vehicles = sb.table("vehicles").select("*").execute().data or []
        trips = sb.table("trips").select("*").execute().data or []
        expenses_data = sb.table("expenses").select("*").execute().data or []
        payments = sb.table("payments").select("*").execute().data or []
        drivers = sb.table("drivers").select("*").execute().data or []
        customers = sb.table("customers").select("*").execute().data or []
    except Exception as e:
        st.error(f"Database error: {e}"); return

    active_v = len([v for v in vehicles if v.get("status") == "Active"])
    total_tons = sum(float(t.get("loading_weight", 0)) for t in trips)
    total_rev = sum(float(t.get("total_freight", 0)) for t in trips)
    total_exp = sum(float(e.get("amount", 0)) for e in expenses_data)
    total_rcv = sum(float(p.get("amount", 0)) for p in payments)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🚛 Vehicles", f"{active_v}/{len(vehicles)}")
    c2.metric("🗺️ Trips", f"{len(trips)}")
    c3.metric("⚖️ Tons", f"{total_tons:,.0f}")
    c4.metric("💰 Revenue", format_pkr(total_rev))
    c5.metric("📈 Profit", format_pkr(total_rev - total_exp))
    st.markdown("")
    c6, c7, c8, c9 = st.columns(4)
    c6.metric("💸 Expenses", format_pkr(total_exp))
    c7.metric("✅ Received", format_pkr(total_rcv))
    c8.metric("⏳ Pending", format_pkr(total_rev - total_rcv))
    c9.metric("👤 Drivers", f"{len(drivers)}")
    gold_divider()

    if not trips:
        empty_state("No trips yet. Add your first trip!", "🗺️"); return

    df = pd.DataFrame(trips)
    df["trip_date"] = pd.to_datetime(df["trip_date"])
    df["loading_weight"] = pd.to_numeric(df["loading_weight"], errors="coerce").fillna(0)
    df["total_freight"] = pd.to_numeric(df["total_freight"], errors="coerce").fillna(0)
    mo = df.groupby(df["trip_date"].dt.to_period("M")).agg(
        rev=("total_freight","sum"), tons=("loading_weight","sum")).reset_index()
    mo["trip_date"] = mo["trip_date"].astype(str)

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("### 📊 Monthly Revenue")
        fig = go.Figure(go.Bar(x=mo["trip_date"], y=mo["rev"], marker_color="#D4AF37"))
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9d1d9"), margin=dict(l=20,r=20,t=30,b=20), height=340)
        st.plotly_chart(fig, use_container_width=True)
    with ch2:
        st.markdown("### ⚖️ Monthly Tons")
        fig2 = go.Figure(go.Scatter(x=mo["trip_date"], y=mo["tons"],
            mode="lines+markers", line=dict(color="#3fb950",width=3)))
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9d1d9"), margin=dict(l=20,r=20,t=30,b=20), height=340)
        st.plotly_chart(fig2, use_container_width=True)
    gold_divider()

    sc, cc = st.columns(2)
    with sc:
        st.markdown("### 🔄 Trip Status")
        sv = df["status"].value_counts()
        fig3 = go.Figure(go.Pie(labels=sv.index, values=sv.values, hole=0.5,
            marker=dict(colors=["#D4AF37","#3fb950","#f85149","#8b949e"])))
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9d1d9"), margin=dict(l=20,r=20,t=30,b=20), height=310)
        st.plotly_chart(fig3, use_container_width=True)
    with cc:
        st.markdown("### 🏭 Top Customers")
        if customers and "customer_id" in df.columns:
            cm = {c["id"]: c["name"] for c in customers}
            df["cust"] = df["customer_id"].map(cm).fillna("Unknown")
            tc = df.groupby("cust")["total_freight"].sum().nlargest(5).reset_index()
            fig4 = go.Figure(go.Bar(x=tc["total_freight"], y=tc["cust"],
                orientation="h", marker_color="#D4AF37"))
            fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9"), margin=dict(l=20,r=20,t=10,b=20),
                height=310, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)

    gold_divider()
    st.markdown("### 🕐 Recent Trips / حالیہ ٹرپس")
    recent = df.sort_values("trip_date", ascending=False).head(10)
    cols = [c for c in ["trip_number","trip_date","loading_point","unloading_point",
            "loading_weight","total_freight","status"] if c in recent.columns]
    if cols:
        st.dataframe(recent[cols], use_container_width=True, hide_index=True)
