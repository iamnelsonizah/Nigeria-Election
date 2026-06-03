from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

import numpy as np
import pandas as pd

from data.nigeria_election_data import (
    GOVERNORSHIP_2023,
    NATIONAL_ASSEMBLY,
    PRESIDENTIAL_DATA,
    STATE_VOTER_DATA_2023,
    STATES_ZONES,
    get_assembly_df,
    get_governorship_df,
    get_state_results,
    get_turnout_df,
    get_zone_summary,
)

PARTY_COLORS: dict[str, str] = {
    "APC": "#2fb36d",
    "PDP": "#d94b4b",
    "LP": "#f2b84b",
    "NNPP": "#3f8fd2",
    "ACN": "#8b5cf6",
    "CPC": "#1db5a8",
    "ANPP": "#e28136",
    "APGA": "#d9469f",
    "Others": "#8a9387",
}

ZONE_COLORS: dict[str, str] = {
    "North Central": "#7ec8a3",
    "North East": "#7aa7d9",
    "North West": "#5d8fd1",
    "South East": "#f0b44c",
    "South South": "#db6559",
    "South West": "#61b876",
}

CORE_PARTIES = ("APC", "PDP", "LP", "NNPP")
STATE_RESULT_YEARS = (2023, 2019, 2015)

REGIONAL_NOTES = {
    "North West": "Historically the most vote-rich zone. APC swept it in 2015 and 2019, while NNPP made a concentrated Kano entry in 2023.",
    "North East": "APC strength is deepest in Borno and Yobe. PDP remains competitive in Adamawa and Taraba.",
    "North Central": "A battleground zone where Benue, Plateau, and FCT often reveal cross-party urban and middle-belt shifts.",
    "South West": "APC's traditional base, with Lagos becoming a major 2023 split between APC and LP.",
    "South East": "LP swept the zone in 2023, marking a dramatic break from the older PDP pattern.",
    "South South": "PDP's historical stronghold, with Rivers, Bayelsa, Akwa Ibom, and Delta remaining decisive states.",
}

TREND_INSIGHTS = [
    {
        "title": "APC vote compression",
        "detail": "APC won three consecutive presidential cycles from 2015 to 2023, but its national vote count fell sharply in 2023.",
    },
    {
        "title": "PDP structural decline",
        "detail": "PDP moved from 22.5M presidential votes in 2011 to roughly 7.0M in 2023.",
    },
    {
        "title": "LP third-party surge",
        "detail": "Labour Party crossed 6M presidential votes in 2023, creating the strongest third-party result in this dataset.",
    },
    {
        "title": "Turnout crisis",
        "detail": "National turnout fell from 53.7% in 2011 to 27.1% in 2023.",
    },
]

