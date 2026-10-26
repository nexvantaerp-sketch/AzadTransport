"""Dropdown Lists — saare dropdowns ki values yahin se add / remove karen."""
from collections import Counter
import streamlit as st
from utils import db, options
from utils.auth import can_edit
from utils.crud import QUICK_ADD, _delete_dialog, _quick_add_dialog, flash
from utils.db import DBError
from utils.helpers import STRETCH, status_text
from utils.styles import page_header, section, empty_state

SQL_HINT = "migration_v3_dropdowns.sql"


def _lists() -> list[dict]:
    """Every free-choice dropdown in the app (status-type dropdowns are locked: app logic depends on them)."""
    from utils.crud import _allow_new
    from views import advances, customers, drivers, expenses, payments, trips, vehicles
    out = []
    for cfg in (trips.CFG, vehicles.CFG, drivers.CFG, customers.CFG, expenses.CFG, payments.CFG, advances.CFG):
        for f in cfg["fields"]:
            if f.get("kind") == "select" and _allow_new(f):
                out.append(dict(key=options.list_key(cfg["table"], f["key"]), label=f"{cfg['title']}  →  {f['label']}",
                                defaults=list(f["options"]), table=cfg["table"], column=f["key"]))
    return out


def _guard(fn, *a):
    try:
        fn(*a)
    except DBError as e:
        st.error(f"⚠️ {e}")
        return False
    return True


# ───────────────────────── tab 1: type / category / method lists ─────────────────────────
def _lists_tab():
    if not options.available():
        st.warning("Is feature ke liye Supabase mein **ek baar** ek chhoti table banani hai.")
        st.markdown(f"Supabase → **SQL Editor** → project ki file **`{SQL_HINT}`** ka content paste karke **Run** karen, phir yahan refresh karen. "
                    "Tab tak app purani (built-in) lists ke saath normal chalti rahegi.")
        try:
            st.code(open(f"{__file__.rsplit('/views/', 1)[0]}/{SQL_HINT}", encoding="utf-8").read(), language="sql")
        except OSError:
            pass
        return

    lists = _lists()
    meta = st.selectbox("Konsi dropdown list edit karni hai?", lists, format_func=lambda x: x["label"], key="dl_pick")
    key, defaults = meta["key"], meta["defaults"]
    try:
        used = Counter(str(r.get(meta["column"])) for r in db.fetch(meta["table"]) if r.get(meta["column"]))
    except DBError:
        used = Counter()
    current = options.effective(key, defaults)

    c1, c2 = st.columns([1.5, 1], gap="large")
    with c1.container(border=True):
        section(f"Current options ({len(current)})")
        for i, v in enumerate(current):
            a, b, c = st.columns([3, 1.6, 1.3], vertical_alignment="center")
            a.markdown(f"**{v}**")
            n = used.get(v, 0)
            b.caption(f"{n} record(s) mein use" if n else "use nahi hui")
            if c.button("🗑️ Remove", key=f"rm_{key}_{i}", **STRETCH):
                if _guard(options.remove, key, v, defaults):
                    flash(f"“{v}” removed", "🗑️")
                    st.rerun()
        st.caption("Remove karne se purane records nahi bigadte — un mein purani value waisi hi rehti hai, bas naye form ke dropdown mein nahi aayegi.")
    with c2:
        with st.form(f"add_opt_{key}", border=True, clear_on_submit=True):
            st.markdown("#### ➕ Naya option")
            new = st.text_input("Option ka naam", placeholder="e.g. Parking Fee", max_chars=options.MAX_LEN)
            go = st.form_submit_button("Add to list", type="primary", **STRETCH)
        if go:
            if _guard(options.add, key, new, defaults):
                flash(f"“{' '.join(new.split())}” added", "✅")
                st.rerun()
        gone = options.removed_defaults(key, defaults)
        if gone:
            with st.expander(f"Removed options ({len(gone)}) — wapas laen"):
                for i, v in enumerate(gone):
                    x, y = st.columns([2, 1.3], vertical_alignment="center")
                    x.write(v)
                    if y.button("↩️ Restore", key=f"rs_{key}_{i}", **STRETCH):
                        if _guard(options.restore, key, v):
                            flash(f"“{v}” restored", "↩️")
                            st.rerun()
        extra = sorted(v for v in used if v not in current)
        if extra:
            with st.expander(f"Records mein ye values hain par list mein nahi ({len(extra)})"):
                for i, v in enumerate(extra):
                    x, y = st.columns([2, 1.3], vertical_alignment="center")
                    x.write(f"{v} · {used[v]}")
                    if y.button("➕ Add", key=f"ex_{key}_{i}", **STRETCH):
                        if _guard(options.add, key, v, defaults):
                            st.rerun()


