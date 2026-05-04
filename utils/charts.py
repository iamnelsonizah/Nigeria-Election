"""Shared chart utilities and color constants."""

import plotly.graph_objects as go
import plotly.express as px

# ── Party Colours ────────────────────────────────────────────────────────────
PARTY_COLORS = {
    "APC":   "#2ecc71",
    "PDP":   "#e74c3c",
    "LP":    "#f39c12",
    "NNPP":  "#3498db",
    "ACN":   "#9b59b6",
    "CPC":   "#1abc9c",
    "ANPP":  "#e67e22",
    "APGA":  "#e91e63",
    "Others":"#95a5a6",
}

ZONE_COLORS = {
    "North West":  "#3498db",
    "North East":  "#2980b9",
    "North Central":"#1abc9c",
    "South West":  "#2ecc71",
    "South East":  "#f39c12",
    "South South": "#e74c3c",
}

DARK_TEMPLATE = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#111827",
    font=dict(color="#c9d8e8", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#1e2a3a", linecolor="#2d3f55", zerolinecolor="#2d3f55"),
    yaxis=dict(gridcolor="#1e2a3a", linecolor="#2d3f55", zerolinecolor="#2d3f55"),
    legend=dict(bgcolor="#111827", bordercolor="#2d3f55", borderwidth=1),
    margin=dict(l=40, r=20, t=50, b=40),
)


def apply_dark(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#e8f4fd"), x=0),
        height=height,
        **DARK_TEMPLATE,
    )
    return fig


def bar_chart(df, x, y, color_col=None, title="", color_map=None, height=400):
    color_map = color_map or PARTY_COLORS
    fig = px.bar(
        df, x=x, y=y,
        color=color_col,
        color_discrete_map=color_map,
        barmode="group",
    )
    fig.update_traces(marker_line_width=0)
    return apply_dark(fig, title, height)


def pie_chart(labels, values, title="", colors=None, height=380):
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors or [PARTY_COLORS.get(l, "#95a5a6") for l in labels],
                    line=dict(color="#0d1117", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#e8f4fd"),
        hovertemplate="<b>%{label}</b><br>Votes: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
    ))
    return apply_dark(fig, title, height)


def line_chart(df, x, y_cols, title="", height=380, names=None):
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        name = (names or y_cols)[i]
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], mode="lines+markers", name=name,
            line=dict(color=PARTY_COLORS.get(name, "#60a5fa"), width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x}}<br>Value: %{{y:,.0f}}<extra></extra>",
        ))
    return apply_dark(fig, title, height)


def stacked_bar(df, x, parties, title="", height=400):
    fig = go.Figure()
    for p in parties:
        if p in df.columns:
            fig.add_trace(go.Bar(
                name=p, x=df[x], y=df[p],
                marker_color=PARTY_COLORS.get(p, "#95a5a6"),
                hovertemplate=f"<b>{p}</b><br>%{{x}}<br>Votes: %{{y:,.0f}}<extra></extra>",
            ))
    fig.update_layout(barmode="stack")
    return apply_dark(fig, title, height)


def gauge(value, title, suffix="%", max_val=100, color="#60a5fa"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=suffix, font=dict(size=28, color="#e8f4fd")),
        title=dict(text=title, font=dict(size=13, color="#8899aa")),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor="#2d3f55"),
            bar=dict(color=color),
            bgcolor="#111827",
            bordercolor="#2d3f55",
            steps=[
                dict(range=[0, max_val * 0.33], color="#1e2a3a"),
                dict(range=[max_val * 0.33, max_val * 0.66], color="#162032"),
                dict(range=[max_val * 0.66, max_val], color="#0f1a28"),
            ],
        ),
    ))
    fig.update_layout(paper_bgcolor="#0d1117", height=220,
                      margin=dict(l=20, r=20, t=40, b=10))
    return fig
