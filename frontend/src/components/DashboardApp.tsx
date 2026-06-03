"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Building2,
  Home,
  Landmark,
  Map,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Users,
  Wifi,
  WifiOff,
  GraduationCap,
  Scale,
  TrendingUp,
} from "lucide-react";

import { BenfordChart, DonutChart, GroupedBars, HorizontalBars, LineChart, ScatterPlot, StackedRows } from "@/components/charts";
import { Badge, CountGrid, DataTable, InsightList, MetricGrid, Panel } from "@/components/ui";
import { fetchJson } from "@/lib/api";
import { compactNumber, pct } from "@/lib/format";
import type {
  AnomaliesPayload,
  ApiRecord,
  AssemblyPayload,
  ColorMap,
  DashboardPayload,
  FiltersPayload,
  GovernorshipPayload,
  OverviewPayload,
  PresidentialPayload,
  RegionalPayload,
  TrendsPayload,
  TurnoutPayload,
  DemographicsPayload,
  TribunalPayload,
  SimulationPayload,
} from "@/lib/types";

type ViewKey = "overview" | "presidential" | "trends" | "regional" | "turnout" | "assembly" | "governorship" | "anomalies" | "demographics" | "tribunal" | "simulator";

const ALL_ZONES = "All zones";

const NAV_ITEMS: Array<{ key: ViewKey; label: string; icon: LucideIcon; description: string }> = [
  { key: "overview", label: "Overview", icon: Home, description: "National picture" },
  { key: "presidential", label: "Presidential", icon: BarChart3, description: "National and state results" },
  { key: "trends", label: "Vote Trends", icon: Activity, description: "Party momentum" },
  { key: "regional", label: "Regional", icon: Map, description: "Geopolitical zones" },
  { key: "turnout", label: "Turnout", icon: Users, description: "Participation patterns" },
  { key: "assembly", label: "Assembly", icon: Landmark, description: "Senate and House" },
  { key: "governorship", label: "Governorship", icon: Building2, description: "State executives" },
  { key: "demographics", label: "Demographics", icon: GraduationCap, description: "Socio-economic analysis" },
  { key: "tribunal", label: "Tribunal cases", icon: Scale, description: "Post-election litigation" },
  { key: "simulator", label: "What-If Simulator", icon: TrendingUp, description: "Voter turnout simulator" },
  { key: "anomalies", label: "Anomalies", icon: ScanSearch, description: "Statistical flags" },
];

const FALLBACK_FILTERS: FiltersPayload = {
  years: [2023, 2019, 2015, 2011],
  stateYears: [2023, 2019, 2015],
  assemblyYears: [2023, 2019, 2015, 2011],
  zones: ["North Central", "North East", "North West", "South East", "South South", "South West"],
  parties: ["APC", "PDP", "LP", "NNPP", "Others"],
  partyColors: {
    APC: "#2fb36d",
    PDP: "#d94b4b",
    LP: "#f2b84b",
    NNPP: "#3f8fd2",
    Others: "#8a9387",
  },
  zoneColors: {},
  sources: [],
};

