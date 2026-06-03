export type ApiScalar = string | number | boolean | null | undefined;

export interface ApiRecord {
  [key: string]: ApiScalar;
}

export type ColorMap = Record<string, string>;

export interface FiltersPayload {
  years: number[];
  stateYears: number[];
  assemblyYears: number[];
  zones: string[];
  parties: string[];
  partyColors: ColorMap;
  zoneColors: ColorMap;
  sources: string[];
}

export interface KpiPayload {
  label: string;
  value: number | string;
  delta: string;
  suffix?: string;
}

export interface OverviewPayload {
  kpis: KpiPayload[];
  voteShare2023: ApiRecord[];
  turnoutTrend: ApiRecord[];
  timeline: ApiRecord[];
  zoneSummary: ApiRecord[];
  stateWinCounts: ApiRecord[];
  governorshipCounts: ApiRecord[];
}

export interface PresidentialPayload {
  year: number;
  summary: ApiRecord;
  nationalResults: ApiRecord[];
  stateResults: ApiRecord[];
  topStates: ApiRecord[];
  partyWins: ApiRecord[];
}

export interface TrendsPayload {
  rows: ApiRecord[];
  summaries: ApiRecord[];
  insights: Array<{ title: string; detail: string }>;
}

export interface RegionalPayload {
  year: number;
  zoneSummary: ApiRecord[];
  stateResults: ApiRecord[];
  dominance: ApiRecord[];
  notes: ApiRecord[];
}

export interface TurnoutPayload {
  nationalTrend: ApiRecord[];
  stateTurnout: ApiRecord[];
  zoneTurnout: ApiRecord[];
  stats: ApiRecord;
}

export interface AssemblyPayload {
  year: number;
  chambers: Array<{
    Chamber: string;
    Total_Seats: number;
    Majority: number;
    Largest_Party: string;
    Largest_Seats: number;
    Has_Majority: boolean;
    Parties: ApiRecord[];
  }>;
  trend: ApiRecord[];
}

export interface GovernorshipPayload {
  year: number;
  records: ApiRecord[];
  partyCounts: ApiRecord[];
  zoneControl: ApiRecord[];
}

export interface AnomaliesPayload {
  year: number;
  disclaimer: string;
  benford: {
    rows: ApiRecord[];
    chiSquare: number;
    conformity: string;
  };
  turnoutOutliers: ApiRecord[];
  marginSpikes: ApiRecord[];
  knownAnomalies: ApiRecord[];
}

export interface DemographicsPayload {
  records: ApiRecord[];
  correlation: Record<string, number>;
}

export interface TribunalCase {
  year: number;
  seat: string;
  state: string;
  petitioner: string;
  respondent: string;
  status: string;
  outcome: string;
  arguments: string;
  date: string;
  severity: string;
}

export interface TribunalPayload {
  cases: TribunalCase[];
}

export interface SimulationPayload {
  total_votes: number;
  results: Record<string, number>;
  winner_party: string;
  pct: Record<string, number>;
  zone_results: ApiRecord[];
  state_results: ApiRecord[];
}

export interface DashboardPayload {
  overview: OverviewPayload;
  presidential: PresidentialPayload;
  trends: TrendsPayload;
  regional: RegionalPayload;
  turnout: TurnoutPayload;
  assembly: AssemblyPayload;
  governorship: GovernorshipPayload;
  anomalies: AnomaliesPayload;
  demographics: DemographicsPayload;
  tribunal: TribunalPayload;
}

