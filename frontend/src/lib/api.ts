type ParamValue = string | number | string[] | number[] | undefined;

function toSearchParams(params?: Record<string, ParamValue>): string {
  if (!params) {
    return "";
  }
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) {
      continue;
    }
    if (Array.isArray(value)) {
      for (const item of value) {
        search.append(key, String(item));
      }
    } else {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function fetchJson<T>(
  path: string,
  params?: Record<string, ParamValue>,
  signal?: AbortSignal
): Promise<T> {
  const response = await fetch(`${path}${toSearchParams(params)}`, {
    headers: { accept: "application/json" },
    cache: "no-store",
    signal,
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}
