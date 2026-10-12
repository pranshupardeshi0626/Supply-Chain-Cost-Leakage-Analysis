"""Page CSS in one place."""
CSS = """
<style>
.stApp { background-color: #f4f6f9; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1b2a4a 0%,#1e3a5f 60%,#22527a 100%); }
[data-testid="stSidebar"] * { color: #e8f0fe !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #1b2a4a !important; }
[data-testid="stMetric"] { background:#fff; border-top:4px solid #2e86de; border-radius:10px;
    padding:14px 16px; box-shadow:0 2px 12px rgba(46,134,222,.12); }
[data-testid="stMetricLabel"] { color:#6b7280 !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#1b2a4a !important; font-weight:800; }
.banner { background:linear-gradient(135deg,#1b2a4a 0%,#2e86de 60%,#1abc9c 100%);
    border-radius:14px; padding:26px 36px; margin-bottom:22px; }
.banner h1 { color:#fff !important; margin:0; font-size:2rem; }
.banner p { color:#d0e8ff !important; margin:6px 0 0 0; }
.card { background:#fff; border:1px solid #e5e7eb; border-left:5px solid #2e86de; border-radius:12px;
    padding:16px 22px; margin-bottom:14px; box-shadow:0 2px 10px rgba(0,0,0,.05); }
.card h4 { color:#1b2a4a !important; margin:0 0 6px 0; }
.card p, .card li { color:#374151 !important; margin:2px 0; }
.card .action { color:#0b6e4f !important; font-weight:600; }
.card .caveat { color:#8a6d1d !important; font-size:.85rem; }
.section-title { font-size:1.1rem; font-weight:700; color:#1b2a4a; border-left:4px solid #2e86de;
    padding-left:10px; margin:22px 0 10px 0; }
</style>
"""
