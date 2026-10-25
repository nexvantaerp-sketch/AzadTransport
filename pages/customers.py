"""Customer Management / کسٹمرز"""
import streamlit as st
from utils.database import get_supabase, insert_row, update_row, delete_row
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Customer Management", "Habib Sugar Mills, Al-Abbas, Unicol etc. / کسٹمر مینجمنٹ", "🏭")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Customers / تمام کسٹمرز", "➕ Add Customer / نیا کسٹمر"])

    with tab1:
        data = sb.table("customers").select("*").order("created_at", desc=True).execute().data or []
        if not data:
            empty_state("No customers added yet", "🏭"); return

        for c in data:
            with st.expander(f"🏭 {c['name']} ({c.get('customer_type','Sugar Mill')}) — City: {c.get('city','—')} "):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Contact Person:** {c.get('contact_person','—')}")
                c1.write(f"**Phone:** {c.get('phone','—')}")
                c1.write(f"**City:** {c.get('city','—')}")
                c2.write(f"**Default Rate/Ton:** {format_pkr(c.get('rate_per_ton',0))}")
                c2.write(f"**Payment Terms:** {c.get('payment_terms',30)} Days")
                c2.write(f"**NTN:** {c.get('ntn','—')}")
                c3.write(f"**Status:** {c.get('status','Active')}")
                if c.get("notes"):
                    st.info(f"📝 {c['notes']}")

                if st.button("🗑️ Delete Customer", key=f"dc_{c['id']}"):
                    delete_row("customers", c["id"])
                    st.success("Deleted!"); st.rerun()

    with tab2:
        with st.form("add_cust", clear_on_submit=True):
            st.markdown("### ➕ Add New Customer / شوگر مل یا فیکٹری شامل کریں")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Customer/Mill Name *", placeholder="Habib Sugar Mills")
            sname = c2.text_input("Short Name", placeholder="HSM")
            ctype = c3.selectbox("Type", ["Sugar Mill", "Factory", "Trader", "Other"])
            c4, c5, c6 = st.columns(3)
            cp = c4.text_input("Contact Person")
            phone = c5.text_input("Phone Number")
            city = c6.text_input("City", placeholder="Nawabshah")
            c7, c8, c9 = st.columns(3)
            ntn = c7.text_input("NTN Number")
            terms = c8.number_input("Payment Terms (Days)", min_value=0, value=30)
            rate = c9.number_input("Default Rate / Ton (PKR)", min_value=0.0, step=100.0, value=2500.0)
            addr = st.text_input("Address")
            notes = st.text_area("Notes")

            if st.form_submit_button("✅ Save Customer", use_container_width=True):
                if not name:
                    st.error("⚠️ Customer name is required!"); return
                row = {
                    "name": name, "short_name": sname, "customer_type": ctype,
                    "contact_person": cp, "phone": phone, "city": city,
                    "ntn": ntn, "payment_terms": terms, "rate_per_ton": rate,
                    "address": addr, "notes": notes, "status": "Active"
                }
                insert_row("customers", row)
                st.success("✅ Customer added successfully!"); st.balloons()
