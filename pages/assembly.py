"""National Assembly (Senate & House of Reps) page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.nigeria_election_data import NATIONAL_ASSEMBLY, get_assembly_df
from utils.charts import PARTY_COLORS, apply_dark, pie_chart


def show():
    st.markdown("# 🏛️ National Assembly Composition")
    st.markdown("Senate (109 seats) and House of Representatives (360 seats) — 2011 to 2023.")
    st.markdown("---")

    year = st.selectbox("Election Year", [2023, 2019, 2015, 2011], index=0)
    data = NATIONAL_ASSEMBLY[year]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    for chamber_name, seats in data.items():
        total = sum(seats.values())
        winner = max(seats, key=seats.get)
        winner_seats = seats[winner]
        majority = total // 2 + 1

        st.markdown(f"### {'🏛️' if chamber_name == 'Senate' else '🏢'} {chamber_name} — {year}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Seats", total)
        c2.metric("Majority Threshold", majority)
        c3.metric("Largest Party", winner)
        c4.metric(f"{winner} Seats", winner_seats,
                  f"{'✅ Majority' if winner_seats >= majority else '❌ No majority'}")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            labels = list(seats.keys())
            values = list(seats.values())
            colors = [PARTY_COLORS.get(l, "#95a5a6") for l in labels]
            fig = pie_chart(labels, values, colors=colors, height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            # Seat bar
            df_c = pd.DataFrame({"Party": list(seats.keys()), "Seats": list(seats.values())})
            df_c = df_c.sort_values("Seats", ascending=True)
            fig2 = go.Figure(go.Bar(
                x=df_c["Seats"], y=df_c["Party"],
                orientation="h",
                marker_color=[PARTY_COLORS.get(p, "#95a5a6") for p in df_c["Party"]],
                text=df_c["Seats"],
                textposition="outside",
                textfont=dict(color="#e8f4fd"),
                hovertemplate="<b>%{y}</b><br>Seats: %{x}<extra></extra>",
            ))
            # Majority line
            fig2.add_vline(x=majority, line_dash="dash", line_color="#f39c12",
                           annotation_text=f"Majority ({majority})",
                           annotation_font_color="#f39c12")
            apply_dark(fig2, f"Seat Distribution — {chamber_name}", height=340)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

    # ── Cross-year trend ──────────────────────────────────────────────────────
    st.markdown("### 📈 Senate Seat Trends (2011–2023)")
    df_a = get_assembly_df()
    df_senate = df_a[df_a["Chamber"] == "Senate"]

    fig3 = go.Figure()
    for party in ["APC", "PDP", "LP", "NNPP", "ACN", "CPC", "ANPP"]:
        sub = df_senate[df_senate["Party"] == party]
        if sub.empty or sub["Seats"].sum() == 0:
            continue
        fig3.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Seats"],
            mode="lines+markers+text",
            name=party,
            text=sub["Seats"],
            textposition="top center",
            textfont=dict(size=11),
            line=dict(color=PARTY_COLORS.get(party, "#aaa"), width=2),
            marker=dict(size=9),
            hovertemplate=f"<b>{party}</b><br>Year: %{{x}}<br>Seats: %{{y}}<extra></extra>",
        ))
    fig3.update_layout(
        xaxis=dict(tickvals=[2011, 2015, 2019, 2023]),
        yaxis=dict(title="Senate Seats", range=[0, 80]),
        legend=dict(orientation="h", y=-0.15),
    )
    apply_dark(fig3, height=400)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 House of Reps Seat Trends (2011–2023)")
    df_house = df_a[df_a["Chamber"] == "House"]
    fig4 = go.Figure()
    for party in ["APC", "PDP", "LP", "NNPP", "ACN", "CPC", "ANPP"]:
        sub = df_house[df_house["Party"] == party]
        if sub.empty or sub["Seats"].sum() == 0:
            continue
        fig4.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Seats"],
            mode="lines+markers+text",
            name=party,
            text=sub["Seats"],
            textposition="top center",
            textfont=dict(size=11),
            line=dict(color=PARTY_COLORS.get(party, "#aaa"), width=2),
            marker=dict(size=9),
        ))
    fig4.update_layout(
        xaxis=dict(tickvals=[2011, 2015, 2019, 2023]),
        yaxis=dict(title="House Seats", range=[0, 260]),
        legend=dict(orientation="h", y=-0.15),
    )
    apply_dark(fig4, height=400)
    st.plotly_chart(fig4, use_container_width=True)

    # ── Insight table ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Legislative Insights")
    st.markdown("""
    | Insight | Detail |
    |---|---|
    | 🏆 APC Senate dominance | APC has held the largest Senate bloc since 2015 |
    | 📉 PDP decline | PDP fell from 71 Senate seats (2011) to 36 (2023) |
    | 🆕 LP breakthrough | LP went from 1 House seat (2019) to 35 seats (2023) |
    | 🔄 2015 shift | The 2015 APC win represented the first peaceful transfer of power in Nigeria's history |
    | 📊 NNPP entry | NNPP secured 2 Senate and 18 House seats in 2023, first major result |
    | ⚖️ Opposition coalition | PDP + LP + NNPP in 2023 collectively outseated APC in some states |
    """)
