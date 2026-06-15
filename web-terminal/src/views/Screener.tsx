import { useEffect, useMemo, useState } from 'react'
import { api, type TopicRow } from '../lib/api'

interface Row extends TopicRow { det: number; conf: number; gap: number; stage: string; ageMin: number }
type SortKey = 'topic_display' | 'det' | 'conf' | 'gap' | 'stage' | 'category' | 'total_mentions' | 'ageMin'

function stageOf(d: number) {
  return d >= 85 ? 'BREAKOUT' : d >= 70 ? 'STRONG' : d >= 55 ? 'EMERGING' : d >= 35 ? 'WATCHING' : 'MONITORING'
}
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

function gapInterp(d: number): [string, boolean, string] {
  const g = Math.abs(d)
  if (d < 0) return ['LAGGING', true, 'Confirmation now exceeds early detection — the hard signal arrived after the early window. A late-stage read.']
  if (g <= 15) return ['ALIGNED', true, 'Detection and confidence agree. High-conviction signal at this level — both rule-sets concur.']
  if (g <= 35) return ['CONFIRMATION BUILDING', false, 'Early edge is running ahead of confirmation. The gap typically closes over the next one to two cycles.']
  return ['VERY EARLY', false, 'Detected but not yet confirmed — corroborated among expert communities, not yet broad across the mainstream.']
}

function DetailRail({ row, onClose }: { row: Row; onClose: () => void }) {
  const [d, setD] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    let alive = true; setLoading(true)
    api.score(row.topic_key).then((x) => alive && setD(x)).catch(() => {}).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [row.topic_key])

  const v = d?.velocity_scores || {}
  const det = v.detection ?? row.det, conf = v.confidence ?? row.conf, gap = Math.round(det - conf)
  const [gs, tight, gt] = gapInterp(gap)
  const comps: [string, number][] = d?.components
    ? Object.entries(d.components).map(([k, val]: any) => [k.replace(/_/g, ' '), Math.round(val?.score ?? 0)])
    : []

  return (
    <aside className="rail">
      <div className="detail-head">
        <div className="detail-top">
          <div>
            <div className="detail-name">{row.topic_display}</div>
            <div className="detail-cat">{row.category || '—'} · <span className={'stage ' + row.stage}>{row.stage}</span></div>
          </div>
          <div className="x" onClick={onClose}>✕</div>
        </div>
        <div className="detail-asof">
          {d?.detection_pathway ? `pathway: ${d.detection_pathway}` : ''}{d?.mainstream_ratio != null ? ` · mratio ${d.mainstream_ratio}` : ''} · updated {ageLabel(row.ageMin)} ago
        </div>
      </div>

      <div className="gauges">
        <div className="gauge det">{ring(det, 'var(--det)')}<div className="gv" style={{ marginTop: -50 }}>{det}</div><div className="gl" style={{ marginTop: 28 }}>Detection</div><div className="gf">~22% FP · speed</div></div>
        <div className="gauge conf">{ring(conf, 'var(--conf)')}<div className="gv" style={{ marginTop: -50 }}>{conf}</div><div className="gl" style={{ marginTop: 28 }}>Confidence</div><div className="gf">&lt;9% FP · precision</div></div>
      </div>

      <div className="sect">
        <h4>Detection–Confidence Gap</h4>
        <div className={'gapband' + (tight ? ' tight' : '')}>
          <div className="gbs">{gs}</div>
          <div className="gbv">{gap > 0 ? '+' : ''}{gap} pts</div>
          <div className="gbt">{gt}</div>
        </div>
      </div>

      {comps.length > 0 && (
        <div className="sect">
          <h4>Component Breakdown</h4>
          {comps.map(([k, val]) => (
            <div className="comp-row" key={k}>
              <span className="cl">{k}</span>
              <span className="comp-bar"><i style={{ width: `${Math.min(100, val)}%`, background: 'var(--det)' }} /></span>
              <span className="cv">{val}</span>
            </div>
          ))}
        </div>
      )}

      <div className="sect">
        <h4>Signal Read</h4>
        <div className="narr">
          {loading ? 'Loading live score…'
            : gap >= 20
              ? `${row.topic_display} shows a wide ${gap}-point gap — leading indicators run ahead of confirmation. The early-mover window: detected, not yet broadly confirmed.`
              : gap < 0
                ? `${row.topic_display} reads with confidence above detection — the hard signal arrived after the early window; the topic is maturing.`
                : `${row.topic_display} has detection and confidence closely aligned (${gap > 0 ? '+' : ''}${gap}) — a high-conviction read at the ${row.stage} level.`}
        </div>
      </div>

      <div className="detail-actions">
        <button className="btn">★ Watchlist</button>
        <button className="btn">⚑ Alert</button>
        <button className="btn">↧ Export</button>
      </div>
    </aside>
  )
}

