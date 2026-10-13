"""Entry point: page config, data loading, sidebar, routing. Business logic lives in src/."""
import io

import streamlit as st

from src.data_loader import load_csv, load_default, load_excel, validate_schema
from src.filters import sidebar_filters
from src.ui import setup
from views import bivariate, cost_drivers, data_profile, key_findings, overview, suppliers, univariate

st.set_page_config(page_title="Supply Chain Cost Leakage EDA", layout="wide", page_icon="📦")
setup()

# page name -> (render function, does it use the sidebar filters?)
PAGES = {
    "Overview": (overview.render, True),
    "Data Profile": (data_profile.render, False),
    "Univariate": (univariate.render, True),
    "Bivariate & Multivariate": (bivariate.render, True),
    "Cost Drivers": (cost_drivers.render, True),
    "Suppliers": (suppliers.render, True),
    "Key Findings": (key_findings.render, False),
}


@st.cache_data(show_spinner="Loading 100K orders...")
def get_default_data():
    return load_default()


@st.cache_data(show_spinner="Reading uploaded file...")
def parse_upload(name: str, content: bytes):
    buffer = io.BytesIO(content)
    return load_csv(buffer) if name.lower().endswith(".csv") else load_excel(buffer)


def get_data(slot):
    """Default dataset, or the user's upload if it has the columns we need. The uploader is drawn
    inside `slot`, a sidebar container reserved at the bottom of the sidebar."""
    with slot:
        st.markdown('<div class="side-label">Your own data</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("CSV or Excel", type=["csv", "xlsx"], label_visibility="collapsed")
        if uploaded is not None:
            try:
                df = parse_upload(uploaded.name, uploaded.getvalue())
                missing = validate_schema(df)
                if missing:
                    st.error("Missing columns: " + ", ".join(missing[:6]) + ("..." if len(missing) > 6 else ""))
                else:
                    st.success(f"Loaded {uploaded.name}")
                    return df
            except Exception as exc:
                st.error(f"Could not read file: {exc}")
    return get_default_data()


st.sidebar.markdown(
    '<div class="brand"><div class="brand-mark">📦</div><div><div class="brand-name">Cost Leakage EDA</div>'
    '<div class="brand-sub">FMCG supply chain</div></div></div>', unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", list(PAGES), label_visibility="collapsed")
filter_slot = st.sidebar.container()     # filters are drawn here, above the uploader
upload_slot = st.sidebar.container()
full_df = get_data(upload_slot)
render_page, uses_filters = PAGES[page]

with filter_slot:
    if uses_filters:
        data = sidebar_filters(full_df)
        if not data.empty:
            st.markdown(f'<div class="side-count"><b>{len(data):,}</b> of {len(full_df):,} orders selected</div>',
                        unsafe_allow_html=True)
    else:
        data = full_df
        st.markdown('<div class="side-count">Filters do not apply to this page.</div>', unsafe_allow_html=True)

if data.empty:
    st.warning("No orders match the current filters. Widen the filters in the sidebar.")
    st.stop()

render_page(data)
