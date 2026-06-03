export function compactNumber(value: number | string | null | undefined): string {
  const numeric = Number(value ?? 0);
  if (!Number.isFinite(numeric)) {
    return "0";
  }
  return new Intl.NumberFormat("en", {
    notation: Math.abs(numeric) >= 1000000 ? "compact" : "standard",
    maximumFractionDigits: Math.abs(numeric) >= 1000000 ? 1 : 0,
  }).format(numeric);
}

export function fullNumber(value: number | string | null | undefined): string {
  const numeric = Number(value ?? 0);
  if (!Number.isFinite(numeric)) {
    return "0";
  }
  return new Intl.NumberFormat("en").format(numeric);
}

export function pct(value: number | string | null | undefined, digits = 1): string {
  const numeric = Number(value ?? 0);
  return `${Number.isFinite(numeric) ? numeric.toFixed(digits) : "0.0"}%`;
}

export function metricValue(value: number | string | null | undefined, suffix?: string): string {
  if (typeof value === "string") {
    return `${value}${suffix ?? ""}`;
  }
  if (suffix === "%") {
    return pct(value);
  }
  return compactNumber(value);
}
