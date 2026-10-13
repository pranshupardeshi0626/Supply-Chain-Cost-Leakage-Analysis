"""Visual identity: CSS for the page chrome and one Plotly template shared by every chart."""
import plotly.graph_objects as go
import plotly.io as pio

from src.config import AMBER, AQUA, CORAL, GREEN, INDIGO, INK, SLATE, TEAL

FONT = "Manrope, 'Segoe UI', system-ui, -apple-system, sans-serif"
COLORWAY = [TEAL, AMBER, INDIGO, CORAL, AQUA, SLATE]

# Diverging scale used by heatmaps: coral (bad / negative) -> white -> teal (good / positive)
DIVERGING = [[0.0, CORAL], [0.5, "#F7F9FB"], [1.0, TEAL]]
SEQUENTIAL = [[0.0, "#E6F4F6"], [0.5, "#5FB4C0"], [1.0, "#0B4F5C"]]


def register_plotly_template():
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family=FONT, size=13, color="#2B3B4D"),
        colorway=COLORWAY,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        title=dict(font=dict(size=16, color="#14283A"), x=0.0, xanchor="left", y=0.96, pad=dict(l=14, t=8)),
        margin=dict(l=22, r=26, t=62, b=18),
        xaxis=dict(automargin=True, showgrid=False, linecolor="#D5DEE7", ticks="outside", tickcolor="#D5DEE7",
                   zeroline=False, title_font=dict(size=12, color="#64748B")),
        yaxis=dict(automargin=True, gridcolor="#E8EEF3", zeroline=False, linecolor="rgba(0,0,0,0)",
                   title_font=dict(size=12, color="#64748B")),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1.0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hoverlabel=dict(bgcolor=INK, font=dict(family=FONT, size=12, color="#FFFFFF"), bordercolor=INK),
        coloraxis=dict(colorbar=dict(outlinewidth=0, thickness=12)),
    )
    pio.templates["leakage"] = template
    pio.templates.default = "leakage"


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

