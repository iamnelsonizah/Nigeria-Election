"""Presidential Results page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.nigeria_election_data import (
    PRESIDENTIAL_DATA, get_state_results, STATE_VOTER_DATA_2023
)
from utils.charts import PARTY_COLORS, apply_dark, pie_chart, stacked_bar


def show():
    st.markdown("# 🗳️ Presidential Election Results")
    st.markdown("State-by-state and national breakdown across all election cycles.")
    st.markdown("---")

    # Filters row
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        year = st.selectbox("Select Election Year", [2023, 2019, 2015, 2011], index=0)
    
    # State-level results only exist for 2015-2023
    has_state_data = year in [2023, 2019, 2015]
    
    selected_zone = "All Zones"
    selected_state = "All States"
    
    if has_state_data:
        df_s = get_state_results(year)
        zones = ["All Zones"] + sorted(list(df_s["Zone"].unique()))
        with col_f2:
            selected_zone = st.selectbox("Select Geopolitical Zone", zones, index=0)
        
        # Filter states based on zone
        if selected_zone == "All Zones":
            available_states = ["All States"] + sorted(list(df_s["State"].unique()))
        else:
            available_states = ["All States"] + sorted(list(df_s[df_s["Zone"] == selected_zone]["State"].unique()))
            
        with col_f3:
            selected_state = st.selectbox("Select State", available_states, index=0)
    else:
        st.info("💡 Zone and State level filtering is available for 2015, 2019, and 2023 cycles.")

    # ── Filter Data ──────────────────────────────────────────────────────────
    national_data = PRESIDENTIAL_DATA[year]
    
    # Initialize variables for dynamic display
    title_suffix = ""
    display_results = {}
    total_votes = 0
    winner_name = national_data["winner"]
    winner_party = national_data["winner_party"]
    registered_voters = national_data["registered_voters"]
    turnout_pct = national_data["turnout_pct"]
    
    if has_state_data and (selected_zone != "All Zones" or selected_state != "All States"):
        df_filtered = df_s.copy()
        if selected_state != "All States":
            df_filtered = df_filtered[df_filtered["State"] == selected_state]
            title_suffix = f" — {selected_state} State ({selected_zone})"
        elif selected_zone != "All Zones":
            df_filtered = df_filtered[df_filtered["Zone"] == selected_zone]
            title_suffix = f" — {selected_zone} Zone"
            
        # Sum up votes for parties
        parties_present = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_filtered.columns]
        for p in parties_present:
            display_results[p] = int(df_filtered[p].sum())
        
        total_votes = sum(display_results.values())
        if total_votes > 0:
            # Determine local winner
            winner_party = max(display_results, key=display_results.get)
            winner_name = f"{winner_party} Leader"  # local winner representation
        
        # Handle Turnout and Registration
        if selected_state != "All States" and year == 2023:
            state_info = STATE_VOTER_DATA_2023.get(selected_state, {})
            registered_voters = state_info.get("registered", 0)
            accredited = state_info.get("accredited", 0)
            turnout_pct = round(accredited / registered_voters * 100, 2) if registered_voters > 0 else 0
        elif selected_zone != "All Zones" and year == 2023:
            # Sum for zone
            reg_sum = 0
            acc_sum = 0
            for s in df_filtered["State"]:
                s_info = STATE_VOTER_DATA_2023.get(s, {})
                reg_sum += s_info.get("registered", 0)
                acc_sum += s_info.get("accredited", 0)
            registered_voters = reg_sum
            turnout_pct = round(acc_sum / reg_sum * 100, 2) if reg_sum > 0 else 0
        else:
            # We don't have detailed state-level voter/turnout numbers for 2015/2019
            registered_voters = None
            turnout_pct = None
    else:
        # National
        display_results = national_data["results"]
        total_votes = national_data["total_votes"]
        title_suffix = " — National"

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Local Winner" if "National" not in title_suffix else "Overall Winner", winner_name)
    c2.metric("Dominant Party" if "National" not in title_suffix else "Winning Party", winner_party)
    
    if registered_voters:
        c3.metric("Registered Voters", f"{registered_voters:,.0f}")
    else:
        c3.metric("Registered Voters", "N/A", help="State/Zone voter metrics only fully mapped for 2023")
        
    if turnout_pct:
        c4.metric("Voter Turnout", f"{turnout_pct}%")
    else:
        c4.metric("Voter Turnout", "N/A", help="State/Zone turnout metrics only fully mapped for 2023")

    st.markdown("")

    # ── National/Filtered vote share ──────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### Vote Share{title_suffix}")
        labels = list(display_results.keys())
        values = list(display_results.values())
        colors = [PARTY_COLORS.get(l, "#95a5a6") for l in labels]
        fig = pie_chart(labels, values, colors=colors, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### Results Summary{title_suffix}")
        rows = []
        for party, votes in display_results.items():
            rows.append({
                "Party": party,
                "Votes": f"{votes:,}",
                "Vote Share": f"{votes/total_votes*100:.1f}%" if total_votes > 0 else "0%",
                "Status": "🏆 Winner" if party == winner_party else ""
            })
        df_table = pd.DataFrame(rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True, height=220)

        # Interpretation card
        st.markdown(f"""
        <div style='background:#111827; border:1px solid #1e2a3a; border-radius:10px; padding:16px; margin-top:12px;'>
            <div style='color:#8899aa; font-size:0.8rem; margin-bottom:8px'>DATA INTERPRETATION & CONTEXT</div>
            <div style='color:#e8f4fd; font-size:0.95rem; line-height:1.6'>
                📊 In this selection, a total of <b>{total_votes:,}</b> votes were recorded.<br>
                🏆 <b>{winner_party}</b> took the lead with <b>{df_table.iloc[0]['Vote Share'] if len(df_table) > 0 else '0%'}</b> of the votes.<br>
                💡 <i>Interpretation:</i> {get_interpretation(year, selected_zone, selected_state, winner_party)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── State-level results (available for 2015–2023) ─────────────────────────
    if has_state_data:
        st.markdown("---")
        st.markdown(f"### 🗺️ Geographic Analysis — {year}")
        
        # Apply zone filtering to state results for visualizations
        df_geo = df_s.copy()
        if selected_zone != "All Zones":
            df_geo = df_geo[df_geo["Zone"] == selected_zone]
            
        parties_present = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_geo.columns]

        # Bar chart: top states
        df_sorted = df_geo.sort_values("Total_Votes", ascending=True)
        if len(df_sorted) > 15:
            df_sorted = df_sorted.tail(15)
            chart_title = f"Top 15 States by Votes Cast (Filtered) — {year}"
        else:
            chart_title = f"States by Votes Cast (Filtered) — {year}"
            
        fig2 = go.Figure()
        for p in parties_present:
            if p in df_sorted.columns:
                fig2.add_trace(go.Bar(
                    y=df_sorted["State"], x=df_sorted[p],
                    name=p, orientation="h",
                    marker_color=PARTY_COLORS.get(p, "#95a5a6"),
                    hovertemplate=f"<b>{p}</b><br>%{{y}}<br>Votes: %{{x:,.0f}}<extra></extra>",
                ))
        fig2.update_layout(barmode="stack", xaxis_title="Votes")
        apply_dark(fig2, chart_title, height=480)
        st.plotly_chart(fig2, use_container_width=True)

        # Winner state distribution
        st.markdown(f"#### Party Wins by State (Filtered) — {year}")
        win_cols = st.columns(6)
        party_win_count = df_geo["Winner_Party"].value_counts()
        for i, (party, count) in enumerate(party_win_count.items()):
            bg = PARTY_COLORS.get(party, "#555")
            win_cols[i % 6].markdown(f"""
            <div style='background:{bg}22; border:1px solid {bg}66; border-radius:8px;
                        padding:10px; text-align:center; margin-bottom:8px;'>
                <div style='font-size:1.4rem; font-weight:700; color:{bg}'>{count}</div>
                <div style='font-size:0.8rem; color:#aaa'>{party} States</div>
            </div>""", unsafe_allow_html=True)

        # Full state table
        with st.expander("📋 Full State-by-State Breakdown"):
            display_cols = ["State", "Zone", "Winner_Party", "Total_Votes"] + parties_present
            display_cols = [c for c in display_cols if c in df_geo.columns]
            df_display = df_geo[display_cols].sort_values("State")
            df_display["Total_Votes"] = df_display["Total_Votes"].apply(lambda x: f"{x:,}")
            for p in parties_present:
                if p in df_display.columns:
                    df_display[p] = df_display[p].apply(lambda x: f"{x:,}" if x > 0 else "-")
            st.dataframe(df_display, use_container_width=True, hide_index=True)


