"""Dropdown options the user can add / remove from the 'Dropdown Lists' page.

Storage: table `dropdown_options` (see migration_v3_dropdowns.sql)
  • is_hidden = FALSE → an option the user ADDED
  • is_hidden = TRUE  → a built-in option the user REMOVED
Table missing? The app still works with the built-in lists (nothing breaks)."""
from __future__ import annotations
from . import db
from .db import DBError

TABLE = "dropdown_options"
MAX_LEN = 50


def list_key(table: str, field: str) -> str:
    return f"{table}.{field}"


def _rows(key: str) -> list[dict]:
    return [r for r in db.fetch(TABLE, "created_at", False) if r.get("list_key") == key]


def available() -> bool:
    try:
        db.fetch(TABLE, "created_at", False)
        return True
    except DBError:
        return False


def effective(key: str, defaults: list[str]) -> list[str]:
    """Built-in options minus removed ones, plus added ones."""
    try:
        rows = _rows(key)
    except DBError:
        return list(defaults)
    hidden = {r["value"] for r in rows if r.get("is_hidden")}
    out = [d for d in defaults if d not in hidden]
    out += [r["value"] for r in rows if not r.get("is_hidden") and r["value"] not in out]
    return out


def removed_defaults(key: str, defaults: list[str]) -> list[str]:
    try:
        hidden = {r["value"] for r in _rows(key) if r.get("is_hidden")}
    except DBError:
        return []
    return [d for d in defaults if d in hidden]


def add(key: str, value: str, defaults: list[str]) -> None:
    value = " ".join((value or "").split())
    if not value:
        raise DBError("Please type the option name first.")
    if len(value) > MAX_LEN:
        raise DBError(f"Option is too long (max {MAX_LEN} characters).")
    rows = _rows(key)
    if any(r["value"] == value and r.get("is_hidden") for r in rows):          # removed built-in → bring it back
        db.delete(TABLE, next(r["id"] for r in rows if r["value"] == value and r.get("is_hidden")))
        return
    if value.lower() in {v.lower() for v in effective(key, defaults)}:
        raise DBError(f"“{value}” is already in this list.")
    db.insert(TABLE, {"list_key": key, "value": value, "is_hidden": False})


def remove(key: str, value: str, defaults: list[str]) -> None:
    if len(effective(key, defaults)) <= 1:
        raise DBError("At least one option must stay in the list.")
    rows = _rows(key)
    for r in rows:
        if r["value"] == value and not r.get("is_hidden"):
            db.delete(TABLE, r["id"])
    if value in defaults and not any(r["value"] == value and r.get("is_hidden") for r in rows):
        db.insert(TABLE, {"list_key": key, "value": value, "is_hidden": True})


def restore(key: str, value: str) -> None:
    for r in _rows(key):
        if r["value"] == value and r.get("is_hidden"):
            db.delete(TABLE, r["id"])
