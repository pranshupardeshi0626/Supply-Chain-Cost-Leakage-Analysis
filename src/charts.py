"""Plotly figure builders. Each function takes a prepared DataFrame and returns a Figure,
so views stay short and charts are easy to find."""
import plotly.express as px
import plotly.graph_objects as go

from src.config import AMBER, BLUE, NAVY, RED, TEAL

LAYOUT = dict(template="plotly_white", margin=dict(l=10, r=10, t=50, b=10), height=380)


def _style(fig, title):
    fig.update_layout(title=title, **LAYOUT)
    return fig


def line_trend(monthly, y, title, y_title, as_pct=True):
    fig = px.line(monthly, x="year_month", y=y, markers=True, color_discrete_sequence=[BLUE])
    fig.update_yaxes(title=y_title, tickformat=".1%" if as_pct else None)
    fig.update_xaxes(title=None)
    return _style(fig, title)


def otif_breakdown(kpis):
    labels = ["On-time", "In-full", "OTIF (both)"]
    vals = [kpis["on_time"], kpis["in_full"], kpis["otif"]]
    fig = go.Figure(go.Bar(x=labels, y=vals, marker_color=[BLUE, TEAL, NAVY],
                           text=[f"{v:.1%}" for v in vals], textposition="outside"))
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
    return _style(fig, "Delivery performance")


def cost_split(kpis):
    fig = go.Figure(go.Pie(labels=["Transport", "Holding"],
                           values=[kpis["transport_cost"], kpis["holding_cost"]],
                           hole=0.55, marker_colors=[BLUE, AMBER]))
    return _style(fig, "What the supply-chain cost is made of")


def bar_by(df, x, y, title, y_title, as_pct=True, color=BLUE, sort=False):
    data = df.sort_values(y) if sort else df
    fig = px.bar(data, x=x, y=y, color_discrete_sequence=[color],
                 text=data[y].map(lambda v: f"{v:.1%}" if as_pct else f"{v:,.0f}"))
    fig.update_yaxes(title=y_title, tickformat=".0%" if as_pct else None)
    fig.update_xaxes(title=None)
    fig.update_traces(textposition="outside")
    return _style(fig, title)


def supplier_scatter(sc):
    fig = px.scatter(sc, x="reliability", y="otif", size="orders", color="at_risk",
                     hover_name="supplier_id", color_discrete_map={True: RED, False: BLUE},
                     labels={"reliability": "Reliability score", "otif": "OTIF", "at_risk": "At risk"})
    fig.update_yaxes(tickformat=".0%")
    return _style(fig, "Supplier reliability score vs actual OTIF")


def pareto(breakdown):
    fig = go.Figure()
    fig.add_bar(x=breakdown["rejection_reason"], y=breakdown["orders"], marker_color=BLUE, name="Orders")
    fig.add_scatter(x=breakdown["rejection_reason"], y=breakdown["cum_share"], yaxis="y2",
                    mode="lines+markers", line=dict(color=RED), name="Cumulative %")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", tickformat=".0%", range=[0, 1.05]),
                      legend=dict(orientation="h", y=-0.15))
    return _style(fig, "Why orders are rejected (Pareto)")


def correlation_bar(corr):
    data = corr.reset_index()
    data.columns = ["driver", "correlation"]
    fig = px.bar(data, x="correlation", y="driver", orientation="h", color_discrete_sequence=[NAVY])
    fig.update_yaxes(autorange="reversed", title=None)
    return _style(fig, "Correlation with total supply-chain cost")


def heatmap(pivot, title, fmt=".0%"):
    fig = px.imshow(pivot, text_auto=fmt, aspect="auto", color_continuous_scale="RdYlGn")
    return _style(fig, title)


def histogram(df, col):
    return _style(px.histogram(df, x=col, nbins=50, color_discrete_sequence=[BLUE]), f"Distribution of {col}")


def box(df, x, y):
    return _style(px.box(df, x=x, y=y, color_discrete_sequence=[BLUE]), f"{y} by {x}")


def scatter(df, x, y, color=None):
    return _style(px.scatter(df, x=x, y=y, color=color, opacity=0.5), f"{y} vs {x}")
