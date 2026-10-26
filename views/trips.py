from datetime import date
from utils import db
from utils.crud import entity_page
from utils.db import DBError
from utils.helpers import num

STATUS_EDITABLE = ["Pending", "In Transit", "Delivered", "Cancelled"]


def _next_trip_no() -> str:
    prefix = f"TRP-{date.today():%Y%m%d}-"
    try:
        n = sum(1 for t in db.fetch("trips") if str(t.get("trip_number", "")).startswith(prefix))
    except DBError:
        n = 0
    return f"{prefix}{n + 1:02d}"


def _before_save(data, old):
    cust = next((c for c in db.fetch("customers") if c["id"] == data["customer_id"]), {})
    if num(data["rate_per_ton"]) <= 0:
        data["rate_per_ton"] = num(cust.get("rate_per_ton"))
    if data["rate_per_ton"] <= 0:
        raise DBError("Rate per ton is required — enter it here or set a default rate on the customer.")
    lw, uw = data["loading_weight"], data["unloading_weight"]
    data["weight_difference"] = round(lw - uw, 2) if uw > 0 else 0
    basis = uw if (data.get("freight_basis") == "Unloading Weight" and uw > 0) else lw
    data["total_freight"] = round(basis * data["rate_per_ton"], 2)
    data["freight_basis"] = data.get("freight_basis") or "Loading Weight"
    if old and old.get("status") == "Billed":
        if abs(num(old.get("total_freight")) - data["total_freight"]) > 0.5 or data["status"] != "Billed":
            raise DBError("This trip is already billed — freight and status are locked. "
                          "Delete the invoice first to change it.")
    return data


def _before_delete(rec):
    if rec.get("status") == "Billed":
        raise DBError("Billed trips cannot be deleted. Delete the invoice first.")


CFG = dict(
    table="trips", title="Trips", noun="Trip", icon="🗺️",
    subtitle="Molasses loading, destination, weights & freight / ٹرپ مینجمنٹ",
    label=lambda r: f"{r.get('trip_number')} ({r.get('trip_date')})",
    date_key="trip_date", order="trip_date",
    fields=[
        dict(key="trip_number", label="Trip Number", required=True, default=_next_trip_no),
        dict(key="trip_date", label="Trip Date", kind="date", required=True, default="today"),
        dict(key="status", label="Status", kind="select", options=STATUS_EDITABLE, default="Pending"),
        dict(key="vehicle_id", label="Vehicle", kind="fk", required=True, ref=("vehicles", "vehicle_number")),
        dict(key="driver_id", label="Driver", kind="fk", required=True, ref=("drivers", "name")),
        dict(key="customer_id", label="Customer", kind="fk", required=True, ref=("customers", "name")),
        dict(key="loading_point", label="Loading Point", ph="Sugar mill / depot"),
        dict(key="unloading_point", label="Destination", ph="Distillery / factory"),
        dict(key="product", label="Product", default="Molasses"),
        dict(key="loading_weight", label="Loading Weight (Tons)", kind="number", step=0.5, positive=True, default=30.0),
        dict(key="unloading_weight", label="Unloading Weight (Tons)", kind="number", step=0.5, default=0.0,
             help="Leave 0 until the load is delivered"),
        dict(key="freight_basis", label="Freight Basis", kind="select",
             options=["Loading Weight", "Unloading Weight"], default="Loading Weight"),
        dict(key="rate_per_ton", label="Rate / Ton (PKR)", kind="money", step=50.0, default=0.0,
             help="0 = use the customer's default rate"),
        dict(key="distance_km", label="Distance (KM)", kind="number", step=10.0, default=0.0),
        dict(key="weighbridge_slip_loading", label="Loading Slip No"),
        dict(key="weighbridge_slip_unloading", label="Unloading Slip No"),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("trip_number", "Trip No", None), ("trip_date", "Date", "date"), ("vehicle_id", "Vehicle", None),
             ("driver_id", "Driver", None), ("customer_id", "Customer", None),
             ("unloading_point", "Destination", None), ("loading_weight", "Load (T)", "num"),
             ("weight_difference", "Shortage (T)", None), ("total_freight", "Freight", "money"),
             ("status", "Status", "status")],
    filters=["status", "vehicle_id", "customer_id"],
    before_save=_before_save, before_delete=_before_delete,
    quick_status=("status", STATUS_EDITABLE),
)


def render():
    entity_page(CFG)
