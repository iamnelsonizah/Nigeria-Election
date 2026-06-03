from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from backend.app.services import election_analytics as analytics

router = APIRouter(tags=["analytics"])

ZonesQuery = Annotated[list[str] | None, Query(description="Repeatable geopolitical zone filter.")]
PartiesQuery = Annotated[list[str] | None, Query(description="Repeatable party filter.")]


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


@router.get("/filters")
def filters() -> dict:
    return analytics.filters_payload()


@router.get("/overview")
def overview() -> dict:
    return analytics.overview_payload()


@router.get("/presidential")
def presidential(
    year: int = Query(2023, description="Election year."),
    zones: ZonesQuery = None,
    parties: PartiesQuery = None,
) -> dict:
    try:
        return analytics.presidential_payload(year=year, zones=zones, parties=parties)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.get("/trends")
def trends(parties: PartiesQuery = None) -> dict:
    return analytics.trends_payload(parties=parties)


@router.get("/regional")
def regional(
    year: int = Query(2023, description="Election year with state-level results."),
    zones: ZonesQuery = None,
) -> dict:
    try:
        return analytics.regional_payload(year=year, zones=zones)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.get("/turnout")
def turnout() -> dict:
    return analytics.turnout_payload()


@router.get("/assembly")
def assembly(year: int = Query(2023, description="National Assembly election year.")) -> dict:
    try:
        return analytics.assembly_payload(year=year)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.get("/governorship")
def governorship(zones: ZonesQuery = None, parties: PartiesQuery = None) -> dict:
    return analytics.governorship_payload(zones=zones, parties=parties)


@router.get("/anomalies")
def anomalies(year: int = Query(2023, description="Election year with state-level results.")) -> dict:
    try:
        return analytics.anomalies_payload(year=year)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.get("/demographics")
def demographics() -> dict:
    return analytics.demographics_payload()


@router.get("/tribunal")
def tribunal(year: int | None = Query(None, description="Filter tribunal cases by year.")) -> dict:
    return analytics.tribunal_payload(year=year)


@router.post("/simulate")
def simulate(body: dict) -> dict:
    zone_turnout = body.get("zoneTurnoutAdjustments", {})
    party_swing = body.get("partySwing", {})
    # Convert zone names keys from body to match exactly
    return analytics.simulation_payload(zone_turnout, party_swing)

