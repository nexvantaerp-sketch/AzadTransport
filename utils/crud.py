"""Generic entity manager: searchable table, add form, edit dialog, delete confirmation, Excel export."""
from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from . import db
from .db import DBError
from .auth import can_edit
from .helpers import STRETCH, num, pkr, tons, fmt_date, status_text, to_date, download_excel
from .styles import page_header, empty_state

DATE_MIN, DATE_MAX = date(1990, 1, 1), date(2100, 12, 31)


# ───────────────────────── flash messages ─────────────────────────
def flash(msg: str, icon: str = "✅") -> None:
    st.session_state["_flash"] = (msg, icon)


def show_flash() -> None:
    f = st.session_state.pop("_flash", None)
    if f:
        st.toast(f[0], icon=f[1])


# ───────────────────────── form building ─────────────────────────
def fk_map(ref) -> dict:
    table, label = ref
    return {r["id"]: (label(r) if callable(label) else str(r.get(label) or "—")) for r in db.fetch(table)}


def _default(f):
    d = f.get("default")
    if callable(d):
        return d()
    return date.today() if d == "today" else d


# Jin dropdowns ki values par app ka logic chalta hai (status, freight basis) wahan nayi value add nahi hoti.
LOCKED_SELECTS = {"status", "freight_basis"}


def _allow_new(f: dict) -> bool:
    return f.get("add_new", f["key"] not in LOCKED_SELECTS)


def _known_values(table: str, column: str) -> list[str]:
    """Is table ke column mein pehle se save ki hui alag alag values (custom options yahin se aati hain)."""
    try:
        vals = {str(r.get(column)).strip() for r in db.fetch(table) if r.get(column) not in (None, "")}
    except DBError:
        return []
    return sorted(vals, key=str.lower)


def _widget(t, f: dict, val, key: str, fkm: dict | None, table: str | None = None):
    kind, label = f.get("kind", "text"), f["label"] + (" *" if f.get("required") else "")
    help_ = f.get("help")
    if kind == "text":
        return t.text_input(label, value=val or "", key=key, placeholder=f.get("ph", ""), help=help_)
    if kind == "textarea":
        return t.text_area(label, value=val or "", key=key, help=help_, height=90)
    if kind == "int":
        return t.number_input(label, value=int(num(val)), min_value=int(f.get("min", 0)),
                              max_value=int(f["max"]) if "max" in f else None, step=1, key=key, help=help_)
    if kind in ("number", "money"):
        step = float(f.get("step", 500.0 if kind == "money" else 1.0))
        return t.number_input(label, value=float(num(val)), min_value=float(f.get("min", 0.0)),
                              step=step, key=key, help=help_, format="%.2f")
    if kind == "date":
        return t.date_input(label, value=to_date(val), key=key, help=help_, format="DD/MM/YYYY",
                            min_value=DATE_MIN, max_value=DATE_MAX)
    if kind == "select":
        opts = list(f["options"])
        if table:                                        # purani saved custom values bhi dropdown mein aayen
            opts += [v for v in _known_values(table, f["key"]) if v not in opts]
        if val is not None and val not in opts:
            opts.insert(0, val)
        if _allow_new(f):
            return t.selectbox(label, opts, index=opts.index(val) if val in opts else 0, key=key, accept_new_options=True,
                               help=(help_ + " · " if help_ else "") + "Nayi value add karne ke liye yahin type karke Enter dabayen")
        return t.selectbox(label, opts, index=opts.index(val) if val in opts else 0, key=key, help=help_)
    if kind == "fk":
        ids = list(fkm or {})
        opts = ids if f.get("required") else [None] + ids
        idx = opts.index(val) if val in opts else 0
        return t.selectbox(label, opts, index=idx, key=key, help=help_,
                           format_func=lambda x: "— None —" if x is None else (fkm or {}).get(x, "?"))
    raise ValueError(f"Unknown field kind {kind}")


