"""Freight & Billing / بلنگ"""
import streamlit as st
from datetime import date
from utils.database import get_supabase, insert_row, delete_row
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Freight & Billing", "Customer invoices & pending payments / بلنگ اور انوائس", "📄")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Invoices / تمام انوائسز", "➕ Create Invoice / نئی انوائس"])

    try:
        customers = sb.table("customers").select("id, name").execute().data or []
    except Exception as e:
        st.error(f"Error: {e}"); return
    c_map = {c["id"]: c["name"] for c in customers}

    with tab1:
        invoices = sb.table("invoices").select("*").order("invoice_date", desc=True).execute().data or []
        if not invoices:
            empty_state("No invoices generated yet", "📄"); return

        for inv in invoices:
            cn = c_map.get(inv.get("customer_id"), "—")
            with st.expander(f"📄 Invoice #{inv['invoice_number']} | Cust: {cn} | Amt: {format_pkr(inv['net_amount'])} | Status: {inv['status']}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Invoice Date:** {inv['invoice_date']}")
                c1.write(f"**Customer:** {cn}")
                c1.write(f"**Due Date:** {inv.get('due_date','—')}")
                c2.write(f"**Total Amount:** {format_pkr(inv['total_amount'])}")
                c2.write(f"**Paid Amount:** {format_pkr(inv.get('paid_amount',0))}")
                c2.write(f"**Balance Due:** {format_pkr(inv.get('balance', inv['total_amount']))}")
                c3.write(f"**Status:** {inv['status']}")
                if inv.get("notes"):
                    st.info(f"📝 {inv['notes']}")

                if st.button("🗑️ Delete Invoice", key=f"di_{inv['id']}"):
                    delete_row("invoices", inv["id"])
                    st.success("Deleted!"); st.rerun()

    with tab2:
        if not customers:
            st.warning("⚠️ Please add customers first!"); return
        with st.form("add_invoice", clear_on_submit=True):
            st.markdown("### ➕ Generate Invoice / نئی انوائس بنائیں")
            c1, c2, c3 = st.columns(3)
            inv_no = c1.text_input("Invoice Number", value=f"INV-{date.today().strftime('%Y%m%d')}-01")
            inv_date = c2.date_input("Invoice Date", value=date.today())
            cust = c3.selectbox("Customer / Mill", options=list(c_map.keys()), format_func=lambda x: c_map[x])

            c4, c5, c6 = st.columns(3)
            tot_amt = c4.number_input("Total Amount (PKR)", min_value=0.0, step=1000.0, value=150000.0)
            tax = c5.number_input("Tax / Withholding (PKR)", min_value=0.0, step=100.0, value=0.0)
            due_dt = c6.date_input("Due Date", value=date.today())
            notes = st.text_area("Notes / تفصیل")

            if st.form_submit_button("✅ Generate Invoice", use_container_width=True):
                net = tot_amt - tax
                row = {
                    "invoice_number": inv_no, "invoice_date": inv_date.isoformat(),
                    "customer_id": cust, "total_amount": tot_amt,
                    "tax_amount": tax, "net_amount": net,
                    "paid_amount": 0.0, "balance": net,
                    "due_date": due_dt.isoformat(), "status": "Pending", "notes": notes
                }
                insert_row("invoices", row)
                st.success("✅ Invoice generated successfully!"); st.balloons()
