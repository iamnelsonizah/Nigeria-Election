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

    year = st.selectbox("Select Election Year", [2023, 2019, 2015, 2011], index=0)
    data = PRESIDENTIAL_DATA[year]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Winner", data["winner"])
    c2.metric("Winning Party", data["winner_party"])
    c3.metric("Registered Voters", f"{data['registered_voters']:,.0f}")
    c4.metric("Voter Turnout", f"{data['turnout_pct']}%")

    st.markdown("")

    # ── National vote share ──────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### National Vote Share — {year}")
        labels = list(data["results"].keys())
        values = list(data["results"].values())
        colors = [PARTY_COLORS.get(l, "#95a5a6") for l in labels]
        fig = pie_chart(labels, values, colors=colors, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### Results Table — {year}")
        total = data["total_votes"]
        rows = []
        for party, votes in data["results"].items():
            rows.append({
                "Party": party,
                "Votes": f"{votes:,}",
                "Vote Share": f"{votes/total*100:.1f}%",
                "Status": "🏆 Winner" if party == data["winner_party"] else ""
            })
        df_table = pd.DataFrame(rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True,
                     height=200)

        st.markdown(f"""
        <div style='background:#111827; border:1px solid #1e2a3a; border-radius:10px; padding:16px; margin-top:12px;'>
            <div style='color:#8899aa; font-size:0.8rem; margin-bottom:8px'>ELECTION SUMMARY</div>
            <div style='color:#e8f4fd; font-size:1rem; line-height:2'>
                📋 Total Votes Cast: <b>{total:,}</b><br>
                🗓️ Year: <b>{year}</b><br>
                🏆 Winner: <b>{data['winner']} ({data['winner_party']})</b><br>
                📊 Turnout: <b>{data['turnout_pct']}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── State-level results (available for 2015–2023) ─────────────────────────
    if year in [2023, 2019, 2015]:
        st.markdown(f"### 🗺️ State-Level Results — {year}")
        df_s = get_state_results(year)

        # Colour states by winning party
        parties_present = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_s.columns]

        # Bar chart: top states by total votes
        df_sorted = df_s.sort_values("Total_Votes", ascending=True).tail(15)
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
        apply_dark(fig2, f"Top 15 States by Votes Cast — {year}", height=480)
        st.plotly_chart(fig2, use_container_width=True)

        # Winner map (text table with colour)
        st.markdown(f"#### Party Wins by State — {year}")
        win_cols = st.columns(6)
        party_win_count = df_s["Winner_Party"].value_counts()
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
            display_cols = [c for c in display_cols if c in df_s.columns]
            df_display = df_s[display_cols].sort_values("State")
            df_display["Total_Votes"] = df_display["Total_Votes"].apply(lambda x: f"{x:,}")
            for p in parties_present:
                if p in df_display.columns:
                    df_display[p] = df_display[p].apply(lambda x: f"{x:,}" if x > 0 else "-")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("📌 State-level breakdown is available for 2015, 2019, and 2023 elections.")
