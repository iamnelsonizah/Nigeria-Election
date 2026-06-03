"use client";

import type { ApiRecord, KpiPayload } from "@/lib/types";
import { compactNumber, fullNumber, metricValue } from "@/lib/format";

export function MetricGrid({ metrics }: { metrics: KpiPayload[] }) {
  return (
    <section className="metric-grid" aria-label="Dashboard metrics">
      {metrics.map((metric) => (
        <article className="metric-card" key={metric.label}>
          <div className="metric-label">{metric.label}</div>
          <div className="metric-value">{metricValue(metric.value, metric.suffix)}</div>
          <div className="metric-delta">{metric.delta}</div>
        </article>
      ))}
    </section>
  );
}

export function Panel({
  title,
  kicker,
  span = 6,
  children,
}: {
  title: string;
  kicker?: string;
  span?: 4 | 5 | 6 | 7 | 8 | 12;
  children: React.ReactNode;
}) {
  return (
    <section className={`panel span-${span}`}>
      <header className="panel-header">
        <div>
          {kicker ? <div className="panel-kicker">{kicker}</div> : null}
          <h2>{title}</h2>
        </div>
      </header>
      {children}
    </section>
  );
}

export function Badge({
  label,
  color,
  value,
}: {
  label: string;
  color?: string;
  value?: string | number;
}) {
  return (
    <span className="badge" style={{ borderColor: color, color }}>
      {color ? <span className="legend-dot" style={{ background: color }} /> : null}
      <span>{label}</span>
      {value !== undefined ? <strong>{value}</strong> : null}
    </span>
  );
}

export function CountGrid({
  rows,
  labelKey = "Party",
  valueKey = "Count",
}: {
  rows: ApiRecord[];
  labelKey?: string;
  valueKey?: string;
}) {
  return (
    <div className="count-grid">
      {rows.map((row) => {
        const label = String(row[labelKey] ?? "");
        const color = String(row.Color ?? "#2fb36d");
        return (
          <article
            className="count-card"
            key={`${label}-${row[valueKey]}`}
            style={{ "--party-color": color } as React.CSSProperties}
          >
            <div className="count-value">{compactNumber(row[valueKey] as number)}</div>
            <strong>{label}</strong>
          </article>
        );
      })}
    </div>
  );
}

export function DataTable({
  rows,
  columns,
  maxRows = 12,
}: {
  rows: ApiRecord[];
  columns: Array<{ key: string; label: string; format?: "number" | "compact" | "percent" }>;
  maxRows?: number;
}) {
  const visibleRows = rows.slice(0, maxRows);
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visibleRows.map((row, index) => (
            <tr key={`${row.State ?? row.Party ?? row.Zone ?? "row"}-${index}`}>
              {columns.map((column) => (
                <td key={column.key}>{formatCell(row[column.key], column.format)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(value: unknown, format?: "number" | "compact" | "percent"): string {
  if (format === "number") {
    return fullNumber(value as number);
  }
  if (format === "compact") {
    return compactNumber(value as number);
  }
  if (format === "percent") {
    return `${Number(value ?? 0).toFixed(1)}%`;
  }
  return String(value ?? "");
}

export function InsightList({
  rows,
  color = "#f2b84b",
}: {
  rows: Array<{ title: string; detail: string }>;
  color?: string;
}) {
  return (
    <div className="insight-list">
      {rows.map((row) => (
        <div className="insight-item" key={row.title} style={{ "--item-color": color } as React.CSSProperties}>
          <strong>{row.title}</strong>
          <p>{row.detail}</p>
        </div>
      ))}
    </div>
  );
}
