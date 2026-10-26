import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "tests"))
os.chdir(BASE)
import streamlit as st
from streamlit.testing.v1 import AppTest
from fake_supabase import FakeSupabase
import utils.db as dbm

FAKE = FakeSupabase()
dbm.get_client = lambda: FAKE          # every module calls db.get_client() at call time


def reset():
    FAKE.tables.clear()
    st.cache_data.clear()


def view_test(module, user=None):
    code = f"""
import sys, os
sys.path.insert(0, {BASE!r}); sys.path.insert(0, {os.path.join(BASE, 'tests')!r})
import streamlit as st
import harness
from utils.styles import inject_css
inject_css()
st.session_state.setdefault('user', {user or {'id':'u1','username':'admin','role':'admin','full_name':'Admin'}!r})
from views import {module} as m
m.render()
"""
    at = AppTest.from_string(code, default_timeout=60)
    return at.run()


def errs(at):
    out = [f"EXCEPTION: {e.value}" for e in at.exception]
    out += [f"st.error: {e.value}" for e in at.error]
    return out
