"""Regional / Geopolitical Zone Analysis page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data.nigeria_election_data import get_state_results, get_zone_summary, STATES_ZONES
from utils.charts import PARTY_COLORS, ZONE_COLORS, apply_dark


def show():
    st.markdown("# 🗺️ Regional & Geopolitical Zone Analysis")
    st.markdown("Explore how Nigeria's six geopolitical zones vote differently.")
    st.markdown("---")

    year = st.selectbox("Election Year", [2023, 2019, 2015], index=0)

    df_s  = get_state_results(year)
    df_z  = get_zone_summary(year)
    parties = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_s.columns]

    # ── Zone overview ─────────────────────────────────────────────────────────
    st.markdown(f"### 🌍 Geopolitical Zone Vote Summary — {year}")
    fig = go.Figure()
    for p in parties:
        if p in df_z.columns:
            fig.add_trace(go.Bar(
                x=df_z["Zone"], y=df_z[p],
                name=p,
                marker_color=PARTY_COLORS.get(p, "#aaa"),
                hovertemplate=f"<b>{p}</b><br>%{{x}}<br>Votes: %{{y:,.0f}}<extra></extra>",
            ))
    fig.update_layout(barmode="group", xaxis_title="Zone", yaxis_title="Votes")
    apply_dark(fig, f"Party Votes by Geopolitical Zone — {year}", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Zone dominant party cards ─────────────────────────────────────────────
    st.markdown("### 🏆 Dominant Party per Zone")
    zone_cols = st.columns(3)
    for i, row in df_z.iterrows():
        zone = row["Zone"]
        dom  = row["Dominant_Party"]
        col  = PARTY_COLORS.get(dom, "#555")
        total = row["Total_Votes"]
        dom_votes = row.get(dom, 0)
        share = dom_votes / total * 100 if total > 0 else 0
        zone_cols[i % 3].markdown(f"""
        <div style='background:{col}18; border:1px solid {col}55;
                    border-radius:12px; padding:14px; margin-bottom:12px;'>
            <div style='font-size:0.85rem; color:#8899aa'>{zone}</div>
            <div style='font-size:1.2rem; font-weight:700; color:{col}; margin:4px 0'>{dom}</div>
            <div style='font-size:0.8rem; color:#aaa'>{share:.1f}% share · {dom_votes:,.0f} votes</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── State treemap ─────────────────────────────────────────────────────────
    st.markdown(f"### 🌳 State Treemap by Votes — {year}")
    df_tree = df_s.copy()
    df_tree["Zone"] = df_tree["State"].map(STATES_ZONES)
    df_tree["Color"] = df_tree["Winner_Party"].map(PARTY_COLORS).fillna("#555")

    fig2 = px.treemap(
        df_tree,
        path=["Zone", "State"],
        values="Total_Votes",
        color="Winner_Party",
        color_discrete_map=PARTY_COLORS,
        hover_data={"Total_Votes": ":,.0f"},
    )
    fig2.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(color="#e8f4fd"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=480,
    )
    fig2.update_traces(marker=dict(line=dict(width=1, color="#0d1117")))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── State-level breakdown by selected zone ────────────────────────────────
    st.markdown("### 🔍 Drill-down: State Results within a Zone")
    zones = sorted(df_s["Zone"].unique())
    sel_zone = st.selectbox("Select Zone", zones)
    df_zone  = df_s[df_s["Zone"] == sel_zone].sort_values("Total_Votes", ascending=False)

    fig3 = go.Figure()
    for p in parties:
        if p in df_zone.columns:
            fig3.add_trace(go.Bar(
                x=df_zone["State"], y=df_zone[p],
                name=p,
                marker_color=PARTY_COLORS.get(p, "#aaa"),
                hovertemplate=f"<b>{p}</b><br>%{{x}}<br>Votes: %{{y:,.0f}}<extra></extra>",
            ))
    fig3.update_layout(barmode="stack", yaxis_title="Votes")
    apply_dark(fig3, f"{sel_zone} — State Breakdown ({year})", height=360)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insight callout ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Regional Insights")
    regional_notes = {
        "North West":  "Historically the most vote-rich zone. APC swept it in 2015 & 2019. NNPP made inroads in Kano in 2023.",
        "North East":  "APC stronghold in Borno, Yobe. PDP competitive in Adamawa and Taraba.",
        "North Central": "Battleground zone — Benue, Plateau swing between parties; FCT tracked LP in 2023.",
        "South West":  "APC's traditional base. Lagos was split between APC and LP in 2023, a significant development.",
        "South East":  "LP swept all 5 states in 2023 with Peter Obi, marking the first time a third party dominated the zone.",
        "South South": "PDP's historical stronghold — Rivers, Bayelsa, Akwa Ibom routinely deliver PDP majorities.",
    }
    for zone, note in regional_notes.items():
        with st.expander(f"🗺️ {zone}"):
            st.write(note)
