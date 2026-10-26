from utils.crud import entity_page

CFG = dict(
    table="customers", title="Customers", noun="Customer", icon="🏭",
    subtitle="Sugar mills, distilleries & traders with agreed rates / کسٹمر مینجمنٹ",
    label=lambda r: r["name"],
    fields=[
        dict(key="name", label="Customer / Mill Name", required=True, ph="Habib Sugar Mills"),
        dict(key="short_name", label="Short Name", ph="HSM"),
        dict(key="customer_type", label="Type", kind="select", options=["Sugar Mill", "Distillery", "Factory", "Trader", "Other"]),
        dict(key="contact_person", label="Contact Person"),
        dict(key="phone", label="Phone"),
        dict(key="email", label="Email"),
        dict(key="city", label="City"),
        dict(key="ntn", label="NTN"),
        dict(key="status", label="Status", kind="select", options=["Active", "Inactive"]),
        dict(key="payment_terms", label="Payment Terms (days)", kind="int", min=0, max=365, default=30),
        dict(key="rate_per_ton", label="Default Rate / Ton (PKR)", kind="money", step=50.0, default=0.0,
             help="Used automatically on trips when the trip rate is left at 0"),
        dict(key="contract_start", label="Contract Start", kind="date"),
        dict(key="contract_end", label="Contract End", kind="date"),
        dict(key="address", label="Address", wide=True),
        dict(key="notes", label="Notes", kind="textarea"),
    ],
    columns=[("name", "Customer", None), ("customer_type", "Type", None), ("city", "City", None),
             ("contact_person", "Contact", None), ("phone", "Phone", None),
             ("rate_per_ton", "Rate/Ton", "money"), ("payment_terms", "Terms (d)", "num"),
             ("status", "Status", "status")],
    filters=["status", "customer_type"],
    quick_status=("status", ["Active", "Inactive"]),
)


def render():
    entity_page(CFG)
