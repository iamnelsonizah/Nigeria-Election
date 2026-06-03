"use client";

import type { ApiRecord, ColorMap } from "@/lib/types";
import { compactNumber, fullNumber, pct } from "@/lib/format";

function asNumber(value: unknown): number {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
}

function asText(value: unknown): string {
  return String(value ?? "");
}

export function DonutChart({
  data,
  valueKey = "Votes",
  labelKey = "Party",
}: {
  data: ApiRecord[];
  valueKey?: string;
  labelKey?: string;
}) {
  const total = data.reduce((sum, item) => sum + asNumber(item[valueKey]), 0);
  let cursor = 0;
  const gradient = data
    .map((item) => {
      const start = cursor;
      const slice = total ? (asNumber(item[valueKey]) / total) * 100 : 0;
      cursor += slice;
      const color = asText(item.Color) || "#8a9387";
      return `${color} ${start}% ${cursor}%`;
    })
    .join(", ");

  return (
    <div className="donut-wrap chart-box">
      <div className="donut" style={{ background: `conic-gradient(${gradient || "#38402f 0% 100%"})` }}>
        <div className="donut-hole">{compactNumber(total)}</div>
      </div>
      <div className="legend">
        {data.map((item) => {
          const value = asNumber(item[valueKey]);
          const color = asText(item.Color) || "#8a9387";
          return (
            <div className="legend-row" key={asText(item[labelKey])}>
              <span className="legend-dot" style={{ background: color }} />
              <span>{asText(item[labelKey])}</span>
              <strong>{pct(total ? (value / total) * 100 : 0)}</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function LineChart({
  series,
  yMax,
  valueFormat = "compact",
}: {
  series: Array<{ label: string; color: string; points: Array<{ x: string | number; y: number }> }>;
  yMax?: number;
  valueFormat?: "compact" | "percent" | "number";
}) {
  const width = 720;
  const height = 280;
  const pad = { top: 18, right: 18, bottom: 36, left: 52 };
  const allPoints = series.flatMap((item) => item.points);
  const labels = Array.from(new Set(allPoints.map((point) => String(point.x))));
  const maxY = yMax ?? Math.max(1, ...allPoints.map((point) => point.y));
  const xStep = labels.length > 1 ? (width - pad.left - pad.right) / (labels.length - 1) : 1;
  const yScale = (value: number) => height - pad.bottom - (value / maxY) * (height - pad.top - pad.bottom);
  const xScale = (label: string) => pad.left + labels.indexOf(label) * xStep;

  return (
    <svg className="svg-chart" viewBox={`0 0 ${width} ${height}`} role="img">
      {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
        const y = yScale(maxY * tick);
        return (
          <g key={tick}>
            <line className="chart-grid-line" x1={pad.left} x2={width - pad.right} y1={y} y2={y} />
            <text className="axis-label" x={6} y={y + 4}>
              {formatValue(maxY * tick, valueFormat)}
            </text>
          </g>
        );
      })}
      {labels.map((label) => (
        <text className="axis-label" key={label} x={xScale(label)} y={height - 10} textAnchor="middle">
          {label}
        </text>
      ))}
      {series.map((item) => {
        const d = item.points
          .map((point, index) => `${index === 0 ? "M" : "L"} ${xScale(String(point.x))} ${yScale(point.y)}`)
          .join(" ");
        return (
          <g key={item.label}>
            <path d={d} fill="none" stroke={item.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            {item.points.map((point) => (
              <circle key={`${item.label}-${point.x}`} cx={xScale(String(point.x))} cy={yScale(point.y)} r="4.5" fill={item.color} />
            ))}
          </g>
        );
      })}
    </svg>
  );
}

export function StackedRows({
  data,
  parties,
  colors,
  maxItems = 12,
  titleKey = "State",
  totalKey = "Total_Votes",
}: {
  data: ApiRecord[];
  parties: string[];
  colors: ColorMap;
  maxItems?: number;
  titleKey?: string;
  totalKey?: string;
}) {
  return (
    <div className="stacked-list">
      {data.slice(0, maxItems).map((row) => {
        const total = asNumber(row[totalKey]) || parties.reduce((sum, party) => sum + asNumber(row[party]), 0);
        return (
          <div className="stacked-row" key={`${row[titleKey]}-${row.Zone ?? ""}`}>
            <div className="row-meta">
              <span className="row-title">{asText(row[titleKey])}</span>
              <span>{compactNumber(total)}</span>
            </div>
            <div className="stacked-track">
              {parties.map((party) => {
                const value = asNumber(row[party]);
                const width = total ? (value / total) * 100 : 0;
                return (
                  <span
                    className="stacked-segment"
                    key={party}
                    title={`${party}: ${fullNumber(value)}`}
                    style={{ width: `${width}%`, background: colors[party] ?? "#8a9387" }}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function HorizontalBars({
  data,
  labelKey,
  valueKey,
  colorKey = "Color",
  maxItems = 12,
  valueFormat = "compact",
}: {
  data: ApiRecord[];
  labelKey: string;
  valueKey: string;
  colorKey?: string;
  maxItems?: number;
  valueFormat?: "compact" | "percent" | "number";
}) {
  const rows = data.slice(0, maxItems);
  const max = Math.max(1, ...rows.map((row) => asNumber(row[valueKey])));
  return (
    <div className="bar-list">
      {rows.map((row) => {
        const value = asNumber(row[valueKey]);
        const color = asText(row[colorKey]) || "#2fb36d";
        return (
          <div className="bar-row" key={`${row[labelKey]}-${value}`}>
            <div className="row-meta">
              <span className="row-title">{asText(row[labelKey])}</span>
              <span>{formatValue(value, valueFormat)}</span>
            </div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${(value / max) * 100}%`, "--bar-color": color } as React.CSSProperties}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function GroupedBars({
  data,
  groups,
  colors,
  labelKey = "Zone",
  maxItems = 8,
}: {
  data: ApiRecord[];
  groups: string[];
  colors: ColorMap;
  labelKey?: string;
  maxItems?: number;
}) {
  const max = Math.max(1, ...data.flatMap((row) => groups.map((group) => asNumber(row[group]))));
  return (
    <div className="bar-list">
      {data.slice(0, maxItems).map((row) => (
        <div className="bar-row" key={asText(row[labelKey])}>
          <div className="row-meta">
            <span className="row-title">{asText(row[labelKey])}</span>
            <span>{compactNumber(row.Total_Votes as number)}</span>
          </div>
          {groups.map((group) => {
            const value = asNumber(row[group]);
            return (
              <div className="bar-track" key={group} title={`${group}: ${fullNumber(value)}`}>
                <div
                  className="bar-fill"
                  style={{
                    width: `${(value / max) * 100}%`,
                    "--bar-color": colors[group] ?? "#8a9387",
                  } as React.CSSProperties}
                />
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

export function ScatterPlot({
  data,
  xKey,
  yKey,
  labelKey,
  colorMap,
  colorKey = "Winner_Party",
  maxItems = 40,
}: {
  data: ApiRecord[];
  xKey: string;
  yKey: string;
  labelKey: string;
  colorMap: ColorMap;
  colorKey?: string;
  maxItems?: number;
}) {
  const width = 720;
  const height = 280;
  const pad = { top: 20, right: 18, bottom: 34, left: 48 };
  const rows = data.slice(0, maxItems);
  const maxX = Math.max(1, ...rows.map((row) => asNumber(row[xKey])));
  const maxY = Math.max(1, ...rows.map((row) => asNumber(row[yKey])));
  const xScale = (value: number) => pad.left + (value / maxX) * (width - pad.left - pad.right);
  const yScale = (value: number) => height - pad.bottom - (value / maxY) * (height - pad.top - pad.bottom);

  return (
    <svg className="svg-chart" viewBox={`0 0 ${width} ${height}`} role="img">
      {[0, 0.5, 1].map((tick) => (
        <g key={tick}>
          <line
            className="chart-grid-line"
            x1={pad.left}
            x2={width - pad.right}
            y1={yScale(maxY * tick)}
            y2={yScale(maxY * tick)}
          />
          <text className="axis-label" x={8} y={yScale(maxY * tick) + 4}>
            {pct(maxY * tick)}
          </text>
        </g>
      ))}
      {rows.map((row) => {
        const color = colorMap[asText(row[colorKey])] ?? "#8a9387";
        const x = xScale(asNumber(row[xKey]));
        const y = yScale(asNumber(row[yKey]));
        return (
          <g key={asText(row[labelKey])}>
            <circle cx={x} cy={y} r="7" fill={color} opacity="0.88" />
            <title>{`${asText(row[labelKey])}: ${pct(row[yKey] as number)}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

export function BenfordChart({ rows }: { rows: ApiRecord[] }) {
  const max = 35;
  return (
    <div className="bar-list">
      {rows.map((row) => {
        const observed = asNumber(row.Observed);
        const expected = asNumber(row.Expected);
        return (
          <div className="bar-row" key={String(row.Digit)}>
            <div className="row-meta">
              <span className="row-title">Digit {row.Digit}</span>
              <span>
                {pct(observed)} / {pct(expected)}
              </span>
            </div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(observed / max) * 100}%`, "--bar-color": "#3f8fd2" } as React.CSSProperties} />
            </div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(expected / max) * 100}%`, "--bar-color": "#f2b84b" } as React.CSSProperties} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function formatValue(value: number, format: "compact" | "percent" | "number"): string {
  if (format === "percent") {
    return pct(value);
  }
  if (format === "number") {
    return fullNumber(value);
  }
  return compactNumber(value);
}
