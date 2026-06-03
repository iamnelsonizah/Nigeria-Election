"""Voter Turnout & Demographics page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.nigeria_election_data import (
    get_turnout_df, STATE_VOTER_DATA_2023, STATES_ZONES
)
from utils.charts import ZONE_COLORS, apply_dark, gauge


def show():
    st.markdown("# 👥 Voter Turnout Analysis")
    st.markdown("Registered voters, accreditation rates, and participation trends.")
    st.markdown("---")

    # ── National trend ────────────────────────────────────────────────────────
    st.markdown("### 📉 National Turnout Trend (2011–2023)")
    df_t = get_turnout_df()

    col1, col2, col3, col4 = st.columns(4)
    for i, (_, row) in enumerate(df_t.iterrows()):
        col = [col1, col2, col3, col4][i]
        color = "#2ecc71" if row["Year"] == 2011 else ("#f39c12" if row["Year"] == 2015 else
                ("#e67e22" if row["Year"] == 2019 else "#e74c3c"))
        col.plotly_chart(
            gauge(row["Turnout_Pct"], str(int(row["Year"])), "%", 65, color),
            use_container_width=True
        )

    # ── Reg vs cast ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Registered Voters vs Votes Cast")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_t["Year"], y=df_t["Registered"],
        fill="tozeroy", fillcolor="rgba(96,165,250,0.1)",
        line=dict(color="#60a5fa", width=2),
        name="Registered Voters",
        mode="lines+markers",
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Registered: %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df_t["Year"], y=df_t["Votes_Cast"],
        fill="tozeroy", fillcolor="rgba(46,204,113,0.15)",
        line=dict(color="#2ecc71", width=2),
        name="Votes Cast",
        mode="lines+markers",
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Votes Cast: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(xaxis=dict(tickvals=[2011,2015,2019,2023]), yaxis_title="Count")
    apply_dark(fig, height=380)
    st.plotly_chart(fig, use_container_width=True)

    # ── Gap analysis ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ❌ Non-Voting Gap — Registered but Did Not Vote")
    df_t["Did_Not_Vote"] = df_t["Registered"] - df_t["Votes_Cast"]
    df_t["Gap_Pct"] = (df_t["Did_Not_Vote"] / df_t["Registered"] * 100).round(1)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_t["Year"], y=df_t["Votes_Cast"], name="Voted",
        marker_color="#2ecc71",
        hovertemplate="<b>%{x}</b><br>Voted: %{y:,.0f}<extra></extra>",
    ))
    fig2.add_trace(go.Bar(
        x=df_t["Year"], y=df_t["Did_Not_Vote"], name="Did Not Vote",
        marker_color="#e74c3c",
        hovertemplate="<b>%{x}</b><br>Did Not Vote: %{y:,.0f}<extra></extra>",
    ))
    fig2.update_layout(barmode="stack", xaxis=dict(tickvals=[2011,2015,2019,2023]), yaxis_title="Voters")
    apply_dark(fig2, height=360)
    st.plotly_chart(fig2, use_container_width=True)

    # ── 2023 State-level accreditation ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗺️ 2023 State-Level Accreditation & Turnout")

    # Geopolitical Zone filter for turnout
    zones = ["All Zones"] + sorted(list(set(STATES_ZONES.values())))
    selected_zone = st.selectbox("Filter States by Geopolitical Zone", zones, index=0)

    rows = []
    for state, d in STATE_VOTER_DATA_2023.items():
        reg = d["registered"]
        acc = d["accredited"]
        rate = round(acc / reg * 100, 1) if reg > 0 else 0
        rows.append({
            "State": state,
            "Zone": STATES_ZONES.get(state, "Unknown"),
            "Registered": reg,
            "Accredited": acc,
            "Turnout_%": rate,
        })
    df_sv = pd.DataFrame(rows)
    
    if selected_zone != "All Zones":
        df_sv = df_sv[df_sv["Zone"] == selected_zone]
        
    df_sv = df_sv.sort_values("Turnout_%", ascending=True)

    # Colour by zone
    zone_color_list = [ZONE_COLORS.get(z, "#555") for z in df_sv["Zone"]]

    # Show a comparison KPI card or Gauge comparing selected zone vs National (27.06%)
    if selected_zone != "All Zones":
        zone_reg = df_sv["Registered"].sum()
        zone_acc = df_sv["Accredited"].sum()
        zone_turnout = round(zone_acc / zone_reg * 100, 2) if zone_reg > 0 else 0
        
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            st.plotly_chart(
                gauge(zone_turnout, f"{selected_zone} Turnout", "%", 65, ZONE_COLORS.get(selected_zone, "#60a5fa")),
                use_container_width=True
            )
        with col_g2:
            st.markdown(f"""
            <div style='background:#111827; border:1px solid #1e2a3a; border-radius:10px; padding:16px; margin-top:20px;'>
                <div style='color:#8899aa; font-size:0.8rem; margin-bottom:8px'>ZONE ANALYSIS SUMMARY</div>
                <div style='color:#e8f4fd; font-size:1rem; line-height:1.8'>
                    📍 Zone: <b>{selected_zone}</b><br>
                    📊 Average Turnout: <b>{zone_turnout}%</b> (National Average: <b>27.1%</b>)<br>
                    👥 Total Registered: <b>{zone_reg:,.0f}</b> | Accredited: <b>{zone_acc:,.0f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    fig3 = go.Figure(go.Bar(
        x=df_sv["Turnout_%"],
        y=df_sv["State"],
        orientation="h",
        marker_color=zone_color_list,
        text=[f"{v}%" for v in df_sv["Turnout_%"]],
        textposition="outside",
        textfont=dict(color="#e8f4fd", size=10),
        hovertemplate="<b>%{y}</b><br>Turnout: %{x:.1f}%<extra></extra>",
    ))
    
    # Adjust chart height based on count of states to keep clean aspect ratio
    chart_height = max(300, len(df_sv) * 24)
    
    fig3.update_layout(
        xaxis_title="Accreditation Rate (%)",
        yaxis=dict(tickfont=dict(size=10)),
        height=chart_height,
    )
    apply_dark(fig3, f"State-level Turnout — {selected_zone if selected_zone != 'All Zones' else 'Nigeria'} (2023)", height=chart_height)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Turnout insights ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Turnout Insights & Interpretations")
    
    # Dynamic context based on selected zone
    zone_interpretation = ""
    if selected_zone == "All Zones":
        zone_interpretation = "National turnout has consistently declined since 2011, hitting an all-time low of 27.1% in 2023. This points to a severe crisis of participation, potentially due to administrative delays, historical voter apathy, security concerns, or a lack of trust in the electoral process."
    else:
        zone_notes = {
            "North West": "North West states like Jigawa and Katsina maintained relatively strong turnouts compared to the south, though overall numbers are still down from historical highs.",
            "North East": "In security-challenged states like Borno and Yobe, the voter turnout was depressed in certain pockets, but remained higher than the national average due to intense mobilization.",
            "North Central": "The Middle Belt shows highly variable turnout. FCT recorded low participation (approx 20%), similar to other major urban centers.",
            "South West": "Lagos recorded a record low turnout of 17.6% despite high registration growth. This reflects typical urban voter apathy, coupled with reported delays and intimidation.",
            "South East": "Despite intense local enthusiasm for Peter Obi, overall accredited turnout remained low, partly due to security tensions and delays in opening polling units.",
            "South South": "Rivers and Delta saw historic lows in official turnout rates, indicating high tension and localized voter suppression."
        }
        zone_interpretation = zone_notes.get(selected_zone, "")
        
    st.markdown(f"""
    <div style='background:#111827; border:1px solid #1e2a3a; border-radius:10px; padding:16px;'>
        <div style='color:#e74c3c; font-weight:700; margin-bottom:8px'>⚠️ ANALYTICAL TAKEAWAY</div>
        <p style='color:#e8f4fd; font-size:0.95rem; line-height:1.6; margin:0;'>{zone_interpretation}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""
    | Observation | Detail |
    |---|---|
    | 📉 Persistent decline | Turnout fell from 53.7% (2011) to 27.1% (2023) — a 26.6pp drop |
    | 📍 Highest 2023 turnout | North West states — Borno (31%), Jigawa (30%), Katsina (31%) |
    | 📍 Lowest 2023 turnout | Lagos (17.6%), Rivers (20.3%) — mega-cities with high voter apathy |
    | 🔬 BVAS impact | INEC's BVAS system reduced result manipulation but didn't raise participation |
    | 🧑‍🤝‍🧑 Youth registration | 9.5M new voters registered for 2023 but many didn't turn out |
    | ⚠️ Disenfranchisement | Insecurity in North East suppressed participation in Borno, Yobe, Adamawa |
    """)

