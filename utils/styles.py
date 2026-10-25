"""
Premium VIP Styling & Theme for Azad Transport ERP
"""
import streamlit as st


def inject_premium_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp{background:linear-gradient(135deg,#0a0a0a 0%,#1a1a2e 50%,#0a0a0a 100%)!important;font-family:'Inter',sans-serif!important;}
    #MainMenu,footer,header{visibility:hidden;}.stDeployButton{display:none;}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1117,#161b22,#0d1117)!important;border-right:1px solid rgba(212,175,55,.2)!important;}
    [data-testid="stSidebar"] .stMarkdown h1,[data-testid="stSidebar"] .stMarkdown h2,[data-testid="stSidebar"] .stMarkdown h3{color:#D4AF37!important;font-weight:700!important;}
    [data-testid="stSidebar"] .stMarkdown p,[data-testid="stSidebar"] label{color:#c9d1d9!important;}
    [data-testid="stMetric"]{background:linear-gradient(135deg,#161b22,#1c2333)!important;border:1px solid rgba(212,175,55,.15)!important;border-radius:16px!important;padding:20px 24px!important;box-shadow:0 4px 20px rgba(0,0,0,.3)!important;}
    [data-testid="stMetric"]:hover{border-color:rgba(212,175,55,.4)!important;transform:translateY(-2px);}
    [data-testid="stMetricLabel"]{color:#8b949e!important;font-size:.85rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:1px!important;}
    [data-testid="stMetricValue"]{color:#D4AF37!important;font-size:1.8rem!important;font-weight:800!important;}
    .stButton>button{background:linear-gradient(135deg,#D4AF37,#B8960C)!important;color:#0a0a0a!important;border:none!important;border-radius:12px!important;padding:10px 28px!important;font-weight:700!important;box-shadow:0 4px 15px rgba(212,175,55,.3)!important;}
    .stButton>button:hover{background:linear-gradient(135deg,#e6c349,#D4AF37)!important;transform:translateY(-2px)!important;}
    .stTextInput>div>div>input,.stNumberInput>div>div>input,.stDateInput>div>div>input,.stTextArea>div>div>textarea{background:#161b22!important;border:1px solid rgba(212,175,55,.2)!important;border-radius:10px!important;color:#e6edf3!important;padding:12px 16px!important;}
    .stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{border-color:#D4AF37!important;box-shadow:0 0 10px rgba(212,175,55,.2)!important;}
    .stSelectbox>div>div,.stMultiSelect>div>div{background:#161b22!important;border:1px solid rgba(212,175,55,.2)!important;border-radius:10px!important;}
    .stTabs [data-baseweb="tab-list"]{background:rgba(22,27,34,.5)!important;border-radius:12px!important;padding:4px!important;}
    .stTabs [data-baseweb="tab"]{border-radius:10px!important;color:#8b949e!important;font-weight:600!important;}
    .stTabs [aria-selected="true"]{background:rgba(212,175,55,.15)!important;color:#D4AF37!important;}
    [data-testid="stForm"]{background:linear-gradient(135deg,#161b22,#1c2333)!important;border:1px solid rgba(212,175,55,.15)!important;border-radius:16px!important;padding:24px!important;}
    h1{color:#D4AF37!important;font-weight:800!important;}h2{color:#e6edf3!important;font-weight:700!important;}h3{color:#c9d1d9!important;font-weight:600!important;}
    p,li,span{color:#c9d1d9!important;}hr{border-color:rgba(212,175,55,.15)!important;}
    .premium-card{background:linear-gradient(135deg,#161b22,#1c2333);border:1px solid rgba(212,175,55,.15);border-radius:16px;padding:24px;margin:10px 0;box-shadow:0 4px 20px rgba(0,0,0,.3);}
    .premium-card:hover{border-color:rgba(212,175,55,.3);}
    .gold-badge{display:inline-block;background:linear-gradient(135deg,#D4AF37,#B8960C);color:#0a0a0a;padding:4px 14px;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;}
    .status-active{display:inline-block;background:rgba(46,160,67,.15);color:#3fb950;padding:4px 14px;border-radius:20px;font-size:.8rem;font-weight:600;}
    .status-pending{display:inline-block;background:rgba(212,175,55,.15);color:#D4AF37;padding:4px 14px;border-radius:20px;font-size:.8rem;font-weight:600;}
    .status-inactive{display:inline-block;background:rgba(248,81,73,.15);color:#f85149;padding:4px 14px;border-radius:20px;font-size:.8rem;font-weight:600;}
    .stat-number{font-size:2.2rem;font-weight:800;color:#D4AF37;line-height:1.2;}
    .stat-label{font-size:.8rem;color:#8b949e;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;}
    @media(max-width:768px){.stat-number{font-size:1.6rem;}.premium-card{padding:16px;}[data-testid="stMetricValue"]{font-size:1.4rem!important;}}
    @media print{[data-testid="stSidebar"]{display:none!important;}.stApp{background:white!important;}h1,h2,h3,p{color:#000!important;}}
    </style>""", unsafe_allow_html=True)


def premium_header(title, subtitle="", icon="🚛"):
    st.markdown(f"""
    <div style="padding:20px 0 30px 0;">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:8px;">
            <span style="font-size:2.5rem;">{icon}</span>
            <div>
                <h1 style="margin:0;padding:0;font-size:2rem;">{title}</h1>
                <p style="margin:0;padding:0;color:#8b949e;font-size:.95rem;">{subtitle}</p>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def premium_metric_card(label, value, icon="📊"):
    st.markdown(f"""
    <div class="premium-card" style="text-align:center;">
        <div style="font-size:1.8rem;margin-bottom:8px;">{icon}</div>
        <div class="stat-number">{value}</div>
        <div class="stat-label">{label}</div>
    </div>""", unsafe_allow_html=True)


def premium_info_row(label, value):
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05);">
        <span style="color:#8b949e;font-weight:500;font-size:.9rem;">{label}</span>
        <span style="color:#e6edf3;font-weight:600;font-size:.95rem;">{value}</span>
    </div>""", unsafe_allow_html=True)


def status_badge(status):
    s = status.lower()
    if s in ("active","completed","paid","delivered"):
        c = "status-active"
    elif s in ("pending","in_transit","partial"):
        c = "status-pending"
    else:
        c = "status-inactive"
    return f'<span class="{c}">{status}</span>'


def gold_divider():
    st.markdown('<hr style="border:1px solid rgba(212,175,55,.2);margin:30px 0;">', unsafe_allow_html=True)


def empty_state(message, icon="📭"):
    st.markdown(f"""
    <div style="text-align:center;padding:60px 20px;color:#8b949e;">
        <div style="font-size:3rem;margin-bottom:16px;">{icon}</div>
        <p style="font-size:1.1rem;font-weight:500;">{message}</p>
    </div>""", unsafe_allow_html=True)

