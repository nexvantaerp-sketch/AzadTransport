"""
Supabase Database Connection Manager
New United Azad Transport - Molasses Transportation ERP
"""
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    if "supabase" not in st.session_state:
        url = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", ""))
        key = os.getenv("SUPABASE_KEY", st.secrets.get("SUPABASE_KEY", ""))
        if not url or not key:
            st.error("⚠️ Supabase credentials not configured! Add SUPABASE_URL and SUPABASE_KEY to .env or Streamlit secrets.")
            st.stop()
        st.session_state.supabase = create_client(url, key)
    return st.session_state.supabase


# ─── CRUD Helpers ────────────────────────────────────────────────────────────

def insert_row(table: str, data: dict):
    """Insert a single row into a table."""
    sb = get_supabase()
    return sb.table(table).insert(data).execute()


def update_row(table: str, row_id: str, data: dict):
    """Update a row by its id."""
    sb = get_supabase()
    return sb.table(table).update(data).eq("id", row_id).execute()


def delete_row(table: str, row_id: str):
    """Soft-delete or hard-delete a row."""
    sb = get_supabase()
    return sb.table(table).delete().eq("id", row_id).execute()


def fetch_all(table: str, order_col: str = "created_at", ascending: bool = False):
    """Fetch all rows from a table, ordered."""
    sb = get_supabase()
    return sb.table(table).select("*").order(order_col, desc=not ascending).execute()


def fetch_by_id(table: str, row_id: str):
    """Fetch a single row by id."""
    sb = get_supabase()
    return sb.table(table).select("*").eq("id", row_id).single().execute()


def fetch_filtered(table: str, column: str, value, order_col: str = "created_at"):
    """Fetch rows filtered by a column value."""
    sb = get_supabase()
    return sb.table(table).select("*").eq(column, value).order(order_col, desc=True).execute()


def rpc_call(function_name: str, params: dict = None):
    """Call a Supabase RPC (stored procedure)."""
    sb = get_supabase()
    return sb.rpc(function_name, params or {}).execute()
