import { useEffect, useMemo, useState } from 'react'
import { api, type TopicRow } from '../lib/api'
import { pullTrends } from '../lib/auth'

// Signal filters — EXACT parity with the mobile app's CATEGORY_DEFS (lib/signals.ts)
// so the two surfaces match. `gap` here is abs(detection − confidence), matching
// mobile's scoreGap. Stage buckets are derived from Detection (stageOf), so the
// Stage column always reconciles with the Det column AND these filter thresholds.
//   • Now TrendIn — everything, ranked by the proprietary N (Now Trending) score.
//   • All Signals — everything, ranked by Detection.
// (The two differ by RANK, which is why "Now TrendIn" must not equal "All Signals".)
const SIGNAL_FILTERS: { k: string; label: string; test?: (r: Row) => boolean; sort?: SortKey }[] = [
  { k: 'nowtrendin', label: 'Now TrendIn', sort: 'n' },
  { k: 'all', label: 'All Signals', sort: 'det' },
  { k: 'breakout', label: 'Breakout ≥85', test: (r) => r.det >= 85 },
  { k: 'strong', label: 'Strong ≥70', test: (r) => r.det >= 70 && r.det < 85 },
  { k: 'emerging', label: 'Emerging', test: (r) => r.det >= 55 && r.det < 70 },
  { k: 'lowrisk', label: 'Low Risk', test: (r) => Math.abs(r.gap) <= 6 },
  { k: 'anomalies', label: 'Anomalies', test: (r) => Math.abs(r.gap) >= 18 },
]

interface Row extends TopicRow { det: number; conf: number; n: number; gap: number; stage: string; ageMin: number }
type SortKey = 'topic_display' | 'det' | 'conf' | 'n' | 'gap' | 'stage' | 'category' | 'total_mentions' | 'ageMin'

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

// ── Score Breakdown — the 4 grouped buckets the mobile app shows, derived from
// the engine's flat G·I·M·D·C·P·N components (same grouping as the engine's
// build_component_groups). Each group carries a status so the read matches mobile.
type BItem = { label: string; value: number; desc?: string }
type BGroup = { title: string; status: string; note: string; items: BItem[] }
function scoreFor(c: any): number { return Math.round(Number(c?.score ?? 0)) }
function deriveGroups(components: any): BGroup[] {
  if (!components) return []
  const G = scoreFor(components.G_gradient_strength)
  const M = scoreFor(components.M_platform_diversity)
  const I = scoreFor(components.I_inertia)
  const P = scoreFor(components.P_persistence)
  const D = scoreFor(components.D_dark_matter)
  const C = scoreFor(components.C_confidence_decay)
  const N = scoreFor(components.N_nowtrendin)
  const band = (v: number, hi: number, mid: number): [string, string] =>
    v >= hi ? ['STRONG', 'Strong'] : v >= mid ? ['MODERATE', 'Moderate'] : ['LOW', 'Low']
  const qa = (G + M) / 2, ma = (I + P) / 2, ca = (D + C) / 2
  const [qs] = band(qa, 60, 35)
  const [ms, msl] = (I <= 1 && P <= 1) ? ['PENDING', 'Pending'] : band(ma, 50, 25)
  const [cs] = band(ca, 40, 20)
  return [
    { title: 'Signal Quality', status: qs, note: 'Niche signal density + cross-platform diffusion', items: [
      { label: 'Niche Concentration', value: G, desc: 'Niche vs mainstream concentration' },
      { label: 'Platform Diversity', value: M, desc: 'Cross-platform diffusion pattern' },
    ] },
    { title: 'Signal Momentum', status: ms, note: ms === 'PENDING' ? 'First collection run — check back ~30 min' : `${msl} — acceleration across windows`, items: [
      { label: 'Acceleration (Inertia)', value: I, desc: 'Sustained acceleration across windows' },
      { label: 'Persistence', value: P, desc: 'Held above threshold across cycles' },
    ] },
    { title: 'Signal Context', status: cs, note: 'Hidden early activity + signal freshness', items: [
      { label: 'Dark Matter', value: D, desc: 'Hidden early activity (first-timers, deep engagement)' },
      { label: 'Freshness (Decay)', value: C, desc: 'How fresh vs decaying the signal is' },
    ] },
    { title: 'Community Demand', status: N >= 50 ? 'HIGH' : N >= 20 ? 'MODERATE' : 'LOW',
      note: 'Now TrendIn user demand — separate signal, NOT part of the Gradient', items: [
      { label: 'Now Trending (N)', value: N, desc: 'Internal query demand — shown, never fed into the score' },
    ] },
  ]
}