# ───────────────────────── tab 2: vehicles / drivers / customers ─────────────────────────
def _records_tab():
    from views import customers, drivers, vehicles
    cfgs = {"🚛 Vehicles": vehicles.CFG, "👤 Drivers": drivers.CFG, "🏭 Customers": customers.CFG}
    pick = st.segmented_control("Kis ki list?", list(cfgs), default="🚛 Vehicles", key="dl_ent") or "🚛 Vehicles"
    cfg = cfgs[pick]
    table = cfg["table"]
    st.caption("**Hide** = dropdown se hat jata hai par purani trips/invoices ka record safe rehta hai (recommended). "
               "**Delete** = hamesha ke liye khatam, sirf tab hota hai jab kisi trip/invoice mein use na hua ho.")
    if st.button(f"➕ New {cfg['noun']}", key=f"dl_new_{table}"):
        _quick_add_dialog(table, "dl_unused")
    try:
        rows = db.fetch(table)
    except DBError as e:
        st.error(f"⚠️ {e}")
        return
    if not rows:
        empty_state(f"Abhi koi {cfg['noun'].lower()} nahi hai.", cfg["icon"])
        return
    rows = sorted(rows, key=lambda r: (r.get("status") == "Inactive", cfg["label"](r).lower()))
    with st.container(border=True):
        section(f"{cfg['title']} ({sum(1 for r in rows if r.get('status') != 'Inactive')} dropdown mein, "
                f"{sum(1 for r in rows if r.get('status') == 'Inactive')} hidden)")
        for r in rows:
            hidden = r.get("status") == "Inactive"
            a, b, c, d = st.columns([2.6, 1.4, 1.5, 1.1], vertical_alignment="center")
            a.markdown(("~~" + cfg["label"](r) + "~~") if hidden else f"**{cfg['label'](r)}**")
            b.markdown(status_text(r.get("status")))
            if hidden:
                if c.button("👁️ Show again", key=f"sh_{r['id']}", **STRETCH):
                    db.update(table, r["id"], {"status": "Active"})
                    flash(f"{cfg['label'](r)} wapas dropdown mein", "👁️")
                    st.rerun()
            elif c.button("🙈 Hide", key=f"hd_{r['id']}", **STRETCH):
                db.update(table, r["id"], {"status": "Inactive"})
                flash(f"{cfg['label'](r)} dropdown se hata diya", "🙈")
                st.rerun()
            if d.button("🗑️", key=f"dd_{r['id']}", help="Permanently delete", **STRETCH):
                _delete_dialog(cfg, r)


def render():
    page_header("Dropdown Lists", "Dropdowns mein values add / remove karen / ڈراپ ڈاؤن لسٹ", "🧰")
    if not can_edit():
        st.info("👁️ View-only access — your role cannot change dropdown lists.")
        return
    try:
        t1, t2 = st.tabs(["📝 Type · Category · Method lists", "🚛 Vehicles · Drivers · Customers"])
        with t1:
            _lists_tab()
        with t2:
            _records_tab()
    except DBError as e:
        st.error(f"⚠️ {e}")
