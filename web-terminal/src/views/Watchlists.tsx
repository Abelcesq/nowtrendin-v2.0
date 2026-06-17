import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import {
  listWatchlists, createWatchlist, deleteWatchlist,
  addWatchItem, removeWatchItem, type WatchlistT, type WatchKind,
} from '../lib/auth'

// Watchlists — backend-synced per-user lists (same API the mobile app uses).
// Items store key/display/kind only; we look up LIVE Detection/Confidence here
// so scores are never stale. Trends use stage (BREAKOUT…), Market uses tier.

interface Live { det: number; conf: number; label: string; kind: WatchKind }

function gapMicro(det: number, conf: number) {
  const W = 70, x = (v: number) => 4 + (v / 100) * (W - 8)
  const lo = Math.min(det, conf), hi = Math.max(det, conf)
  const wide = Math.abs(det - conf) >= 20, col = wide ? 'var(--early)' : '#aab4c1'
  return (
    <svg width={W} height="16" viewBox={`0 0 ${W} 16`}>
      <line x1={x(lo)} y1="8" x2={x(hi)} y2="8" stroke={col} strokeWidth={wide ? 2.5 : 1.5} />
      <circle cx={x(det)} cy="8" r="3" fill="var(--det)" />
      <circle cx={x(conf)} cy="8" r="3" fill="var(--conf)" />
    </svg>
  )
}
const stageOf = (d: number) => d >= 85 ? 'BREAKOUT' : d >= 70 ? 'STRONG' : d >= 55 ? 'EMERGING' : d >= 35 ? 'MARGINAL' : 'MONITORING'

