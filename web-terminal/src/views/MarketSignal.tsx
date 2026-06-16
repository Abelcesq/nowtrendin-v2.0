import { useEffect, useMemo, useState } from 'react'
import { api, type RiskRow } from '../lib/api'

// Market Signal — the finance-native dual score, wired to the live /risk/scores
// (the SAME data the mobile Market tab renders). Detection = analyst sentiment +
// smart-money positioning; tiers are ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT,
// measured RELATIVE TO each item's own baseline. No prices/returns/accuracy are
// shown — only what the engine actually produces.

interface MRow {
  key: string; name: string; det: number; conf: number; gap: number
  tier: string; cls: string; pct: number | null; lev: number | null
  sigs: number; ageMin: number; calibrating: boolean
  interp: string; comps: [string, number, string][]
}
type SortKey = 'name' | 'det' | 'conf' | 'gap' | 'tier' | 'pct' | 'lev' | 'sigs' | 'ageMin'

// mobile MARKET_CATEGORY_DEFS parity — the tier axis.
const TIERS = ['ELEVATED', 'ACTIVE', 'BUILDING', 'ROUTINE', 'DORMANT']
const FILTERS: { k: string; label: string; test?: (r: MRow) => boolean }[] = [
  { k: 'all', label: 'All' },
  { k: 'elevated', label: 'Elevated', test: (r) => r.tier === 'ELEVATED' },
  { k: 'active', label: 'Active', test: (r) => r.tier === 'ACTIVE' },
  { k: 'building', label: 'Building', test: (r) => r.tier === 'BUILDING' },
  { k: 'routine', label: 'Routine', test: (r) => r.tier === 'ROUTINE' },
  { k: 'dormant', label: 'Dormant', test: (r) => r.tier === 'DORMANT' },
  { k: 'watch', label: 'Watch / Unusual', test: (r) => ['WATCH', 'ELEVATED', 'UNUSUAL'].includes(r.cls) },
  { k: 'leverage', label: 'Leverage ≥60', test: (r) => (r.lev ?? 0) >= 60 },
]

function minsSince(iso?: string) {
  if (!iso) return 9999
  const d = new Date(iso); return isNaN(+d) ? 9999 : Math.max(0, Math.round((Date.now() - +d) / 60000))
}
function ageLabel(m: number) { return m >= 1440 ? `${Math.round(m / 1440)}d` : m >= 60 ? `${Math.round(m / 60)}h` : `${m}m` }

function gapMicro(det: number, conf: number) {
  const W = 78, x = (v: number) => 4 + (v / 100) * (W - 8)
  const lo = Math.min(det, conf), hi = Math.max(det, conf)
  const wide = Math.abs(det - conf) >= 20, col = wide ? 'var(--early)' : '#aab4c1'
  return (
    <svg width={W} height="16" viewBox={`0 0 ${W} 16`}>
      <line x1={x(lo)} y1="8" x2={x(hi)} y2="8" stroke={col} strokeWidth={wide ? 2.5 : 1.5} />
      <circle cx={x(det)} cy="8" r="3.2" fill="var(--det)" />
      <circle cx={x(conf)} cy="8" r="3.2" fill="var(--conf)" />
    </svg>
  )
}
function ring(val: number, color: string) {
  const r = 26, c = 2 * Math.PI * r, off = c * (1 - val / 100)
  return (
    <svg width="72" height="72" viewBox="0 0 72 72">
      <circle cx="36" cy="36" r={r} fill="none" stroke="var(--line)" strokeWidth="6" />
      <circle cx="36" cy="36" r={r} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={off} transform="rotate(-90 36 36)" />
    </svg>
  )
}

function toRow(r: RiskRow): MRow {
  const mg = r.market_gradient || {}
  const det = Math.round((mg.detection ?? r.detection_score ?? 0))
  const conf = Math.round((mg.confidence ?? r.confidence_score ?? 0))
  const comps: [string, number, string][] = mg.components
    ? Object.entries(mg.components).map(([k, v]) => [k, Math.round(v?.score ?? 0), v?.feeds || ''])
    : []
  return {
    key: r.risk_topic, name: r.risk_display || r.risk_topic,
    det, conf, gap: det - conf,
    tier: (mg.tier || r.risk_stage || 'ROUTINE').toUpperCase(),
    cls: (r.classification || '').toUpperCase(),
    pct: r.percent_delta ?? null, lev: mg.leverage_health ?? null,
    sigs: r.total_signals ?? 0, ageMin: minsSince(r.scored_at),
    calibrating: !!mg.calibrating || r.sufficient_baseline === false,
    interp: mg.interpretation || r.interpretation || '',
    comps,
  }
}

