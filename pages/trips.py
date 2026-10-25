"""Trips Management / ٹرپس"""
import streamlit as st
from datetime import date
from utils.database import get_supabase, insert_row, update_row, delete_row
from utils.styles import premium_header, gold_divider, empty_state
from utils.helpers import format_pkr, format_tons


def render():
    premium_header("Trip Management", "Molasses Loading, Destination & Weight / ٹرپ مینجমেন্ট", "🗺️")
    sb = get_supabase()
    tab1, tab2 = st.tabs(["📋 All Trips / تمام ٹرپس", "➕ Add New Trip / نیا ٹرپ"])

    try:
        vehicles = sb.table("vehicles").select("id, vehicle_number").execute().data or []
        drivers = sb.table("drivers").select("id, name").execute().data or []
        customers = sb.table("customers").select("id, name").execute().data or []
    except Exception as e:
        st.error(f"Error: {e}"); return

    v_map = {v["id"]: v["vehicle_number"] for v in vehicles}
    d_map = {d["id"]: d["name"] for d in drivers}
    c_map = {c["id"]: c["name"] for c in customers}

    with tab1:
        trips = sb.table("trips").select("*").order("trip_date", desc=True).execute().data or []
        if not trips:
            empty_state("No trips recorded yet", "🗺️"); return

        for t in trips:
            vn = v_map.get(t.get("vehicle_id"), "—")
            dn = d_map.get(t.get("driver_id"), "—")
            cn = c_map.get(t.get("customer_id"), "—")
            with st.expander(f"🗺️ {t.get('trip_number')} | {t.get('trip_date')} | {vn} | {cn} ({t.get('status','')}):"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Vehicle:** {vn}"); c1.write(f"**Driver:** {dn}"); c1.write(f"**Customer:** {cn}")
                c2.write(f"**Loading:** {t.get('loading_point','—')}"); c2.write(f"**Destination:** {t.get('unloading_point','—')}")
                c3.write(f"**Load Wt:** {format_tons(t.get('loading_weight',0))}")
                c3.write(f"**Freight:** {format_pkr(t.get('total_freight',0))}")

                bc1, bc2 = st.columns(2)
                ns = bc1.selectbox("Status", ["Pending","In Transit","Delivered","Billed","Cancelled"],
                    index=["Pending","In Transit","Delivered","Billed","Cancelled"].index(t.get("status","Pending")),
                    key=f"ts_{t['id']}")
                if bc1.button("Update", key=f"uts_{t['id']}"):
                    update_row("trips", t["id"], {"status": ns}); st.success("Updated!"); st.rerun()
                if bc2.button("Delete", key=f"dt_{t['id']}"):
                    delete_row("trips", t["id"]); st.success("Deleted!"); st.rerun()

    with tab2:
        if not vehicles or not customers:
            st.warning("⚠️ Please add Vehicles and Customers first!"); return
        with st.form("add_trip", clear_on_submit=True):
            st.markdown("### ➕ Add New Trip")
            c1, c2, c3 = st.columns(3)
            tnum = c1.text_input("Trip Number", value=f"TRP-{date.today().strftime('%Y%m%d')}-01")
            tdate = c2.date_input("Trip Date")
            prod = c3.text_input("Product", value="Molasses")
            c4, c5, c6 = st.columns(3)
            veh = c4.selectbox("Vehicle", options=list(v_map.keys()), format_func=lambda x: v_map[x])
            drv = c5.selectbox("Driver", options=list(d_map.keys()), format_func=lambda x: d_map[x])
            cust = c6.selectbox("Customer", options=list(c_map.keys()), format_func=lambda x: c_map[x])
            c7, c8 = st.columns(2)
            load_pt = c7.text_input("Loading Point (Sugar Mill)")
            unload_pt = c8.text_input("Destination")
            c9, c10, c11 = st.columns(3)
            lw = c9.number_input("Loading Weight (Tons)", value=30.0)
            uw = c10.number_input("Unloading Weight (Tons)", value=29.8)
            rate = c11.number_input("Rate Per Ton", value=2500.0)
            c12, c13, c14 = st.columns(3)
            slip_l = c12.text_input("Loading Slip")
            slip_u = c13.text_input("Unloading Slip")
            dist = c14.number_input("Distance (KM)", value=250.0)
            notes = st.text_area("Notes")

            if st.form_submit_button("✅ Save Trip", use_container_width=True):
                diff = lw - uw
                freight = lw * rate
                row = {
                    "trip_number": tnum, "trip_date": tdate.isoformat(),
                    "vehicle_id": veh, "driver_id": drv, "customer_id": cust,
                    "loading_point": load_pt, "unloading_point": unload_pt,
                    "product": prod, "loading_weight": lw, "unloading_weight": uw,
                    "weight_difference": diff, "weighbridge_slip_loading": slip_l,
                    "weighbridge_slip_unloading": slip_u, "rate_per_ton": rate,
                    "total_freight": freight, "distance_km": dist, "status": "Pending", "notes": notes
                }
                insert_row("trips", row)
                st.success("✅ Trip saved successfully!"); st.balloons()
