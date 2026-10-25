"""Vehicles Management / گاڑیاں"""
import streamlit as st
import pandas as pd
from datetime import date
from utils.database import get_supabase, insert_row, update_row, delete_row
from utils.styles import premium_header, gold_divider, empty_state, status_badge


def render():
    premium_header("Vehicles Management", "Trucks, Tankers & Trailers / گاڑیوں کا انتظام", "🚛")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Vehicles / تمام گاڑیاں", "➕ Add Vehicle / نئی گاڑی"])

    with tab1:
        try:
            data = sb.table("vehicles").select("*").order("created_at", desc=True).execute().data or []
        except Exception as e:
            st.error(f"Error: {e}"); return
        if not data:
            empty_state("No vehicles added yet / ابھی کوئی گاڑی نہیں", "🚛"); return

        # Filters
        fc1, fc2, fc3 = st.columns(3)
        statuses = list(set(v.get("status","") for v in data))
        types = list(set(v.get("vehicle_type","") for v in data))
        sel_status = fc1.selectbox("Filter by Status", ["All"] + statuses, key="v_st")
        sel_type = fc2.selectbox("Filter by Type", ["All"] + types, key="v_ty")
        search = fc3.text_input("🔍 Search Vehicle Number", key="v_sr")

        filtered = data
        if sel_status != "All":
            filtered = [v for v in filtered if v.get("status") == sel_status]
        if sel_type != "All":
            filtered = [v for v in filtered if v.get("vehicle_type") == sel_type]
        if search:
            filtered = [v for v in filtered if search.lower() in v.get("vehicle_number","").lower()]

        st.markdown(f"**Showing {len(filtered)} vehicles**")
        for v in filtered:
            with st.expander(f"🚛 {v['vehicle_number']} — {v.get('vehicle_type','')} — {v.get('status','')}"):
                ec1, ec2, ec3 = st.columns(3)
                ec1.write(f"**Make:** {v.get('make','—')}")
                ec1.write(f"**Model:** {v.get('model','—')}")
                ec1.write(f"**Year:** {v.get('year','—')}")
                ec2.write(f"**Capacity:** {v.get('capacity_tons',0)} Tons")
                ec2.write(f"**Fuel:** {v.get('fuel_type','Diesel')}")
                ec2.write(f"**Chassis:** {v.get('chassis_number','—')}")
                ec3.write(f"**Reg Expiry:** {v.get('registration_expiry','—')}")
                ec3.write(f"**Insurance:** {v.get('insurance_expiry','—')}")
                ec3.write(f"**Fitness:** {v.get('fitness_expiry','—')}")
                if v.get("notes"):
                    st.info(f"📝 {v['notes']}")

                bc1, bc2 = st.columns(2)
                new_status = bc1.selectbox("Change Status", ["Active","Under Maintenance","Inactive"],
                    index=["Active","Under Maintenance","Inactive"].index(v.get("status","Active")),
                    key=f"vs_{v['id']}")
                if bc1.button("Update Status", key=f"vus_{v['id']}"):
                    update_row("vehicles", v["id"], {"status": new_status})
                    st.success("✅ Updated!"); st.rerun()
                if bc2.button("🗑️ Delete", key=f"vd_{v['id']}"):
                    delete_row("vehicles", v["id"])
                    st.success("✅ Deleted!"); st.rerun()

    with tab2:
        with st.form("add_vehicle", clear_on_submit=True):
            st.markdown("### ➕ Add New Vehicle / نئی گاڑی شامل کریں")
            ac1, ac2, ac3 = st.columns(3)
            vnum = ac1.text_input("Vehicle Number *", placeholder="ABC-1234")
            vtype = ac2.selectbox("Vehicle Type", ["Tanker","Truck","Trailer","Other"])
            make = ac3.text_input("Make", placeholder="Hino, UD etc.")
            ac4, ac5, ac6 = st.columns(3)
            model = ac4.text_input("Model")
            yr = ac5.number_input("Year", min_value=1990, max_value=2030, value=2020)
            cap = ac6.number_input("Capacity (Tons)", min_value=0.0, step=1.0, value=30.0)
            ac7, ac8, ac9 = st.columns(3)
            chassis = ac7.text_input("Chassis Number")
            engine = ac8.text_input("Engine Number")
            fuel = ac9.selectbox("Fuel Type", ["Diesel","Petrol","CNG"])
            ac10, ac11, ac12 = st.columns(3)
            reg_exp = ac10.date_input("Registration Expiry", value=None)
            ins_exp = ac11.date_input("Insurance Expiry", value=None)
            fit_exp = ac12.date_input("Fitness Expiry", value=None)
            notes = st.text_area("Notes / نوٹس")

            if st.form_submit_button("✅ Add Vehicle / گاڑی شامل کریں", use_container_width=True):
                if not vnum:
                    st.error("⚠️ Vehicle number is required!"); return
                row = {"vehicle_number": vnum, "vehicle_type": vtype, "make": make,
                       "model": model, "year": yr, "capacity_tons": cap,
                       "chassis_number": chassis, "engine_number": engine,
                       "fuel_type": fuel, "notes": notes, "status": "Active"}
                if reg_exp: row["registration_expiry"] = reg_exp.isoformat()
                if ins_exp: row["insurance_expiry"] = ins_exp.isoformat()
                if fit_exp: row["fitness_expiry"] = fit_exp.isoformat()
                try:
                    insert_row("vehicles", row)
                    st.success("✅ Vehicle added successfully! / گاڑی شامل ہو گئی")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
