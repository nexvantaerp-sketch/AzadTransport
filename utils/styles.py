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

/* ---------- sidebar (always navy, always readable) ---------- */
[data-testid="stSidebar"],[data-testid="stSidebar"]>div:first-child{background:linear-gradient(180deg,#0B1B3A 0%,#0E2247 55%,#0B1B3A 100%)!important;}
[data-testid="stSidebar"]{border-right:1px solid #1E3A6B;box-shadow:4px 0 24px rgba(11,27,58,.18);}
[data-testid="stSidebar"] *{color:#E2E8F0;}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"]{padding-bottom:.4rem;}
[data-testid="stSidebar"] [data-testid="stSidebarNav"]{padding-top:.2rem;}
[data-testid="stSidebar"] [data-testid="stSidebarNavItems"]{gap:0!important;}
[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] ul{gap:0!important;}
[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],[data-testid="stSidebar"] [data-testid="stNavSectionHeader"]{margin-top:.5rem!important;padding-top:.3rem!important;padding-bottom:.1rem!important;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]{padding:.38rem .75rem!important;min-height:0!important;}
[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li{margin:0!important;}
[data-testid="stSidebar"] [data-testid="stSidebarNav"]{padding-bottom:9.5rem!important;}
/* user card + Sign out: hamesha neeche chipka rahe, scroll karne ki zaroorat nahi */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{position:sticky;bottom:0;z-index:20;padding:.6rem 1rem 1rem!important;background:linear-gradient(180deg,rgba(11,27,58,0) 0,#0B1B3A 18%);}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]{border-radius:10px;margin:2px 8px;padding:.5rem .75rem;font-weight:500;color:#CBD5E1!important;transition:background .15s,color .15s;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] span,[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] p{color:inherit!important;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover{background:rgba(255,255,255,.09);color:#fff!important;}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"]{background:linear-gradient(90deg,rgba(231,198,90,.28),rgba(231,198,90,.05));
box-shadow:inset 3px 0 0 var(--gold2);color:#fff!important;font-weight:700;}
[data-testid="stSidebar"] [data-testid="stNavSectionHeader"],[data-testid="stSidebar"] [data-testid="stSidebarNav"] span[data-testid="stHeader"]{
color:#8FA3C8!important;font-size:.68rem!important;letter-spacing:.14em;text-transform:uppercase;font-weight:700;}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] *{color:#CBD5E1!important;}
[data-testid="stSidebarCollapsedControl"] button,[data-testid="stExpandSidebarButton"]{color:var(--navy)!important;}
.side-user{display:flex;gap:10px;align-items:center;padding:12px;border-radius:14px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);margin:6px 4px 10px;}
.side-avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,var(--gold2),var(--gold));color:var(--navy)!important;display:flex;align-items:center;justify-content:center;font-weight:800;box-shadow:0 4px 12px rgba(0,0,0,.3);}
.side-name{color:#FFFFFF!important;font-weight:700;font-size:.92rem;line-height:1.2;}.side-role{color:#A9BAD9!important;font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;margin-top:2px;}
/* Sign out button — hamesha clearly visible */
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.10)!important;color:#FFFFFF!important;border:1px solid rgba(255,255,255,.28)!important;font-weight:600;}
[data-testid="stSidebar"] .stButton>button *{color:#FFFFFF!important;fill:#FFFFFF!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(220,38,38,.9)!important;border-color:#F87171!important;transform:translateY(-1px);box-shadow:0 6px 16px rgba(220,38,38,.35);}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.12);}

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
/* ---------- global readability (text, bullets, lists) ---------- */
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--ink);}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,[data-testid="stMain"] h4,[data-testid="stMain"] h5{color:var(--navy)!important;font-weight:800;letter-spacing:-.01em;}
[data-testid="stMain"] p,[data-testid="stMain"] li,[data-testid="stMain"] span,[data-testid="stMain"] label,[data-testid="stMain"] td{color:inherit;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,[data-testid="stMain"] [data-testid="stMarkdownContainer"] li{color:var(--ink);line-height:1.6;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] ul,[data-testid="stMain"] [data-testid="stMarkdownContainer"] ol{padding-left:1.3rem;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li::marker{color:var(--gold);font-weight:700;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] code{background:#EEF2F8;color:#0B1B3A;border-radius:6px;padding:1px 6px;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] *{color:#475569!important;opacity:1!important;}
label[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] *{color:#1E293B!important;}
.pg-title{color:var(--navy)!important;}.pg-sub{color:#475569!important;}
.sec-title{color:var(--navy)!important;}

/* ---------- premium surfaces ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]){background:var(--card);border-color:var(--line)!important;box-shadow:0 1px 2px rgba(15,23,42,.04),0 8px 24px rgba(15,23,42,.05);}
.kpi{transition:transform .15s,box-shadow .15s;}.kpi:hover{transform:translateY(-2px);box-shadow:0 2px 4px rgba(15,23,42,.05),0 12px 28px rgba(15,23,42,.10);}
.kpi-label{color:#475569!important;}.kpi-val{color:var(--navy)!important;}.kpi-sub{color:#64748B!important;}
.pg-head{padding:14px 18px;background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:0 1px 2px rgba(15,23,42,.04),0 8px 24px rgba(15,23,42,.05);}
.pg-icon{flex:none;}

/* ---------- inputs: white box, dark text, visible border ---------- */
.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea,.stTimeInput input{background:#fff!important;color:var(--ink)!important;border:1px solid #CBD5E1!important;}
.stTextInput input::placeholder,.stTextArea textarea::placeholder,.stNumberInput input::placeholder{color:#94A3B8!important;}
[data-baseweb="select"]>div{background:#fff!important;color:var(--ink)!important;border:1px solid #CBD5E1!important;}
[data-baseweb="select"] *{color:var(--ink);}
[data-baseweb="popover"] [role="listbox"],[data-baseweb="popover"] ul{background:#fff!important;}
[data-baseweb="popover"] li,[data-baseweb="popover"] [role="option"]{color:var(--ink)!important;}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] [aria-selected="true"]{background:#EEF2F8!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stDateInput input:focus,.stTextArea textarea:focus{border-color:var(--gold)!important;box-shadow:0 0 0 3px rgba(201,162,39,.22)!important;}
[data-baseweb="select"]>div:focus-within{border-color:var(--gold)!important;box-shadow:0 0 0 3px rgba(201,162,39,.22)!important;}
.stCheckbox label,.stRadio label,.stToggle label{color:var(--ink)!important;}
.stRadio [role="radiogroup"] label p,.stCheckbox label p,.stToggle label p{color:var(--ink)!important;}

/* ---------- buttons ---------- */
.stButton>button:not([data-testid="stBaseButton-primary"]),.stDownloadButton>button{background:#fff;color:var(--navy);border:1px solid #CBD5E1;}
.stButton>button:not([data-testid="stBaseButton-primary"]):hover,.stDownloadButton>button:hover{border-color:var(--gold);color:var(--navy);background:#FFFBEB;}
.stButton>button[data-testid="stBaseButton-primary"] *,[data-testid="stFormSubmitButton"]>button[kind="primaryFormSubmit"] *{color:#fff!important;}
[data-testid="stSidebar"] .stButton>button:not([data-testid="stBaseButton-primary"]){background:rgba(255,255,255,.10)!important;color:#fff!important;}

/* ---------- tabs / segmented / expander ---------- */
.stTabs [data-baseweb="tab"]{color:#475569;}.stTabs [data-baseweb="tab"]:hover{color:var(--navy);background:rgba(11,27,58,.04);}
.stTabs [aria-selected="true"],.stTabs [aria-selected="true"] *{color:var(--navy)!important;font-weight:700;}
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--line)!important;border-radius:14px!important;}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary *{color:var(--navy)!important;font-weight:600;}
[data-testid="stSegmentedControl"] button{color:#334155;}

/* ---------- metrics, tables, alert boxes ---------- */
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] *{color:#475569!important;}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] *{color:var(--navy)!important;font-weight:800;}
[data-testid="stDataFrame"]{background:#fff;box-shadow:0 1px 2px rgba(15,23,42,.04),0 6px 18px rgba(15,23,42,.05);}
[data-testid="stAlert"]{border-radius:12px;border:1px solid transparent;}
[data-testid="stAlert"] *{color:inherit;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]){background:#EFF6FF;color:#1E3A8A;border-color:#BFDBFE;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]){background:#F0FDF4;color:#14532D;border-color:#BBF7D0;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]){background:#FFFBEB;color:#78350F;border-color:#FDE68A;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]){background:#FEF2F2;color:#7F1D1D;border-color:#FECACA;}
[data-testid="stToast"],[data-testid="stToast"] *{color:#0F172A!important;}
[data-testid="stDialog"] [role="dialog"]{background:#fff;color:var(--ink);border-radius:18px;}
[data-testid="stDialog"] h1,[data-testid="stDialog"] h2,[data-testid="stDialog"] h3{color:var(--navy)!important;}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:8px}::-webkit-scrollbar-thumb:hover{background:#94A3B8}
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
