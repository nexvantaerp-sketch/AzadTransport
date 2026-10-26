from utils.crud import entity_page
from utils.helpers import pkr

CFG = dict(
    table="driver_advances", title="Driver Advances", noun="Advance", icon="🤝",
    subtitle="Cash given to drivers & its settlement / ڈرائیور ایڈوانس",
    label=lambda r: f"{pkr(r.get('amount'))} · {r.get('advance_date')}",
    date_key="advance_date", order="advance_date",
    fields=[
        dict(key="advance_date", label="Date", kind="date", required=True, default="today"),
        dict(key="driver_id", label="Driver", kind="fk", required=True, ref=("drivers", "name")),
        dict(key="trip_id", label="Trip (optional)", kind="fk", ref=("trips", "trip_number")),
        dict(key="amount", label="Amount (PKR)", kind="money", positive=True, step=500.0, default=0.0),
        dict(key="purpose", label="Purpose", ph="Diesel, food, toll…"),
        dict(key="status", label="Status", kind="select", options=["Given", "Adjusted", "Returned"]),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("advance_date", "Date", "date"), ("driver_id", "Driver", None), ("trip_id", "Trip", None),
             ("amount", "Amount", "money"), ("purpose", "Purpose", None), ("status", "Status", "status")],
    filters=["driver_id", "status"],
    quick_status=("status", ["Given", "Adjusted", "Returned"]),
)


def render():
    entity_page(CFG)
