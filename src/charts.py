"""Plotly figure builders. Each function takes a prepared DataFrame and returns a Figure,
so views stay short and charts are easy to find. Styling comes from the shared template."""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import AMBER, AQUA, CORAL, GREEN, INDIGO, INK, SLATE, TEAL
from src.theme import DIVERGING, SEQUENTIAL

H = 360


def _finish(fig, title, height=H):
    fig.update_layout(title=title, height=height)
    return fig


def _label(v, as_pct):
    return f"{v:.1%}" if as_pct else f"{v:,.0f}"


# ---------- trends -------------------------------------------------------------
def line_trend(monthly, y, title, y_title, as_pct=True, color=TEAL):
    """Monthly line with a soft fill and a dashed average line."""
    fig = go.Figure()
    fig.add_scatter(x=monthly["year_month"], y=monthly[y], mode="lines+markers", name=y_title,
                    line=dict(color=color, width=3), marker=dict(size=6, color=color),
                    fill="tozeroy", fillcolor="rgba(11,114,133,0.08)",
                    hovertemplate="%{x|%b %Y}<br>%{y:" + (".1%" if as_pct else ",.0f") + "}<extra></extra>")
    avg = monthly[y].mean()
    fig.add_hline(y=avg, line_dash="dash", line_color=SLATE, line_width=1,
                  annotation_text=f"avg {_label(avg, as_pct)}", annotation_position="top right",
                  annotation_font=dict(size=11, color=SLATE))
    lo, hi = monthly[y].min(), monthly[y].max()
    pad = (hi - lo) * 0.6 or hi * 0.05
    fig.update_yaxes(title=y_title, tickformat=".1%" if as_pct else None, range=[max(lo - pad, 0), hi + pad])
    fig.update_xaxes(title=None)
    fig.update_layout(showlegend=False)
    return _finish(fig, title)


def delivery_breakdown(kpis):
    """Horizontal bars: on-time, in-full, and the combined OTIF that sits below both."""
    labels = ["OTIF (both)", "In-full", "On-time"]
    vals = [kpis["otif"], kpis["in_full"], kpis["on_time"]]
    fig = go.Figure(go.Bar(y=labels, x=vals, orientation="h", marker_color=[CORAL, TEAL, AQUA],
                           text=[f"{v:.1%}" for v in vals], textposition="outside", cliponaxis=False))
    fig.update_xaxes(range=[0, 1.12], tickformat=".0%", showgrid=True, gridcolor="#E8EEF3")
    fig.update_yaxes(showgrid=False)
    return _finish(fig, "Delivery performance")


