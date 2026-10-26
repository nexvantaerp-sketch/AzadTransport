from utils import db
from utils.crud import entity_page
from utils.config import EXPENSE_CATEGORIES
from utils.helpers import pkr


def _before_save(data, old):
    if data.get("trip_id") and not data.get("vehicle_id"):
        t = next((t for t in db.fetch("trips") if t["id"] == data["trip_id"]), None)
        if t:
            data["vehicle_id"] = t.get("vehicle_id")
            data["driver_id"] = data.get("driver_id") or t.get("driver_id")
    return data


CFG = dict(
    table="expenses", title="Expenses", noun="Expense", icon="💸",
    subtitle="Diesel, toll, maintenance, salaries & more / اخراجات",
    label=lambda r: f"{r.get('category')} · {pkr(r.get('amount'))} · {r.get('expense_date')}",
    date_key="expense_date", order="expense_date",
    fields=[
        dict(key="expense_date", label="Date", kind="date", required=True, default="today"),
        dict(key="category", label="Category", kind="select", options=EXPENSE_CATEGORIES),
        dict(key="amount", label="Amount (PKR)", kind="money", positive=True, step=100.0, default=0.0),
        dict(key="vehicle_id", label="Vehicle", kind="fk", ref=("vehicles", "vehicle_number")),
        dict(key="driver_id", label="Driver", kind="fk", ref=("drivers", "name")),
        dict(key="trip_id", label="Trip", kind="fk", ref=("trips", "trip_number"),
             help="Picking a trip auto-fills vehicle/driver when left empty"),
        dict(key="payment_method", label="Payment Method", kind="select", options=["Cash", "Bank Transfer", "Online", "Credit"]),
        dict(key="receipt_number", label="Receipt / Voucher No"),
        dict(key="description", label="Description / تفصیل", kind="textarea"),
    ],
    columns=[("expense_date", "Date", "date"), ("category", "Category", None), ("amount", "Amount", "money"),
             ("vehicle_id", "Vehicle", None), ("driver_id", "Driver", None), ("trip_id", "Trip", None),
             ("payment_method", "Method", None), ("description", "Description", None)],
    filters=["category", "vehicle_id"],
    before_save=_before_save,
)


def render():
    entity_page(CFG)
