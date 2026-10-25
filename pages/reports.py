"""Reports & P&L / رپورٹس"""
import streamlit as st
import pandas as pd
from utils.database import get_supabase
from utils.styles import premium_header, empty_state
from utils.helpers import format_pkr, format_tons


def render():
    premium_header("Reports & Profit / Loss", "Vehicle-wise & Customer-wise Profit & Loss / رپورٹیں", "📊")
    sb = get_supabase()

    try:
        trips = sb.table("trips").select("*").execute().data or []
        expenses = sb.table("expenses").select("*").execute().data or []
        vehicles = sb.table("vehicles").select("id, vehicle_number").execute().data or []
        customers = sb.table("customers").select("id, name").execute().data or []
    except Exception as e:
        st.error(f"Error: {e}"); return

    v_map = {v["id"]: v["vehicle_number"] for v in vehicles}
    c_map = {c["id"]: c["name"] for c in customers}

    tab1, tab2, tab3 = st.tabs(["🚛 Vehicle P&L / گاڑی کا منافع", "🏭 Customer Report / کسٹمر رپورٹ", "📈 Summary Report / خلاصہ"])

    with tab1:
        st.markdown("### 🚛 Vehicle-wise Profit & Loss")
        if not vehicles or not trips:
            empty_state("No data available", "🚛")
        else:
            df_trips = pd.DataFrame(trips)
            df_exp = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["vehicle_id", "amount"])

            records = []
            for v_id, v_num in v_map.items():
                v_trips = df_trips[df_trips["vehicle_id"] == v_id] if not df_trips.empty else pd.DataFrame()
                rev = v_trips["total_freight"].astype(float).sum() if not v_trips.empty and "total_freight" in v_trips.columns else 0
                tons = v_trips["loading_weight"].astype(float).sum() if not v_trips.empty and "loading_weight" in v_trips.columns else 0
                trip_count = len(v_trips)

                v_ex = df_exp[df_exp["vehicle_id"] == v_id] if not df_exp.empty and "vehicle_id" in df_exp.columns else pd.DataFrame()
                exp = v_ex["amount"].astype(float).sum() if not v_ex.empty and "amount" in v_ex.columns else 0
                profit = rev - exp

                records.append({
                    "Vehicle": v_num, "Trips": trip_count, "Tons": tons,
                    "Revenue": format_pkr(rev), "Expenses": format_pkr(exp), "Profit": format_pkr(profit)
                })

            df_res = pd.DataFrame(records)
            st.dataframe(df_res, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 🏭 Customer-wise Business Report")
        if not customers or not trips:
            empty_state("No data available", "🏭")
        else:
            df_trips = pd.DataFrame(trips)
            records = []
            for c_id, c_name in c_map.items():
                c_trips = df_trips[df_trips["customer_id"] == c_id] if not df_trips.empty else pd.DataFrame()
                rev = c_trips["total_freight"].astype(float).sum() if not c_trips.empty and "total_freight" in c_trips.columns else 0
                tons = c_trips["loading_weight"].astype(float).sum() if not c_trips.empty and "loading_weight" in c_trips.columns else 0
                trip_count = len(c_trips)
                records.append({
                    "Customer / Mill": c_name, "Trips": trip_count, "Total Tons": format_tons(tons), "Total Revenue": format_pkr(rev)
                })
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 📈 Comprehensive Financial Summary")
        tot_rev = sum(float(t.get("total_freight", 0)) for t in trips)
        tot_exp = sum(float(e.get("amount", 0)) for e in expenses)
        tot_net = tot_rev - tot_exp
        tot_tons = sum(float(t.get("loading_weight", 0)) for t in trips)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", format_pkr(tot_rev))
        c2.metric("Total Expenses", format_pkr(tot_exp))
        c3.metric("Net Profit", format_pkr(tot_net))
        c4.metric("Total Tons", format_tons(tot_tons))
