from utils.crud import entity_page
from utils.db import DBError
from utils.config import VEHICLE_STATUSES

CFG = dict(
    table="vehicles", title="Vehicles", noun="Vehicle", icon="🚛",
    subtitle="Fleet register, capacity & document expiry / گاڑیوں کا انتظام",
    label=lambda r: r["vehicle_number"],
    fields=[
        dict(key="vehicle_number", label="Vehicle Number", required=True, ph="ABC-1234"),
        dict(key="vehicle_type", label="Type", kind="select", options=["Tanker", "Truck", "Trailer", "Other"]),
        dict(key="status", label="Status", kind="select", options=VEHICLE_STATUSES),
        dict(key="make", label="Make", ph="Hino, UD, Isuzu…"),
        dict(key="model", label="Model"),
        dict(key="year", label="Year", kind="int", min=1980, max=2035, default=2020),
        dict(key="capacity_tons", label="Capacity (Tons)", kind="number", step=1.0, default=30.0),
        dict(key="fuel_type", label="Fuel", kind="select", options=["Diesel", "Petrol", "CNG"]),
        dict(key="chassis_number", label="Chassis No"),
        dict(key="engine_number", label="Engine No"),
        dict(key="registration_date", label="Registration Date", kind="date"),
        dict(key="registration_expiry", label="Registration Expiry", kind="date"),
        dict(key="insurance_expiry", label="Insurance Expiry", kind="date"),
        dict(key="fitness_expiry", label="Fitness Expiry", kind="date"),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("vehicle_number", "Vehicle", None), ("vehicle_type", "Type", None), ("make", "Make", None),
             ("capacity_tons", "Capacity (T)", "num"), ("registration_expiry", "Reg. Expiry", "date"),
             ("insurance_expiry", "Insurance", "date"), ("fitness_expiry", "Fitness", "date"),
             ("status", "Status", "status")],
    filters=["status", "vehicle_type"],
    quick_status=("status", VEHICLE_STATUSES),
)


def _before_save(data, old):
    data["vehicle_number"] = data["vehicle_number"].upper()
    return data


CFG["before_save"] = _before_save


def render():
    entity_page(CFG)
