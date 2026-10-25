"""Payment Tracking / ادائیگیاں"""
import streamlit as st
from datetime import date
from utils.database import get_supabase, insert_row, delete_row
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Payment Tracking", "Record received payments & bank cheques / ادائیگیوں کا ریکارڈ", "💳")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 Received Payments / موصول شدہ ادائیگیاں", "➕ Record Payment / نئی ادائیگی درج کریں"])

    try:
        customers = sb.table("customers").select("id, name").execute().data or []
        invoices = sb.table("invoices").select("id, invoice_number, balance").execute().data or []
    except Exception as e:
        st.error(f"Error: {e}"); return
    c_map = {c["id"]: c["name"] for c in customers}
    i_map = {i["id"]: i["invoice_number"] for i in invoices}

    with tab1:
        data = sb.table("payments").select("*").order("payment_date", desc=True).execute().data or []
        if not data:
            empty_state("No payments recorded yet", "💳"); return

        for p in data:
            cn = c_map.get(p.get("customer_id"), "—")
            in_no = i_map.get(p.get("invoice_id"), "—")
            with st.expander(f"💳 {p['payment_date']} | Cust: {cn} | Amt: {format_pkr(p['amount'])} | Method: {p.get('payment_method','Cash')}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Customer:** {cn}")
                c1.write(f"**Invoice No:** {in_no}")
                c1.write(f"**Amount:** {format_pkr(p['amount'])}")
                c2.write(f"**Method:** {p.get('payment_method','Bank')}")
                c2.write(f"**Reference / Cheque:** {p.get('reference_number','—')}")
                c2.write(f"**Bank Name:** {p.get('bank_name','—')}")
                c3.write(f"**Status:** {p.get('status','Received')}")
                if p.get("notes"):
                    st.info(f"📝 {p['notes']}")

                if st.button("🗑️ Delete Payment", key=f"dp_{p['id']}"):
                    delete_row("payments", p["id"])
                    st.success("Deleted!"); st.rerun()

    with tab2:
        with st.form("add_payment", clear_on_submit=True):
            st.markdown("### ➕ Record Payment Received / نئی ادائیگی درج کریں")
            c1, c2, c3 = st.columns(3)
            pdate = c1.date_input("Payment Date", value=date.today())
            cust = c2.selectbox("Customer", options=list(c_map.keys()), format_func=lambda x: c_map[x])
            inv = c3.selectbox("Invoice (Optional)", options=[None] + list(i_map.keys()), format_func=lambda x: "None" if not x else i_map[x])

            c4, c5, c6 = st.columns(3)
            amt = c4.number_input("Amount Received (PKR)", min_value=0.0, step=1000.0, value=50000.0)
            pmethod = c5.selectbox("Payment Method", ["Bank Transfer", "Cheque", "Cash", "Online"])
            ref = c6.text_input("Cheque / Ref Number")

            c7, c8 = st.columns(2)
            bank = c7.text_input("Bank Name", placeholder="HBL, Meezan etc.")
            status = c8.selectbox("Status", ["Received", "Cleared", "Pending Clearance", "Bounced"])
            notes = st.text_area("Notes")

            if st.form_submit_button("✅ Save Payment", use_container_width=True):
                row = {
                    "payment_date": pdate.isoformat(), "customer_id": cust,
                    "amount": amt, "payment_method": pmethod,
                    "reference_number": ref, "bank_name": bank,
                    "status": status, "notes": notes
                }
                if inv: row["invoice_id"] = inv
                insert_row("payments", row)
                st.success("✅ Payment recorded successfully!"); st.balloons()