export function Screener({ onRail }: { onRail: (node: React.ReactNode | null) => void }) {
  const [rows, setRows] = useState<Row[]>([])
  const [cats, setCats] = useState<{ key: string; label: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')
  const [sortKey, setSortKey] = useState<SortKey>('det')
  const [sortDir, setSortDir] = useState(-1)
  const [sel, setSel] = useState<string | null>(null)

  useEffect(() => {
    let alive = true; setLoading(true); setErr(null)
    Promise.all([api.topics(200), api.categories().catch(() => ({ categories: [] }))])
      .then(([t, c]) => {
        if (!alive) return
        setRows((t.topics || []).map((r) => {
          const det = Math.round(r.detection_score ?? 0), conf = Math.round(r.confidence_score ?? 0)
          return { ...r, det, conf, gap: det - conf, stage: (r.current_stage || stageOf(det)).toUpperCase(), ageMin: minsSince(r.last_seen_at) }
        }))
        setCats((c.categories || []).filter((x) => x.count > 0))
      })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const view = useMemo(() => {
    let r = rows.slice()
    if (filter === 'early') r = r.filter((x) => x.gap >= 20)
    else if (filter === 'breakout') r = r.filter((x) => x.det >= 85)
    else if (filter === 'strong') r = r.filter((x) => x.det >= 70)
    else if (filter === 'cooling') r = r.filter((x) => x.gap < 0)
    else if (filter !== 'all') r = r.filter((x) => (x.category || '').toLowerCase() === filter)
    r.sort((a, b) => {
      const va = a[sortKey] as any, vb = b[sortKey] as any
      if (typeof va === 'string') return String(va).localeCompare(String(vb)) * sortDir
      return ((va ?? -1) - (vb ?? -1)) * sortDir
    })
    return r
  }, [rows, filter, sortKey, sortDir])

  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'topic_display' || k === 'category' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const select = (key: string) => {
    if (key === sel) { setSel(null); onRail(null); return }
    setSel(key)
    const row = rows.find((r) => r.topic_key === key)!
    onRail(<DetailRail row={row} onClose={() => { setSel(null); onRail(null) }} />)
  }

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Signal Screener</div>
          <div className="main-sub"><b>{view.length}</b> topics · diffusion-scored · {filter === 'all' ? 'all categories' : filter}</div>
          <div className="main-actions">
            <button className="btn">▦ Columns</button>
            <button className="btn primary">↧ Export</button>
          </div>
        </div>
        <div className="chips">
          <div className={'chip' + (filter === 'all' ? ' active' : '')} onClick={() => setFilter('all')}>All</div>
          <div className={'chip early' + (filter === 'early' ? ' active' : '')} onClick={() => { setFilter('early'); setSortKey('gap'); setSortDir(-1) }}>⟡ Early Signals</div>
          <div className={'chip' + (filter === 'breakout' ? ' active' : '')} onClick={() => setFilter('breakout')}>Breakout ≥85</div>
          <div className={'chip' + (filter === 'strong' ? ' active' : '')} onClick={() => setFilter('strong')}>Strong ≥70</div>
          <div className={'chip' + (filter === 'cooling' ? ' active' : '')} onClick={() => setFilter('cooling')}>Cooling</div>
          {cats.slice(0, 8).map((c) => (
            <div key={c.key} className={'chip' + (filter === c.key ? ' active' : '')} onClick={() => setFilter(c.key)}>
              {c.label} <span className="c-cnt">{c.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading live signals…</div>
        ) : err ? (
          <div className="center-state">Could not load signals.<div className="muted">{err}</div></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th onClick={() => sort('topic_display')} className={sortKey === 'topic_display' ? 'sorted' : ''}>Topic <span className="sort">{arrow('topic_display')}</span></th>
                <th onClick={() => sort('det')} className={'r ' + (sortKey === 'det' ? 'sorted' : '')}>Det <span className="sort">{arrow('det')}</span></th>
                <th onClick={() => sort('conf')} className={'r ' + (sortKey === 'conf' ? 'sorted' : '')}>Conf <span className="sort">{arrow('conf')}</span></th>
                <th onClick={() => sort('gap')} className={'r ' + (sortKey === 'gap' ? 'sorted' : '')}>Gap <span className="sort">{arrow('gap')}</span></th>
                <th onClick={() => sort('stage')} className={sortKey === 'stage' ? 'sorted' : ''}>Stage <span className="sort">{arrow('stage')}</span></th>
                <th onClick={() => sort('category')} className={sortKey === 'category' ? 'sorted' : ''}>Category <span className="sort">{arrow('category')}</span></th>
                <th onClick={() => sort('total_mentions')} className={'r ' + (sortKey === 'total_mentions' ? 'sorted' : '')}>Mentions <span className="sort">{arrow('total_mentions')}</span></th>
                <th onClick={() => sort('ageMin')} className={'r ' + (sortKey === 'ageMin' ? 'sorted' : '')}>Updated <span className="sort">{arrow('ageMin')}</span></th>
              </tr>
            </thead>
            <tbody>
              {view.map((r) => {
                const gw = Math.abs(r.gap) >= 20 ? 'wide' : r.gap < 0 ? 'neg' : 'tight'
                return (
                  <tr key={r.topic_key} className={r.topic_key === sel ? 'sel' : ''} onClick={() => select(r.topic_key)}>
                    <td><div className="topic-name">{r.topic_display}</div><div className="topic-cat">{r.topic_key}</div></td>
                    <td className="r"><span className="score-cell det">{r.det}</span></td>
                    <td className="r"><span className="score-cell conf">{r.conf}</span></td>
                    <td className="r"><div className="gapviz">{gapMicro(r.det, r.conf)}<span className={'gapnum ' + gw}>{r.gap > 0 ? '+' : ''}{r.gap}</span></div></td>
                    <td><span className={'stage ' + r.stage}>{r.stage}</span></td>
                    <td><span className="muted" style={{ textTransform: 'capitalize' }}>{r.category || '—'}</span></td>
                    <td className="r"><span className="muted">{r.total_mentions ?? '—'}</span></td>
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
