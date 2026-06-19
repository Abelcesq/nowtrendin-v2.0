import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import {
  listWatchlists, createWatchlist, deleteWatchlist, updateWatchlist,
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

export function Watchlists({ onOpenDetail }: { onOpenDetail?: (key: string, kind: WatchKind, display: string) => void }) {
  const [lists, setLists] = useState<WatchlistT[]>([])
  const [live, setLive] = useState<Record<string, Live>>({})
  const [active, setActive] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [adding, setAdding] = useState('')
  const [picked, setPicked] = useState<{ key: string; display: string; kind: WatchKind } | null>(null)
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
  // Searchable universe from the live lookup, so we only ever add a VERIFIED,
  // linkable entity (never raw free text).
  const matches = useMemo(() => {
    const q = adding.trim().toLowerCase()
    if (q.length < 2) return [] as { key: string; display: string; kind: WatchKind }[]
    return Object.entries(live).map(([k, v]) => ({
      key: k.split(':').slice(1).join(':'), display: v.label, kind: v.kind,
    })).filter((e) => e.display.toLowerCase().includes(q) || e.key.toLowerCase().includes(q)).slice(0, 8)
  }, [live, adding])

  const addItem = async () => {
    if (!current || !picked) return  // hard gate — must be a verified entity
    setBusy(true)
    try {
      const item = await addWatchItem(current.id, { key: picked.key, display: picked.display, kind: picked.kind })
      setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: [...l.items.filter((i) => i.key !== item.key), item] } : l))
      setAdding(''); setPicked(null)
    } catch (e: any) { setErr(e?.data?.detail || 'Could not add item.') }
    finally { setBusy(false) }
  }
  const removeItem = async (itemId: number) => {
    if (!current) return
    setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: l.items.filter((i) => i.id !== itemId) } : l))
    try { await removeWatchItem(current.id, itemId) } catch { load() }
  }
  // Per-list movement notifications (email / text). Optimistic; reverts on error.
  const setNotify = async (fields: { notify_email?: boolean; notify_sms?: boolean; notify_threshold?: number }) => {
    if (!current) return
    setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, ...fields } : l))
    try { await updateWatchlist(current.id, fields) } catch { load() }
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
        <div className="add-wrap">
          <div className="add-row">
            {picked ? (
              <div className="wl-picked" onClick={() => setPicked(null)} title="Clear">
                ✓ {picked.display} <span>· {picked.kind === 'market' ? 'Market' : 'Trend'}</span> ✕
              </div>
            ) : (
              <input value={adding} onChange={(e) => { setAdding(e.target.value); setPicked(null) }}
                placeholder="Search a topic or instrument to add… (e.g. world models, Nvidia)" />
            )}
            <button className="add-btn" onClick={addItem} disabled={busy || !picked}>Add</button>
          </div>
          {!picked && adding.trim().length >= 2 && (
            matches.length > 0 ? (
              <div className="wl-suggest">
                {matches.map((e) => (
                  <div key={`${e.kind}:${e.key}`} className="wl-suggest-item" onClick={() => { setPicked(e); setAdding(e.display) }}>
                    {e.display}<span>{e.kind === 'market' ? 'Market' : 'Trend'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="wl-suggest-empty">Not in our database — only existing topics/instruments can be added.</div>
            )
          )}
        </div>
      )}

      {current && (
        <div className="wl-notify">
          <span className="wl-notify-lbl">Notify me when any item crosses Detection</span>
          <select value={current.notify_threshold ?? 75} onChange={(e) => setNotify({ notify_threshold: Number(e.target.value) })}>
            {[60, 70, 75, 80, 85, 90].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
          <label className="wl-notify-ch"><input type="checkbox" checked={!!current.notify_email} onChange={(e) => setNotify({ notify_email: e.target.checked })} /> Email</label>
          <label className="wl-notify-ch"><input type="checkbox" checked={!!current.notify_sms} onChange={(e) => setNotify({ notify_sms: e.target.checked })} /> Text</label>
          <span className="wl-notify-hint">Text needs a verified phone (Account).</span>
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
                const go = () => { if (onOpenDetail && window.confirm(`Go to the detail page for "${it.display || it.key}"?`)) onOpenDetail(it.key, it.kind, it.display || it.key) }
                return (
                  <tr key={it.id}>
                    <td><div className="topic-name link" onClick={go} title="Open detail page">{it.display || it.key}</div><div className="topic-cat">{it.kind === 'market' ? 'Market Signal' : 'Trend'}</div></td>
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