def cost_split(kpis):
    total = kpis["transport_cost"] + kpis["holding_cost"]
    fig = go.Figure(go.Pie(labels=["Transport", "Holding"],
                           values=[kpis["transport_cost"], kpis["holding_cost"]], hole=0.62,
                           marker=dict(colors=[TEAL, AMBER], line=dict(color="#fff", width=3)),
                           textinfo="percent", textfont=dict(size=13, color="#fff"), sort=False))
    fig.add_annotation(text=f"<b>₹{total / 1e7:,.0f} Cr</b><br><span style='font-size:11px;color:#64748B'>"
                            "total cost</span>", showarrow=False, font=dict(size=18, color=INK))
    fig.update_layout(legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"))
    return _finish(fig, "What the cost is made of")


# ---------- category comparisons --------------------------------------------------
def bar_by(df, x, y, title, y_title, as_pct=True, color=TEAL, sort=False, highlight=None):
    """Vertical bars with value labels. highlight='max'/'min' paints that bar coral."""
    data = df.sort_values(y, ascending=False) if sort else df
    colors = [color] * len(data)
    if highlight:
        idx = int(np.argmax(data[y].values) if highlight == "max" else np.argmin(data[y].values))
        colors[idx] = CORAL
    fig = go.Figure(go.Bar(x=data[x], y=data[y], marker_color=colors,
                           text=[_label(v, as_pct) for v in data[y]], textposition="outside",
                           cliponaxis=False))
    top = data[y].max()
    fig.update_yaxes(title=y_title, tickformat=".0%" if as_pct else None, range=[0, top * 1.25])
    fig.update_xaxes(title=None)
    return _finish(fig, title)


def bar_h(df, x, y, title, as_pct=True, color=TEAL, highlight=None):
    """Horizontal ranked bars (best for long category names)."""
    data = df.sort_values(x, ascending=True)
    colors = [color] * len(data)
    if highlight == "max":
        colors[-1] = CORAL
    elif highlight == "min":
        colors[0] = CORAL
    fig = go.Figure(go.Bar(x=data[x], y=data[y], orientation="h", marker_color=colors,
                           text=[_label(v, as_pct) for v in data[x]], textposition="outside",
                           cliponaxis=False))
    fig.update_xaxes(tickformat=".0%" if as_pct else None, showgrid=True, gridcolor="#E8EEF3",
                     range=[0, data[x].max() * 1.18])
    fig.update_yaxes(title=None, showgrid=False)
    return _finish(fig, title)


def stacked_cost(df, category, title):
    """Transport vs holding cost as a share of order value, per category."""
    data = df.assign(transport_pct=df["transport_cost"] / df["order_value"],
                     holding_pct=df["holding_cost"] / df["order_value"]).sort_values("cost_pct")
    fig = go.Figure()
    fig.add_bar(y=data[category], x=data["transport_pct"], orientation="h", name="Transport", marker_color=TEAL,
                text=[f"{v:.2%}" for v in data["transport_pct"]], textposition="inside",
                textfont=dict(color="#fff"))
    fig.add_bar(y=data[category], x=data["holding_pct"], orientation="h", name="Holding", marker_color=AMBER,
                text=[f"{v:.2%}" for v in data["holding_pct"]], textposition="inside",
                textfont=dict(color="#fff"))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(tickformat=".1%", showgrid=True, gridcolor="#E8EEF3", title="Cost as % of order value")
    fig.update_yaxes(title=None, showgrid=False)
    return _finish(fig, title)


def grouped_bars(df, x, series, title, names, colors, as_pct=True):
    """Side-by-side bars for several metrics of the same categories."""
    fig = go.Figure()
    for col, name, color in zip(series, names, colors):
        fig.add_bar(x=df[x], y=df[col], name=name, marker_color=color,
                    text=[_label(v, as_pct) for v in df[col]], textposition="outside", cliponaxis=False)
    fig.update_layout(barmode="group")
    top = max(df[c].max() for c in series)
    fig.update_yaxes(tickformat=".0%" if as_pct else None, range=[0, top * 1.28])
    fig.update_xaxes(title=None)
    return _finish(fig, title)


# ---------- suppliers ------------------------------------------------------------
def supplier_scatter(sc):
    sc = sc.assign(status=sc["at_risk"].map({True: "At risk", False: "On track"}))
    fig = px.scatter(sc, x="reliability", y="otif", size="orders", color="status", hover_name="supplier_id",
                     color_discrete_map={"At risk": CORAL, "On track": TEAL}, size_max=17,
                     category_orders={"status": ["On track", "At risk"]},
                     labels={"reliability": "Reliability score", "otif": "OTIF", "status": ""})
    fig.update_traces(marker=dict(line=dict(color="#fff", width=1.5), opacity=0.9))
    fig.update_yaxes(tickformat=".0%")
    return _finish(fig, "Supplier reliability score vs actual OTIF")


def pareto(breakdown):
    fig = go.Figure()
    fig.add_bar(x=breakdown["rejection_reason"], y=breakdown["orders"], marker_color=TEAL, name="Rejected orders",
                text=[f"{v:,}" for v in breakdown["orders"]], textposition="outside", cliponaxis=False)
    fig.add_scatter(x=breakdown["rejection_reason"], y=breakdown["cum_share"], yaxis="y2", mode="lines+markers",
                    line=dict(color=CORAL, width=3), marker=dict(size=8), name="Cumulative share")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", tickformat=".0%", range=[0, 1.05],
                                  dtick=0.25, showgrid=False))
    fig.update_yaxes(range=[0, breakdown["orders"].max() * 1.2], selector=dict(title=None))
    return _finish(fig, "Why orders are rejected (Pareto)")


# ---------- statistics / EDA -------------------------------------------------------
def correlation_bar(corr):
    data = corr.reset_index()
    data.columns = ["driver", "correlation"]
    data = data.sort_values("correlation")
    colors = [CORAL if v < 0 else TEAL for v in data["correlation"]]
    fig = go.Figure(go.Bar(x=data["correlation"], y=data["driver"], orientation="h", marker_color=colors,
                           text=[f"{v:+.2f}" for v in data["correlation"]], textposition="outside",
                           cliponaxis=False))
    fig.update_xaxes(range=[min(-0.1, data["correlation"].min() * 1.25), max(0.1, data["correlation"].max() * 1.25)],
                     showgrid=True, gridcolor="#E8EEF3", zeroline=True, zerolinecolor="#94A3B8")
    fig.update_yaxes(title=None, showgrid=False)
    return _finish(fig, "Correlation with total supply-chain cost")