export function DashboardApp() {
  const [view, setView] = useState<ViewKey>("overview");
  const [year, setYear] = useState(2023);
  const [zone, setZone] = useState(ALL_ZONES);
  const [selectedState, setSelectedState] = useState("All states");
  const [selectedParties, setSelectedParties] = useState<string[]>(["APC", "PDP", "LP", "NNPP"]);
  const [filters, setFilters] = useState<FiltersPayload>(FALLBACK_FILTERS);
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshedAt, setRefreshedAt] = useState<Date | null>(null);

  const queryZones = useMemo(() => (zone === ALL_ZONES ? undefined : [zone]), [zone]);
  const queryParties = useMemo(() => (selectedParties.length ? selectedParties : undefined), [selectedParties]);
  
  const availableStates = useMemo(() => {
    // @ts-expect-error statesByZone may come from API but not in FiltersPayload type
    if (!filters.statesByZone) return filters.states || [];
    if (zone === ALL_ZONES) {
      // @ts-expect-error states may come from API but not in FiltersPayload type
      return filters.states || [];
    }
    // @ts-expect-error statesByZone may come from API but not in FiltersPayload type
    return filters.statesByZone[zone] || [];
  }, [filters, zone]);

  const loadFilters = useCallback(async (signal?: AbortSignal) => {
    const payload = await fetchJson<FiltersPayload>("/api/filters", undefined, signal);
    setFilters(payload);
  }, []);

  const loadData = useCallback(
    async (signal?: AbortSignal) => {
      setLoading(true);
      setError(null);
      try {
        const [overview, presidential, trends, regional, turnout, assembly, governorship, anomalies, demographics, tribunal] = await Promise.all([
          fetchJson<OverviewPayload>("/api/overview", undefined, signal),
          fetchJson<PresidentialPayload>("/api/presidential", { year, zones: queryZones, parties: queryParties }, signal),
          fetchJson<TrendsPayload>("/api/trends", { parties: queryParties }, signal),
          fetchJson<RegionalPayload>("/api/regional", { year, zones: queryZones }, signal),
          fetchJson<TurnoutPayload>("/api/turnout", undefined, signal),
          fetchJson<AssemblyPayload>("/api/assembly", { year }, signal),
          fetchJson<GovernorshipPayload>("/api/governorship", { zones: queryZones, parties: queryParties }, signal),
          fetchJson<AnomaliesPayload>("/api/anomalies", { year }, signal),
          fetchJson<DemographicsPayload>("/api/demographics", undefined, signal),
          fetchJson<TribunalPayload>("/api/tribunal", undefined, signal),
        ]);
        setData({ overview, presidential, trends, regional, turnout, assembly, governorship, anomalies, demographics, tribunal });
        setRefreshedAt(new Date());
      } catch (requestError) {
        if ((requestError as Error).name !== "AbortError") {
          setError((requestError as Error).message);
        }
      } finally {
        setLoading(false);
      }
    },
    [queryParties, queryZones, year]
  );


  useEffect(() => {
    const controller = new AbortController();
    loadFilters(controller.signal).catch(() => undefined);
    return () => controller.abort();
  }, [loadFilters]);

  useEffect(() => {
    const controller = new AbortController();
    loadData(controller.signal);
    return () => controller.abort();
  }, [loadData]);

  const partyColors = filters.partyColors;
  const visibleParties = useMemo(
    () => selectedParties.filter((party) => ["APC", "PDP", "LP", "NNPP"].includes(party)),
    [selectedParties]
  );

  const activeNav = NAV_ITEMS.find((item) => item.key === view) ?? NAV_ITEMS[0];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-kicker">Civic analytics</div>
          <h1>Nigeria Election Analytics</h1>
          <p>Presidential, gubernatorial, turnout, legislative, and anomaly intelligence.</p>
        </div>

        <nav className="nav-list" aria-label="Dashboard navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={`nav-button ${view === item.key ? "active" : ""}`}
                key={item.key}
                onClick={() => setView(item.key)}
                type="button"
                title={item.description}
              >
                <Icon aria-hidden />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <section className="filter-section">
          <div className="filter-stack">
            <h2>Filters</h2>
            <label className="filter-stack">
              <span className="field-label">Cycle</span>
              <div className="segments">
                {filters.stateYears.map((item) => (
                  <button
                    className={`segment-button ${year === item ? "active" : ""}`}
                    key={item}
                    onClick={() => setYear(item)}
                    type="button"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </label>

            <label className="filter-stack">
              <span className="field-label">Zone</span>
              <select 
                className="select" 
                value={zone} 
                onChange={(event) => {
                  setZone(event.target.value);
                  setSelectedState("All states");
                }}
              >
                <option>{ALL_ZONES}</option>
                {filters.zones.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <label className="filter-stack">
              <span className="field-label">State</span>
              <select 
                className="select" 
                value={selectedState} 
                onChange={(event) => setSelectedState(event.target.value)}
              >
                <option>All states</option>
                {availableStates.map((item: string) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <div className="filter-stack">
              <span className="field-label">Parties</span>
              <div className="party-grid">
                {["APC", "PDP", "LP", "NNPP"].map((party) => {
                  const active = selectedParties.includes(party);
                  return (
                    <button
                      className={`party-toggle ${active ? "active" : ""}`}
                      key={party}
                      onClick={() =>
                        setSelectedParties((current) =>
                          current.includes(party) ? current.filter((item) => item !== party) : [...current, party]
                        )
                      }
                      style={{ "--party-color": partyColors[party] } as React.CSSProperties}
                      type="button"
                    >
                      <span>{party}</span>
                      <span className="party-dot" />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </section>
      </aside>

      <section className="content">
        <header className="topbar">
          <div className="view-heading">
            <h2>{activeNav.label}</h2>
            <p>{activeNav.description}</p>
          </div>
          <div className="toolbar-actions">
            {refreshedAt ? <span className="status-pill">Updated {refreshedAt.toLocaleTimeString()}</span> : null}
            <button className="icon-button" type="button" onClick={() => loadData()} title="Refresh data">
              <RefreshCw size={17} />
            </button>
          </div>
        </header>

        {error ? <ErrorState message={error} /> : null}
        {!error && loading && !data ? <div className="empty-state">Loading election analytics...</div> : null}
        {!error && data ? (
          <DashboardViews
            data={data}
            view={view}
            year={year}
            partyColors={partyColors}
            selectedParties={visibleParties.length ? visibleParties : ["APC", "PDP", "LP", "NNPP"]}
          />
        ) : null}
      </section>
    </main>
  );
}

function DashboardViews({
  data,
  view,
  year,
  partyColors,
  selectedParties,
}: {
  data: DashboardPayload;
  view: ViewKey;
  year: number;
  partyColors: ColorMap;
  selectedParties: string[];
}) {
  if (view === "overview") {
    return <OverviewView payload={data.overview} partyColors={partyColors} />;
  }
  if (view === "presidential") {
    return <PresidentialView payload={data.presidential} partyColors={partyColors} selectedParties={selectedParties} />;
  }
  if (view === "trends") {
    return <TrendsView payload={data.trends} partyColors={partyColors} selectedParties={selectedParties} />;
  }
  if (view === "regional") {
    return <RegionalView payload={data.regional} partyColors={partyColors} selectedParties={selectedParties} />;
  }
  if (view === "turnout") {
    return <TurnoutView payload={data.turnout} />;
  }
  if (view === "assembly") {
    return <AssemblyView payload={data.assembly} partyColors={partyColors} selectedParties={selectedParties} year={year} />;
  }
  if (view === "governorship") {
    return <GovernorshipView payload={data.governorship} />;
  }
  if (view === "demographics") {
    return <DemographicsView payload={data.demographics} partyColors={partyColors} />;
  }
  if (view === "tribunal") {
    return <TribunalView payload={data.tribunal} />;
  }
  if (view === "simulator") {
    return <SimulatorView partyColors={partyColors} />;
  }
  return <AnomaliesView payload={data.anomalies} partyColors={partyColors} />;
}


function OverviewView({ payload, partyColors }: { payload: OverviewPayload; partyColors: ColorMap }) {
  const turnoutSeries = [
    {
      label: "Turnout",
      color: "#f2b84b",
      points: payload.turnoutTrend.map((row) => ({ x: row.Year as number, y: Number(row.Turnout_Pct) })),
    },
  ];

  return (
    <>
      <MetricGrid metrics={payload.kpis} />
      <section className="dashboard-grid">
        <Panel title="2023 presidential vote share" kicker="National result" span={5}>
          <DonutChart data={payload.voteShare2023} />
        </Panel>
        <Panel title="Turnout decline" kicker="2011-2023" span={7}>
          <LineChart series={turnoutSeries} yMax={65} valueFormat="percent" />
        </Panel>
        <Panel title="Election winners" kicker="Timeline" span={12}>
          <div className="timeline">
            {payload.timeline.map((row) => (
              <article className="timeline-card" key={String(row.Year)} style={{ borderColor: String(row.Color) }}>
                <div className="timeline-year">{row.Year}</div>
                <strong>{row.Winner}</strong>
                <Badge label={String(row.Party)} color={String(row.Color)} value={compactNumber(row.Votes as number)} />
                <div className="metric-delta">{pct(row.Turnout as number)} turnout</div>
              </article>
            ))}
          </div>
        </Panel>
        <Panel title="Zone vote concentration" kicker="2023 state results" span={8}>
          <GroupedBars data={payload.zoneSummary} groups={["APC", "PDP", "LP", "NNPP"]} colors={partyColors} />
        </Panel>
        <Panel title="Control snapshots" kicker="2023" span={4}>
          <div className="panel-list">
            <CountGrid rows={payload.stateWinCounts} />
            <CountGrid rows={payload.governorshipCounts} />
          </div>
        </Panel>
      </section>
    </>
  );
}

function PresidentialView({
  payload,
  partyColors,
  selectedParties,
}: {
  payload: PresidentialPayload;
  partyColors: ColorMap;
  selectedParties: string[];
}) {
  const summary = payload.summary;
  return (
    <>
      <MetricGrid
        metrics={[
          { label: "Winner", value: String(summary.Winner), delta: String(summary.Winner_Party) },
          { label: "Registered", value: Number(summary.Registered), delta: `${payload.year} register` },
          { label: "Votes cast", value: Number(summary.Total_Votes), delta: "National total" },
          { label: "Turnout", value: Number(summary.Turnout), suffix: "%", delta: "Accredited turnout" },
          { label: "State rows", value: payload.stateResults.length, delta: "Filtered coverage" },
        ]}
      />
      <section className="dashboard-grid">
        <Panel title={`${payload.year} national vote share`} kicker="Presidential" span={5}>
          <DonutChart data={payload.nationalResults} />
        </Panel>
        <Panel title="Top states by votes cast" kicker="State stack" span={7}>
          <StackedRows data={payload.topStates} parties={selectedParties} colors={partyColors} maxItems={15} />
        </Panel>
        <Panel title="Party wins by state" kicker="State winners" span={4}>
          <CountGrid rows={payload.partyWins} />
        </Panel>
        <Panel title="State breakdown" kicker="Filtered table" span={8}>
          <DataTable
            rows={payload.stateResults}
            columns={[
              { key: "State", label: "State" },
              { key: "Zone", label: "Zone" },
              { key: "Winner_Party", label: "Winner" },
              { key: "Total_Votes", label: "Total", format: "compact" },
              ...selectedParties.map((party) => ({ key: party, label: party, format: "compact" as const })),
            ]}
          />
        </Panel>
      </section>
    </>
  );
}

function TrendsView({
  payload,
  partyColors,
  selectedParties,
}: {
  payload: TrendsPayload;
  partyColors: ColorMap;
  selectedParties: string[];
}) {
  const shareSeries = selectedParties.map((party) => ({
    label: party,
    color: partyColors[party] ?? "#8a9387",
    points: payload.rows.filter((row) => row.Party === party).map((row) => ({ x: row.Year as number, y: Number(row.Pct) })),
  }));
  const voteSeries = selectedParties.map((party) => ({
    label: party,
    color: partyColors[party] ?? "#8a9387",
    points: payload.rows.filter((row) => row.Party === party).map((row) => ({ x: row.Year as number, y: Number(row.Votes) })),
  }));

  return (
    <section className="dashboard-grid">
      <Panel title="Vote share trajectory" kicker="Presidential cycles" span={7}>
        <LineChart series={shareSeries} yMax={65} valueFormat="percent" />
      </Panel>
      <Panel title="Absolute vote trajectory" kicker="Vote counts" span={5}>
        <LineChart series={voteSeries} valueFormat="compact" />
      </Panel>
      <Panel title="Party summaries" kicker="Peak vs latest" span={5}>
        <DataTable
          rows={payload.summaries}
          columns={[
            { key: "Party", label: "Party" },
            { key: "Peak_Year", label: "Peak" },
            { key: "Peak_Votes", label: "Peak votes", format: "compact" },
            { key: "Latest_Pct", label: "2023 share", format: "percent" },
          ]}
          maxRows={8}
        />
      </Panel>
      <Panel title="Analytical notes" kicker="Signals" span={7}>
        <InsightList rows={payload.insights} />
      </Panel>
    </section>
  );
}

function RegionalView({
  payload,
  partyColors,
  selectedParties,
}: {
  payload: RegionalPayload;
  partyColors: ColorMap;
  selectedParties: string[];
}) {
  return (
    <section className="dashboard-grid">
      <Panel title={`${payload.year} zone vote summary`} kicker="Grouped votes" span={7}>
        <GroupedBars data={payload.zoneSummary} groups={selectedParties} colors={partyColors} />
      </Panel>
      <Panel title="Dominant party per zone" kicker="Regional control" span={5}>
        <div className="panel-list">
          {payload.dominance.map((row) => (
            <article className="timeline-card" key={String(row.Zone)} style={{ borderColor: String(row.Color) }}>
              <div className="timeline-year">{row.Zone}</div>
              <strong>{row.Dominant_Party}</strong>
              <div className="metric-delta">
                {pct(row.Share as number)} share, {compactNumber(row.Votes as number)} votes
              </div>
            </article>
          ))}
        </div>
      </Panel>
      <Panel title="State vote mix" kicker="Within selected zone" span={8}>
        <StackedRows data={payload.stateResults} parties={selectedParties} colors={partyColors} maxItems={18} />
      </Panel>
      <Panel title="Regional notes" kicker="Context" span={4}>
        <div className="insight-list">
          {payload.notes.map((row) => (
            <div className="insight-item" key={String(row.Zone)} style={{ "--item-color": String(row.Color) } as React.CSSProperties}>
              <strong>{row.Zone}</strong>
              <p>{row.Note}</p>
            </div>
          ))}
        </div>
      </Panel>
    </section>
  );
}

function TurnoutView({ payload }: { payload: TurnoutPayload }) {
  const nationalSeries = [
    {
      label: "Registered",
      color: "#3f8fd2",
      points: payload.nationalTrend.map((row) => ({ x: row.Year as number, y: Number(row.Registered) })),
    },
    {
      label: "Votes cast",
      color: "#2fb36d",
      points: payload.nationalTrend.map((row) => ({ x: row.Year as number, y: Number(row.Votes_Cast) })),
    },
  ];
  const sortedState = [...payload.stateTurnout].sort((a, b) => Number(b.Turnout_Pct) - Number(a.Turnout_Pct));

  return (
    <>
      <MetricGrid
        metrics={[
          { label: "Highest state", value: String(payload.stats.Highest_State), delta: pct(payload.stats.Highest_Turnout as number) },
          { label: "Lowest state", value: String(payload.stats.Lowest_State), delta: pct(payload.stats.Lowest_Turnout as number) },
          { label: "State mean", value: Number(payload.stats.Mean_State_Turnout), suffix: "%", delta: "2023 accreditation" },
          { label: "Drop", value: Number(payload.stats.National_Drop_Points), suffix: "%", delta: "2011 to 2023" },
          { label: "States", value: sortedState.length, delta: "Includes FCT" },
        ]}
      />
      <section className="dashboard-grid">
        <Panel title="Registered voters vs votes cast" kicker="National trend" span={7}>
          <LineChart series={nationalSeries} valueFormat="compact" />
        </Panel>
        <Panel title="Zone turnout" kicker="2023 average" span={5}>
          <HorizontalBars data={payload.zoneTurnout} labelKey="Zone" valueKey="Turnout_Pct" maxItems={6} valueFormat="percent" />
        </Panel>
        <Panel title="State accreditation rates" kicker="2023" span={12}>
          <HorizontalBars data={sortedState} labelKey="State" valueKey="Turnout_Pct" maxItems={18} valueFormat="percent" />
        </Panel>
      </section>
    </>
  );
}

function AssemblyView({
  payload,
  partyColors,
  selectedParties,
  year,
}: {
  payload: AssemblyPayload;
  partyColors: ColorMap;
  selectedParties: string[];
  year: number;
}) {
  const senateSeries = selectedParties.map((party) => ({
    label: party,
    color: partyColors[party] ?? "#8a9387",
    points: payload.trend
      .filter((row) => row.Chamber === "Senate" && row.Party === party)
      .map((row) => ({ x: row.Year as number, y: Number(row.Seats) })),
  }));
  const houseSeries = selectedParties.map((party) => ({
    label: party,
    color: partyColors[party] ?? "#8a9387",
    points: payload.trend
      .filter((row) => row.Chamber === "House" && row.Party === party)
      .map((row) => ({ x: row.Year as number, y: Number(row.Seats) })),
  }));

  return (
    <section className="dashboard-grid">
      <Panel title={`${year} chamber composition`} kicker="Seats" span={12}>
        <div className="chamber-grid">
          {payload.chambers.map((chamber) => (
            <div className="compact-panel" key={chamber.Chamber}>
              <div className="panel-header">
                <div>
                  <div className="panel-kicker">{chamber.Total_Seats} seats</div>
                  <h2>{chamber.Chamber}</h2>
                </div>
                <Badge label={chamber.Has_Majority ? "Majority" : "Plurality"} color={partyColors[chamber.Largest_Party]} />
              </div>
              <HorizontalBars data={chamber.Parties} labelKey="Party" valueKey="Seats" maxItems={8} valueFormat="number" />
              <div className="metric-delta">Majority threshold: {chamber.Majority}</div>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Senate trend" kicker="2011-2023" span={6}>
        <LineChart series={senateSeries} yMax={80} valueFormat="number" />
      </Panel>
      <Panel title="House trend" kicker="2011-2023" span={6}>
        <LineChart series={houseSeries} yMax={260} valueFormat="number" />
      </Panel>
    </section>
  );
}

function GovernorshipView({ payload }: { payload: GovernorshipPayload }) {
  const rows = payload.records.map<ApiRecord>((row) => ({ ...row, Color: colorForParty(String(row.Party)) }));
  return (
    <section className="dashboard-grid">
      <Panel title="Party control" kicker={`${payload.year} governorship`} span={4}>
        <CountGrid rows={payload.partyCounts} />
      </Panel>
      <Panel title="Winning votes by state" kicker="2023" span={8}>
        <HorizontalBars data={[...rows].sort((a, b) => Number(b.Votes) - Number(a.Votes))} labelKey="State" valueKey="Votes" maxItems={18} />
      </Panel>
      <Panel title="State executives" kicker="Complete table" span={12}>
        <DataTable
          rows={payload.records}
          columns={[
            { key: "State", label: "State" },
            { key: "Zone", label: "Zone" },
            { key: "Governor", label: "Governor" },
            { key: "Party", label: "Party" },
            { key: "Votes", label: "Votes", format: "number" },
          ]}
          maxRows={20}
        />
      </Panel>
    </section>
  );
}

function AnomaliesView({ payload, partyColors }: { payload: AnomaliesPayload; partyColors: ColorMap }) {
  const flaggedMargins = payload.marginSpikes.filter((row) => row.Margin_Flag !== "Normal");
  return (
    <section className="dashboard-grid">
      <Panel title="Statistical caveat" kicker={`${payload.year} anomaly model`} span={12}>
        <div className="status-pill">
          <ShieldCheck size={15} />
          {payload.disclaimer}
        </div>
      </Panel>
      <Panel title="Benford first-digit test" kicker={payload.benford.conformity} span={5}>
        <div className="metric-card" style={{ marginBottom: 12 }}>
          <div className="metric-label">Chi-square deviation</div>
          <div className="metric-value">{payload.benford.chiSquare.toFixed(2)}</div>
          <div className="metric-delta">{payload.benford.conformity}</div>
        </div>
        <BenfordChart rows={payload.benford.rows} />
      </Panel>
      <Panel title="Margin spikes" kicker="Winner vs runner-up" span={7}>
        <ScatterPlot data={payload.marginSpikes} xKey="Margin" yKey="Margin_Pct" labelKey="State" colorMap={partyColors} />
      </Panel>
      <Panel title="Flagged margins" kicker="High signal states" span={6}>
        <DataTable
          rows={flaggedMargins}
          columns={[
            { key: "State", label: "State" },
            { key: "Zone", label: "Zone" },
            { key: "Winner_Party", label: "Winner" },
            { key: "Margin_Pct", label: "Margin", format: "percent" },
            { key: "Margin_Flag", label: "Flag" },
          ]}
          maxRows={10}
        />
      </Panel>
      <Panel title="Known incident report" kicker="Contextual flags" span={6}>
        <div className="panel-list">
          {payload.knownAnomalies.map((row) => {
            const color = severityColor(String(row.Severity));
            return (
              <article className="anomaly-row" key={String(row.Title)} style={{ borderColor: color }}>
                <span className="severity" style={{ "--severity-color": color } as React.CSSProperties}>
                  {row.Severity}
                </span>
                <strong>{row.Title}</strong>
                <div className="metric-delta">{row.Description}</div>
              </article>
            );
          })}
        </div>
      </Panel>
    </section>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="error-state">
      <div>
        <strong>Backend connection failed</strong>
        <p>{message}</p>
      </div>
    </div>
  );
}

function colorForParty(party: string): string {
  const map: ColorMap = {
    APC: "#2fb36d",
    PDP: "#d94b4b",
    LP: "#f2b84b",
    NNPP: "#3f8fd2",
    APGA: "#d9469f",
  };
  return map[party] ?? "#8a9387";
}

function severityColor(severity: string): string {
  if (severity === "Critical") {
    return "#d94b4b";
  }
  if (severity === "High") {
    return "#f2b84b";
  }
  if (severity === "Positive") {
    return "#2fb36d";
  }
  return "#3f8fd2";
}

function DemographicsView({
  payload,
}: {
  payload: DemographicsPayload;
  partyColors?: ColorMap;
}) {
  const correlationMap = [
    { label: "Literacy vs Voter Turnout", value: payload.correlation.literacy_turnout, desc: "A positive value indicates that highly literate states had higher turnout." },
    { label: "Poverty Rate vs Turnout", value: payload.correlation.poverty_turnout, desc: "Shows if economically disadvantaged regions had higher/lower turnout rates." },
    { label: "State GDP vs Turnout", value: payload.correlation.gdp_turnout, desc: "Correlates total economic output with state participation." },
    { label: "Literacy vs Labour Party (LP) Share", value: payload.correlation.literacy_lp, desc: "Measures correlation of state literacy with third-party surge." },
    { label: "Poverty vs APC Vote Share", value: payload.correlation.poverty_apc, desc: "Measures poverty rates against the ruling party vote share." },
  ];

  return (
    <section className="dashboard-grid">
      <Panel title="Socio-Economic Correlations" kicker="Pearson R coefficient" span={5}>
        <div className="panel-list">
          {correlationMap.map((c) => (
            <div className="compact-panel" key={c.label} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>{c.label}</strong>
                <span className={`status-pill ${c.value > 0.4 ? "online" : c.value < -0.4 ? "offline" : ""}`} style={{ fontSize: 13, fontWeight: "bold" }}>
                  {c.value > 0 ? `+${c.value}` : c.value}
                </span>
              </div>
              <p style={{ fontSize: 12, opacity: 0.8, marginTop: 4 }}>{c.desc}</p>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Demographic and Election Layer" kicker="2023 cycle data" span={7}>
        <DataTable
          rows={payload.records}
          columns={[
            { key: "State", label: "State" },
            { key: "Zone", label: "Geopolitical Zone" },
            { key: "Literacy_Rate", label: "Literacy %", format: "percent" },
            { key: "Poverty_Rate", label: "Poverty %", format: "percent" },
            { key: "GDP_Billion", label: "GDP (Billion ₦)" },
            { key: "Turnout_Pct", label: "Turnout %", format: "percent" },
          ]}
          maxRows={50}
        />
      </Panel>
    </section>
  );
}

function TribunalView({ payload }: { payload: TribunalPayload }) {
  const [filterSeat, setFilterSeat] = useState<string>("All");
  const filteredCases = useMemo(() => {
    if (filterSeat === "All") return payload.cases;
    return payload.cases.filter((c) => c.seat === filterSeat);
  }, [payload.cases, filterSeat]);

  return (
    <section className="dashboard-grid">
      <Panel title="Litigation Timeline & Status" kicker="Post-election dispute cases" span={12}>
        <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
          {["All", "Presidential", "Governorship", "Senate"].map((seat) => (
            <button
              className={`segment-button ${filterSeat === seat ? "active" : ""}`}
              key={seat}
              onClick={() => setFilterSeat(seat)}
              type="button"
            >
              {seat}
            </button>
          ))}
        </div>
        <div className="panel-list">
          {filteredCases.map((row, idx) => {
            const color = severityColor(row.severity === "Critical" ? "Critical" : row.severity === "High" ? "High" : row.severity === "Positive" ? "Positive" : "Medium");
            return (
              <article className="anomaly-row" key={`${row.state}-${row.petitioner}-${idx}`} style={{ borderColor: color, padding: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <strong>{row.petitioner} vs. {row.respondent}</strong>
                  <Badge label={row.status} color={color} value={row.state} />
                </div>
                <div style={{ fontSize: 13, marginBottom: 6 }}>
                  <strong>Court Arguments:</strong> {row.arguments}
                </div>
                <div style={{ fontSize: 13 }}>
                  <strong>Final Judicial Ruling:</strong> {row.outcome}
                </div>
                <div style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>
                  Judged on {row.date} • Seat: {row.seat}
                </div>
              </article>
            );
          })}
        </div>
      </Panel>
    </section>
  );
}

function SimulatorView({ partyColors }: { partyColors: ColorMap }) {
  const [zoneTurnout, setZoneTurnout] = useState<Record<string, number>>({
    "North Central": 27.1,
    "North East": 27.1,
    "North West": 27.1,
    "South East": 27.1,
    "South South": 27.1,
    "South West": 27.1,
  });

  const [partySwing, setPartySwing] = useState<Record<string, number>>({
    APC: 0,
    PDP: 0,
    LP: 0,
    NNPP: 0,
  });

  const [simResults, setSimResults] = useState<SimulationPayload | null>(null);

  const zones = ["North Central", "North East", "North West", "South East", "South South", "South West"];
  const parties = ["APC", "PDP", "LP", "NNPP"];

  const runSimulation = useCallback(async () => {
    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zoneTurnoutAdjustments: zoneTurnout,
          partySwing: partySwing,
        }),
      });
      const json = (await res.json()) as SimulationPayload;
      setSimResults(json);
    } catch (e) {
      console.error(e);
    } finally {
    }
  }, [zoneTurnout, partySwing]);

  useEffect(() => {
    runSimulation();
  }, [zoneTurnout, partySwing, runSimulation]);

  const simulatedShareData = useMemo(() => {
    if (!simResults) return [];
    return Object.entries(simResults.results).map(([party, votes]) => ({
      Party: party,
      Votes: votes as number,
      Color: partyColors[party] ?? "#8a9387",
    }));
  }, [simResults, partyColors]);

  return (
    <section className="dashboard-grid">
      <Panel title="1. Voter Turnout Slider per Geopolitical Zone" kicker="Simulate turnout percentage adjustments" span={6}>
        <div style={{ display: "flex", flexDirection: "column", gap: 15 }}>
          {zones.map((zone) => (
            <div key={zone} style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                <span>{zone}</span>
                <strong>{zoneTurnout[zone]}%</strong>
              </div>
              <input
                type="range"
                min="5"
                max="90"
                step="0.5"
                value={zoneTurnout[zone]}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setZoneTurnout((prev) => ({ ...prev, [zone]: val }));
                }}
                style={{ width: "100%" }}
              />
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="2. Voter Swing Percentage" kicker="Simulate swings (+ gains, - losses)" span={6}>
        <div style={{ display: "flex", flexDirection: "column", gap: 15 }}>
          {parties.map((party) => (
            <div key={party} style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                <span>{party} Swing</span>
                <strong style={{ color: partySwing[party] > 0 ? "#2fb36d" : partySwing[party] < 0 ? "#d94b4b" : "inherit" }}>
                  {partySwing[party] > 0 ? `+${partySwing[party]}` : partySwing[party]}%
                </strong>
              </div>
              <input
                type="range"
                min="-50"
                max="100"
                step="1"
                value={partySwing[party]}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  setPartySwing((prev) => ({ ...prev, [party]: val }));
                }}
                style={{ width: "100%" }}
              />
            </div>
          ))}
          <button
            className="segment-button active"
            style={{ marginTop: 15, padding: "10px", width: "100%" }}
            onClick={() => {
              setZoneTurnout({
                "North Central": 27.1,
                "North East": 27.1,
                "North West": 27.1,
                "South East": 27.1,
                "South South": 27.1,
                "South West": 27.1,
              });
              setPartySwing({ APC: 0, PDP: 0, LP: 0, NNPP: 0 });
            }}
            type="button"
          >
            Reset to Actual 2023 Results
          </button>
        </div>
      </Panel>

      <Panel title="3. Simulated Outcome" kicker="Dynamic election simulation model" span={12}>
        {simResults ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 15 }}>
              <div className="compact-panel" style={{ textAlign: "center" }}>
                <span className="field-label">Simulated Winner</span>
                <h3 style={{ fontSize: 24, margin: "8px 0" }}>{simResults.winner_party}</h3>
                <Badge label="Projected" color={partyColors[simResults.winner_party]} />
              </div>
              <div className="compact-panel" style={{ textAlign: "center" }}>
                <span className="field-label">Simulated Total Votes</span>
                <h3 style={{ fontSize: 24, margin: "8px 0" }}>{compactNumber(simResults.total_votes)}</h3>
                <span className="metric-delta">Cast nationally</span>
              </div>
              {parties.map((p) => (
                <div className="compact-panel" key={p} style={{ textAlign: "center" }}>
                  <span className="field-label">{p} Simulated Share</span>
                  <h3 style={{ fontSize: 24, margin: "8px 0" }}>{simResults.pct[p]}%</h3>
                  <span className="metric-delta">{compactNumber(simResults.results[p])} votes</span>
                </div>
              ))}
            </div>

            <div style={{ maxWidth: 500, margin: "0 auto", width: "100%" }}>
              <DonutChart data={simulatedShareData} />
            </div>

            <div>
              <h3 style={{ marginBottom: 12 }}>Simulated Regional Details</h3>
              <DataTable
                rows={simResults.zone_results}
                columns={[
                  { key: "Zone", label: "Geopolitical Zone" },
                  { key: "Total_Votes", label: "Simulated Total", format: "compact" },
                  { key: "APC", label: "APC", format: "compact" },
                  { key: "PDP", label: "PDP", format: "compact" },
                  { key: "LP", label: "LP", format: "compact" },
                  { key: "NNPP", label: "NNPP", format: "compact" },
                ]}
              />
            </div>
          </div>
        ) : (
          <div className="empty-state">Calculating simulation...</div>
        )}
      </Panel>
    </section>
  );
}

