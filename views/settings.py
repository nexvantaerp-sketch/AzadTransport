import re
import streamlit as st
from utils import db
from utils.auth import current_user, hash_password, is_admin, verify_password
from utils.config import COMPANY
from utils.crud import flash
from utils.db import DBError
from utils.helpers import STRETCH
from utils.styles import page_header, section

REQUIRED = {
    "vehicles": "id,vehicle_number,registration_expiry,insurance_expiry,fitness_expiry",
    "drivers": "id,name,cnic,license_expiry",
    "customers": "id,name,rate_per_ton,payment_terms",
    "trips": "id,trip_number,total_freight,weight_difference,freight_basis",
    "expenses": "id,category,amount",
    "invoices": "id,invoice_number,total_amount,tax_amount,net_amount,paid_amount,balance,due_date",
    "invoice_items": "id,invoice_id,trip_id,amount",
    "payments": "id,amount,invoice_id,status",
    "driver_advances": "id,driver_id,amount",
    "app_users": "id,username,password_hash,role,status",
}


def _account():
    u = current_user()
    with st.container(border=True):
        section("My Account")
        st.markdown(f"**{u.get('full_name') or u.get('username')}** · `{u.get('username')}` · role: **{u.get('role')}**")
    with st.form("chg_pw", border=True):
        st.markdown("#### 🔐 Change password")
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password (min 8 characters)", type="password")
        new2 = st.text_input("Confirm new password", type="password")
        go = st.form_submit_button("Update password", type="primary", **STRETCH)
    if go:
        row = next(iter(db.where("app_users", "id", u["id"])), None)
        if not row or not verify_password(old, row["password_hash"]):
            st.error("Current password is incorrect.")
        elif len(new) < 8:
            st.error("New password must be at least 8 characters.")
        elif new != new2:
            st.error("Passwords do not match.")
        elif new == "admin123":
            st.error("Please choose a password other than the default.")
        else:
            db.update("app_users", u["id"], {"password_hash": hash_password(new)})
            st.session_state["user"]["using_default_password"] = False
            flash("Password updated", "🔐")
            st.rerun()


def _users():
    if not is_admin():
        st.info("Only administrators can manage users.")
        return
    users = db.fetch("app_users", "created_at", False)
    st.dataframe([{"Username": x["username"], "Name": x.get("full_name"), "Role": x.get("role"), "Status": x.get("status")}
                  for x in users], hide_index=True, **STRETCH)
    with st.form("add_user", border=True, clear_on_submit=True):
        st.markdown("#### ➕ Add user")
        c1, c2, c3 = st.columns(3)
        un = c1.text_input("Username *")
        fn = c2.text_input("Full name")
        role = c3.selectbox("Role", ["staff", "viewer", "admin"],
                            help="admin: everything · staff: add/edit data · viewer: read-only")
        pw = st.text_input("Password * (min 8 characters)", type="password")
        add = st.form_submit_button("Create user", type="primary", **STRETCH)
    if add:
        un = un.strip().lower()
        if not re.fullmatch(r"[a-z0-9._-]{3,30}", un):
            st.error("Username: 3–30 chars, letters/numbers/._- only.")
        elif len(pw) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            try:
                db.insert("app_users", {"username": un, "full_name": fn or None, "role": role,
                                        "password_hash": hash_password(pw), "status": "Active"})
            except DBError as e:
                st.error(str(e))
            else:
                flash(f"User {un} created", "👤")
                st.rerun()
    if not users:
        return
    with st.container(border=True):
        st.markdown("#### 🛠️ Manage user")
        opts = {x["id"]: f"{x['username']} ({x.get('role')}, {x.get('status')})" for x in users}
        uid = st.selectbox("User", list(opts), format_func=lambda k: opts[k])
        target = next(x for x in users if x["id"] == uid)
        a, b = st.columns(2)
        newpw = a.text_input("New password", type="password", key="rst_pw")
        if a.button("Reset password", **STRETCH):
            if len(newpw) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                db.update("app_users", uid, {"password_hash": hash_password(newpw)})
                flash("Password reset", "🔐")
                st.rerun()
        flip = "Inactive" if target.get("status") == "Active" else "Active"
        if b.button(f"Set {flip}", **STRETCH):
            if uid == current_user().get("id"):
                st.error("You cannot deactivate your own account.")
            else:
                db.update("app_users", uid, {"status": flip})
                flash(f"User set to {flip}")
                st.rerun()


def _system():
    st.caption("Verifies that your Supabase tables and columns match what this app needs.")
    if st.button("🔍 Run system check", type="primary"):
        bad = 0
        try:
            sb = db.get_client()
        except DBError as e:
            st.error(str(e))
            return
        for table, cols in REQUIRED.items():
            try:
                res = sb.table(table).select(cols, count="exact").limit(1).execute()
                st.success(f"✅ `{table}` — OK ({res.count or 0} rows)")
            except Exception as e:
                bad += 1
                st.error(f"❌ `{table}` — {db.friendly(e)}")
        if bad:
            st.warning("Open **migration_v2.sql** (included in the project), paste it in Supabase → SQL Editor → Run, then re-check.")
        else:
            st.balloons()


def render():
    page_header("Settings", "Account, users and system health / سیٹنگز", "⚙️")
    try:
        t1, t2, t3, t4 = st.tabs(["🔐 My Account", "👥 Users", "🩺 System Check", "🏢 About"])
        with t1:
            _account()
        with t2:
            _users()
        with t3:
            _system()
        with t4:
            st.markdown(f"**{COMPANY['name']}**  \n{COMPANY['name_ur']}  \n{COMPANY['tagline']}")
            st.caption("Built with Streamlit + Supabase. Edit company details in `utils/config.py`.")
    except DBError as e:
        st.error(f"⚠️ {e}")
