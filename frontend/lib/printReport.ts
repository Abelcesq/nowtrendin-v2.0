import { Platform } from 'react-native';
import { Signal, scoreGap, contentCategoryMeta } from './signals';

/**
 * Print / export-to-PDF the FULL scored list as a clean report.
 *
 * Why this exists: the app renders inside a React-Native ScrollView, which on
 * web is a fixed-height overflow container — so the browser's native print only
 * captures the visible viewport ("1 sheet"), not the whole list. This renders
 * the entire dataset into a fresh, semantic HTML document (a table paginates
 * naturally across pages) in a new window and triggers print, so the user gets
 * the complete report as a PDF.
 *
 * Web-only; a no-op on native (where OS share/print would be wired separately).
 */
export function printSignalsReport(
  signals: Signal[],
  opts: { title?: string; subtitle?: string } = {},
): void {
  if (Platform.OS !== 'web' || typeof window === 'undefined') return;

  const esc = (s: unknown) =>
    String(s ?? '').replace(/[&<>"]/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] as string));

  const when = new Date().toLocaleString();
  const title = opts.title ?? 'Now TrendIn — Signal Report';
  const subtitle = opts.subtitle ?? `${signals.length} signals · generated ${when}`;

  const rows = signals
    .map((s, i) => {
      const cat = contentCategoryMeta(s.category);
      const gap = scoreGap(s);
      const platforms = (s.platforms ?? []).join(', ') || '—';
      return `<tr>
        <td class="num">${i + 1}</td>
        <td class="topic">${esc(s.topic)}</td>
        <td>${esc(cat.label)}</td>
        <td>${esc(s.stage)}</td>
        <td class="num det">${esc(s.detection)}</td>
        <td class="num conf">${esc(s.confidence)}</td>
        <td class="num">${esc(gap)}</td>
        <td class="num">${esc(s.nowTrending ?? 0)}</td>
        <td class="num">${esc(s.totalMentions ?? 0)}</td>
        <td class="src">${esc(platforms)}</td>
      </tr>`;
    })
    .join('');

  const html = `<!doctype html><html><head><meta charset="utf-8">
  <title>${esc(title)}</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
           color: #16264A; margin: 24px; }
    h1 { font-size: 18px; margin: 0 0 2px; }
    h1 .now { color: #B11226; } h1 .trend { color: #B11226; }
    .sub { color: #3C4663; font-size: 12px; margin: 0 0 16px; }
    table { width: 100%; border-collapse: collapse; font-size: 11px; }
    thead th { text-align: left; border-bottom: 2px solid #16264A; padding: 6px 8px;
               font-size: 9px; letter-spacing: .04em; text-transform: uppercase; color: #3C4663; }
    tbody td { padding: 6px 8px; border-bottom: 1px solid #ECECEC; vertical-align: top; }
    tbody tr:nth-child(even) { background: #F1F1F4; }
    .num { text-align: right; white-space: nowrap; }
    .topic { font-weight: 700; }
    .det { color: #2A5B9E; font-weight: 700; }
    .conf { color: #246B4A; font-weight: 700; }
    .src { color: #3C4663; max-width: 220px; }
    tfoot td { padding-top: 10px; color: #9A9AA2; font-size: 10px; }
    @media print {
      body { margin: 12mm; }
      thead { display: table-header-group; }   /* repeat header on every page */
      tr { page-break-inside: avoid; }
    }
  </style></head><body>
  <h1><span class="now">Now</span><span class="trend">TrendIn</span> — Signal Report</h1>
  <p class="sub">${esc(subtitle)}</p>
  <table>
    <thead><tr>
      <th>#</th><th>Topic</th><th>Category</th><th>Stage</th>
      <th>Det</th><th>Conf</th><th>Gap</th><th>N</th><th>Signals</th><th>Platforms</th>
    </tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td colspan="10">
      Gradient Score is proprietary to Now TrendIn LLC. Det = Detection (speed),
      Conf = Confidence (precision), N = Now TrendIn demand. Generated ${esc(when)}.
    </td></tr></tfoot>
  </table>
  <script>
    window.addEventListener('load', function () {
      setTimeout(function () { window.print(); }, 150);
    });
  </script>
  </body></html>`;

  const w = window.open('', '_blank');
  if (!w) {
    // Popup blocked — fall back to printing the current document.
    window.print();
    return;
  }
  w.document.open();
  w.document.write(html);
  w.document.close();
}
