"""Design system: CSS + reusable HTML components."""
from html import escape
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Nastaliq+Urdu:wght@500;700&display=swap');
:root{--navy:#0B1B3A;--navy2:#13294F;--gold:#C9A227;--gold2:#E7C65A;--ink:#0F172A;--muted:#64748B;
--line:#E2E8F0;--bg:#F3F5F9;--card:#FFFFFF;--ok:#16A34A;--bad:#DC2626;--warn:#D97706;--info:#2563EB;}
.stApp{font-family:'Inter',system-ui,sans-serif;}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],.stDeployButton{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:1.6rem!important;padding-bottom:3rem!important;max-width:1440px;}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{border-right:1px solid #1E3A6B;}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]{border-radius:10px;margin:2px 8px;padding:.5rem .75rem;font-weight:500;color:#CBD5E1!important;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover{background:rgba(255,255,255,.07);color:#fff!important;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"]{background:linear-gradient(90deg,rgba(212,175,55,.22),rgba(212,175,55,.04));
box-shadow:inset 3px 0 0 var(--gold2);color:#fff!important;font-weight:700;}
[data-testid="stSidebar"] [data-testid="stNavSectionHeader"],[data-testid="stSidebar"] [data-testid="stSidebarNav"] span[data-testid="stHeader"]{
color:#7F93B8!important;font-size:.68rem!important;letter-spacing:.14em;text-transform:uppercase;font-weight:700;}
.side-user{display:flex;gap:10px;align-items:center;padding:12px;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);margin:6px 4px 10px;}
.side-avatar{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--gold2),var(--gold));color:var(--navy);display:flex;align-items:center;justify-content:center;font-weight:800;}
.side-name{color:#fff;font-weight:700;font-size:.9rem;line-height:1.2;}.side-role{color:#8FA3C8;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.07);color:#E2E8F0;border:1px solid rgba(255,255,255,.14);}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(220,38,38,.18);border-color:rgba(248,113,113,.5);color:#fff;}

/* ---------- page header ---------- */
.pg-head{display:flex;align-items:center;gap:16px;margin:0 0 1.2rem;}
.pg-icon{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,var(--navy),var(--navy2));display:flex;align-items:center;justify-content:center;font-size:1.5rem;
box-shadow:0 6px 16px rgba(11,27,58,.25);border:1px solid rgba(212,175,55,.45);}
.pg-title{font-size:1.65rem;font-weight:800;color:var(--ink);line-height:1.15;letter-spacing:-.01em;}
.pg-sub{color:var(--muted);font-size:.92rem;margin-top:2px;}

/* ---------- KPI cards ---------- */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:.2rem 0 1.1rem;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;box-shadow:0 1px 2px rgba(15,23,42,.04),0 6px 18px rgba(15,23,42,.05);position:relative;overflow:hidden;}
.kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--gold);}
.kpi.green:before{background:var(--ok);}.kpi.red:before{background:var(--bad);}.kpi.blue:before{background:var(--info);}.kpi.navy:before{background:var(--navy);}
.kpi-top{display:flex;justify-content:space-between;align-items:center;}
.kpi-label{font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;}
.kpi-ico{font-size:1.15rem;opacity:.9;}
.kpi-val{font-size:1.65rem;font-weight:800;color:var(--ink);margin-top:6px;letter-spacing:-.02em;}
.kpi-sub{font-size:.78rem;color:var(--muted);margin-top:2px;}