export function Watchlists() {
  const [lists, setLists] = useState<WatchlistT[]>([])
  const [live, setLive] = useState<Record<string, Live>>({})
  const [active, setActive] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [adding, setAdding] = useState('')
  const [busy, setBusy] = useState(false)

  // live score lookup table, keyed by `${kind}:${key}`
  const liveKey = (kind: string, key: string) => `${kind}:${key.toLowerCase()}`

  const load = async () => {
    setErr(null)
    try {
      const [wls, topics, risk] = await Promise.all([
        listWatchlists(),
        api.topics(400).catch(() => ({ topics: [] as any[] })),
        api.risk(200).catch(() => ({ results: [] as any[] })),
      ])
      const map: Record<string, Live> = {}
      for (const t of (topics.topics || [])) {
        const det = Math.round(t.detection_score ?? 0), conf = Math.round(t.confidence_score ?? 0)
        map[liveKey('topic', t.topic_key)] = { det, conf, label: t.topic_display || t.topic_key, kind: 'topic' }
      }
      for (const r of (risk.results || [])) {
        const mg = r.market_gradient || {}
        const det = Math.round(mg.detection ?? r.detection_score ?? 0)
        const conf = Math.round(mg.confidence ?? r.confidence_score ?? 0)
        map[liveKey('market', r.risk_topic)] = { det, conf, label: r.risk_display || r.risk_topic, kind: 'market' }
      }
      setLive(map)
      setLists(wls)
      setActive((cur) => cur ?? (wls[0]?.id ?? null))
    } catch (e: any) {
      setErr(e?.data?.detail || e?.message || 'Could not load watchlists.')
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const current = useMemo(() => lists.find((l) => l.id === active) || null, [lists, active])

  const newList = async () => {
    const name = (window.prompt('Name this watchlist:', 'New list') || '').trim()
    if (!name) return
    setBusy(true)
    try { const wl = await createWatchlist(name); setLists((ls) => [...ls, wl]); setActive(wl.id) }
    finally { setBusy(false) }
  }
  const removeList = async (id: number) => {
    if (!window.confirm('Delete this watchlist?')) return
    setBusy(true)
    try { await deleteWatchlist(id); setLists((ls) => ls.filter((l) => l.id !== id)); setActive((a) => (a === id ? null : a)) }
    finally { setBusy(false) }
  }
  const addItem = async () => {
    const raw = adding.trim(); if (!raw || !current) return
    // resolve against the live universe by key OR display name
    const q = raw.toLowerCase()
    const hit = Object.values(live).find((v) => v.label.toLowerCase() === q) ||
      live[liveKey('market', raw)] || live[liveKey('topic', raw)]
    const key = hit ? Object.keys(live).find((k) => live[k] === hit)!.split(':').slice(1).join(':') : raw
    const payload = hit
      ? { key, display: hit.label, kind: hit.kind }
      : { key: raw, display: raw, kind: 'topic' as WatchKind }
    setBusy(true)
    try {
      const item = await addWatchItem(current.id, payload)
      setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: [...l.items.filter((i) => i.key !== item.key), item] } : l))
      setAdding('')
    } catch (e: any) { setErr(e?.data?.detail || 'Could not add item.') }
    finally { setBusy(false) }
  }
  const removeItem = async (itemId: number) => {
    if (!current) return
    setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: l.items.filter((i) => i.id !== itemId) } : l))
    try { await removeWatchItem(current.id, itemId) } catch { load() }
  }

  return (
    <>
      <div className="main-head" style={{ paddingBottom: 0 }}>
        <div className="main-title-row">
          <div className="main-title">Watchlists</div>
          <div className="main-sub">Track the gap on the names you care about · synced across your devices</div>
        </div>
        <div className="wl-tabs">
          {lists.map((l) => (
            <div key={l.id} className={'wl-tab' + (l.id === active ? ' on' : '')} onClick={() => setActive(l.id)}>
              {l.name}<span className="wc">{l.items.length}</span>
              {l.id === active && <span className="wl-del" title="Delete list" onClick={(e) => { e.stopPropagation(); removeList(l.id) }}>✕</span>}
            </div>
          ))}
          <div className="wl-tab add" onClick={newList}>+ New list</div>
        </div>
      </div>

      {current && (
        <div className="add-row">
          <input value={adding} onChange={(e) => setAdding(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') addItem() }}
            placeholder="Add a topic or instrument to this list… (e.g. world models, Nvidia)" />
          <button className="add-btn" onClick={addItem} disabled={busy}>Add</button>
        </div>
      )}

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading watchlists…</div>
        ) : err ? (
          <div className="center-state">{err}<div className="muted">Sign in is required; lists are per-account.</div></div>
        ) : !current ? (
          <div className="center-state"><div className="big">No watchlist selected</div><div className="muted">Create a list to start tracking.</div></div>
        ) : current.items.length === 0 ? (
          <div className="center-state"><div className="big">Nothing tracked yet</div><div className="muted">Add a topic or instrument above to start watching its gap.</div></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th><th className="r">Detection</th><th className="r">Confidence</th>
                <th className="r">Gap (lead)</th><th>Stage / Tier</th><th></th>
              </tr>
            </thead>
            <tbody>
              {current.items.map((it) => {
                const lv = live[liveKey(it.kind, it.key)]
                const det = lv?.det ?? 0, conf = lv?.conf ?? 0, gap = det - conf
                const scored = !!lv
                const gw = Math.abs(gap) >= 20 ? 'wide' : gap < 0 ? 'neg' : 'tight'
                return (
                  <tr key={it.id}>
                    <td><div className="topic-name">{it.display || it.key}</div><div className="topic-cat">{it.kind === 'market' ? 'Market Signal' : 'Trend'}</div></td>
                    {scored ? (<>
                      <td className="r"><span className="score-cell det">{det}</span></td>
                      <td className="r"><span className="score-cell conf">{conf}</span></td>
                      <td className="r"><div className="gapviz">{gapMicro(det, conf)}<span className={'gapnum ' + gw}>{gap > 0 ? '+' : ''}{gap}</span></div></td>
                      <td><span className="stage">{it.kind === 'market' ? '—' : stageOf(det)}</span></td>
                    </>) : (
                      <td className="r muted" colSpan={4} style={{ textAlign: 'left' }}>Not yet scored — will populate when it next appears in a cycle.</td>
                    )}
                    <td className="r"><button className="rm" title="Remove" onClick={() => removeItem(it.id)}>✕</button></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
