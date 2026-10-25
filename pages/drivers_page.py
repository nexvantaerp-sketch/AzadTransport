"""Drivers Management / ڈرائیور"""
import streamlit as st
from datetime import date
from utils.database import get_supabase, insert_row, update_row, delete_row
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr


def render():
    premium_header("Driver Management", "Driver details, salary & advances / ڈرائیور مینجمنٹ", "👤")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Drivers / تمام ڈرائیور", "➕ Add Driver / نیا ڈرائیور"])

    with tab1:
        data = sb.table("drivers").select("*").order("created_at", desc=True).execute().data or []
        if not data:
            empty_state("No drivers added yet", "👤"); return

        for d in data:
            with st.expander(f"👤 {d['name']} — CNIC: {d.get('cnic','—')} — Phone: {d.get('phone','—')} "):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**CNIC:** {d.get('cnic','—')}")
                c1.write(f"**Phone:** {d.get('phone','—')}")
                c1.write(f"**Salary:** {format_pkr(d.get('salary',0))}")
                c2.write(f"**License:** {d.get('license_number','—')}")
                c2.write(f"**License Expiry:** {d.get('license_expiry','—')}")
                c2.write(f"**Joining Date:** {d.get('date_of_joining','—')}")
                c3.write(f"**Emergency Contact:** {d.get('emergency_contact','—')}")
                c3.write(f"**Status:** {d.get('status','Active')}")
                if d.get("notes"):
                    st.info(f"📝 {d['notes']}")

                if st.button("🗑️ Delete Driver", key=f"dd_{d['id']}"):
                    delete_row("drivers", d["id"])
                    st.success("Deleted!"); st.rerun()

    with tab2:
        with st.form("add_driver", clear_on_submit=True):
            st.markdown("### ➕ Add New Driver / نیا ڈرائیور شامل کریں")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Driver Name *")
            cnic = c2.text_input("CNIC", placeholder="42101-1234567-1")
            phone = c3.text_input("Phone Number")
            c4, c5, c6 = st.columns(3)
            lic = c4.text_input("License Number")
            lic_exp = c5.date_input("License Expiry", value=None)
            sal = c6.number_input("Monthly Salary (PKR)", min_value=0.0, step=1000.0, value=35000.0)
            c7, c8 = st.columns(2)
            join_dt = c7.date_input("Date of Joining", value=date.today())
            emg = c8.text_input("Emergency Contact")
            addr = st.text_input("Address")
            notes = st.text_area("Notes")

            if st.form_submit_button("✅ Save Driver", use_container_width=True):
                if not name:
                    st.error("⚠️ Driver name is required!"); return
                row = {
                    "name": name, "cnic": cnic, "phone": phone,
                    "license_number": lic, "salary": sal,
                    "date_of_joining": join_dt.isoformat(),
                    "emergency_contact": emg, "address": addr,
                    "notes": notes, "status": "Active"
                }
                if lic_exp: row["license_expiry"] = lic_exp.isoformat()
                insert_row("drivers", row)
                st.success("✅ Driver added successfully!"); st.balloons()
