"""
🇳🇬 Nigeria Election Analytics Dashboard
Main entry point — Streamlit multi-page app
"""

import streamlit as st

st.set_page_config(
    page_title="Nigeria Election Analytics",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .main { background-color: #0d1117; }
    .stApp { background-color: #0d1117; }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2a3a, #162032);
        border: 1px solid #2d3f55;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label { color: #8899aa !important; font-size: 0.8rem; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #e8f4fd !important; font-size: 1.6rem; font-weight: 700;
    }

    h1 { color: #e8f4fd !important; font-weight: 800; }
    h2 { color: #c9d8e8 !important; font-weight: 600; }
    h3 { color: #a8bfd0 !important; }

    .stTabs [data-baseweb="tab-list"] {
        background: #111827; border-radius: 10px; padding: 4px; gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 8px;
        color: #8899aa; padding: 8px 20px; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #1f4068 !important; color: #60a5fa !important;
    }
    hr { border-color: #1e2a3a; }
    div[data-testid="stExpander"] {
        background: #111827; border: 1px solid #1e2a3a; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇳🇬 Nigeria Elections")
    st.markdown("**Analytics Dashboard**")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏠  Overview",
            "🗳️  Presidential Results",
            "📊  Vote Share & Trends",
            "🗺️  Regional Analysis",
            "👥  Voter Turnout",
            "🏛️  National Assembly",
            "🏙️  Governorship",
            "🔍  Anomaly Detector",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#556677; line-height:1.8'>
    📌 <b style='color:#7799bb'>Data Sources</b><br>
    • INEC Official Results Portal<br>
    • IFES Election Guide<br>
    • Dataphyte Elections DB<br>
    • IPU Parline Data<br><br>
    📅 <b style='color:#7799bb'>Coverage:</b> 2011–2023<br>
    🔄 <b style='color:#7799bb'>Elections:</b> Presidential,
    Senate, House, Governorship
    </div>
    """, unsafe_allow_html=True)

# ── Page Routing ─────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

if page == "🏠  Overview":
    from pages.overview import show
    show()
elif page == "🗳️  Presidential Results":
    from pages.presidential import show
    show()
elif page == "📊  Vote Share & Trends":
    from pages.trends import show
    show()
elif page == "🗺️  Regional Analysis":
    from pages.regional import show
    show()
elif page == "👥  Voter Turnout":
    from pages.turnout import show
    show()
elif page == "🏛️  National Assembly":
    from pages.assembly import show
    show()
elif page == "🏙️  Governorship":
    from pages.governorship import show
    show()
elif page == "🔍  Anomaly Detector":
    from pages.anomaly import show
    show()
