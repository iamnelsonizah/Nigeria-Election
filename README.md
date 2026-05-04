# 🇳🇬 Nigeria Election Analytics Hub

A real-time Streamlit dashboard for comprehensive analysis of Nigeria's election data spanning 2015–2023.

---

## 📊 Features

| Module | What It Shows |
|---|---|
| **Election Results** | Presidential winners, gubernatorial state-by-state table, party win counts |
| **Vote Share & Trends** | National vote share over time, zone-level stacked bars, scatter analysis |
| **Regional Patterns** | Animated zone bars, APC heatmap, treemap of state dominance |
| **Voter Turnout** | Turnout trends, participation funnel, youth/female demographics |
| **National Assembly** | Senate & House seat distribution, zone breakdown, area charts |
| **Anomaly Indicators** | Turnout swings, rejection outliers, landslide wins, flagged anomalies |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

### 3. Open in browser
The dashboard opens at: `http://localhost:8501`

---

## 📁 Project Structure

```
nigeria_election_dashboard/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── data/
    ├── presidential_results.csv  # Pres. votes by state/party (2015-2023)
    ├── gubernatorial_results.csv # Gov. winners by state (2015-2023)
    ├── voter_turnout.csv         # Turnout & demographics (2015-2023)
    └── national_assembly.csv    # Senate/House seats by zone/party
```

---

## 📦 Data Sources

- **INEC** — Independent National Electoral Commission official results
- **Stears Elections** — stears.co election database
- **YIAGA Africa** — Parallel vote tabulation & civic observer data
- **SBM Intelligence** — Electoral analytics reports
- **Academic literature** — Electoral Studies, African Affairs journals

---

## 🎛️ Dashboard Controls

Use the **sidebar** to filter:
- **Election Years**: 2015, 2019, 2023 (multi-select)
- **Geopolitical Zones**: All 6 zones (multi-select)
- **Parties**: APC, PDP, LP (multi-select)

Filters apply across all tabs dynamically.

---

## 🔍 Key Insights Covered

1. **APC's North West fortress** — contributes ~35% of APC's total presidential votes
2. **LP's 2023 South East sweep** — historic shift from PDP dominance
3. **Lagos near-flip** — Obi vs Tinubu separated by <10,000 votes
4. **FCT urban shift** — educated urban voters moving to LP
5. **Declining turnout** — National avg dropped from 57% (2015) to 38% (2023)
6. **Anomaly flags** — Rivers 2015, Borno 2019, Bayelsa patterns

---

## ⚠️ Disclaimer

This dashboard is for **research and civic transparency purposes only**. Anomaly indicators are statistical flags and do not constitute legal evidence of electoral fraud.

---

*Built with Streamlit · Plotly · Pandas*
