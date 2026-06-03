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

    # Dynamic Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        zones = ["All Zones"] + sorted(list(df["Zone"].unique()))
        selected_zone = st.selectbox("Select Geopolitical Zone", zones, index=0)
    
    with col_f2:
        if selected_zone == "All Zones":
            available_states = ["All States"] + sorted(list(df["State"].unique()))
        else:
            available_states = ["All States"] + sorted(list(df[df["Zone"] == selected_zone]["State"].unique()))
        selected_state = st.selectbox("Select State", available_states, index=0)

    # Filter dataframe
    df_filtered = df.copy()
    if selected_zone != "All Zones":
        df_filtered = df_filtered[df_filtered["Zone"] == selected_zone]
    if selected_state != "All States":
        df_filtered = df_filtered[df_filtered["State"] == selected_state]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown("### 📊 Results Overview")
    party_wins = df_filtered["Party"].value_counts()
    
    if len(party_wins) > 0:
        cols = st.columns(len(party_wins))
        for i, (party, wins) in enumerate(party_wins.items()):
            bg = PARTY_COLORS.get(party, "#555")
            cols[i].markdown(f"""
            <div style='background:{bg}22; border:1px solid {bg}66; border-radius:12px;
                        padding:14px; text-align:center;'>
                <div style='font-size:2rem; font-weight:800; color:{bg}'>{wins}</div>
                <div style='font-size:0.85rem; color:#aaa'>{party} States Won</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("No records found for current selection.")

    st.markdown("")

    # If single state selected, show customized card
    if selected_state != "All States" and not df_filtered.empty:
        row = df_filtered.iloc[0]
        bg = PARTY_COLORS.get(row["Party"], "#555")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, {bg}11, {bg}22); border:1px solid {bg}44; border-radius:12px; padding:20px; text-align:center; margin-bottom:20px;'>
            <h3 style='margin:0 0 10px 0; color:{bg};'>{selected_state} Governorship Outcome</h3>
            <p style='font-size:1.1rem; margin:4px 0;'>Governor-Elect: <b>{row["Governor"]}</b></p>
            <p style='font-size:1rem; margin:4px 0;'>Sponsoring Party: <b style='color:{bg};'>{row["Party"]}</b></p>
            <p style='font-size:0.95rem; margin:4px 0; color:#8899aa;'>Total Winner Votes: <b>{row["Votes"]:,.0f}</b></p>
        </div>
        """, unsafe_allow_html=True)

    # ── State map (bubble-ish bar) ─────────────────────────────────────────────
    st.markdown("### 🗺️ Governorship Wins by State")
    df_sorted = df_filtered.sort_values("Votes", ascending=True)
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
    
    chart_height = max(300, len(df_sorted) * 35)
    
    fig.update_layout(
        xaxis_title="Winning Candidate Votes",
        height=chart_height,
        yaxis=dict(tickfont=dict(size=10)),
    )
    apply_dark(fig, "2023 Governorship — Winning Votes per State (Filtered)", height=chart_height)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Treemap by zone ───────────────────────────────────────────────────────
    if selected_state == "All States":
        st.markdown("### 🌳 Governorship Control Treemap")
        fig2 = px.treemap(
            df_filtered,
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
    df_display = df_filtered[["State", "Zone", "Governor", "Party", "Votes"]].sort_values("State")
    df_display["Votes"] = df_display["Votes"].apply(lambda x: f"{x:,}")

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