def get_interpretation(year, zone, state, leader_party):
    """Generate context/interpretation based on selection."""
    if state != "All States":
        if year == 2023:
            if state == "Lagos":
                return "The Labour Party (LP) achieved a historic upset in Lagos, Nigeria's commercial nerve center, driven by strong youth mobilization and urban voter turnout, breaking APC's long-standing dominance."
            if state == "Kano":
                return "Kano voted overwhelmingly for NNPP, led by Kwankwaso, showing how strong regional figures can shift state-level outcomes dramatically away from national frontrunners."
            if leader_party == "LP":
                return f"{state} delivered a decisive win for the Labour Party (LP), reflecting the regional wave of Obi-support across the South East/South South and urban hubs."
        return f"In {year}, {state} served as a key battleground, with {leader_party} securing the lead. State-level dynamics were heavily influenced by local alignment and voter turnout."
    
    if zone != "All Zones":
        if zone == "South East":
            return "The South East zone represents a major shift in 2023, turning from a traditional PDP stronghold to voting almost entirely for the Labour Party (LP)."
        if zone == "North West":
            return "The North West is Nigeria's largest voting bloc. APC and PDP have traditionally locked horns here, but NNPP's rise in Kano added a tri-polar dynamic in 2023."
        return f"The {zone} zone showed clear preferences for {leader_party} in {year}. Regional voting patterns in Nigeria are historically aligned along geopolitical interest blocks."

    if year == 2023:
        return "The 2023 election was the most competitive in Nigeria's modern history, transitioning from a two-party system (APC vs PDP) to a highly fragmented three/four-way contest with LP and NNPP."
    elif year == 2015:
        return "2015 marked a historic milestone where the opposition coalition (APC) defeated an incumbent president (PDP) for the first time in Nigeria's history."
    return f"The {year} election consolidated the two-party system with APC and PDP dominating the electoral map."