def render_fields(fields, initial: dict, prefix: str, fkmaps: dict, table: str | None = None) -> dict:
    out, cols, n = {}, None, 0
    for f in fields:
        if f.get("wide") or f.get("kind") == "textarea":
            target, cols = st, None
        else:
            if cols is None or n >= 3:
                cols, n = st.columns(3), 0
            target, n = cols[n], n + 1
        out[f["key"]] = _widget(target, f, initial.get(f["key"]), f"{prefix}_{f['key']}", fkmaps.get(f["key"]), table)
    return out


def clean(fields, raw: dict):
    data, errors = {}, []
    for f in fields:
        k, kind, v = f["key"], f.get("kind", "text"), raw.get(f["key"])
        if kind in ("text", "textarea"):
            v = (v or "").strip() or None
        elif kind == "select":
            v = str(v).strip() if v not in (None, "") else None
        elif kind == "date":
            v = v.isoformat() if v else None
        elif kind == "int":
            v = int(v)
        elif kind in ("number", "money"):
            v = float(v)
        if f.get("required") and (v is None or v == ""):
            errors.append(f"{f['label']} is required")
        if f.get("positive") and (v is None or v <= 0):
            errors.append(f"{f['label']} must be greater than 0")
        data[k] = v
    return data, errors


# ───────────────────────── display ─────────────────────────
def _fmt(v, fmt):
    if fmt == "money":
        return pkr(v)
    if fmt == "tons":
        return tons(v)
    if fmt == "date":
        return fmt_date(v)
    if fmt == "status":
        return status_text(v)
    if fmt == "num":
        return f"{num(v):,.0f}"
    return "—" if v in (None, "") else str(v)


def build_view(cfg: dict, rows: list[dict], fkmaps: dict) -> pd.DataFrame:
    recs = []
    for r in rows:
        d = {"_id": r["id"]}
        for key, label, fmt in cfg["columns"]:
            d[label] = fkmaps[key].get(r.get(key), "—") if key in fkmaps else _fmt(r.get(key), fmt)
        recs.append(d)
    return pd.DataFrame(recs)


# ───────────────────────── dialogs ─────────────────────────
@st.dialog("Edit record", width="large")
def _edit_dialog(cfg: dict, rec: dict, fkmaps: dict):
    st.caption(f"Editing: **{cfg['label'](rec)}**")
    with st.form(f"edit_{cfg['table']}_{rec['id']}", border=False):
        raw = render_fields(cfg["fields"], rec, f"e_{cfg['table']}_{rec['id']}", fkmaps, cfg["table"])
        saved = st.form_submit_button("💾 Save changes", type="primary", **STRETCH)
    if saved:
        data, errors = clean(cfg["fields"], raw)
        if errors:
            st.error("  \n".join(errors))
            return
        try:
            if cfg.get("before_save"):
                data = cfg["before_save"](data, rec) or data
            row = db.update(cfg["table"], rec["id"], data)
            if cfg.get("after_save"):
                cfg["after_save"](row or {**rec, **data}, rec)
        except DBError as e:
            st.error(str(e))
            return
        flash(f"{cfg['noun']} updated")
        st.rerun()


@st.dialog("Confirm delete")
def _delete_dialog(cfg: dict, rec: dict):
    st.warning(f"Delete **{cfg['label'](rec)}**? This cannot be undone.")
    c1, c2 = st.columns(2)
    if c1.button("Yes, delete", type="primary", key=f"yes_{rec['id']}", **STRETCH):
        try:
            if cfg.get("before_delete"):
                cfg["before_delete"](rec)
            db.delete(cfg["table"], rec["id"])
            if cfg.get("after_delete"):
                cfg["after_delete"](rec)
        except DBError as e:
            st.error(str(e))
            return
        flash(f"{cfg['noun']} deleted", "🗑️")
        st.rerun()
    if c2.button("Cancel", key=f"no_{rec['id']}", **STRETCH):
        st.rerun()


# ───────────────────────── quick add (➕ New customer / vehicle / driver) ─────────────────────────
QUICK_ADD = {"customers": ("views.customers", "Customer"), "vehicles": ("views.vehicles", "Vehicle"),
             "drivers": ("views.drivers", "Driver")}