// Why Detection and Confidence diverge for THIS topic (mobile parity). Detection
// weights early-edge components (dark matter, first-timers, asymmetry); Confidence
// weights cross-platform confirmation. We show the signal's ACTUAL values.
function deriveDivergence(components: any, gap: number) {
  const rows: { label: string; value: string; favors: 'DET' | 'CONF'; note: string }[] = []
  const d = components?.D_dark_matter, m = components?.M_platform_diversity
  if (d?.score != null) rows.push({ label: 'DARK MATTER', value: `${Math.round(d.score)}/100`, favors: 'DET', note: 'hidden early activity → lifts Detection' })
  if (d?.first_timer_ratio != null) rows.push({ label: 'FIRST-TIMER RATIO', value: `${Math.round(d.first_timer_ratio * 100)}%`, favors: 'DET', note: 'new participants flooding in → lifts Detection' })
  if (d?.asymmetry_detected != null) rows.push({ label: 'ENGAGEMENT ASYMMETRY', value: d.asymmetry_detected ? 'Detected' : 'Normal', favors: 'DET', note: 'deep discussion vs surface votes → lifts Detection' })
  const pc = Array.isArray(m?.platforms) ? m.platforms.length : null
  if (pc != null) rows.push({ label: 'PLATFORM SPREAD', value: `${pc} platform${pc === 1 ? '' : 's'}`, favors: 'CONF', note: 'broad cross-platform presence → lifts Confidence' })
  const g = Math.abs(gap)
  const summary = g >= 18
    ? `This signal's ${g}-pt gap means its early-edge components run well ahead of cross-platform confirmation — detected early, not yet broadly confirmed.`
    : g >= 8
      ? `A ${g}-pt gap: the early-edge signal is somewhat ahead of confirmation — building, not yet fully aligned.`
      : `A ${g}-pt gap: early-edge and confirmation are closely aligned — both rule-sets agree on where this sits.`
  return { summary, rows }
}

