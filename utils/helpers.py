"""Formatting helpers, Excel export, Streamlit version shims."""
from __future__ import annotations
import io
from datetime import date, datetime
import pandas as pd
import streamlit as st

_VER = tuple(int(x) for x in st.__version__.split(".")[:2] if x.isdigit())
# `use_container_width` was replaced by `width="stretch"` in newer Streamlit versions.
STRETCH = {"width": "stretch"} if _VER >= (1, 50) else {"use_container_width": True}


def num(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None and v != "" else default
    except (ValueError, TypeError):
        return default


def pkr(amount) -> str:
    return f"PKR {num(amount):,.0f}"


def pkr_short(amount) -> str:
    a = num(amount)
    s = "-" if a < 0 else ""
    a = abs(a)
    if a >= 10_000_000:
        return f"{s}PKR {a / 10_000_000:.2f} Cr"
    if a >= 100_000:
        return f"{s}PKR {a / 100_000:.2f} Lac"
    return f"{s}PKR {a:,.0f}"


def tons(v) -> str:
    return f"{num(v):,.2f} T"


def fmt_date(d) -> str:
    if not d:
        return "—"
    if isinstance(d, (datetime, date)):
        return d.strftime("%d %b %Y")
    try:
        return datetime.fromisoformat(str(d)[:10]).strftime("%d %b %Y")
    except ValueError:
        return str(d)


def to_date(v) -> date | None:
    if not v:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def safe_div(a, b) -> float:
    b = num(b)
    return num(a) / b if b else 0.0


STATUS_ICON = {
    "active": "🟢", "completed": "🟢", "paid": "🟢", "delivered": "🟢", "received": "🟢",
    "cleared": "🟢", "given": "🟢",
    "pending": "🟡", "in transit": "🔵", "partial": "🟠", "billed": "🟣", "adjusted": "🟣",
    "under maintenance": "🟠", "pending clearance": "🟡", "overdue": "🔴",
    "inactive": "🔴", "cancelled": "🔴", "bounced": "🔴",
}


def status_text(s) -> str:
    if not s:
        return "—"
    return f"{STATUS_ICON.get(str(s).lower(), '⚪')} {s}"


def to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
            ws = xw.sheets[name[:31]]
            for i, col in enumerate(df.columns, 1):
                width = max([len(str(col))] + [len(str(x)) for x in df[col].head(200)]) + 3
                ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(width, 45)
    return buf.getvalue()


def download_excel(label: str, sheets: dict[str, pd.DataFrame], filename: str, key: str) -> None:
    st.download_button(label, to_excel_bytes(sheets), file_name=filename, key=key,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