function MarketRail({ row, onClose }: { row: MRow; onClose: () => void }) {
  return (
    <aside className="rail">
      <div className="detail-head">
        <div className="detail-top">
          <div>
            <div className="detail-name">{row.name}</div>
            <div className="detail-cat">
              Market Signal · <span className={'tier ' + row.tier}>{row.tier}</span>
              {row.calibrating && <span className="cal-chip">calibrating</span>}
            </div>
          </div>
          <div className="x" onClick={onClose}>✕</div>
        </div>
        <div className="detail-asof">
          {row.cls ? `vs baseline: ${row.cls}` : ''}{row.pct != null ? ` · ${row.pct > 0 ? '+' : ''}${Math.round(row.pct)}% vs baseline` : ''} · updated {ageLabel(row.ageMin)} ago
        </div>
      </div>

      <div className="gauges">
        <div className="gauge det">{ring(row.det, 'var(--det)')}<div className="gv" style={{ marginTop: -50 }}>{row.det}</div><div className="gl" style={{ marginTop: 28 }}>Detection</div><div className="gf">analyst + positioning</div></div>
        <div className="gauge conf">{ring(row.conf, 'var(--conf)')}<div className="gv" style={{ marginTop: -50 }}>{row.conf}</div><div className="gl" style={{ marginTop: 28 }}>Confidence</div><div className="gf">fundamentals + price</div></div>
      </div>

      {row.interp && (
        <div className="sect"><h4>Market Read</h4><div className="narr">{row.interp}</div></div>
      )}

      {row.comps.length > 0 && (
        <div className="sect">
          <h4>Market Components</h4>
          {row.comps.map(([k, val, feeds]) => (
            <div className="comp-row" key={k}>
              <span className="cl" title={k}>{k.replace(/\s*\(.*\)$/, '')}</span>
              <span className="comp-bar"><i style={{ width: `${Math.min(100, val)}%`, background: feeds === 'confidence' ? 'var(--conf)' : 'var(--det)' }} /></span>
              <span className="cv">{val}</span>
            </div>
          ))}
        </div>
      )}

      {row.lev != null && (
        <div className="sect">
          <h4>Macro Leverage</h4>
          <div className="comp-row"><span className="cl">Leverage health</span><span className="comp-bar"><i style={{ width: `${Math.min(100, row.lev)}%`, background: 'var(--early)' }} /></span><span className="cv">{Math.round(row.lev)}</span></div>
        </div>
      )}

      <div className="detail-actions">
        <button className="btn">★ Watchlist</button>
        <button className="btn">⚑ Alert</button>
        <button className="btn">↧ Export</button>
      </div>
    </aside>
  )
}