/* font is applied to text elements only: a blanket rule would break Streamlit's icon font */
.stApp.stApp, .stApp :is(p, h1, h2, h3, h4, h5, label, li, th, td, input, textarea, button),
.hero, .hero *, .kpi, .kpi *, .insight, .insight *, .sec *, .page-head *, .note, .brand *, .side-count,
.side-label {{ font-family: {FONT}; }}
[data-testid="stAppDeployButton"], [data-testid="stToolbar"] {{ display:none; }}
.stApp {{ background: #F1F5F9; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, h4 {{ letter-spacing: -0.01em; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ border-right: 1px solid #1A3550; }}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
.brand {{ display:flex; align-items:center; gap:12px; padding:4px 2px 14px 2px;
    border-bottom:1px solid #223F5B; margin-bottom:14px; }}
.brand-mark {{ width:38px; height:38px; border-radius:10px; flex:none;
    background: linear-gradient(145deg, {TEAL}, {AQUA}); display:flex; align-items:center;
    justify-content:center; font-size:19px; }}
.brand-name {{ font-weight:800; font-size:1.02rem; color:#FFFFFF; line-height:1.15; }}
.brand-sub {{ font-size:.74rem; color:#8FA8BF; font-weight:500; }}
.side-label {{ font-size:.78rem; font-weight:700; color:#8FA8BF; margin:18px 0 6px 2px;
    letter-spacing:.02em; }}
.side-count {{ background:#16304A; border:1px solid #223F5B; border-radius:10px; padding:10px 12px;
    font-size:.82rem; color:#DCE7F0; margin-top:10px; }}
.side-count b {{ color:{AQUA}; font-size:1.05rem; }}

/* navigation radio -> vertical menu */
[data-testid="stSidebar"] [role="radiogroup"] {{ gap:2px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:9px 12px; border-radius:9px; width:100%;
    transition: background .15s; cursor:pointer; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background:#17314A; }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background:#1D3E5E;
    box-shadow: inset 3px 0 0 {AQUA}; }}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display:none; }}
[data-testid="stSidebar"] [role="radiogroup"] label p {{ font-weight:600; font-size:.93rem; }}

/* ---------- hero (overview only) ---------- */
.hero {{ background: radial-gradient(1200px 400px at 85% -20%, #17607A 0%, rgba(23,96,122,0) 60%), {INK};
    border-radius:20px; padding:34px 40px 30px 40px; margin-bottom:24px; color:#fff; }}
.hero-kicker {{ color:{AQUA}; font-weight:700; font-size:.88rem; margin-bottom:10px; }}
.hero-title {{ font-size:2rem; font-weight:800; line-height:1.15; color:#fff; margin:0 0 6px 0;
    max-width:1000px; }}
.hero-title span {{ color:#FF9A76; }}
.hero-sub {{ color:#A9BED1; font-size:1rem; max-width:760px; margin:0 0 24px 0; }}
.hero-stats {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:0; border-top:1px solid #2A4764;
    padding-top:18px; }}
.hero-stat {{ padding-right:18px; }}
.hero-stat + .hero-stat {{ border-left:1px solid #2A4764; padding-left:22px; }}
.hero-stat .v {{ font-size:1.7rem; font-weight:800; color:#fff; }}
.hero-stat .l {{ font-size:.82rem; color:#93AEC5; font-weight:500; }}

/* ---------- page header (other pages) ---------- */
.page-head {{ margin-bottom:22px; padding-bottom:16px; border-bottom:1px solid #DCE5EC; }}
.page-head h1 {{ font-size:1.9rem; font-weight:800; color:#14283A; margin:0; padding:0; }}
.page-head p {{ color:#5F7285; margin:4px 0 0 0; font-size:1rem; }}

/* ---------- section titles ---------- */
.sec {{ display:flex; align-items:baseline; gap:12px; margin:30px 0 12px 0; }}
.sec h3 {{ font-size:1.18rem; font-weight:800; color:#14283A; margin:0; padding:0; }}
.sec p {{ color:#6B7C8E; font-size:.9rem; margin:0; }}

/* ---------- KPI cards ---------- */
.kpi {{ background:#fff; border:1px solid #E1E8EE; border-radius:14px; padding:16px 18px 14px 18px;
    height:100%; position:relative; overflow:hidden; }}
.kpi::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--accent); }}
.kpi .l {{ font-size:.82rem; font-weight:600; color:#64748B; }}
.kpi .v {{ overflow:hidden; text-overflow:ellipsis; font-size:1.6rem; font-weight:800; color:#14283A; line-height:1.25; margin-top:4px; white-space:nowrap; }}
.kpi .s {{ font-size:.78rem; color:#7B8A9A; margin-top:2px; min-height:1.1em; }}
.kpi.bad .v {{ color:{CORAL}; }}
.kpi.good .v {{ color:{GREEN}; }}

/* ---------- chart + table containers ---------- */
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{ background:#fff; border:1px solid #E1E8EE;
    border-radius:14px; padding:0; overflow:hidden; }}
[data-testid="stPlotlyChart"] > div, [data-testid="stPlotlyChart"] .js-plotly-plot {{ background:#fff !important; }}

/* ---------- insight cards ---------- */
.insight {{ background:#fff; border:1px solid #E1E8EE; border-radius:14px; padding:20px 24px 16px 24px;
    margin-bottom:14px; }}
.insight .ihead {{ display:flex; align-items:center; gap:12px; }}
.insight .ihead h4 {{ margin:0; padding:0; }}
.insight .num {{ flex:none; display:inline-flex; width:28px; height:28px; border-radius:50%; background:{TEAL};
    color:#fff; font-weight:800; font-size:.85rem; align-items:center; justify-content:center; }}
.insight h4 {{ font-size:1.08rem; font-weight:800; color:#14283A; }}
.insight .finding {{ color:#2B3B4D; margin:10px 0 8px 0; font-size:.98rem; }}
.insight ul {{ margin:0 0 12px 0; padding-left:20px; color:#4B5C6E; font-size:.9rem; }}
.insight .action {{ background:#E8F6F1; border-radius:10px; padding:9px 14px; color:#16694C;
    font-weight:600; font-size:.9rem; margin-bottom:8px; }}
.insight .caveat {{ color:#8B6B1A; font-size:.82rem; padding-left:2px; }}

/* ---------- callouts ---------- */
.note {{ background:#EAF4F7; border-left:4px solid {TEAL}; border-radius:8px; padding:11px 16px;
    color:#1D4A57; font-size:.9rem; margin:10px 0; }}
.note.warn {{ background:#FDF3E1; border-left-color:{AMBER}; color:#7A5410; }}

/* ---------- tabs ---------- */
[data-baseweb="tab-list"] {{ gap:6px; }}
[data-baseweb="tab"] {{ font-weight:700; }}
</style>
"""
