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

    # Dynamic filter columns
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        year = st.selectbox("Election Year", [2023, 2019, 2015], index=0)
        
    df_s  = get_state_results(year)
    df_z  = get_zone_summary(year)
    parties = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_s.columns]

    with col_f2:
        zones = ["All Zones"] + sorted(list(df_s["Zone"].unique()))
        selected_zone = st.selectbox("Select Geopolitical Zone", zones, index=0)

    with col_f3:
        if selected_zone == "All Zones":
            available_states = ["All States"] + sorted(list(df_s["State"].unique()))
        else:
            available_states = ["All States"] + sorted(list(df_s[df_s["Zone"] == selected_zone]["State"].unique()))
        selected_state = st.selectbox("Select State for Analysis", available_states, index=0)

    # ── Filter Summary Details ───────────────────────────────────────────────
    st.markdown("### 🌍 Geopolitical Zone Vote Summary")
    
    # Highlight or filter the zone summary chart
    df_z_display = df_z.copy()
    if selected_zone != "All Zones":
        df_z_display = df_z_display[df_z_display["Zone"] == selected_zone]

    fig = go.Figure()
    for p in parties:
        if p in df_z_display.columns:
            fig.add_trace(go.Bar(
                x=df_z_display["Zone"], y=df_z_display[p],
                name=p,
                marker_color=PARTY_COLORS.get(p, "#aaa"),
                hovertemplate=f"<b>{p}</b><br>%{{x}}<br>Votes: %{{y:,.0f}}<extra></extra>",
            ))
    fig.update_layout(barmode="group", xaxis_title="Zone", yaxis_title="Votes")
    apply_dark(fig, f"Party Votes by Geopolitical Zone — {year}" + (f" ({selected_zone})" if selected_zone != "All Zones" else ""), height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Zone dominant party cards ─────────────────────────────────────────────
    st.markdown("### 🏆 Dominant Party per Zone")
    zone_cols = st.columns(3)
    cards_df = df_z if selected_zone == "All Zones" else df_z[df_z["Zone"] == selected_zone]
    
    for i, (_, row) in enumerate(cards_df.iterrows()):
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
    st.markdown("### 🌳 State Treemap by Votes")
    df_tree = df_s.copy()
    if selected_zone != "All Zones":
        df_tree = df_tree[df_tree["Zone"] == selected_zone]
    if selected_state != "All States":
        df_tree = df_tree[df_tree["State"] == selected_state]

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

    # ── State-level breakdown by selected zone/state ──────────────────────────
    st.markdown("### 🔍 Drill-down: State Results")
    
    zone_to_drill = selected_zone if selected_zone != "All Zones" else "North West"
    st.info(f"Showing detailed state-by-state breakdown for **{zone_to_drill}** geopolitical zone.")
    
    df_zone  = df_s[df_s["Zone"] == zone_to_drill].sort_values("Total_Votes", ascending=False)

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
    apply_dark(fig3, f"{zone_to_drill} — State Breakdown ({year})", height=360)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Dynamic Interpretation & Regional Insights ───────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Interpretation & Geopolitical Insights")
    
    # Custom interpretation card based on filters
    zone_desc = ""
    if selected_zone == "All Zones":
        zone_desc = "Nigeria's voting pattern is heavily split along regional lines. The northern zones generally see higher absolute voter turnouts and strong contests between APC and PDP (with NNPP joining in 2023), while southern zones often experience dramatic political realignments (like the rise of LP in the South East and parts of the South South in 2023)."
    else:
        regional_notes = {
            "North West": "North West is historically the most vote-rich zone. Swept by APC in 2015 & 2019, it remains a critical prize. NNPP's rise in Kano in 2023 disrupted the typical APC-PDP binary.",
            "North East": "North East has been a strong base for APC (e.g. Borno, Yobe), while PDP remains highly competitive in Adamawa, Taraba, and Gombe.",
            "North Central": "Often called the Middle Belt, North Central is Nigeria's premier swing/battleground zone with high ethnoreligious diversity leading to split tickets and close contests.",
            "South West": "A highly sophisticated voter base that shifted towards APC historically, but saw a massive multi-party division in 2023, particularly in Lagos between APC and LP.",
            "South East": "Voted overwhelmingly for LP (Peter Obi) in 2023, registering some of the highest margins of victory in the country and shifting completely away from its traditional PDP alignment.",
            "South South": "A historic stronghold for PDP, though LP made significant inroads in 2023, particularly in Edo and Delta."
        }
        zone_desc = regional_notes.get(selected_zone, "")

    st.markdown(f"""
    <div style='background:#111827; border-left:4px solid #3498db; border-radius:4px; padding:16px; margin-bottom:20px;'>
        <h4 style='margin:0 0 8px 0; color:#3498db;'>Regional Context: {selected_zone if selected_zone != "All Zones" else "National Map"}</h4>
        <p style='margin:0; font-size:0.95rem; color:#c9d8e8; line-height:1.6;'>{zone_desc}</p>
    </div>
    """, unsafe_allow_html=True)

