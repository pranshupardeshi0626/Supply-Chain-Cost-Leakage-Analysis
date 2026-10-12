"""Entry point: page config, data loading, sidebar, routing. Business logic lives in src/."""
import io

import streamlit as st

from src.data_loader import load_csv, load_default, load_excel, validate_schema
from src.filters import sidebar_filters
from src.ui import inject_css
from views import cost_drivers, explorer, key_findings, overview, sql_lab, suppliers

st.set_page_config(page_title="Supply Chain Cost Leakage", layout="wide", page_icon="📦")
inject_css()

# page name -> (render function, does it use the sidebar filters?)
PAGES = {
    "Overview": (overview.render, True),
    "Key Findings": (key_findings.render, False),
    "Supplier Scorecard": (suppliers.render, True),
    "Cost Drivers": (cost_drivers.render, True),
    "Data Explorer": (explorer.render, True),
    "SQL Lab": (sql_lab.render, False),
}


@st.cache_data(show_spinner="Loading 100K orders...")
def get_default_data():
    return load_default()


@st.cache_data(show_spinner="Reading uploaded file...")
def parse_upload(name: str, content: bytes):
    buffer = io.BytesIO(content)
    return load_csv(buffer) if name.lower().endswith(".csv") else load_excel(buffer)


def get_data():
    """Default dataset, or the user's upload if it has the columns we need."""
    uploaded = st.sidebar.file_uploader("Use your own data (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded is not None:
        try:
            df = parse_upload(uploaded.name, uploaded.getvalue())
            missing = validate_schema(df)
            if missing:
                st.sidebar.error("Missing columns: " + ", ".join(missing[:6]) + ("..." if len(missing) > 6 else ""))
            else:
                st.sidebar.success(f"Loaded {uploaded.name}")
                return df
        except Exception as exc:
            st.sidebar.error(f"Could not read file: {exc}")
    return get_default_data()


st.sidebar.title("📦 Supply Chain")
full_df = get_data()
page = st.sidebar.radio("Navigate", list(PAGES))
st.sidebar.markdown("---")
render_page, uses_filters = PAGES[page]

if uses_filters:
    data = sidebar_filters(full_df)
    if data.empty:
        st.warning("No orders match the current filters. Widen the filters in the sidebar.")
        st.stop()
    st.sidebar.caption(f"{len(data):,} of {len(full_df):,} orders selected")
else:
    data = full_df
    st.sidebar.caption("Filters do not apply to this page.")

render_page(data)