@st.dialog("➕ Add new", width="large")
def _quick_add_dialog(table: str, select_key: str):
    import importlib
    cfg = importlib.import_module(QUICK_ADD[table][0]).CFG
    st.caption(f"Naya **{cfg['noun']}** yahin se add karen — save hote hi dropdown mein select ho jayega.")
    with st.form(f"qa_{table}", border=False):
        raw = render_fields(cfg["fields"], {f["key"]: _default(f) for f in cfg["fields"]}, f"qa_{table}", {}, table)
        saved = st.form_submit_button(f"💾 Save {cfg['noun']}", type="primary", **STRETCH)
    if not saved:
        return
    data, errors = clean(cfg["fields"], raw)
    if errors:
        st.error("  \n".join(errors))
        return
    try:
        if cfg.get("before_save"):
            data = cfg["before_save"](data, None) or data
        row = db.insert(table, data)
        if cfg.get("after_save"):
            cfg["after_save"](row or data, None)
    except DBError as e:
        st.error(str(e))
        return
    try:
        st.session_state[select_key] = row["id"]             # naya record dropdown mein khud select
    except Exception:
        pass
    flash(f"{cfg['noun']} added")
    st.rerun()


def quick_add_buttons(items: list[tuple[str, str]]) -> None:
    """items: (table, widget_key_of_its_dropdown). Dropdown ke upar '➕ New …' buttons dikhata hai."""
    uniq, seen = [], set()
    for t, k in items:
        if t in QUICK_ADD and t not in seen:
            seen.add(t)
            uniq.append((t, k))
    items = uniq
    if not items or not can_edit():
        return
    cols = st.columns([1] * len(items) + [max(1, 5 - len(items))])
    for col, (table, key) in zip(cols, items):
        if col.button(f"➕ New {QUICK_ADD[table][1]}", key=f"qa_btn_{table}_{key}", help="Dropdown mein nahi hai? Yahin se add karen", **STRETCH):
            _quick_add_dialog(table, key)


# ───────────────────────── tabs ─────────────────────────
def _records_tab(cfg: dict, fkmaps: dict):
    t = cfg["table"]
    rows = db.fetch(t, cfg.get("order", "created_at"), cfg.get("desc", True))
    if not rows:
        empty_state(f"No {cfg['title'].lower()} yet — add the first one from the “New” tab.", cfg["icon"])
        return
    by_id = {r["id"]: r for r in rows}

    # date-range prefilter
    dkey = cfg.get("date_key")
    filters = cfg.get("filters", [])
    labels = {k: l for k, l, _ in cfg["columns"]}
    ncols = 1 + len(filters) + (1 if dkey else 0)
    cols = st.columns([2.4] + [1.2] * (ncols - 1))
    q = cols[0].text_input("Search", placeholder=f"🔍 Search {cfg['title'].lower()}…",
                           label_visibility="collapsed", key=f"{t}_q")
    rng, i = (), 1
    if dkey:
        rng = cols[i].date_input("Date range", value=(), key=f"{t}_rng", format="DD/MM/YYYY",
                                 label_visibility="collapsed", help="Filter by date range", min_value=DATE_MIN,
                                 max_value=DATE_MAX)
        i += 1
    if dkey and len(rng) == 2:
        a, b = rng
        rows = [r for r in rows if (d := to_date(r.get(dkey))) and a <= d <= b]

    view = build_view(cfg, rows, fkmaps)
    if view.empty:
        empty_state("No records in this date range.", "🔎")
        return
    for fk in filters:
        lab = labels[fk]
        opts = ["All " + lab] + sorted(view[lab].dropna().unique().tolist())
        pick = cols[i].selectbox(lab, opts, label_visibility="collapsed", key=f"{t}_f_{fk}")
        if pick != opts[0]:
            view = view[view[lab] == pick]
        i += 1
    if q:
        ql = q.lower()
        mask = view.drop(columns="_id").astype(str).apply(lambda s: s.str.lower().str.contains(ql, regex=False)).any(axis=1)
        view = view[mask]
    view = view.reset_index(drop=True)
    if view.empty:
        empty_state("No records match your search.", "🔎")
        return

    shown = view.drop(columns="_id")
    h1, h2 = st.columns([5, 1])
    h1.caption(f"{len(view)} record(s) — select a row (checkbox on the left) to edit or delete")
    with h2:
        download_excel("⬇ Excel", {cfg["title"][:28]: shown}, f"{t}.xlsx", key=f"{t}_xl")
    ev = st.dataframe(shown, hide_index=True, on_select="rerun", selection_mode="single-row",
                      key=f"{t}_tbl", height=min(480, 38 + 35 * len(shown)), **STRETCH)
    sel = ev.selection.rows if ev and ev.selection else []
    if not sel or sel[0] >= len(view) or not can_edit():
        return
    rec = by_id.get(view.loc[sel[0], "_id"])
    if not rec:
        return
    with st.container(border=True):
        st.markdown(f"**Selected:** {cfg['label'](rec)}")
        qs = cfg.get("quick_status")
        a, b, c = st.columns([1, 1, 3])
        if a.button("✏️ Edit", key=f"{t}_edit", type="primary", **STRETCH):
            _edit_dialog(cfg, rec, fkmaps)
        if b.button("🗑️ Delete", key=f"{t}_del", **STRETCH):
            _delete_dialog(cfg, rec)
        if qs and rec.get(qs[0]) in qs[1]:
            with c:
                s1, s2 = st.columns([2, 1])
                new = s1.selectbox("Set status", qs[1], index=qs[1].index(rec[qs[0]]),
                                   label_visibility="collapsed", key=f"{t}_qs_{rec['id']}")
                if s2.button("Update status", key=f"{t}_qsb_{rec['id']}", **STRETCH):
                    try:
                        db.update(t, rec["id"], {qs[0]: new})
                    except DBError as e:
                        st.error(str(e))
                    else:
                        flash(f"Status set to {new}")
                        st.rerun()


