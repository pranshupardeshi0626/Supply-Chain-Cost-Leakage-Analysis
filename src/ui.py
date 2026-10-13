"""Small reusable Streamlit components: hero, headers, KPI cards, insight cards, callouts."""
import html

import streamlit as st

from src.config import AMBER, CORAL, GREEN, TEAL
from src.theme import CSS, register_plotly_template

ACCENTS = {"teal": TEAL, "coral": CORAL, "amber": AMBER, "green": GREEN}


def setup():
    """Call once per run: global CSS + the shared Plotly template."""
    register_plotly_template()
    st.markdown(CSS, unsafe_allow_html=True)


def show(fig):
    """Render a Plotly figure full-width. Backgrounds are set on the figure itself because Streamlit
    would otherwise paint the page colour behind the chart."""
    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def table(df, **kwargs):
    st.dataframe(df, hide_index=True, width="stretch", **kwargs)


def hero(kicker, title_html, subtitle, stats):
    """stats = [(value, label), ...] shown as a strip under the headline."""
    cells = "".join(f'<div class="hero-stat"><div class="v">{v}</div><div class="l">{l}</div></div>'
                    for v, l in stats)
    st.markdown(
        f'<div class="hero"><div class="hero-kicker">{kicker}</div>'
        f'<div class="hero-title">{title_html}</div><p class="hero-sub">{subtitle}</p>'
        f'<div class="hero-stats">{cells}</div></div>', unsafe_allow_html=True)


def page_header(title, subtitle=""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="page-head"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def section(title, hint=""):
    tail = f"<p>{hint}</p>" if hint else ""
    st.markdown(f'<div class="sec"><h3>{title}</h3>{tail}</div>', unsafe_allow_html=True)


def note(text, warn=False):
    st.markdown(f'<div class="note{" warn" if warn else ""}">{text}</div>', unsafe_allow_html=True)


def kpi_card(label, value, sub="", accent="teal", tone=""):
    color = ACCENTS.get(accent, accent)
    return (f'<div class="kpi {tone}" style="--accent:{color}"><div class="l">{html.escape(label)}</div>'
            f'<div class="v">{value}</div><div class="s">{html.escape(sub)}</div></div>')


def kpi_row(items):
    """items = [(label, value_text, sub_text, accent, tone), ...]; sub/accent/tone are optional."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value, *rest = item
        col.markdown(kpi_card(label, value, *rest), unsafe_allow_html=True)
    st.write("")


def insight_card(i, number):
    evidence = "".join(f"<li>{e}</li>" for e in i.evidence)
    st.markdown(
        f'<div class="insight"><div class="ihead"><span class="num">{number}</span><h4>{i.title}</h4></div>'
        f'<p class="finding">{i.finding}</p><ul>{evidence}</ul>'
        f'<div class="action">Recommendation: {i.action}</div>'
        f'<div class="caveat">Caveat: {i.caveat}</div></div>', unsafe_allow_html=True)
