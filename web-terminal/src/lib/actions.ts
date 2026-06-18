// Shared detail-rail actions (Trend + Market). Keeps "Add to Watchlist" and
// "Export" behaving identically on both surfaces (UI-consistency mandate §0.6).
import { listWatchlists, createWatchlist, addWatchItem, type WatchKind } from './auth'

// Add an entity to the member's first watchlist (creates "My Watchlist" if none).
// Same backend the mobile app uses, so the list is shared across surfaces.
export async function addToWatchlist(key: string, display: string, kind: WatchKind = 'topic'): Promise<string> {
  try {
    const lists = await listWatchlists()
    const target = lists?.[0]
    const id = target?.id ?? (await createWatchlist('My Watchlist')).id
    await addWatchItem(id, { key, display, kind })
    return `Added "${display}" to ${target?.name || 'My Watchlist'}`
  } catch {
    return 'Sign in to save to a watchlist'
  }
}

// Download a single entity's key fields as CSV (opens natively in Excel). Reliable,
// dependency-free — satisfies the "export to Excel" requirement for the detail rails.
export function exportEntityCsv(filename: string, rows: Array<[string, any]>) {
  const esc = (s: any) => `"${String(s ?? '').replace(/"/g, '""')}"`
  const csv = [['Field', 'Value'].join(','), ...rows.map(([k, v]) => [esc(k), esc(v)].join(','))].join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
  a.download = filename
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}
