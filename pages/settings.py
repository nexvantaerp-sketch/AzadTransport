"""Settings / سیٹنگز"""
import streamlit as st
from utils.styles import premium_header
from utils.database import get_supabase


def render():
    premium_header("Settings", "System configuration & profile / سیٹنگز", "⚙️")

    st.markdown("### 🏢 Company Profile")
    st.info("""
    **New United Azad Transport**
    Molasses Transportation Specialists
    Serving Sugar Mills across Pakistan (Habib Sugar Mills, Al-Abbas, Unicol, Shah Murad etc.)
    """)

    st.markdown("### 🔒 Security & Users")
    user = st.session_state.get("user", {})
    st.write(f"**Logged in user:** {user.get('full_name', 'Admin')} ({user.get('username', 'admin')})")
    st.write(f"**Role:** {user.get('role', 'admin')}")

    st.markdown("### 🌐 Database Connection")
    try:
        sb = get_supabase()
        res = sb.table("vehicles").select("count", count="exact").execute()
        st.success("✅ Connected to Supabase Database successfully!")
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")

    st.markdown("### 📱 Mobile Access")
    st.markdown("""
    You can access this software on your **iPhone / Android** phone browser via your Streamlit Cloud URL or local network IP!
    """)
