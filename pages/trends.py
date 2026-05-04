"""Vote Share & Party Trends page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.nigeria_election_data import PRESIDENTIAL_DATA
from utils.charts import PARTY_COLORS, apply_dark


def show():
    st.markdown("# 📊 Vote Share & Party Trends")
    st.markdown("How party dominance has shifted across election cycles.")
    st.markdown("---")

    years = [2011, 2015, 2019, 2023]

    # ── Build long-form party-year data ──────────────────────────────────────
    all_parties = set()
    for y in years:
        all_parties.update(PRESIDENTIAL_DATA[y]["results"].keys())
    all_parties = sorted(all_parties)

    rows = []
    for y in years:
        total = PRESIDENTIAL_DATA[y]["total_votes"]
        res = PRESIDENTIAL_DATA[y]["results"]
        for p in all_parties:
            v = res.get(p, 0)
            rows.append({"Year": y, "Party": p, "Votes": v, "Pct": round(v / total * 100, 2)})
    df = pd.DataFrame(rows)

    # ── Line chart: vote share over time ─────────────────────────────────────
    st.markdown("### 📈 Presidential Vote Share Trend (2011–2023)")
    focus_parties = ["APC", "PDP", "LP", "NNPP"]
    fig = go.Figure()
    for p in focus_parties:
        sub = df[df["Party"] == p]
        if sub["Votes"].sum() == 0:
            continue
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Pct"],
            mode="lines+markers+text",
            name=p,
            text=[f"{v:.1f}%" for v in sub["Pct"]],
            textposition="top center",
            textfont=dict(size=11),
            line=dict(color=PARTY_COLORS.get(p, "#aaa"), width=3),
            marker=dict(size=10),
            hovertemplate=f"<b>{p}</b><br>Year: %{{x}}<br>Vote Share: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(tickvals=years),
        yaxis=dict(title="Vote Share (%)", range=[0, 65]),
        legend=dict(orientation="h", y=-0.15),
    )
    apply_dark(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Absolute votes bar ────────────────────────────────────────────────────
    st.markdown("### 🏛️ Absolute Votes by Party (2011–2023)")
    fig2 = go.Figure()
    for p in focus_parties:
        sub = df[df["Party"] == p]
        fig2.add_trace(go.Bar(
            x=sub["Year"], y=sub["Votes"], name=p,
            marker_color=PARTY_COLORS.get(p, "#aaa"),
            hovertemplate=f"<b>{p}</b><br>Year: %{{x}}<br>Votes: %{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(
        barmode="group",
        xaxis=dict(tickvals=years),
        yaxis=dict(title="Votes"),
    )
    apply_dark(fig2, height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Party comparison metrics ──────────────────────────────────────────────
    st.markdown("### 🔎 Party Performance Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### APC — All Progressives Congress")
        apc = df[df["Party"] == "APC"]
        fig3 = go.Figure(go.Waterfall(
            x=apc["Year"].astype(str),
            y=apc["Votes"].diff().fillna(apc["Votes"].iloc[0]),
            measure=["absolute"] + ["relative"] * (len(apc) - 1),
            connector=dict(line=dict(color="#2d3f55")),
            decreasing=dict(marker_color="#e74c3c"),
            increasing=dict(marker_color="#2ecc71"),
            totals=dict(marker_color="#60a5fa"),
            hovertemplate="<b>%{x}</b><br>Change: %{y:,.0f}<extra></extra>",
        ))
        apply_dark(fig3, "APC Vote Change per Cycle", height=300)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("#### PDP — People's Democratic Party")
        pdp = df[df["Party"] == "PDP"]
        fig4 = go.Figure(go.Waterfall(
            x=pdp["Year"].astype(str),
            y=pdp["Votes"].diff().fillna(pdp["Votes"].iloc[0]),
            measure=["absolute"] + ["relative"] * (len(pdp) - 1),
            connector=dict(line=dict(color="#2d3f55")),
            decreasing=dict(marker_color="#e74c3c"),
            increasing=dict(marker_color="#2ecc71"),
            totals=dict(marker_color="#e74c3c"),
            hovertemplate="<b>%{x}</b><br>Change: %{y:,.0f}<extra></extra>",
        ))
        apply_dark(fig4, "PDP Vote Change per Cycle", height=300)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ── Key insights ──────────────────────────────────────────────────────────
    st.markdown("### 💡 Key Analytical Insights")
    insights = [
        ("🟢 APC Dominance", "APC won 3 consecutive presidential elections (2015, 2019, 2023), though with sharply declining vote counts — from 15.4M (2015) to just 8.8M (2023)."),
        ("🔴 PDP Erosion", "PDP fell from 22.5M votes in 2011 to 7.0M in 2023 — a 69% decline over 12 years, reflecting structural party weakening."),
        ("🟡 LP Emergence", "Labour Party surged from obscurity to 6.1M votes (24.2% share) in 2023, signalling a major third-party breakthrough."),
        ("📉 Turnout Crisis", "Turnout dropped from 53.7% in 2011 to 27.1% in 2023 — the lowest since the return to democracy in 1999, raising serious concerns about voter disenchantment."),
        ("🔵 NNPP Kano Factor", "NNPP's 1.5M votes in 2023 were largely concentrated in Kano State, illustrating how regional strongholds can skew national totals."),
    ]
    for title, body in insights:
        with st.expander(title):
            st.write(body)