/* ---------- containers, tabs, inputs ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]){border-radius:16px;}
div[data-testid="stForm"]{background:var(--card);border:1px solid var(--line)!important;border-radius:16px;padding:1.4rem 1.4rem .8rem;box-shadow:0 1px 2px rgba(15,23,42,.04),0 6px 18px rgba(15,23,42,.05);}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{height:44px;padding:0 16px;font-weight:600;color:var(--muted);border-radius:10px 10px 0 0;}
.stTabs [aria-selected="true"]{color:var(--navy)!important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--gold)!important;height:3px;}
.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea,[data-baseweb="select"]>div{border-radius:10px!important;}
label[data-testid="stWidgetLabel"] p{font-weight:600;font-size:.84rem;color:#334155;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:10px;font-weight:600;padding:.5rem 1.1rem;transition:all .15s;}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primaryFormSubmit"],.stButton>button[data-testid="stBaseButton-primary"]{
background:linear-gradient(135deg,var(--navy),#17305F)!important;border:1px solid var(--navy)!important;color:#fff!important;box-shadow:0 4px 12px rgba(11,27,58,.25);}
.stButton>button[data-testid="stBaseButton-primary"]:hover,[data-testid="stFormSubmitButton"]>button:hover{box-shadow:0 6px 16px rgba(11,27,58,.35);transform:translateY(-1px);}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;}
.sec-title{font-weight:700;font-size:1.02rem;color:var(--ink);margin:.4rem 0 .6rem;display:flex;align-items:center;gap:8px;}
.sec-title:after{content:"";flex:1;height:1px;background:var(--line);}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.74rem;font-weight:700;}
.pill.ok{background:#DCFCE7;color:#166534;}.pill.bad{background:#FEE2E2;color:#991B1B;}.pill.warn{background:#FEF3C7;color:#92400E;}.pill.info{background:#DBEAFE;color:#1E40AF;}
.alert-row{display:flex;justify-content:space-between;gap:10px;padding:9px 12px;border-radius:10px;background:#FFF7ED;border:1px solid #FED7AA;margin-bottom:6px;font-size:.86rem;color:#7C2D12;}
.alert-row.red{background:#FEF2F2;border-color:#FECACA;color:#7F1D1D;}
.empty{text-align:center;padding:44px 20px;color:var(--muted);}.empty .e-ico{font-size:2.6rem;margin-bottom:8px;}.empty .e-msg{font-weight:600;color:#334155;}

/* ---------- login ---------- */
.login-brand{background:radial-gradient(1200px 500px at 0% 0%,#1C3A74 0%,transparent 60%),linear-gradient(160deg,#0B1B3A,#0F2A5C 60%,#0B1B3A);border-radius:22px;padding:44px 40px;color:#fff;min-height:540px;
box-shadow:0 24px 60px rgba(11,27,58,.35);border:1px solid rgba(212,175,55,.35);display:flex;flex-direction:column;justify-content:space-between;}
.lb-mark{width:60px;height:60px;border-radius:16px;background:linear-gradient(135deg,var(--gold2),var(--gold));display:flex;align-items:center;justify-content:center;font-size:1.9rem;box-shadow:0 8px 24px rgba(212,175,55,.35);}
.lb-name{font-size:1.9rem;font-weight:800;letter-spacing:.02em;margin-top:22px;line-height:1.15;}
.lb-ur{font-family:'Noto Nastaliq Urdu',serif;color:var(--gold2);font-size:1.3rem;margin-top:10px;line-height:2;}
.lb-tag{color:#9FB2D6;font-size:.95rem;margin-top:4px;}
.lb-feats{margin-top:30px;display:grid;gap:12px;}
.lb-feat{display:flex;gap:12px;align-items:center;color:#DCE6F7;font-size:.93rem;}
.lb-feat i{font-style:normal;width:34px;height:34px;border-radius:10px;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;}
.lb-foot{color:#7F93B8;font-size:.78rem;margin-top:26px;}
.login-title{font-size:1.6rem;font-weight:800;color:var(--ink);margin:6px 0 2px;}
.login-sub{color:var(--muted);margin-bottom:14px;font-size:.92rem;}
@media(max-width:768px){.pg-title{font-size:1.3rem;}.kpi-val{font-size:1.35rem;}.login-brand{min-height:auto;padding:28px;}}
</style>
"""

LOGIN_BG = """<style>.stApp{background:radial-gradient(900px 500px at 100% 0%,#E8EDF8 0%,transparent 60%),#F3F5F9!important;}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"]{display:none!important;}</style>"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "🚛") -> None:
    st.markdown(
        f'<div class="pg-head"><div class="pg-icon">{icon}</div><div><div class="pg-title">{escape(title)}</div>'
        f'<div class="pg-sub">{escape(subtitle)}</div></div></div>', unsafe_allow_html=True)


def section(title: str) -> None:
    st.markdown(f'<div class="sec-title">{escape(title)}</div>', unsafe_allow_html=True)


def kpi_row(items: list[tuple]) -> None:
    """items: (label, value, sub, icon, tone) — tone in gold|green|red|blue|navy"""
    cards = []
    for it in items:
        label, value = it[0], it[1]
        sub = it[2] if len(it) > 2 else ""
        icon = it[3] if len(it) > 3 else ""
        tone = it[4] if len(it) > 4 else "gold"
        cards.append(f'<div class="kpi {tone}"><div class="kpi-top"><span class="kpi-label">{escape(str(label))}</span>'
                     f'<span class="kpi-ico">{icon}</span></div><div class="kpi-val">{escape(str(value))}</div>'
                     f'<div class="kpi-sub">{escape(str(sub))}</div></div>')
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def pill(text: str, tone: str = "info") -> str:
    return f'<span class="pill {tone}">{escape(str(text))}</span>'


def empty_state(message: str, icon: str = "📭") -> None:
    st.markdown(f'<div class="empty"><div class="e-ico">{icon}</div><div class="e-msg">{escape(message)}</div></div>',
                unsafe_allow_html=True)


def alert_rows(rows: list[tuple[str, str, bool]]) -> None:
    """rows: (left text, right text, is_critical)"""
    html = "".join(f'<div class="alert-row {"red" if crit else ""}"><span>{escape(l)}</span><b>{escape(r)}</b></div>'
                   for l, r, crit in rows)
    st.markdown(html, unsafe_allow_html=True)
