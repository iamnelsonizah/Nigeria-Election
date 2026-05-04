"""Governorship Results page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data.nigeria_election_data import get_governorship_df, STATES_ZONES
from utils.charts import PARTY_COLORS, apply_dark


def show():
    st.markdown("# 🏙️ Governorship Election Results")
    st.markdown("2023 governorship outcomes across all 36 states.")
    st.markdown("---")

    df = get_governorship_df()
    df = df[df["Party"] != "N/A"]  # Remove FCT (no governor)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    party_wins = df["Party"].value_counts()
    cols = st.columns(len(party_wins))
    for i, (party, wins) in enumerate(party_wins.items()):
        bg = PARTY_COLORS.get(party, "#555")
        cols[i].markdown(f"""
        <div style='background:{bg}22; border:1px solid {bg}66; border-radius:12px;
                    padding:14px; text-align:center;'>
            <div style='font-size:2rem; font-weight:800; color:{bg}'>{wins}</div>
            <div style='font-size:0.85rem; color:#aaa'>{party} States Won</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── State map (bubble-ish bar) ─────────────────────────────────────────────
    st.markdown("### 🗺️ Governorship Wins by State — 2023")
    df_sorted = df.sort_values("Votes", ascending=True)
    colors = [PARTY_COLORS.get(p, "#aaa") for p in df_sorted["Party"]]

    fig = go.Figure(go.Bar(
        x=df_sorted["Votes"],
        y=df_sorted["State"],
        orientation="h",
        marker_color=colors,
        text=[f"{p} — {v:,.0f}" for p, v in zip(df_sorted["Party"], df_sorted["Votes"])],
        textposition="outside",
        textfont=dict(color="#e8f4fd", size=10),
        hovertemplate="<b>%{y}</b><br>Votes: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title="Winning Candidate Votes",
        height=850,
        yaxis=dict(tickfont=dict(size=10)),
    )
    apply_dark(fig, "2023 Governorship — Winning Votes per State", height=850)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Treemap by zone ───────────────────────────────────────────────────────
    st.markdown("### 🌳 Governorship Control Treemap — 2023")
    fig2 = px.treemap(
        df,
        path=["Zone", "State"],
        values="Votes",
        color="Party",
        color_discrete_map=PARTY_COLORS,
        hover_data={"Governor": True, "Votes": ":,.0f"},
    )
    fig2.update_layout(
        paper_bgcolor="#0d1117",
        font=dict(color="#e8f4fd"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
    )
    fig2.update_traces(marker=dict(line=dict(width=1, color="#0d1117")))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Full table ────────────────────────────────────────────────────────────
    st.markdown("### 📋 Complete Governorship Results Table")
    df_display = df[["State", "Zone", "Governor", "Party", "Votes"]].sort_values("State")
    df_display["Votes"] = df_display["Votes"].apply(lambda x: f"{x:,}")

    def color_party(val):
        color = PARTY_COLORS.get(val, "#555")
        return f"background-color: {color}30; color: {color}; font-weight: bold; border-radius: 4px;"

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Insights ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Governorship Insights")
    st.markdown("""
    | Insight | Detail |
    |---|---|
    | 🟢 APC dominance | APC controls ~62% of states (22/36), reflecting executive strength |
    | 🔴 PDP South South | PDP retained Rivers, Delta, Bayelsa, Akwa Ibom, Adamawa — its South South stronghold |
    | 🟡 LP upset | LP's Alex Otti won Abia, traditionally a PDP state — major upset |
    | 🔵 NNPP Kano | Abba Yusuf won Kano (NNPP) with nearly 1 million votes, defeating APC |
    | 🗺️ South East | LP dominated with Ebonyi going APC; historically PDP country |
    | ⚖️ PDP–PDP Osun | PDP's Adeleke held Osun despite fierce APC contestation |
    """)
