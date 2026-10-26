"""Invoice maths + printable invoice HTML."""
from html import escape
from . import db
from .config import COMPANY
from .helpers import num, pkr, fmt_date, tons


def recalc_invoice(invoice_id) -> None:
    """Re-derive paid / balance / status of an invoice from its (non-bounced) payments."""
    if not invoice_id:
        return
    inv = db.where("invoices", "id", invoice_id)
    if not inv:
        return
    inv = inv[0]
    paid = sum(num(p.get("amount")) for p in db.where("payments", "invoice_id", invoice_id)
               if p.get("status") != "Bounced")
    net = num(inv.get("net_amount"))
    balance = round(max(net - paid, 0), 2)
    status = "Paid" if net > 0 and balance <= 0.5 else ("Partial" if paid > 0 else "Pending")
    db.update("invoices", invoice_id, {"paid_amount": round(paid, 2), "balance": balance, "status": status})


def invoice_html(inv: dict, customer: dict, items: list[dict], trips_by_id: dict, vehicles: dict) -> bytes:
    rows = ""
    for i, it in enumerate(items, 1):
        t = trips_by_id.get(it.get("trip_id"), {})
        rows += (f"<tr><td>{i}</td><td>{escape(str(it.get('description') or ''))}</td>"
                 f"<td>{escape(vehicles.get(t.get('vehicle_id'), '—'))}</td>"
                 f"<td class='r'>{num(it.get('quantity')):,.2f}</td><td class='r'>{num(it.get('rate')):,.0f}</td>"
                 f"<td class='r'>{num(it.get('amount')):,.0f}</td></tr>")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Invoice {escape(inv['invoice_number'])}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;color:#0F172A;margin:40px;}}
.top{{display:flex;justify-content:space-between;border-bottom:3px solid #0B1B3A;padding-bottom:14px;}}
h1{{margin:0;color:#0B1B3A;font-size:24px}}.gold{{color:#B8891A;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-top:22px}}th{{background:#0B1B3A;color:#fff;text-align:left;padding:9px;font-size:13px}}
td{{padding:9px;border-bottom:1px solid #E2E8F0;font-size:13px}}.r{{text-align:right}}
.tot{{margin-left:auto;width:320px;margin-top:18px}}.tot div{{display:flex;justify-content:space-between;padding:6px 0;font-size:14px}}
.tot .g{{border-top:2px solid #0B1B3A;font-weight:800;font-size:16px}}.meta{{display:flex;justify-content:space-between;margin-top:20px;font-size:13px}}
@media print{{body{{margin:12mm}}}}</style></head><body>
<div class="top"><div><h1>{escape(COMPANY['name'])}</h1><div class="gold">{escape(COMPANY['tagline'])}</div>
<div style="font-size:12px;color:#64748B">{escape(COMPANY['address'])} {escape(COMPANY['phone'])}</div></div>
<div style="text-align:right"><h1>INVOICE</h1><div><b>{escape(inv['invoice_number'])}</b></div></div></div>
<div class="meta"><div><b>Bill To</b><br>{escape(customer.get('name',''))}<br>{escape(customer.get('address') or '')}<br>
{escape(customer.get('city') or '')} {('· NTN ' + escape(customer['ntn'])) if customer.get('ntn') else ''}</div>
<div style="text-align:right">Invoice Date: <b>{fmt_date(inv.get('invoice_date'))}</b><br>Due Date: <b>{fmt_date(inv.get('due_date'))}</b><br>Status: <b>{escape(inv.get('status',''))}</b></div></div>
<table><tr><th>#</th><th>Description</th><th>Vehicle</th><th class="r">Qty (Tons)</th><th class="r">Rate</th><th class="r">Amount (PKR)</th></tr>{rows}</table>
<div class="tot"><div><span>Subtotal</span><span>{pkr(inv.get('total_amount'))}</span></div>
<div><span>Tax / Withholding</span><span>- {pkr(inv.get('tax_amount'))}</span></div>
<div class="g"><span>Net Payable</span><span>{pkr(inv.get('net_amount'))}</span></div>
<div><span>Received</span><span>{pkr(inv.get('paid_amount'))}</span></div>
<div class="g"><span>Balance Due</span><span>{pkr(inv.get('balance'))}</span></div></div>
<p style="margin-top:30px;font-size:12px;color:#64748B">{escape(inv.get('notes') or '')}</p>
<p style="margin-top:60px;font-size:12px;color:#64748B">Authorised Signature ____________________</p></body></html>"""
    return html.encode("utf-8")
