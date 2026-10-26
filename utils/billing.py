"""Invoice maths + printable invoice (HTML and PDF)."""
import io
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


def invoice_pdf(inv: dict, customer: dict, items: list[dict], trips_by_id: dict, vehicles: dict) -> bytes:
    """A4 print-ready invoice PDF (customer ko print/WhatsApp karne ke liye)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    NAVY, GOLD, MUTED, LINE = colors.HexColor("#0B1B3A"), colors.HexColor("#B8891A"), colors.HexColor("#64748B"), colors.HexColor("#E2E8F0")
    st_ = lambda name, **kw: ParagraphStyle(name, fontName=kw.pop("font", "Helvetica"), fontSize=kw.pop("size", 9.5),
                                            leading=kw.pop("lead", 13), textColor=kw.pop("color", colors.HexColor("#0F172A")), **kw)
    body, small = st_("b"), st_("s", size=8.5, color=MUTED, lead=11)
    right = st_("r", alignment=2)
    e = lambda v: escape(str(v if v not in (None, "") else ""))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
                            title=f"Invoice {inv.get('invoice_number', '')}", author=COMPANY["name"])
    W = A4[0] - 32 * mm
    story = []

    # header band
    contact = " · ".join(x for x in (COMPANY.get("address"), COMPANY.get("phone")) if x)
    left = [Paragraph(e(COMPANY["name"]), st_("h", font="Helvetica-Bold", size=17, lead=21, color=colors.white)),
            Paragraph(e(COMPANY["tagline"]), st_("t", size=9, color=colors.HexColor("#E7C65A"), lead=12))]
    if contact:
        left.append(Paragraph(e(contact), st_("c", size=8, color=colors.HexColor("#CBD5E1"), lead=11)))
    rt = [Paragraph("INVOICE", st_("i", font="Helvetica-Bold", size=20, lead=24, color=colors.white, alignment=2)),
          Paragraph(e(inv.get("invoice_number")), st_("n", font="Helvetica-Bold", size=10.5, color=colors.HexColor("#E7C65A"), alignment=2))]
    head = Table([[left, rt]], colWidths=[W * 0.62, W * 0.38])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                              ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                              ("LINEBELOW", (0, 0), (-1, -1), 3, GOLD)]))
    story += [head, Spacer(1, 12)]

    # bill-to / meta
    c = customer or {}
    bill = [Paragraph("BILL TO", st_("l", font="Helvetica-Bold", size=8, color=MUTED)),
            Paragraph(f"<b>{e(c.get('name'))}</b>", st_("cn", size=11, lead=15))]
    for line in (c.get("address"), " ".join(x for x in (c.get("city"), ("NTN " + c["ntn"]) if c.get("ntn") else "") if x), c.get("phone")):
        if line:
            bill.append(Paragraph(e(line), small))
    meta = [Paragraph(f"Invoice Date: <b>{e(fmt_date(inv.get('invoice_date')))}</b>", right),
            Paragraph(f"Due Date: <b>{e(fmt_date(inv.get('due_date')))}</b>", right),
            Paragraph(f"Status: <b>{e(inv.get('status'))}</b>", right)]
    info = Table([[bill, meta]], colWidths=[W * 0.55, W * 0.45])
    info.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [info, Spacer(1, 14)]

    # items
    hs = st_("th", font="Helvetica-Bold", size=8.5, color=colors.white)
    hr = st_("thr", font="Helvetica-Bold", size=8.5, color=colors.white, alignment=2)
    data = [[Paragraph("#", hs), Paragraph("Description", hs), Paragraph("Vehicle", hs),
             Paragraph("Qty (Tons)", hr), Paragraph("Rate", hr), Paragraph("Amount (PKR)", hr)]]
    cell = st_("cell", size=9, lead=12)
    for i, it in enumerate(items, 1):
        t = trips_by_id.get(it.get("trip_id"), {})
        data.append([Paragraph(str(i), cell), Paragraph(e(it.get("description")), cell),
                     Paragraph(e(vehicles.get(t.get("vehicle_id"), "—")), cell),
                     Paragraph(f"{num(it.get('quantity')):,.2f}", st_("q", size=9, alignment=2)),
                     Paragraph(f"{num(it.get('rate')):,.0f}", st_("q2", size=9, alignment=2)),
                     Paragraph(f"{num(it.get('amount')):,.0f}", st_("q3", size=9, alignment=2, font="Helvetica-Bold"))])
    tbl = Table(data, colWidths=[W * .06, W * .38, W * .14, W * .12, W * .12, W * .18], repeatRows=1)
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                             ("LINEBELOW", (0, 1), (-1, -1), 0.5, LINE), ("TOPPADDING", (0, 0), (-1, -1), 6),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story += [tbl, Spacer(1, 10)]

    # totals
    lab, val = st_("tl", size=9.5), st_("tv", size=9.5, alignment=2)
    labb, valb = st_("tlb", font="Helvetica-Bold", size=11, lead=15), st_("tvb", font="Helvetica-Bold", size=11, lead=15, alignment=2)
    rows = [[Paragraph("Subtotal", lab), Paragraph(pkr(inv.get("total_amount")), val)],
            [Paragraph("Tax / Withholding", lab), Paragraph("- " + pkr(inv.get("tax_amount")), val)],
            [Paragraph("Net Payable", labb), Paragraph(pkr(inv.get("net_amount")), valb)],
            [Paragraph("Received", lab), Paragraph(pkr(inv.get("paid_amount")), val)],
            [Paragraph("Balance Due", labb), Paragraph(pkr(inv.get("balance")), valb)]]
    tot = Table(rows, colWidths=[W * .20, W * .22], hAlign="RIGHT")
    tot.setStyle(TableStyle([("LINEABOVE", (0, 2), (-1, 2), 1.2, NAVY), ("LINEABOVE", (0, 4), (-1, 4), 1.2, NAVY),
                             ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#FFF8E1")),
                             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(KeepTogether([tot]))

    if inv.get("notes"):
        story += [Spacer(1, 14), Paragraph("<b>Notes</b>", small), Paragraph(e(inv["notes"]), body)]
    story += [Spacer(1, 46)]
    sig = Table([[Paragraph("Customer Signature / Stamp", small), Paragraph("Authorised Signature", st_("sr", size=8.5, color=MUTED, lead=11, alignment=2))]],
                colWidths=[W * .5, W * .5])
    sig.setStyle(TableStyle([("LINEABOVE", (0, 0), (0, 0), 0.8, MUTED), ("LINEABOVE", (1, 0), (1, 0), 0.8, MUTED),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(Table([[sig]], colWidths=[W], style=[("LEFTPADDING", (0, 0), (-1, -1), 0)]))

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(A4[0] / 2, 9 * mm, f"{COMPANY['name']} · Computer generated invoice · Page {d.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
