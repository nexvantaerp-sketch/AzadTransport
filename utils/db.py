"""Supabase access layer: cached client, paginated cached reads, friendly errors."""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class DBError(Exception):
    """Error with a message that is safe to show to the user."""


def _secret(name: str) -> str:
    val = os.getenv(name)
    if val:
        return val
    try:                                   # st.secrets raises when no secrets file exists
        return str(st.secrets.get(name, "") or "")
    except Exception:
        return ""


@st.cache_resource(show_spinner=False)
def get_client():
    from supabase import create_client
    url, key = _secret("SUPABASE_URL"), _secret("SUPABASE_KEY")
    if not url or not key:
        raise DBError("Supabase credentials missing. Add SUPABASE_URL and SUPABASE_KEY "
                      "to Streamlit secrets (or a local .env file).")
    return create_client(url, key)


def friendly(e: Exception) -> str:
    m = str(e)
    low = m.lower()
    if "23505" in m or "duplicate key" in low:
        return "This record already exists (a unique value such as number / CNIC is duplicated)."
    if "23503" in m or "foreign key" in low:
        return ("This record is linked to other records (trips, invoices, payments…) "
                "and cannot be deleted. Mark it Inactive/Cancelled instead.")
    if "42703" in m or "pgrst204" in low or ("column" in low and "does not exist" in low) \
            or "could not find the" in low and "column" in low:
        return ("Database structure is outdated. Run `migration_v2.sql` once in the "
                "Supabase SQL Editor, then reload.")
    if "42p01" in m or "pgrst205" in low or ("relation" in low and "does not exist" in low) \
            or "could not find the table" in low:
        return "A required table is missing. Run `supabase_schema.sql` in the Supabase SQL Editor."
    if "jwt" in low or "invalid api key" in low or "apikey" in low:
        return "Supabase API key is invalid. Check SUPABASE_KEY in your secrets."
    if "failed to resolve" in low or "connection" in low or "timed out" in low or "name or service" in low:
        return "Cannot reach Supabase. Check SUPABASE_URL and your internet connection."
    return m


@st.cache_data(ttl=15, show_spinner=False)
def fetch(table: str, order: str | None = "created_at", desc: bool = True) -> list[dict]:
    """Fetch every row of a table (paginated past the 1000-row API limit)."""
    rows, start, step = [], 0, 1000
    try:
        sb = get_client()
        while True:
            q = sb.table(table).select("*")
            if order:
                q = q.order(order, desc=desc)
            q = q.order("id")
            data = q.range(start, start + step - 1).execute().data or []
            rows += data
            if len(data) < step:
                break
            start += step
    except DBError:
        raise
    except Exception as e:
        raise DBError(friendly(e)) from e
    return rows


def where(table: str, column: str, value) -> list[dict]:
    """Uncached filtered read (used right before/after writes)."""
    try:
        return get_client().table(table).select("*").eq(column, value).execute().data or []
    except DBError:
        raise
    except Exception as e:
        raise DBError(friendly(e)) from e


def _write(fn):
    try:
        res = fn()
    except DBError:
        raise
    except Exception as e:
        raise DBError(friendly(e)) from e
    st.cache_data.clear()
    return res


def insert(table: str, row: dict) -> dict:
    res = _write(lambda: get_client().table(table).insert(row).execute())
    return (res.data or [{}])[0]


def insert_many(table: str, rows: list[dict]) -> None:
    if rows:
        _write(lambda: get_client().table(table).insert(rows).execute())


def update(table: str, row_id: str, row: dict) -> dict:
    res = _write(lambda: get_client().table(table).update(row).eq("id", row_id).execute())
    return (res.data or [{}])[0]


def delete(table: str, row_id: str) -> None:
    _write(lambda: get_client().table(table).delete().eq("id", row_id).execute())


def delete_where(table: str, column: str, value) -> None:
    _write(lambda: get_client().table(table).delete().eq(column, value).execute())
