"""Overview / Home page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data.nigeria_election_data import (
    PRESIDENTIAL_DATA, get_presidential_summary, get_turnout_df, STATES_ZONES
)
from utils.charts import PARTY_COLORS, apply_dark, pie_chart


def show():
    st.markdown("# 🇳🇬 Nigeria Election Analytics Dashboard")
    st.markdown("**Comprehensive insights across Presidential, Gubernatorial & Legislative elections (2011–2023)**")
    st.markdown("---")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Election Cycles", "4", "2011 → 2023")
    c2.metric("Registered Voters (2023)", "93.5M", "+11.1M vs 2019")
    c3.metric("Votes Cast (2023)", "25.3M", "-3.3M vs 2019")
    c4.metric("Turnout (2023)", "27.1%", "-7.7pp vs 2019")
    c5.metric("States Covered", "36 + FCT", "All geopolitical zones")

    st.markdown("")

    # ── Two-column: latest result pie + turnout trend ─────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🗳️ 2023 Presidential — Vote Share")
        res2023 = PRESIDENTIAL_DATA[2023]["results"]
        labels = list(res2023.keys())
        values = list(res2023.values())
        colors = [PARTY_COLORS.get(l, "#95a5a6") for l in labels]
        fig = pie_chart(labels, values, colors=colors, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 📉 Voter Turnout Decline (2011–2023)")
        df_t = get_turnout_df()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_t["Year"], y=df_t["Turnout_Pct"],
            mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in df_t["Turnout_Pct"]],
            textposition="top center",
            textfont=dict(color="#60a5fa", size=12),
            line=dict(color="#60a5fa", width=3),
            marker=dict(size=10, color="#60a5fa"),
            fill="tozeroy", fillcolor="rgba(96,165,250,0.08)",
            hovertemplate="<b>%{x}</b><br>Turnout: %{y:.1f}%<extra></extra>",
        ))
        fig2.update_layout(
            xaxis=dict(tickvals=[2011, 2015, 2019, 2023]),
            yaxis=dict(range=[0, 65], title="Turnout %"),
        )
        apply_dark(fig2, height=340)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Registered voters growth ──────────────────────────────────────────────
    st.markdown("### 📈 Registered Voters vs Votes Cast (2011–2023)")
    df_t = get_turnout_df()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_t["Year"], y=df_t["Registered"],
        name="Registered Voters",
        marker_color="#1f4068",
        hovertemplate="<b>%{x}</b><br>Registered: %{y:,.0f}<extra></extra>",
    ))
    fig3.add_trace(go.Bar(
        x=df_t["Year"], y=df_t["Votes_Cast"],
        name="Votes Cast",
        marker_color="#60a5fa",
        hovertemplate="<b>%{x}</b><br>Votes Cast: %{y:,.0f}<extra></extra>",
    ))
    fig3.update_layout(barmode="group", xaxis=dict(tickvals=[2011, 2015, 2019, 2023]))
    apply_dark(fig3, height=360)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Election timeline ─────────────────────────────────────────────────────
    st.markdown("### 📅 Election Timeline & Winners")
    winners = [
        {"Year": 2011, "Winner": "Goodluck Jonathan", "Party": "PDP", "Votes": "22.5M", "Turnout": "53.7%"},
        {"Year": 2015, "Winner": "Muhammadu Buhari",  "Party": "APC", "Votes": "15.4M", "Turnout": "43.7%"},
        {"Year": 2019, "Winner": "Muhammadu Buhari",  "Party": "APC", "Votes": "15.2M", "Turnout": "34.8%"},
        {"Year": 2023, "Winner": "Bola Tinubu",       "Party": "APC", "Votes": "8.8M",  "Turnout": "27.1%"},
    ]

    cols = st.columns(4)
    party_bg = {"PDP": "#8b1a1a", "APC": "#1a5c35"}
    for i, w in enumerate(winners):
        bg = party_bg.get(w["Party"], "#1a3d8b")
        cols[i].markdown(f"""
        <div style='background:linear-gradient(135deg,{bg}22,{bg}44);
                    border:1px solid {bg}88; border-radius:12px; padding:16px; text-align:center;'>
            <div style='font-size:1.5rem; font-weight:800; color:#e8f4fd'>{w["Year"]}</div>
            <div style='font-size:1rem; color:#ccc; margin:4px 0'>{w["Winner"]}</div>
            <div style='display:inline-block; background:{bg}; color:#fff;
                        padding:2px 12px; border-radius:20px; font-size:0.8rem; font-weight:600;
                        margin:4px 0'>{w["Party"]}</div>
            <div style='font-size:0.85rem; color:#aaa; margin-top:6px'>
                🗳 {w["Votes"]} votes<br>📊 {w["Turnout"]} turnout
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.info("💡 Use the sidebar to explore Presidential results, regional patterns, voter turnout trends, assembly compositions, and anomaly detection.")
