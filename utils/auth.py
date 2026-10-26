"""Authentication: salted PBKDF2 hashes, legacy SHA-256 upgrade, first-run admin bootstrap."""
import hashlib
import hmac
import re
import secrets
import time
import streamlit as st
from . import db

ITERATIONS = 200_000
DEFAULT_ADMIN = ("admin", "admin123")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS)
    return f"pbkdf2${ITERATIONS}${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, iters, salt, digest = stored.split("$")
            dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iters))
            return hmac.compare_digest(dk.hex(), digest)
        except Exception:
            return False
    if re.fullmatch(r"[0-9a-f]{64}", stored):          # legacy unsalted sha256
        return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)
    return False


def _valid_hash(h: str) -> bool:
    h = h or ""
    return h.startswith("pbkdf2$") or re.fullmatch(r"[0-9a-f]{64}", h) is not None


def ensure_admin() -> None:
    """First run: create admin/admin123 if no usable user exists (drops the old broken placeholder row)."""
    users = db.fetch("app_users")
    if any(_valid_hash(u.get("password_hash", "")) for u in users):
        return
    for u in users:
        db.delete("app_users", u["id"])
    db.insert("app_users", {"username": DEFAULT_ADMIN[0], "password_hash": hash_password(DEFAULT_ADMIN[1]),
                            "full_name": "Administrator", "role": "admin", "status": "Active"})


def attempt_login(username: str, password: str):
    """Returns (user_dict | None, message)."""
    lock = st.session_state.get("lock_until", 0)
    if time.time() < lock:
        return None, f"Too many attempts. Try again in {int(lock - time.time())}s."
    username = (username or "").strip()
    rows = [u for u in db.where("app_users", "username", username) if u.get("status") == "Active"]
    user = rows[0] if rows else None
    if user and verify_password(password, user["password_hash"]):
        if not user["password_hash"].startswith("pbkdf2$"):      # upgrade legacy hash silently
            db.update("app_users", user["id"], {"password_hash": hash_password(password)})
        st.session_state["fails"] = 0
        user["using_default_password"] = (password == DEFAULT_ADMIN[1])
        return user, "ok"
    st.session_state["fails"] = st.session_state.get("fails", 0) + 1
    if st.session_state["fails"] >= 5:
        st.session_state["lock_until"] = time.time() + 60
        st.session_state["fails"] = 0
    return None, "Invalid username or password / غلط آئی ڈی یا پاسورڈ"


def current_user() -> dict:
    return st.session_state.get("user") or {}


def is_admin() -> bool:
    return current_user().get("role") == "admin"


def can_edit() -> bool:
    """viewer role is read-only."""
    return current_user().get("role", "admin") in ("admin", "staff")
