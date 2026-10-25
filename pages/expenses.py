"""Expense Management / اخراجات"""
import streamlit as st
from datetime import date
from utils.database import get_supabase, insert_row, delete_row
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Expense Management", "Diesel, Toll Tax, Maintenance & Advances / اخراجات", "💰")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Expenses / تمام اخراجات", "➕ Add Expense / نیا خرچہ"])

    try:
        vehicles = sb.table("vehicles").select("id, vehicle_number").execute().data or []
        drivers = sb.table("drivers").select("id, name").execute().data or []
        trips = sb.table("trips").select("id, trip_number").execute().data or []
    except Exception as e:
        st.error(f"Error: {e}"); return

    v_map = {v["id"]: v["vehicle_number"] for v in vehicles}
    d_map = {d["id"]: d["name"] for d in drivers}
    t_map = {t["id"]: t["trip_number"] for t in trips}

    with tab1:
        data = sb.table("expenses").select("*").order("expense_date", desc=True).execute().data or []
        if not data:
            empty_state("No expenses recorded yet", "💰"); return

        for e in data:
            vn = v_map.get(e.get("vehicle_id"), "—")
            dn = d_map.get(e.get("driver_id"), "—")
            tn = t_map.get(e.get("trip_id"), "—")
            with st.expander(f"💸 {e['expense_date']} | {e['category']} | {format_pkr(e['amount'])} | Veh: {vn}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Category:** {e['category']}")
                c1.write(f"**Amount:** {format_pkr(e['amount'])}")
                c1.write(f"**Payment Method:** {e.get('payment_method','Cash')}")
                c2.write(f"**Vehicle:** {vn}")
                c2.write(f"**Driver:** {dn}")
                c2.write(f"**Trip:** {tn}")
                c3.write(f"**Receipt No:** {e.get('receipt_number','—')}")
                if e.get("description"):
                    st.info(f"📝 {e['description']}")

                if st.button("🗑️ Delete Expense", key=f"de_{e['id']}"):
                    delete_row("expenses", e["id"])
                    st.success("Deleted!"); st.rerun()

    with tab2:
        with st.form("add_exp", clear_on_submit=True):
            st.markdown("### ➕ Add New Expense / نیا خرچہ درج کریں")
            c1, c2, c3 = st.columns(3)
            edate = c1.date_input("Expense Date", value=date.today())
            cat = c2.selectbox("Category", ["Diesel", "Toll Tax", "Driver Advance", "Maintenance", "Repair", "Tyre", "Salary", "Food/Tea", "Other"])
            amount = c3.number_input("Amount (PKR)", min_value=0.0, step=100.0, value=5000.0)

            c4, c5, c6 = st.columns(3)
            veh = c4.selectbox("Vehicle (Optional)", options=[None] + list(v_map.keys()), format_func=lambda x: "None" if not x else v_map[x])
            drv = c5.selectbox("Driver (Optional)", options=[None] + list(d_map.keys()), format_func=lambda x: "None" if not x else d_map[x])
            trp = c6.selectbox("Trip (Optional)", options=[None] + list(t_map.keys()), format_func=lambda x: "None" if not x else t_map[x])

            c7, c8 = st.columns(2)
            pmethod = c7.selectbox("Payment Method", ["Cash", "Bank Transfer", "Online", "Credit"])
            rec_no = c8.text_input("Receipt / Voucher Number")
            desc = st.text_area("Description / تفصیل")

            if st.form_submit_button("✅ Save Expense", use_container_width=True):
                row = {
                    "expense_date": edate.isoformat(), "category": cat,
                    "amount": amount, "payment_method": pmethod,
                    "receipt_number": rec_no, "description": desc
                }
                if veh: row["vehicle_id"] = veh
                if drv: row["driver_id"] = drv
                if trp: row["trip_id"] = trp
                insert_row("expenses", row)
                st.success("✅ Expense saved successfully!"); st.balloons()
