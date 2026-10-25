"""
🚛 New United Azad Transport
Molasses Transportation Management System — Premium ERP
"""
import streamlit as st
import hashlib
import os
import sys

# Ensure current directory is in python path for cloud/local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="New United Azad Transport ERP",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import inject_premium_css, premium_header, gold_divider
from utils.database import get_supabase

inject_premium_css()

# ─── Authentication ──────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username: str, password: str) -> bool:
    try:
        sb = get_supabase()
        pwd_hash = hash_password(password)
        res = sb.table("app_users").select("*").eq(
            "username", username
        ).eq("password_hash", pwd_hash).eq("status", "Active").execute()
        if res.data and len(res.data) > 0:
            st.session_state["user"] = res.data[0]
            st.session_state["logged_in"] = True
            return True
    except Exception as e:
        st.error(f"Connection error: {e}")
    return False

def show_login():
    # Hide sidebar via CSS when on login screen
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none !important;}
            [data-testid="collapsedControl"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;justify-content:center;align-items:center;min-height:82vh;padding:20px;">
    <div style="width:100%;max-width:440px;">
    <div class="premium-card" style="text-align:center;padding:40px 30px;background:linear-gradient(135deg,#161b22,#1c2333);border:1px solid rgba(212,175,55,0.3);box-shadow:0 12px 40px rgba(0,0,0,0.6);">
        <div style="font-size:3.8rem;margin-bottom:12px;filter:drop-shadow(0 4px 10px rgba(212,175,55,0.3));">🚛</div>
        <div style="font-size:1.55rem;font-weight:800;color:#D4AF37;letter-spacing:1px;margin-bottom:6px;">
            NEW UNITED AZAD TRANSPORT</div>
        <div style="font-size:.9rem;color:#c9d1d9;margin-bottom:28px;font-weight:500;">
            نیو یونائیٹڈ آزاد ٹرانسپورٹ<br><span style="color:#8b949e;font-size:.8rem;">Molasses Transportation Management ERP</span></div>
    </div></div></div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Secure Portal Login")
            st.markdown("<p style='color:#8b949e;font-size:0.85rem;margin-bottom:20px;'>Enter your credentials to access the ERP system.</p>", unsafe_allow_html=True)
            username = st.text_input("Username / آئی ڈی", placeholder="Enter username (e.g. admin)")
            password = st.text_input("Password / پاسورڈ", type="password", placeholder="Enter password")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔓 Login to Dashboard", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("⚠️ Please enter username and password")
                elif check_login(username, password):
                    st.success("✅ Login successful! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password / غلط آئی ڈی یا پاسورڈ")

        st.markdown("""
        <div style="text-align:center;margin-top:20px;color:#8b949e;font-size:.82rem;background:rgba(22,27,34,0.7);padding:14px;border-radius:12px;border:1px solid rgba(212,175,55,0.1);">
            <strong style="color:#D4AF37;">Default Login:</strong> admin / admin123<br>
            <span style="font-size:.75rem;color:#8b949e;margin-top:4px;display:inline-block;">🔒 Secure Supabase Cloud Authentication</span>
        </div>""", unsafe_allow_html=True)

# ─── Main App ────────────────────────────────────────────────
def main_app():
    user = st.session_state.get("user", {})

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0;">
            <div style="font-size:2.5rem;">🚛</div>
            <div style="font-size:1.1rem;font-weight:800;color:#D4AF37;">
                AZAD TRANSPORT</div>
            <div style="font-size:.75rem;color:#8b949e;">
                نیو یونائیٹڈ آزاد ٹرانسپورٹ</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        page = st.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "🚛 Vehicles / گاڑیاں",
                "🗺️ Trips / ٹرپس",
                "👤 Drivers / ڈرائیور",
                "🏭 Customers / کسٹمرز",
                "💰 Expenses / اخراجات",
                "📄 Billing / بلنگ",
                "💳 Payments / ادائیگیاں",
                "📊 Reports / رپورٹیں",
                "⚙️ Settings / سیٹنگز",
            ],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown(f"""
        <div style="padding:10px;text-align:center;">
            <div style="color:#8b949e;font-size:.75rem;">Logged in as</div>
            <div style="color:#D4AF37;font-weight:700;font-size:.9rem;">
                {user.get('full_name', 'Admin')}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🚪 Logout / لاگ آؤٹ", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ── Route Pages ──
    if "Dashboard" in page:
        from pages import dashboard
        dashboard.render()
    elif "Vehicles" in page:
        from pages import vehicles
        vehicles.render()
    elif "Trips" in page:
        from pages import trips
        trips.render()
    elif "Drivers" in page:
        from pages import drivers_page
        drivers_page.render()
    elif "Customers" in page:
        from pages import customers
        customers.render()
    elif "Expenses" in page:
        from pages import expenses
        expenses.render()
    elif "Billing" in page:
        from pages import billing
        billing.render()
    elif "Payments" in page:
        from pages import payments
        payments.render()
    elif "Reports" in page:
        from pages import reports
        reports.render()
    elif "Settings" in page:
        from pages import settings
        settings.render()


# ─── Entry Point ─────────────────────────────────────────────
if st.session_state.get("logged_in", False):
    main_app()
else:
    show_login()
