"""Small reusable Streamlit components."""
import streamlit as st

from src.styles import CSS


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def banner(title, subtitle=""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="banner"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def kpi_row(items):
    """items = [(label, value_text, help_text_or_None), ...]"""
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def insight_card(i):
    evidence = "".join(f"<li>{e}</li>" for e in i.evidence)
    st.markdown(
        f'<div class="card"><h4>{i.title}</h4><p>{i.finding}</p><ul>{evidence}</ul>'
        f'<p class="action">Recommendation: {i.action}</p>'
        f'<p class="caveat">Caveat: {i.caveat}</p></div>', unsafe_allow_html=True)
