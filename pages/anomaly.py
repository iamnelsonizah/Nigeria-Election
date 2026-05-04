"""Anomaly & Fraud Indicator Detection page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.nigeria_election_data import (
    get_state_results, STATE_VOTER_DATA_2023, STATES_ZONES
)
from utils.charts import PARTY_COLORS, apply_dark


def benford_analysis(votes_series):
    """Apply Benford's Law — first-digit distribution test."""
    first_digits = votes_series[votes_series > 0].apply(lambda x: int(str(x)[0]))
    observed = first_digits.value_counts().sort_index()
    expected_pcts = {d: np.log10(1 + 1/d) * 100 for d in range(1, 10)}
    obs_pcts = (observed / observed.sum() * 100).reindex(range(1, 10), fill_value=0)
    return obs_pcts, expected_pcts


def show():
    st.markdown("# 🔍 Anomaly & Fraud Indicator Detection")
    st.markdown("Statistical methods to flag irregularities in election data.")
    st.markdown("---")

    st.warning("""
    ⚠️ **Disclaimer:** This analysis uses statistical methods (Benford's Law, outlier detection,
    turnout analysis) to highlight *potential* anomalies. Statistical flags are not proof of fraud —
    they are signals for further investigation. All data sourced from official INEC results.
    """)

    year = st.selectbox("Select Year for Analysis", [2023, 2019, 2015], index=0)
    df_s = get_state_results(year)
    parties_present = [p for p in ["APC", "PDP", "LP", "NNPP"] if p in df_s.columns]

    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 Benford's Law", "📊 Turnout Outliers",
        "⚡ Vote Spike Detection", "📋 Anomaly Report"
    ])

    # ── Tab 1: Benford's Law ──────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📐 Benford's Law Analysis")
        st.markdown("""
        Benford's Law predicts that in naturally occurring datasets, the leading digit is **1** about 30%
        of the time. Significant deviations may suggest fabricated or manipulated data.
        """)

        all_votes = pd.Series(dtype=float)
        for p in parties_present:
            if p in df_s.columns:
                all_votes = pd.concat([all_votes, df_s[p]])

        obs, exp = benford_analysis(all_votes)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(obs.index), y=obs.values,
            name="Observed",
            marker_color="#60a5fa",
            hovertemplate="<b>Digit %{x}</b><br>Observed: %{y:.1f}%<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=list(obs.index), y=[exp[d] for d in obs.index],
            mode="lines+markers",
            name="Expected (Benford)",
            line=dict(color="#f39c12", width=3, dash="dash"),
            marker=dict(size=8),
            hovertemplate="<b>Digit %{x}</b><br>Expected: %{y:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            xaxis=dict(title="First Digit", tickvals=list(range(1, 10))),
            yaxis=dict(title="Frequency (%)"),
        )
        apply_dark(fig, f"Benford's Law — {year} Presidential Vote Totals", height=420)
        st.plotly_chart(fig, use_container_width=True)

        # Chi-square style deviation
        obs_arr = np.array([obs.get(d, 0) for d in range(1, 10)])
        exp_arr = np.array([exp[d] for d in range(1, 10)])
        chi_sq = np.sum((obs_arr - exp_arr)**2 / exp_arr)
        conformity = "✅ Broadly conforms" if chi_sq < 15 else ("⚠️ Mild deviation" if chi_sq < 25 else "🚨 Significant deviation")

        st.metric("Chi-Square Deviation Score", f"{chi_sq:.2f}", conformity)
        st.caption("Threshold: <15 = Conforms, 15–25 = Mild deviation, >25 = Significant")

    # ── Tab 2: Turnout Outliers ───────────────────────────────────────────────
    with tab2:
        st.markdown("### 📊 Turnout Outlier Detection")
        st.markdown("States with unusually high or low accreditation rates are flagged.")

        rows = []
        for state, d in STATE_VOTER_DATA_2023.items():
            reg, acc = d["registered"], d["accredited"]
            rate = round(acc / reg * 100, 1) if reg > 0 else 0
            rows.append({"State": state, "Zone": STATES_ZONES.get(state, "?"),
                         "Registered": reg, "Accredited": acc, "Turnout_%": rate})
        df_sv = pd.DataFrame(rows)

        mean_t = df_sv["Turnout_%"].mean()
        std_t  = df_sv["Turnout_%"].std()
        df_sv["Z_Score"] = ((df_sv["Turnout_%"] - mean_t) / std_t).round(2)
        df_sv["Flag"] = df_sv["Z_Score"].apply(
            lambda z: "🚨 High outlier" if z > 2 else ("⚠️ Low outlier" if z < -2 else "✅ Normal")
        )

        fig2 = go.Figure()
        colors = df_sv["Z_Score"].apply(
            lambda z: "#e74c3c" if z > 2 else ("#f39c12" if z < -2 else "#60a5fa")
        )
        fig2.add_trace(go.Bar(
            x=df_sv["State"], y=df_sv["Turnout_%"],
            marker_color=colors,
            text=df_sv["Flag"],
            textposition="outside",
            textfont=dict(size=9),
            hovertemplate="<b>%{x}</b><br>Turnout: %{y:.1f}%<extra></extra>",
        ))
        fig2.add_hline(y=mean_t + 2*std_t, line_dash="dash", line_color="#e74c3c",
                       annotation_text="+2σ", annotation_font_color="#e74c3c")
        fig2.add_hline(y=mean_t - 2*std_t, line_dash="dash", line_color="#f39c12",
                       annotation_text="–2σ", annotation_font_color="#f39c12")
        fig2.add_hline(y=mean_t, line_dash="dot", line_color="#2ecc71",
                       annotation_text=f"Mean: {mean_t:.1f}%", annotation_font_color="#2ecc71")
        fig2.update_layout(xaxis=dict(tickangle=-45))
        apply_dark(fig2, "2023 State Turnout with Statistical Bounds", height=480)
        st.plotly_chart(fig2, use_container_width=True)

        flagged = df_sv[df_sv["Flag"] != "✅ Normal"][["State", "Zone", "Turnout_%", "Z_Score", "Flag"]]
        if not flagged.empty:
            st.markdown("#### 🚩 Flagged States")
            st.dataframe(flagged, use_container_width=True, hide_index=True)
        else:
            st.success("No states fall outside 2 standard deviations.")

    # ── Tab 3: Vote Spike Detection ───────────────────────────────────────────
    with tab3:
        st.markdown("### ⚡ Vote Margin Spike Detection")
        st.markdown("States where a party's vote margin vs runner-up is abnormally large.")

        df_s2 = df_s.copy()
        sorted_parties = parties_present
        if len(sorted_parties) >= 2:
            df_s2["Max_Votes"]  = df_s2[sorted_parties].max(axis=1)
            df_s2["2nd_Votes"]  = df_s2[sorted_parties].apply(lambda r: r.nlargest(2).iloc[-1], axis=1)
            df_s2["Margin"]     = df_s2["Max_Votes"] - df_s2["2nd_Votes"]
            df_s2["Margin_Pct"] = (df_s2["Margin"] / df_s2["Total_Votes"] * 100).round(1)

            mean_m = df_s2["Margin_Pct"].mean()
            std_m  = df_s2["Margin_Pct"].std()
            df_s2["Margin_Z"]  = ((df_s2["Margin_Pct"] - mean_m) / std_m).round(2)
            df_s2["Margin_Flag"] = df_s2["Margin_Z"].apply(
                lambda z: "🚨 Extreme margin" if z > 2 else ("⚠️ High margin" if z > 1.5 else "✅ Normal")
            )

            df_m = df_s2[["State", "Zone", "Winner_Party", "Margin", "Margin_Pct", "Margin_Z", "Margin_Flag"]]\
                        .sort_values("Margin_Pct", ascending=False)

            fig3 = px.scatter(
                df_m, x="State", y="Margin_Pct",
                color="Winner_Party",
                color_discrete_map=PARTY_COLORS,
                size="Margin_Pct",
                hover_data={"Zone": True, "Margin": ":,.0f", "Margin_Z": True},
                symbol="Margin_Flag",
            )
            fig3.add_hline(y=mean_m + 2*std_m, line_dash="dash", line_color="#e74c3c",
                           annotation_text="Extreme threshold")
            fig3.update_layout(xaxis=dict(tickangle=-45))
            apply_dark(fig3, f"Win Margin % by State — {year}", height=440)
            st.plotly_chart(fig3, use_container_width=True)

            flagged_m = df_m[df_m["Margin_Flag"] != "✅ Normal"]
            if not flagged_m.empty:
                st.markdown("#### 🚩 States with Extreme Win Margins")
                st.dataframe(flagged_m[["State", "Zone", "Winner_Party", "Margin_Pct", "Margin_Flag"]],
                             use_container_width=True, hide_index=True)

    # ── Tab 4: Anomaly Report ─────────────────────────────────────────────────
    with tab4:
        st.markdown("### 📋 Summary Anomaly Report")
        st.markdown(f"#### Known/Documented Irregularities — {year} Election")

        known_anomalies = {
            2023: [
                ("🚨 BVAS Failure", "Critical", "BVAS and IReV portal did not function as required in multiple polling units, delaying result transmission."),
                ("🚨 Ekiti State Arithmetic", "Critical", "Vote totals for multiple parties exceeded accredited voters in Ekiti — flagged by PDP petitioners."),
                ("⚠️ Rivers State Violence", "High", "Widespread reports of ballot box snatching and violence in Rivers state suppressed voting significantly."),
                ("⚠️ Delayed Result Upload", "High", "Results were not uploaded in real-time as promised; EU observers noted significant delays."),
                ("⚠️ Lagos Voter Suppression", "High", "Voter intimidation reports in multiple Lagos LGAs correlated with abnormally low turnout (17.6%)."),
                ("📌 NNPP Kano Concentration", "Medium", "NNPP's 1.5M national votes came almost entirely from Kano — geographically concentrated support."),
                ("📌 Borno APC Dominance", "Medium", "APC received 81% of votes in Borno — historically high, partly explained by security conditions limiting opposition campaign."),
            ],
            2019: [
                ("🚨 Kano Over-voting", "Critical", "Reports of voter collusion and card reader bypassing in several Kano LGAs."),
                ("⚠️ Rivers Annulment", "High", "Several Rivers State results were annulled by electoral tribunals post-election."),
                ("📌 North West Block Vote", "Medium", "APC swept North West with unusually uniform margins across states."),
            ],
            2015: [
                ("📌 Historic Transfer", "Positive", "First-ever peaceful transfer of power between parties in Nigeria's democratic history."),
                ("⚠️ Card Reader Malfunctions", "High", "Smart card readers failed in several polling units, causing disputes."),
            ],
        }

        anomalies = known_anomalies.get(year, [])
        severity_color = {"Critical": "#e74c3c", "High": "#f39c12", "Medium": "#3498db", "Positive": "#2ecc71"}

        for icon, severity, desc in anomalies:
            col = severity_color.get(severity, "#aaa")
            st.markdown(f"""
            <div style='background:{col}15; border-left:4px solid {col};
                        border-radius:0 8px 8px 0; padding:12px 16px; margin-bottom:10px;'>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <span style='font-size:1.1rem'>{icon}</span>
                    <span style='color:{col}; font-weight:600; font-size:0.85rem'>{severity}</span>
                </div>
                <div style='color:#e0e0e0; font-size:0.9rem; margin-top:4px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        **📚 Investigation Resources:**
        - [INEC IReV Portal](https://irev.inec.gov.ng/)
        - [YIAGA Africa ERAD Platform](https://erad.ng/)
        - [EU Election Observation Mission 2023](https://www.eeas.europa.eu/eom-nigeria-2023)
        - [Dataphyte Elections Portal](https://elections.dataphyte.com/)
        """)
