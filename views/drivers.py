import re
from utils.crud import entity_page
from utils.db import DBError

CFG = dict(
    table="drivers", title="Drivers", noun="Driver", icon="👤",
    subtitle="Driver profiles, licences & salary / ڈرائیور مینجمنٹ",
    label=lambda r: r["name"],
    fields=[
        dict(key="name", label="Driver Name", required=True),
        dict(key="cnic", label="CNIC", ph="42101-1234567-1"),
        dict(key="phone", label="Phone"),
        dict(key="phone2", label="Phone 2"),
        dict(key="emergency_contact", label="Emergency Contact"),
        dict(key="status", label="Status", kind="select", options=["Active", "Inactive"]),
        dict(key="license_number", label="Licence Number"),
        dict(key="license_expiry", label="Licence Expiry", kind="date"),
        dict(key="date_of_joining", label="Date of Joining", kind="date", default="today"),
        dict(key="salary", label="Monthly Salary (PKR)", kind="money", step=1000.0, default=35000.0),
        dict(key="address", label="Address", wide=True),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("name", "Driver", None), ("cnic", "CNIC", None), ("phone", "Phone", None),
             ("license_number", "Licence", None), ("license_expiry", "Licence Expiry", "date"),
             ("salary", "Salary", "money"), ("status", "Status", "status")],
    filters=["status"],
    quick_status=("status", ["Active", "Inactive"]),
)


def _before_save(data, old):
    if data.get("cnic") and not re.fullmatch(r"\d{5}-?\d{7}-?\d", data["cnic"]):
        raise DBError("CNIC format should be 12345-1234567-1")
    return data


CFG["before_save"] = _before_save


def render():
    entity_page(CFG)