function DetailRail({ row, onClose }: { row: Row; onClose: () => void }) {
  const [d, setD] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [ex, setEx] = useState<{ short?: string; full?: string } | null>(null)
  const [exLoading, setExLoading] = useState(true)
  const [showFull, setShowFull] = useState(false)
  useEffect(() => {
    let alive = true; setLoading(true); setExLoading(true); setShowFull(false)
    api.score(row.topic_key).then((x) => alive && setD(x)).catch(() => {}).finally(() => alive && setLoading(false))
    // Source-aware AI definition (same /explainer the mobile app shows).
    api.explainer(row.topic_key)
      .then((x) => alive && setEx(x?.available ? x : null))
      .catch(() => {}).finally(() => alive && setExLoading(false))
    return () => { alive = false }
  }, [row.topic_key])

  const v = d?.velocity_scores || {}
  const det = v.detection ?? row.det, conf = v.confidence ?? row.conf, gap = Math.round(det - conf)
  const [gs, tight, gt] = gapInterp(gap)
  const groups: BGroup[] = d?.components ? deriveGroups(d.components) : []
  const diverge = d?.components ? deriveDivergence(d.components, gap) : null
  const platforms: string[] = Array.isArray(d?.components?.M_platform_diversity?.platforms)
    ? d.components.M_platform_diversity.platforms : (Array.isArray(d?.platforms_active) ? d.platforms_active : [])
  const why = d?.why_this_matters || ''
  const watch = d?.what_to_watch || ''

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

      {/* AI Context — source-aware definition (preview + full), parity with mobile */}
      <div className="sect">
        <h4>AI Context</h4>
        {ex?.short ? (
          <div className="ai-ctx">
            <div className="ai-preview">{ex.short}</div>
            {ex.full && ex.full.trim() !== ex.short.trim() && (
              showFull
                ? <div className="ai-full">{ex.full}</div>
                : <button className="ai-more" onClick={() => setShowFull(true)}>Read full definition ↓</button>
            )}
          </div>
        ) : (
          <div className="narr muted">
            {exLoading ? 'Generating a source-aware definition…'
              : 'No AI definition yet — it generates on first view and is cached.'}
          </div>
        )}
      </div>

      <div className="sect">
        <h4>Detection–Confidence Gap</h4>
        <div className={'gapband' + (tight ? ' tight' : '')}>
          <div className="gbs">{gs}</div>
          <div className="gbv">{gap > 0 ? '+' : ''}{gap} pts</div>
          <div className="gbt">{gt}</div>
        </div>
      </div>

      {groups.length > 0 && (
        <div className="sect">
          <h4>Score Breakdown</h4>
          {groups.map((grp) => (
            <div className="bgroup" key={grp.title}>
              <div className="bgroup-head">
                <span className="bgroup-title">{grp.title}</span>
                <span className={'bgroup-status s-' + grp.status.toLowerCase()}>{grp.status}</span>
              </div>
              <div className="bgroup-note">{grp.note}</div>
              {grp.items.map((it) => (
                <div className="comp-row" key={it.label} title={it.desc}>
                  <span className="cl">{it.label}</span>
                  <span className="comp-bar"><i style={{ width: `${Math.min(100, it.value)}%`, background: grp.title === 'Community Demand' ? 'var(--early)' : 'var(--det)' }} /></span>
                  <span className="cv">{it.value}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {diverge && diverge.rows.length > 0 && (
        <div className="sect">
          <h4>Why the Scores Diverge</h4>
          <div className="narr" style={{ marginBottom: 8 }}>{diverge.summary}</div>
          <div className="div-grid">
            {diverge.rows.map((dr) => (
              <div className="div-cell" key={dr.label}>
                <div className="div-label">{dr.label}</div>
                <div className="div-val" style={{ color: dr.favors === 'DET' ? 'var(--det)' : 'var(--conf)' }}>
                  <span className="div-dot" style={{ background: dr.favors === 'DET' ? 'var(--det)' : 'var(--conf)' }} />{dr.value}
                </div>
                <div className="div-note">{dr.note}</div>
              </div>
            ))}
          </div>
          <div className="div-legend">
            <span style={{ color: 'var(--det)' }}>● Blue</span> lifts Detection (earliness) ·
            <span style={{ color: 'var(--conf)' }}> ● Green</span> lifts Confidence (confirmation)
          </div>
        </div>
      )}

      {(platforms.length > 0 || why) && (
        <div className="sect">
          <h4>Source &amp; Why</h4>
          {platforms.length > 0 && (
            <div className="src-row">
              {platforms.map((p) => <span className="src-chip" key={p}>{p}</span>)}
            </div>
          )}
          {why && <div className="narr">{why}</div>}
          {watch && <div className="narr" style={{ marginTop: 8 }}>{watch}</div>}
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

export function Screener({ onRail, query = '' }: { onRail: (node: React.ReactNode | null) => void; query?: string }) {
  const [rows, setRows] = useState<Row[]>([])
  const [cats, setCats] = useState<{ key: string; label: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState('nowtrendin')   // mobile default = Now TrendIn
  const [sortKey, setSortKey] = useState<SortKey>('det')
  const [sortDir, setSortDir] = useState(-1)
  const [sel, setSel] = useState<string | null>(null)
  const [pulling, setPulling] = useState(false)
  const [pullMsg, setPullMsg] = useState<string | null>(null)

  // When a SIGNAL chip is active we screen the top-ranked set client-side; when a
  // CATEGORY chip is active we ask the engine for THAT category server-side, so the
  // chip count (global, from /categories) matches the rows shown — fixes "Business 5
  // but empty" (the 5 ranked below the top-200 default load).
  const catParam = SIGNAL_FILTERS.some((f) => f.k === filter) ? '' : filter

  useEffect(() => {
    let alive = true; setLoading(true); setErr(null)
    Promise.all([api.topics(200, catParam), api.categories().catch(() => ({ categories: [] }))])
      .then(([t, c]) => {
        if (!alive) return
        setRows((t.topics || []).map((r) => {
          const det = Math.round(r.detection_score ?? 0), conf = Math.round(r.confidence_score ?? 0)
          // Stage from Detection (stageOf) — NOT the server's current_stage — so the
          // Stage column always reconciles with the Det column + the filter buckets.
          return { ...r, det, conf, n: Math.round(r.nowtrendin_score ?? 0), gap: det - conf, stage: stageOf(det), ageMin: minsSince(r.last_seen_at) }
        }))
        if ((c.categories || []).length) setCats((c.categories || []).filter((x) => x.count > 0))
      })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [catParam])

  const view = useMemo(() => {
    let r = rows.slice()
    const sig = SIGNAL_FILTERS.find((f) => f.k === filter)
    if (sig) { if (sig.test) r = r.filter(sig.test) }     // nowtrendin/all = no filter
    // category rows already filtered server-side (catParam) — no client re-filter
    const ql = query.trim().toLowerCase()
    if (ql) r = r.filter((x) => (x.topic_display || '').toLowerCase().includes(ql) || (x.topic_key || '').toLowerCase().includes(ql))
    r.sort((a, b) => {
      const va = a[sortKey] as any, vb = b[sortKey] as any
      if (typeof va === 'string') return String(va).localeCompare(String(vb)) * sortDir
      return ((va ?? -1) - (vb ?? -1)) * sortDir
    })
    return r
  }, [rows, filter, sortKey, sortDir, query])

  // Selecting a signal chip also sets its ranking: "Now TrendIn" → by N score,
  // "All Signals" → by Detection. (This is what makes the two views differ.)
  const selectSignal = (f: typeof SIGNAL_FILTERS[number]) => {
    setFilter(f.k)
    if (f.sort) { setSortKey(f.sort); setSortDir(-1) }
  }
  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'topic_display' || k === 'category' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const doPull = async () => {
    setPulling(true); setPullMsg(null)
    try {
      const r = await pullTrends()
      setPullMsg(r?.message || 'Pull queued — fresh signals arrive next cycle.')
    } catch (e: any) {
      setPullMsg(e?.data?.detail || e?.message || 'Pull failed.')
    } finally { setPulling(false) }
  }

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
          <div className="main-title">Trends</div>
          <div className="main-sub"><b>{view.length}</b> topics · diffusion-scored{pullMsg ? ` · ${pullMsg}` : ''}</div>
          <div className="main-actions">
            <button className="btn primary" onClick={doPull} disabled={pulling} title="Enterprise — costs 1 token">
              {pulling ? '⟳ Pulling…' : '⚡ Pull Trends · 1 token'}
            </button>
            <button className="btn">▦ Columns</button>
            <button className="btn">↧ Export</button>
          </div>
        </div>
        {/* Row 1 — TRENDS (signal) filters — EXACT mobile parity (CATEGORY_DEFS) */}
        <div className="chips tight">
          <span className="chip-label">Trends</span>
          {SIGNAL_FILTERS.map((f) => (
            <div key={f.k} className={'chip' + (filter === f.k ? ' active' : '')}
              onClick={() => selectSignal(f)}>{f.label}</div>
          ))}
        </div>
        {/* Row 2 — CATEGORY filters (the WHAT axis) */}
        {cats.length > 0 && (
          <div className="chips">
            <span className="chip-label">Category</span>
            {cats.slice(0, 12).map((c) => (
              <div key={c.key} className={'chip' + (filter === c.key ? ' active' : '')} onClick={() => setFilter(c.key)}>
                {c.label} <span className="c-cnt">{c.count}</span>
              </div>
            ))}
          </div>
        )}
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
                <th onClick={() => sort('n')} className={'r ' + (sortKey === 'n' ? 'sorted' : '')} title="Now Trending — proprietary N (community-demand) score">N <span className="sort">{arrow('n')}</span></th>
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
                    <td className="r"><span className="score-cell" style={{ color: 'var(--early)' }}>{r.n || '—'}</span></td>
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