export function MarketSignal({ onRail }: { onRail: (node: React.ReactNode | null) => void }) {
  const [rows, setRows] = useState<MRow[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')
  const [q, setQ] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('det')
  const [sortDir, setSortDir] = useState(-1)
  const [sel, setSel] = useState<string | null>(null)

  useEffect(() => {
    let alive = true; setLoading(true); setErr(null)
    api.risk(200)
      .then((d) => { if (alive) setRows((d.results || []).map(toRow)) })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const anyCalibrating = useMemo(() => rows.some((r) => r.calibrating), [rows])

  const view = useMemo(() => {
    let r = rows.slice()
    const f = FILTERS.find((x) => x.k === filter)
    if (f?.test) r = r.filter(f.test)
    if (q) { const s = q.toLowerCase(); r = r.filter((x) => x.name.toLowerCase().includes(s) || x.key.toLowerCase().includes(s)) }
    r.sort((a, b) => {
      const va = a[sortKey] as any, vb = b[sortKey] as any
      if (typeof va === 'string') return String(va).localeCompare(String(vb)) * sortDir
      return ((va ?? -1) - (vb ?? -1)) * sortDir
    })
    return r
  }, [rows, filter, q, sortKey, sortDir])

  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'name' || k === 'tier' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const select = (key: string) => {
    if (key === sel) { setSel(null); onRail(null); return }
    setSel(key)
    const row = rows.find((r) => r.key === key)!
    onRail(<MarketRail row={row} onClose={() => { setSel(null); onRail(null) }} />)
  }

  const csv = () => {
    const hdr = ['item', 'detection', 'confidence', 'gap', 'tier', 'classification', 'pct_vs_baseline', 'leverage_health', 'signals', 'updated_min']
    const lines = [hdr.join(',')].concat(view.map((r) =>
      [`"${r.name}"`, r.det, r.conf, r.gap, r.tier, r.cls, r.pct ?? '', r.lev ?? '', r.sigs, r.ageMin].join(',')))
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' }))
    a.download = 'nowtrendin_market_signal.csv'; a.click()
  }

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Market Signal</div>
          <div className="main-sub"><b>{view.length}</b> instruments · finance-native dual score · baseline-relative</div>
          <div className="main-actions">
            <button className="btn" onClick={csv}>↧ Export CSV</button>
          </div>
        </div>
        <div className="chips">
          <span className="chip-label">Tier</span>
          {FILTERS.map((f) => (
            <div key={f.k} className={'chip' + (filter === f.k ? ' active' : '')} onClick={() => setFilter(f.k)}>{f.label}</div>
          ))}
          <input className="chip-search" placeholder="Filter instruments…" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>

      {anyCalibrating && (
        <div className="cal-banner">
          ◷ Market Gradient is <b>baseline-relative</b>. Items with limited history read “calibrating” — tiers settle (Routine → Active/Elevated) as each item's baseline accumulates over the coming cycles. Measurement only — not financial advice, not a risk rating.
        </div>
      )}

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading live market signals…</div>
        ) : err ? (
          <div className="center-state">Could not load market signals.<div className="muted">{err}</div></div>
        ) : view.length === 0 ? (
          <div className="center-state">No instruments match.<div className="muted">Try a different tier or clear the filter.</div></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th onClick={() => sort('name')} className={sortKey === 'name' ? 'sorted' : ''}>Instrument <span className="sort">{arrow('name')}</span></th>
                <th onClick={() => sort('det')} className={'r ' + (sortKey === 'det' ? 'sorted' : '')}>Detection <span className="sort">{arrow('det')}</span></th>
                <th onClick={() => sort('conf')} className={'r ' + (sortKey === 'conf' ? 'sorted' : '')}>Confidence <span className="sort">{arrow('conf')}</span></th>
                <th onClick={() => sort('gap')} className={'r ' + (sortKey === 'gap' ? 'sorted' : '')}>Gap (lead) <span className="sort">{arrow('gap')}</span></th>
                <th onClick={() => sort('tier')} className={sortKey === 'tier' ? 'sorted' : ''}>Tier <span className="sort">{arrow('tier')}</span></th>
                <th onClick={() => sort('pct')} className={'r ' + (sortKey === 'pct' ? 'sorted' : '')}>%Δ baseline <span className="sort">{arrow('pct')}</span></th>
                <th onClick={() => sort('lev')} className={'r ' + (sortKey === 'lev' ? 'sorted' : '')}>Leverage <span className="sort">{arrow('lev')}</span></th>
                <th onClick={() => sort('sigs')} className={'r ' + (sortKey === 'sigs' ? 'sorted' : '')}>Signals <span className="sort">{arrow('sigs')}</span></th>
                <th onClick={() => sort('ageMin')} className={'r ' + (sortKey === 'ageMin' ? 'sorted' : '')}>Updated <span className="sort">{arrow('ageMin')}</span></th>
              </tr>
            </thead>
            <tbody>
              {view.map((r) => {
                const gw = Math.abs(r.gap) >= 20 ? 'wide' : r.gap < 0 ? 'neg' : 'tight'
                return (
                  <tr key={r.key} className={r.key === sel ? 'sel' : ''} onClick={() => select(r.key)}>
                    <td><div className="topic-name">{r.name}{r.calibrating && <span className="cal-chip">cal</span>}</div><div className="topic-cat">{r.cls ? r.cls.toLowerCase() : 'market'}</div></td>
                    <td className="r"><span className="score-cell det">{r.det}</span></td>
                    <td className="r"><span className="score-cell conf">{r.conf}</span></td>
                    <td className="r"><div className="gapviz">{gapMicro(r.det, r.conf)}<span className={'gapnum ' + gw}>{r.gap > 0 ? '+' : ''}{r.gap}</span></div></td>
                    <td><span className={'tier ' + r.tier}>{r.tier}</span></td>
                    <td className="r"><span className={'pct ' + (r.pct == null ? 'na' : r.pct > 0 ? 'up' : r.pct < 0 ? 'down' : 'flat')}>{r.pct == null ? '—' : `${r.pct > 0 ? '+' : ''}${Math.round(r.pct)}%`}</span></td>
                    <td className="r"><span className="muted">{r.lev == null ? '—' : Math.round(r.lev)}</span></td>
                    <td className="r"><span className="muted">{r.sigs || '—'}</span></td>
                    <td className="r"><span className="muted">{ageLabel(r.ageMin)}</span></td>
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
