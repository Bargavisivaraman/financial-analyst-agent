export function mdToHtml(md: string | undefined): string {
  if (!md) return "";
  return md
    .replace(/^### (.*$)/gim, "<h2>$1</h2>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/_(.*?)_/g, "<em>$1</em>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>");
}

export function fmtCap(n: number | null): string {
  if (!n) return "—";
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n}`;
}

export function fmtNum(n: number | null, suffix = ""): string {
  if (n === null || n === undefined) return "—";
  return `${n}${suffix}`;
}

export function fmtPct(n: number | null): string {
  if (n === null || n === undefined) return "—";
  const v = Math.abs(n) < 1 ? n * 100 : n; // handle ratios vs already-percent
  return `${v > 0 ? "+" : ""}${v.toFixed(1)}%`;
}