def _new_tab(cfg: dict, fkmaps: dict):
    t = cfg["table"]
    ver0 = st.session_state.setdefault(f"{t}_ver", 0)
    quick_add_buttons([(f["ref"][0], f"n_{t}_{ver0}_{f['key']}") for f in cfg["fields"] if f.get("kind") == "fk"])
    for f in cfg["fields"]:
        if f.get("kind") == "fk" and f.get("required") and not fkmaps[f["key"]]:
            st.warning(f"⚠️ Please add at least one **{f['ref'][0].replace('_', ' ')}** record first — "
                       f"it is required for this form.")
            return
    ver = st.session_state.setdefault(f"{t}_ver", 0)
    initial = {f["key"]: _default(f) for f in cfg["fields"]}
    with st.form(f"new_{t}_{ver}", border=True):
        st.markdown(f"#### ➕ New {cfg['noun']}")
        raw = render_fields(cfg["fields"], initial, f"n_{t}_{ver}", fkmaps, t)
        submitted = st.form_submit_button(f"💾 Save {cfg['noun']}", type="primary", **STRETCH)
    if not submitted:
        return
    data, errors = clean(cfg["fields"], raw)
    if errors:
        st.error("  \n".join(errors))
        return
    try:
        if cfg.get("before_save"):
            data = cfg["before_save"](data, None) or data
        row = db.insert(t, data)
        if cfg.get("after_save"):
            cfg["after_save"](row or data, None)
    except DBError as e:
        st.error(str(e))
        return
    st.session_state[f"{t}_ver"] = ver + 1          # fresh blank form next time
    flash(f"{cfg['noun']} saved successfully")
    st.rerun()


def entity_page(cfg: dict) -> None:
    page_header(cfg["title"], cfg["subtitle"], cfg["icon"])
    try:
        fkmaps = {f["key"]: fk_map(f["ref"]) for f in cfg["fields"] if f.get("kind") == "fk"}
        if not can_edit():
            st.info("👁️ View-only access — your role cannot add or change records.")
            _records_tab(cfg, fkmaps)
            return
        t1, t2 = st.tabs(["📋 Records", f"➕ New {cfg['noun']}"])
        with t1:
            _records_tab(cfg, fkmaps)
        with t2:
            _new_tab(cfg, fkmaps)
    except DBError as e:
        st.error(f"⚠️ {e}")
