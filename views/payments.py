from utils import db
from utils.crud import entity_page
from utils.db import DBError
from utils.billing import recalc_invoice
from utils.config import PAYMENT_METHODS
from utils.helpers import num, pkr


def _before_save(data, old):
    if data.get("invoice_id"):
        inv = next((i for i in db.fetch("invoices") if i["id"] == data["invoice_id"]), None)
        if not inv:
            raise DBError("Selected invoice not found.")
        if inv.get("customer_id") != data["customer_id"]:
            raise DBError("This invoice belongs to a different customer.")
        avail = num(inv.get("balance"))
        if old and old.get("invoice_id") == inv["id"] and old.get("status") != "Bounced":
            avail += num(old.get("amount"))
        if data["status"] != "Bounced" and data["amount"] > avail + 0.5:
            raise DBError(f"Amount exceeds the invoice balance ({pkr(avail)}).")
    return data


def _after_save(row, old):
    recalc_invoice(row.get("invoice_id"))
    if old and old.get("invoice_id") and old.get("invoice_id") != row.get("invoice_id"):
        recalc_invoice(old["invoice_id"])


CFG = dict(
    table="payments", title="Payments", noun="Payment", icon="💳",
    subtitle="Receipts from customers — linked invoices update automatically / ادائیگیاں",
    label=lambda r: f"{pkr(r.get('amount'))} · {r.get('payment_date')}",
    date_key="payment_date", order="payment_date",
    fields=[
        dict(key="payment_date", label="Payment Date", kind="date", required=True, default="today"),
        dict(key="customer_id", label="Customer", kind="fk", required=True, ref=("customers", "name")),
        dict(key="invoice_id", label="Against Invoice", kind="fk",
             ref=("invoices", lambda r: f"{r['invoice_number']} · Bal {pkr(r.get('balance'))}"),
             help="Optional. The invoice balance & status update automatically"),
        dict(key="amount", label="Amount Received (PKR)", kind="money", positive=True, step=1000.0, default=0.0),
        dict(key="payment_method", label="Method", kind="select", options=PAYMENT_METHODS),
        dict(key="status", label="Status", kind="select",
             options=["Received", "Cleared", "Pending Clearance", "Bounced"]),
        dict(key="reference_number", label="Cheque / Reference No"),
        dict(key="bank_name", label="Bank", ph="HBL, Meezan…"),
        dict(key="cheque_date", label="Cheque Date", kind="date"),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("payment_date", "Date", "date"), ("customer_id", "Customer", None), ("invoice_id", "Invoice", None),
             ("amount", "Amount", "money"), ("payment_method", "Method", None),
             ("reference_number", "Reference", None), ("bank_name", "Bank", None), ("status", "Status", "status")],
    filters=["customer_id", "status"],
    before_save=_before_save, after_save=_after_save,
    after_delete=lambda rec: recalc_invoice(rec.get("invoice_id")),
)


def render():
    entity_page(CFG)
