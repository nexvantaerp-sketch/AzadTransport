"""
New United Azad Transport — Molasses Transportation ERP
Entry point: login gate + sidebar navigation.
"""
import os
import sys

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

st.set_page_config(page_title="Azad Transport ERP", page_icon="🚛", layout="wide",
                   initial_sidebar_state="expanded")

from utils import auth                                  # noqa: E402
from utils.config import COMPANY                        # noqa: E402
from utils.crud import show_flash                       # noqa: E402
from utils.db import DBError                            # noqa: E402
from utils.helpers import STRETCH                       # noqa: E402
from utils.styles import LOGIN_BG, inject_css           # noqa: E402

inject_css()


# ───────────────────────── login ─────────────────────────
def login_screen() -> None:
    st.markdown(LOGIN_BG, unsafe_allow_html=True)

    if not st.session_state.get("_boot"):
        try:
            auth.ensure_admin()
            st.session_state["_boot"] = True
        except DBError as e:
            st.error(f"⚠️ Cannot start: {e}")
            st.info("Setup: ① create a Supabase project ② run `supabase_schema.sql` in the SQL Editor "
                    "③ add `SUPABASE_URL` and `SUPABASE_KEY` to Streamlit secrets.")
            st.stop()

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        feats = [("🗺️", "Trips, weights & freight in one place"), ("🧾", "Invoices, payments & receivable ageing"),
                 ("🚛", "Fleet, drivers & document expiry alerts"), ("📈", "Vehicle-wise profit & loss reports")]
        st.markdown(
            '<div class="login-brand"><div>'
            '<div class="lb-mark">🚛</div>'
            f'<div class="lb-name">{COMPANY["name"].upper()}</div>'
            f'<div class="lb-ur">{COMPANY["name_ur"]}</div>'
            f'<div class="lb-tag">{COMPANY["tagline"]}</div>'
            '<div class="lb-feats">' + "".join(f'<div class="lb-feat"><i>{i}</i><span>{t}</span></div>' for i, t in feats) +
            '</div></div><div class="lb-foot">© New United Azad Transport · Secure access for authorised staff only</div></div>',
            unsafe_allow_html=True)
    with right:
        st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="login-title">Welcome back 👋</div>'
                    '<div class="login-sub">Sign in to your workspace / اپنے اکاؤنٹ میں داخل ہوں</div>', unsafe_allow_html=True)
        with st.form("login", border=True):
            username = st.text_input("Username / آئی ڈی", placeholder="e.g. admin")
            password = st.text_input("Password / پاسورڈ", type="password", placeholder="••••••••")
            go = st.form_submit_button("Sign in  →", type="primary", **STRETCH)
        if go:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                try:
                    user, msg = auth.attempt_login(username, password)
                except DBError as e:
                    st.error(f"⚠️ {e}")
                    return
                if user:
                    st.session_state["user"] = user
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error(msg)


# ───────────────────────── main app ─────────────────────────
def main_app() -> None:
    from views import (advances, billing, customers, dashboard, drivers, expenses,
                       payments, reports, settings, trips, vehicles)

    st.logo(os.path.join(BASE, "assets", "logo.svg"), icon_image=os.path.join(BASE, "assets", "icon.svg"))

    def P(fn, title, icon, path, default=False):
        return st.Page(fn, title=title, icon=icon, url_path=path, default=default)

    pages = {
        "Overview": [P(dashboard.render, "Dashboard", ":material/dashboard:", "dashboard", True)],
        "Operations": [
            P(trips.render, "Trips", ":material/route:", "trips"),
            P(vehicles.render, "Vehicles", ":material/local_shipping:", "vehicles"),
            P(drivers.render, "Drivers", ":material/badge:", "drivers"),
            P(customers.render, "Customers", ":material/factory:", "customers"),
        ],
        "Finance": [
            P(billing.render, "Billing", ":material/receipt_long:", "billing"),
            P(payments.render, "Payments", ":material/payments:", "payments"),
            P(expenses.render, "Expenses", ":material/receipt:", "expenses"),
            P(advances.render, "Driver Advances", ":material/handshake:", "advances"),
        ],
        "Insights": [P(reports.render, "Reports", ":material/monitoring:", "reports")],
        "Administration": [P(settings.render, "Settings", ":material/settings:", "settings")],
    }
    nav = st.navigation(pages)

    user = auth.current_user()
    name = user.get("full_name") or user.get("username") or "User"
    with st.sidebar:
        st.markdown(
            f'<div class="side-user"><div class="side-avatar">{name[:1].upper()}</div><div>'
            f'<div class="side-name">{name}</div><div class="side-role">{user.get("role", "")}</div></div></div>',
            unsafe_allow_html=True)
        if st.button("Sign out", icon=":material/logout:", **STRETCH):
            st.session_state.clear()
            st.rerun()

    show_flash()
    nav.run()


if st.session_state.get("logged_in"):
    main_app()
else:
    login_screen()
