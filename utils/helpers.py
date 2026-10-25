"""
Utility helpers for Azad Transport ERP
"""
import pandas as pd
from datetime import datetime, date


def format_pkr(amount):
    """Format amount as PKR currency."""
    if amount is None:
        return "PKR 0"
    try:
        amt = float(amount)
        if amt >= 10000000:
            return f"PKR {amt/10000000:.2f} Cr"
        elif amt >= 100000:
            return f"PKR {amt/100000:.2f} Lac"
        elif amt >= 1000:
            return f"PKR {amt/1000:.1f}K"
        return f"PKR {amt:,.0f}"
    except (ValueError, TypeError):
        return "PKR 0"


def format_pkr_full(amount):
    """Format amount as full PKR currency with commas."""
    if amount is None:
        return "PKR 0"
    try:
        return f"PKR {float(amount):,.0f}"
    except (ValueError, TypeError):
        return "PKR 0"


def format_tons(tons):
    """Format tonnage value."""
    if tons is None:
        return "0 Tons"
    try:
        return f"{float(tons):,.2f} Tons"
    except (ValueError, TypeError):
        return "0 Tons"


def format_date(d):
    """Format date for display."""
    if d is None:
        return "-"
    if isinstance(d, str):
        try:
            d = datetime.fromisoformat(d.replace("Z", "+00:00"))
        except ValueError:
            return d
    if isinstance(d, datetime):
        return d.strftime("%d %b %Y")
    if isinstance(d, date):
        return d.strftime("%d %b %Y")
    return str(d)


def safe_divide(numerator, denominator):
    """Safe division to avoid ZeroDivisionError."""
    try:
        if denominator and float(denominator) != 0:
            return float(numerator) / float(denominator)
    except (ValueError, TypeError):
        pass
    return 0


def calculate_profit(revenue, expenses):
    """Calculate profit from revenue and expenses."""
    try:
        return float(revenue or 0) - float(expenses or 0)
    except (ValueError, TypeError):
        return 0


def data_to_df(response_data):
    """Convert Supabase response data to DataFrame."""
    if response_data and hasattr(response_data, 'data') and response_data.data:
        return pd.DataFrame(response_data.data)
    return pd.DataFrame()


def get_month_range(year, month):
    """Get start and end date for a month."""
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start.isoformat(), end.isoformat()


# Urdu/English Labels
LABELS = {
    "en": {
        "dashboard": "Dashboard",
        "vehicles": "Vehicles",
        "trips": "Trips",
        "drivers": "Drivers",
        "customers": "Customers",
        "expenses": "Expenses",
        "billing": "Freight & Billing",
        "payments": "Payments",
        "reports": "Reports",
        "settings": "Settings",
        "add": "Add New",
        "edit": "Edit",
        "delete": "Delete",
        "save": "Save",
        "cancel": "Cancel",
        "search": "Search",
        "total": "Total",
        "profit": "Profit",
        "loss": "Loss",
        "revenue": "Revenue",
        "pending": "Pending",
        "paid": "Paid",
    },
    "ur": {
        "dashboard": "ڈیش بورڈ",
        "vehicles": "گاڑیاں",
        "trips": "ٹرپس",
        "drivers": "ڈرائیور",
        "customers": "کسٹمرز",
        "expenses": "اخراجات",
        "billing": "فریٹ اور بلنگ",
        "payments": "ادائیگیاں",
        "reports": "رپورٹیں",
        "settings": "سیٹنگز",
        "add": "نیا شامل کریں",
        "edit": "ترمیم",
        "delete": "حذف",
        "save": "محفوظ",
        "cancel": "منسوخ",
        "search": "تلاش",
        "total": "کل",
        "profit": "نفع",
        "loss": "نقصان",
        "revenue": "آمدن",
        "pending": "زیر التوا",
        "paid": "ادا شدہ",
    }
}


def get_label(key, lang="en"):
    """Get label in specified language."""
    return LABELS.get(lang, LABELS["en"]).get(key, key)
