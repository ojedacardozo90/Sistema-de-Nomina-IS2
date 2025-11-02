// src/utils/query.js
export function buildQuery(params = {}) {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== ""
  );
  if (!entries.length) return "";
  const qs = new URLSearchParams();
  for (const [k, v] of entries) qs.append(k, v);
  return `?${qs.toString()}`;
}