def heatmap(pivot, title, fmt=".0%", diverging=False, height=H):
    scale = DIVERGING if diverging else SEQUENTIAL
    kwargs = dict(zmin=-1, zmax=1) if diverging else {}
    fig = px.imshow(pivot, text_auto=fmt, aspect="auto", color_continuous_scale=scale, **kwargs)
    fig.update_xaxes(title=None, side="bottom", showgrid=False)
    fig.update_yaxes(title=None, showgrid=False)
    fig.update_traces(xgap=3, ygap=3)
    if not diverging and fmt.endswith('%'):
        fig.update_coloraxes(colorbar_tickformat='.0%')
    return _finish(fig, title, height)


def histogram(df, col, color=TEAL):
    """Histogram with a box plot on top, plus mean / median markers."""
    fig = px.histogram(df, x=col, nbins=50, marginal="box", color_discrete_sequence=[color])
    fig.update_traces(marker_line_color="#fff", marker_line_width=0.5, selector=dict(type="histogram"))
    fig.add_vline(x=df[col].mean(), line_dash="dash", line_color=CORAL, line_width=2,
                  annotation_text="mean", annotation_font=dict(color=CORAL, size=11), row=1, col=1)
    fig.add_vline(x=df[col].median(), line_dash="dot", line_color=INK, line_width=2,
                  annotation_text="median", annotation_position="bottom right",
                  annotation_font=dict(color=INK, size=11), row=1, col=1)
    fig.update_yaxes(title="Orders", row=1, col=1)
    fig.update_xaxes(title=col, row=1, col=1)
    fig.update_xaxes(title=None, row=2, col=1)
    return _finish(fig, f"Distribution of {col}", 440)


def category_counts(summary, col):
    fig = go.Figure(go.Bar(x=summary[col], y=summary["Orders"], marker_color=TEAL,
                           text=[f"{s:.1%}" for s in summary["Share"]], textposition="outside",
                           cliponaxis=False))
    fig.update_yaxes(title="Orders", range=[0, summary["Orders"].max() * 1.15])
    fig.update_xaxes(title=None)
    return _finish(fig, f"Orders by {col}")


def box(df, x, y):
    order = df.groupby(x)[y].median().sort_values(ascending=False).index.tolist()
    fig = px.box(df, x=x, y=y, color=x, category_orders={x: order}, points=False)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title=None)
    return _finish(fig, f"{y} by {x}", 420)


def scatter(df, x, y, color=None):
    """Scatter of a sample plus a least-squares trend line."""
    fig = px.scatter(df, x=x, y=y, color=color, opacity=0.45, color_discrete_sequence=[TEAL, AMBER, INDIGO, CORAL, AQUA])
    fig.update_traces(marker=dict(size=5))
    ok = df[[x, y]].dropna()
    if len(ok) > 2 and ok[x].nunique() > 1:
        slope, intercept = np.polyfit(ok[x], ok[y], 1)
        xs = np.array([ok[x].min(), ok[x].max()])
        fig.add_scatter(x=xs, y=slope * xs + intercept, mode="lines", name="Trend",
                        line=dict(color=CORAL, width=3))
    return _finish(fig, f"{y} vs {x}", 440)


def missing_bar(summary):
    data = summary.sort_values("Missing %")
    fig = go.Figure(go.Bar(x=data["Missing %"], y=data["Column"], orientation="h", marker_color=AMBER,
                           text=[f"{v:.1%}" for v in data["Missing %"]], textposition="outside", cliponaxis=False))
    fig.update_xaxes(tickformat=".0%", range=[0, 1.1], showgrid=True, gridcolor="#E8EEF3")
    fig.update_yaxes(title=None, showgrid=False)
    return _finish(fig, "Blank cells by column", 200)


def outlier_bar(table):
    data = table.sort_values("outlier_pct")
    fig = go.Figure(go.Bar(x=data["outlier_pct"], y=data["Column"], orientation="h", marker_color=INDIGO,
                           text=[f"{v:.1%}" for v in data["outlier_pct"]], textposition="outside",
                           cliponaxis=False))
    fig.update_xaxes(tickformat=".0%", showgrid=True, gridcolor="#E8EEF3", range=[0, max(data["outlier_pct"].max() * 1.25, 0.01)])
    fig.update_yaxes(title=None, showgrid=False)
    return _finish(fig, "Share of values outside the 1.5 x IQR fences", 440)