KNOWN_ANOMALIES = {
    2023: [
        ("BVAS failure", "Critical", "BVAS and IReV transmission issues delayed result uploads in multiple polling units."),
        ("Ekiti arithmetic concerns", "Critical", "Petitioners alleged vote total inconsistencies in Ekiti during post-election litigation."),
        ("Rivers violence reports", "High", "Observer and media reports described ballot disruption and violence in parts of Rivers State."),
        ("Delayed result upload", "High", "Real-time electronic result upload fell short of public expectations and observer recommendations."),
        ("Lagos voter suppression reports", "High", "Voter intimidation reports in parts of Lagos coincided with very low accreditation rates."),
        ("NNPP Kano concentration", "Medium", "NNPP's national vote was heavily concentrated in Kano, revealing a regional stronghold pattern."),
        ("Borno APC dominance", "Medium", "APC's Borno margin was unusually high, though security and campaign conditions are relevant context."),
    ],
    2019: [
        ("Kano over-voting allegations", "Critical", "Reports alleged card-reader bypassing and voter collusion in several Kano LGAs."),
        ("Rivers annulments", "High", "Several Rivers results were contested or annulled by election tribunals after the vote."),
        ("North West block vote", "Medium", "APC margins across the North West were unusually uniform relative to other regions."),
    ],
    2015: [
        ("Historic transfer", "Positive", "The 2015 result produced Nigeria's first peaceful democratic transfer of power between parties."),
        ("Card reader failures", "High", "Smart card reader failures in several polling units created disputes and delays."),
    ],
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(val) for key, val in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return _json_safe(df.replace({np.nan: None}).to_dict(orient="records"))


def _party_sort_key(party: str) -> tuple[int, str]:
    order = ["APC", "PDP", "LP", "NNPP", "APGA", "ACN", "CPC", "ANPP", "Others"]
    return (order.index(party) if party in order else len(order), party)


def _all_parties() -> list[str]:
    parties: set[str] = set()
    for data in PRESIDENTIAL_DATA.values():
        parties.update(data["results"].keys())
    for chamber_data in NATIONAL_ASSEMBLY.values():
        for seats in chamber_data.values():
            parties.update(seats.keys())
    parties.update(record["party"] for record in GOVERNORSHIP_2023.values())
    parties.discard("N/A")
    return sorted(parties, key=_party_sort_key)


def _normalise_parties(parties: Iterable[str] | None, available: Iterable[str] | None = None) -> list[str]:
    available_set = set(available or _all_parties())
    if not parties:
        return sorted(available_set, key=_party_sort_key)
    selected = [party.upper() for party in parties if party.upper() in available_set]
    return sorted(selected, key=_party_sort_key) or sorted(available_set, key=_party_sort_key)


def _filter_zones(df: pd.DataFrame, zones: Iterable[str] | None) -> pd.DataFrame:
    if not zones or "Zone" not in df.columns:
        return df
    zone_set = set(zones)
    return df[df["Zone"].isin(zone_set)]


def _validate_year(year: int, allowed: Iterable[int], label: str) -> None:
    if year not in set(allowed):
        allowed_text = ", ".join(str(item) for item in sorted(allowed, reverse=True))
        raise ValueError(f"{label} must be one of: {allowed_text}.")


def _party_results(results: dict[str, int], total: int, parties: Iterable[str] | None = None) -> list[dict[str, Any]]:
    selected = _normalise_parties(parties, results.keys()) if parties else sorted(results.keys(), key=_party_sort_key)
    rows = []
    for party in selected:
        votes = int(results.get(party, 0))
        rows.append(
            {
                "Party": party,
                "Votes": votes,
                "Pct": round(votes / total * 100, 2) if total else 0,
                "Color": PARTY_COLORS.get(party, "#8a9387"),
            }
        )
    return rows


def _state_turnout_df() -> pd.DataFrame:
    rows = []
    for state, data in STATE_VOTER_DATA_2023.items():
        registered = data["registered"]
        accredited = data["accredited"]
        rows.append(
            {
                "State": state,
                "Zone": STATES_ZONES.get(state, "Unknown"),
                "Registered": registered,
                "Accredited": accredited,
                "Turnout_Pct": round(accredited / registered * 100, 1) if registered else 0,
            }
        )
    return pd.DataFrame(rows)


def filters_payload() -> dict[str, Any]:
    states_by_zone = {}
    for state, zone in STATES_ZONES.items():
        states_by_zone.setdefault(zone, []).append(state)
    for zone in states_by_zone:
        states_by_zone[zone] = sorted(states_by_zone[zone])

    return {
        "years": sorted(PRESIDENTIAL_DATA.keys(), reverse=True),
        "stateYears": list(STATE_RESULT_YEARS),
        "assemblyYears": sorted(NATIONAL_ASSEMBLY.keys(), reverse=True),
        "zones": sorted(set(STATES_ZONES.values())),
        "states": sorted(STATES_ZONES.keys()),
        "statesByZone": states_by_zone,
        "parties": _all_parties(),
        "partyColors": PARTY_COLORS,
        "zoneColors": ZONE_COLORS,
        "sources": [
            "INEC official result releases",
            "IReV and election observer summaries",
            "IFES Election Guide",
            "IPU Parline",
        ],
    }
def overview_payload() -> dict[str, Any]:
    turnout_df = get_turnout_df()
    latest = PRESIDENTIAL_DATA[2023]
    previous = PRESIDENTIAL_DATA[2019]
    state_df = get_state_results(2023)
    gov_counts = Counter(row["party"] for row in GOVERNORSHIP_2023.values() if row["party"] != "N/A")

    timeline = []
    for year in sorted(PRESIDENTIAL_DATA):
        data = PRESIDENTIAL_DATA[year]
        winner_votes = data["results"].get(data["winner_party"], 0)
        timeline.append(
            {
                "Year": year,
                "Winner": data["winner"],
                "Party": data["winner_party"],
                "Votes": winner_votes,
                "Turnout": data["turnout_pct"],
                "Color": PARTY_COLORS.get(data["winner_party"], "#8a9387"),
            }
        )

    return _json_safe(
        {
            "kpis": [
                {"label": "Election cycles", "value": len(PRESIDENTIAL_DATA), "delta": "2011-2023"},
                {"label": "Registered voters", "value": latest["registered_voters"], "delta": "+11.1M vs 2019"},
                {"label": "Votes cast", "value": latest["total_votes"], "delta": f"{latest['total_votes'] - previous['total_votes']:,} vs 2019"},
                {"label": "Turnout", "value": latest["turnout_pct"], "delta": "-7.7pp vs 2019", "suffix": "%"},
                {"label": "States covered", "value": 37, "delta": "36 states + FCT"},
            ],
            "voteShare2023": _party_results(latest["results"], latest["total_votes"]),
            "turnoutTrend": _records(turnout_df),
            "timeline": timeline,
            "zoneSummary": _records(get_zone_summary(2023)),
            "stateWinCounts": [
                {"Party": party, "Count": int(count), "Color": PARTY_COLORS.get(party, "#8a9387")}
                for party, count in state_df["Winner_Party"].value_counts().items()
            ],
            "governorshipCounts": [
                {"Party": party, "Count": int(count), "Color": PARTY_COLORS.get(party, "#8a9387")}
                for party, count in gov_counts.most_common()
            ],
        }
    )


def presidential_payload(year: int, zones: Iterable[str] | None = None, parties: Iterable[str] | None = None) -> dict[str, Any]:
    _validate_year(year, PRESIDENTIAL_DATA.keys(), "year")
    data = PRESIDENTIAL_DATA[year]
    national_results = _party_results(data["results"], data["total_votes"], parties)
    payload: dict[str, Any] = {
        "year": year,
        "summary": {
            "Winner": data["winner"],
            "Winner_Party": data["winner_party"],
            "Registered": data["registered_voters"],
            "Total_Votes": data["total_votes"],
            "Turnout": data["turnout_pct"],
        },
        "nationalResults": national_results,
        "stateResults": [],
        "topStates": [],
        "partyWins": [],
    }

    if year in STATE_RESULT_YEARS:
        state_df = _filter_zones(get_state_results(year), zones)
        selected_parties = _normalise_parties(parties, [p for p in CORE_PARTIES if p in state_df.columns])
        state_df = state_df.copy()
        state_df["Selected_Votes"] = state_df[selected_parties].sum(axis=1) if selected_parties else state_df["Total_Votes"]
        top_states = state_df.sort_values("Total_Votes", ascending=False).head(15)
        payload.update(
            {
                "stateResults": _records(state_df.sort_values(["Zone", "State"])),
                "topStates": _records(top_states),
                "partyWins": [
                    {"Party": party, "Count": int(count), "Color": PARTY_COLORS.get(party, "#8a9387")}
                    for party, count in state_df["Winner_Party"].value_counts().items()
                ],
            }
        )

    return _json_safe(payload)


def trends_payload(parties: Iterable[str] | None = None) -> dict[str, Any]:
    all_parties = _normalise_parties(parties, _all_parties())
    rows = []
    for year in sorted(PRESIDENTIAL_DATA):
        data = PRESIDENTIAL_DATA[year]
        for party in all_parties:
            votes = int(data["results"].get(party, 0))
            rows.append(
                {
                    "Year": year,
                    "Party": party,
                    "Votes": votes,
                    "Pct": round(votes / data["total_votes"] * 100, 2) if data["total_votes"] else 0,
                    "Color": PARTY_COLORS.get(party, "#8a9387"),
                }
            )
    df = pd.DataFrame(rows)
    summaries = []
    for party, group in df.groupby("Party"):
        ordered = group.sort_values("Year")
        summaries.append(
            {
                "Party": party,
                "Peak_Year": int(ordered.loc[ordered["Votes"].idxmax(), "Year"]),
                "Peak_Votes": int(ordered["Votes"].max()),
                "Latest_Votes": int(ordered[ordered["Year"] == 2023]["Votes"].iloc[0]) if (ordered["Year"] == 2023).any() else 0,
                "Latest_Pct": float(ordered[ordered["Year"] == 2023]["Pct"].iloc[0]) if (ordered["Year"] == 2023).any() else 0,
                "Color": PARTY_COLORS.get(party, "#8a9387"),
            }
        )
    return _json_safe({"rows": rows, "summaries": summaries, "insights": TREND_INSIGHTS})


def regional_payload(year: int, zones: Iterable[str] | None = None) -> dict[str, Any]:
    _validate_year(year, STATE_RESULT_YEARS, "year")
    state_df = _filter_zones(get_state_results(year), zones)
    zone_df = get_zone_summary(year)
    zone_df = _filter_zones(zone_df, zones)

    dominance = []
    for row in zone_df.to_dict(orient="records"):
        dominant_party = row["Dominant_Party"]
        total = row["Total_Votes"]
        votes = row.get(dominant_party, 0)
        dominance.append(
            {
                "Zone": row["Zone"],
                "Dominant_Party": dominant_party,
                "Votes": votes,
                "Share": round(votes / total * 100, 1) if total else 0,
                "Color": PARTY_COLORS.get(dominant_party, "#8a9387"),
                "Note": REGIONAL_NOTES.get(row["Zone"], ""),
            }
        )

    return _json_safe(
        {
            "year": year,
            "zoneSummary": _records(zone_df.sort_values("Total_Votes", ascending=False)),
            "stateResults": _records(state_df.sort_values(["Zone", "Total_Votes"], ascending=[True, False])),
            "dominance": dominance,
            "notes": [{"Zone": zone, "Note": note, "Color": ZONE_COLORS.get(zone, "#8a9387")} for zone, note in REGIONAL_NOTES.items()],
        }
    )


def turnout_payload() -> dict[str, Any]:
    national = get_turnout_df()
    state = _state_turnout_df()
    state["Non_Voters"] = state["Registered"] - state["Accredited"]
    zone = (
        state.groupby("Zone", as_index=False)
        .agg({"Registered": "sum", "Accredited": "sum", "Turnout_Pct": "mean"})
        .sort_values("Turnout_Pct", ascending=False)
    )
    zone["Turnout_Pct"] = zone["Turnout_Pct"].round(1)

    national = national.copy()
    national["Did_Not_Vote"] = national["Registered"] - national["Votes_Cast"]
    national["Gap_Pct"] = (national["Did_Not_Vote"] / national["Registered"] * 100).round(1)
    highest = state.loc[state["Turnout_Pct"].idxmax()]
    lowest = state.loc[state["Turnout_Pct"].idxmin()]

    return _json_safe(
        {
            "nationalTrend": _records(national),
            "stateTurnout": _records(state.sort_values("Turnout_Pct", ascending=False)),
            "zoneTurnout": _records(zone),
            "stats": {
                "Highest_State": highest["State"],
                "Highest_Turnout": highest["Turnout_Pct"],
                "Lowest_State": lowest["State"],
                "Lowest_Turnout": lowest["Turnout_Pct"],
                "National_Drop_Points": round(float(national.iloc[0]["Turnout_Pct"] - national.iloc[-1]["Turnout_Pct"]), 1),
                "Mean_State_Turnout": round(float(state["Turnout_Pct"].mean()), 1),
            },
        }
    )


def assembly_payload(year: int) -> dict[str, Any]:
    _validate_year(year, NATIONAL_ASSEMBLY.keys(), "year")
    chambers = []
    for chamber, seats in NATIONAL_ASSEMBLY[year].items():
        total = sum(seats.values())
        majority = total // 2 + 1
        largest = max(seats, key=seats.get)
        chambers.append(
            {
                "Chamber": chamber,
                "Total_Seats": total,
                "Majority": majority,
                "Largest_Party": largest,
                "Largest_Seats": seats[largest],
                "Has_Majority": seats[largest] >= majority,
                "Parties": [
                    {
                        "Party": party,
                        "Seats": count,
                        "Seat_Pct": round(count / total * 100, 1) if total else 0,
                        "Color": PARTY_COLORS.get(party, "#8a9387"),
                    }
                    for party, count in sorted(seats.items(), key=lambda item: item[1], reverse=True)
                ],
            }
        )
    return _json_safe({"year": year, "chambers": chambers, "trend": _records(get_assembly_df())})


def governorship_payload(zones: Iterable[str] | None = None, parties: Iterable[str] | None = None) -> dict[str, Any]:
    df = get_governorship_df()
    df = df[df["Party"] != "N/A"]
    df = _filter_zones(df, zones)
    if parties:
        selected = set(_normalise_parties(parties, df["Party"].unique()))
        df = df[df["Party"].isin(selected)]
    counts = [
        {"Party": party, "Count": int(count), "Color": PARTY_COLORS.get(party, "#8a9387")}
        for party, count in df["Party"].value_counts().items()
    ]
    zone_control = (
        df.groupby(["Zone", "Party"], as_index=False)
        .size()
        .rename(columns={"size": "Count"})
        .sort_values(["Zone", "Count"], ascending=[True, False])
    )
    return _json_safe(
        {
            "year": 2023,
            "records": _records(df.sort_values(["Zone", "State"])),
            "partyCounts": counts,
            "zoneControl": _records(zone_control),
        }
    )


def _benford_analysis(values: pd.Series) -> dict[str, Any]:
    first_digits = values[values > 0].apply(lambda value: int(str(int(value))[0]))
    observed_counts = first_digits.value_counts().sort_index()
    total = int(observed_counts.sum())
    rows = []
    chi_square = 0.0
    for digit in range(1, 10):
        observed_pct = float(observed_counts.get(digit, 0) / total * 100) if total else 0
        expected_pct = float(np.log10(1 + 1 / digit) * 100)
        chi_square += (observed_pct - expected_pct) ** 2 / expected_pct
        rows.append({"Digit": digit, "Observed": round(observed_pct, 2), "Expected": round(expected_pct, 2)})
    conformity = "Broadly conforms" if chi_square < 15 else ("Mild deviation" if chi_square < 25 else "Significant deviation")
    return {"rows": rows, "chiSquare": round(chi_square, 2), "conformity": conformity}


def _turnout_outliers() -> list[dict[str, Any]]:
    state = _state_turnout_df()
    mean = state["Turnout_Pct"].mean()
    std = state["Turnout_Pct"].std()
    state["Z_Score"] = ((state["Turnout_Pct"] - mean) / std).round(2)
    state["Flag"] = state["Z_Score"].apply(
        lambda z: "High outlier" if z > 2 else ("Low outlier" if z < -2 else "Normal")
    )
    return _records(state.sort_values("Z_Score", ascending=False))


def _margin_spikes(year: int) -> list[dict[str, Any]]:
    state = get_state_results(year)
    parties = [party for party in CORE_PARTIES if party in state.columns]
    state = state.copy()
    state["Max_Votes"] = state[parties].max(axis=1)
    state["Second_Votes"] = state[parties].apply(lambda row: row.nlargest(2).iloc[-1], axis=1)
    state["Margin"] = state["Max_Votes"] - state["Second_Votes"]
    state["Margin_Pct"] = (state["Margin"] / state["Total_Votes"] * 100).round(1)
    mean = state["Margin_Pct"].mean()
    std = state["Margin_Pct"].std()
    state["Margin_Z"] = ((state["Margin_Pct"] - mean) / std).round(2)
    state["Margin_Flag"] = state["Margin_Z"].apply(
        lambda z: "Extreme margin" if z > 2 else ("High margin" if z > 1.5 else "Normal")
    )
    return _records(
        state[
            ["State", "Zone", "Winner_Party", "Margin", "Margin_Pct", "Margin_Z", "Margin_Flag"]
        ].sort_values("Margin_Pct", ascending=False)
    )


def anomalies_payload(year: int) -> dict[str, Any]:
    _validate_year(year, STATE_RESULT_YEARS, "year")
    state = get_state_results(year)
    parties = [party for party in CORE_PARTIES if party in state.columns]
    all_votes = pd.concat([state[party] for party in parties], ignore_index=True)
    return _json_safe(
        {
            "year": year,
            "disclaimer": "Statistical flags are signals for further review and are not legal evidence of fraud.",
            "benford": _benford_analysis(all_votes),
            "turnoutOutliers": _turnout_outliers(),
            "marginSpikes": _margin_spikes(year),
            "knownAnomalies": [
                {"Title": title, "Severity": severity, "Description": description}
                for title, severity, description in KNOWN_ANOMALIES.get(year, [])
            ],
        }
    )


def demographics_payload() -> dict[str, Any]:
    from data.nigeria_election_data import get_demographics_df
    df = get_demographics_df()
    return _json_safe({
        "records": _records(df),
        "correlation": {
            "literacy_turnout": round(float(df["Literacy_Rate"].corr(df["Turnout_Pct"])), 3),
            "poverty_turnout": round(float(df["Poverty_Rate"].corr(df["Turnout_Pct"])), 3),
            "gdp_turnout": round(float(df["GDP_Billion"].corr(df["Turnout_Pct"])), 3),
            "literacy_lp": round(float(df["Literacy_Rate"].corr(df["LP_Pct"])), 3),
            "poverty_apc": round(float(df["Poverty_Rate"].corr(df["APC_Pct"])), 3),
        }
    })


def tribunal_payload(year: int | None = None) -> dict[str, Any]:
    from data.nigeria_election_data import get_tribunal_cases
    cases = get_tribunal_cases(year)
    return _json_safe({
        "cases": cases
    })


def simulation_payload(zone_turnout_adjustments: dict[str, float], party_swing: dict[str, float]) -> dict[str, Any]:
    from data.nigeria_election_data import simulate_election
    res = simulate_election(zone_turnout_adjustments, party_swing)
    return _json_safe(res)

