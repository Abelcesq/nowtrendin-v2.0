import { useEffect, useMemo, useState } from 'react'
import { TrendingUp, Flame, DollarSign, Scale, LineChart, GripVertical, X, Plus, Pencil, Check } from 'lucide-react'
import { api, type TopicRow, type RiskRow } from '../lib/api'
import { getDashboard, saveDashboard, type DashTile } from '../lib/auth'
import type { NavKey } from '../components/Shell'

// Customizable at-a-glance dashboard (Charter §0.6). Tiles are user-configurable —
// add / delete / drag-reorder, plus a "Create new metric" builder (Trends, Market,
// or Track-a-topic). Layout persists per-user via /api/dashboard/ (cross-device).

const r0 = (v: any) => Math.round(Number(v || 0))
let _idc = 0
const newId = () => `t${Date.now()}_${_idc++}`

const DEFAULT_TILES: DashTile[] = [
  { id: 'd1', type: 'top-trends-mingap' },
  { id: 'd2', type: 'top-n' },
  { id: 'd3', type: 'top-market' },
  { id: 'd4', type: 'leverage-spread' },
]

const BUILTIN_META: Record<string, { title: string; icon: any; color: string }> = {
  'top-trends-mingap': { title: 'Top trends · minimal gap', icon: TrendingUp, color: 'var(--det)' },
  'top-n': { title: 'Top N · demand leaders', icon: Flame, color: 'var(--early)' },
  'top-market': { title: 'Top market signals', icon: DollarSign, color: 'var(--conf)' },
  'leverage-spread': { title: 'Leverage spread', icon: Scale, color: 'var(--text-2)' },
}

function stagePill(stage?: string) {
  const s = (stage || '').toUpperCase()
  const cls = ['BREAKOUT', 'STRONG', 'EMERGING', 'WATCHING', 'MARGINAL', 'MONITORING'].includes(s) ? s : 'MONITORING'
  // Display rename: EMERGING shown as INDICATING (internal key unchanged for color).
  return <span className={'stage ' + cls}>{(s === 'EMERGING' ? 'INDICATING' : s) || '—'}</span>
}
const num = (v: number, c: string) => <span className="dash-row-v" style={{ color: c }}>{v}</span>
const pill = (t: string, col: string, bg: string) => <span className="dash-pill" style={{ color: col, background: bg }}>{t}</span>

export function Dashboard({ onNav, onNavHistory }: { onNav: (k: NavKey) => void; onNavHistory?: (q: string) => void }) {
  const [topics, setTopics] = useState<TopicRow[]>([])
  const [risks, setRisks] = useState<RiskRow[]>([])
  const [tiles, setTiles] = useState<DashTile[]>(DEFAULT_TILES)
  const [loading, setLoading] = useState(true)
  const [edit, setEdit] = useState(false)
  const [building, setBuilding] = useState(false)
  const [drag, setDrag] = useState<number | null>(null)

  useEffect(() => {
    let alive = true
    Promise.all([
      api.topics(200).catch(() => ({ topics: [] as TopicRow[] })),
      api.risk(200).catch(() => ({ results: [] as RiskRow[] })),
      getDashboard().catch(() => ({ tiles: [] as DashTile[] })),
    ]).then(([t, r, d]) => {
      if (!alive) return
      setTopics(t.topics || [])
      setRisks((r as any).results || [])
      setTiles(d.tiles && d.tiles.length ? d.tiles : DEFAULT_TILES)
    }).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const persist = (next: DashTile[]) => { setTiles(next); saveDashboard(next).catch(() => {}) }
  const removeTile = (id: string) => persist(tiles.filter((t) => t.id !== id))
  const addTile = (t: DashTile) => { persist([...tiles, t]); setBuilding(false) }
  const drop = (to: number) => {
    if (drag === null || drag === to) return
    const next = tiles.slice(); const [m] = next.splice(drag, 1); next.splice(to, 0, m)
    setDrag(null); persist(next)
  }

  // ── derived data ─────────────────────────────────────────────
  const T = useMemo(() => topics.map((t) => ({
    key: t.topic_key, name: t.topic_display || t.topic_key, det: r0(t.detection_score),
    conf: r0(t.confidence_score), n: r0(t.nowtrendin_score), stage: t.current_stage,
    category: (t.category || '').toLowerCase(),
  })), [topics])
  const M = useMemo(() => risks.map((r) => {
    const mg = r.market_gradient || {}
    return { key: r.risk_topic, name: r.risk_display || r.risk_topic, det: r0(mg.detection ?? r.detection_score),
      tier: (mg.tier || r.risk_stage || '—'), lev: mg.leverage_health == null ? null : r0(mg.leverage_health) }
  }), [risks])

  function rowsForTrends(cfg: any) {
    let r = T.slice()
    if (cfg?.stage) r = r.filter((x) => (x.stage || '').toUpperCase() === cfg.stage)
    if (cfg?.category) r = r.filter((x) => x.category === cfg.category)
    const by = cfg?.rankBy || 'n'
    if (by === 'mingap') r = r.filter((x) => x.det >= 70).sort((a, b) => Math.abs(a.det - a.conf) - Math.abs(b.det - b.conf))
    else r.sort((a, b) => (b as any)[by] - (a as any)[by])
    return r.slice(0, 5)
  }
  function rowsForMarket(cfg: any) {
    let r = M.slice()
    if (cfg?.tier) r = r.filter((x) => (x.tier || '').toUpperCase() === cfg.tier)
    const by = cfg?.rankBy || 'det'
    if (by === 'leverage') r = r.filter((x) => x.lev != null).sort((a, b) => (b.lev! - a.lev!))
    else r.sort((a, b) => b.det - a.det)
    return r.slice(0, 5)
  }

  function renderTileBody(t: DashTile) {
    switch (t.type) {
      case 'top-trends-mingap': {
        const rows = T.filter((x) => x.det >= 70).sort((a, b) => Math.abs(a.det - a.conf) - Math.abs(b.det - b.conf)).slice(0, 5)
        return rows.length ? rows.map((x) => <div className="dash-row" key={x.key} onClick={() => onNav('trends')}><span className="dash-nm">{x.name}</span>{num(x.det, 'var(--det)')}{num(x.conf, 'var(--conf)')}{pill('gap ' + Math.abs(x.det - x.conf), 'var(--em-t)', 'var(--em-b)')}</div>) : <div className="dash-empty">No high-conviction trends.</div>
      }
      case 'top-n': {
        const rows = [...T].sort((a, b) => b.n - a.n).slice(0, 5)
        return rows.map((x) => <div className="dash-row" key={x.key} onClick={() => onNav('trends')}><span className="dash-nm">{x.name}</span>{pill('N ' + x.n, 'var(--early)', 'var(--early-soft)')}{num(x.det, 'var(--text-3)')}</div>)
      }
      case 'top-market': {
        const rows = [...M].sort((a, b) => b.det - a.det).slice(0, 5)
        return rows.length ? rows.map((x) => <div className="dash-row" key={x.key} onClick={() => onNav('market')}><span className="dash-nm">{x.name}</span>{num(x.det, 'var(--det)')}{pill(x.tier, 'var(--st-t)', 'var(--st-b)')}</div>) : <div className="dash-empty">Market unavailable.</div>
      }
      case 'leverage-spread': {
        const lev = M.filter((m) => m.lev != null) as any[]
        const low = [...lev].sort((a, b) => b.lev - a.lev).slice(0, 4)
        const high = [...lev].sort((a, b) => a.lev - b.lev).slice(0, 4)
        return lev.length ? (
          <div className="dash-split">
            <div><div className="dash-lbl" style={{ color: 'var(--conf)' }}>LOW RISK</div>{low.map((m) => <div className="dash-row" key={m.key} onClick={() => onNav('market')}><span className="dash-nm">{m.name}</span>{num(m.lev, 'var(--conf)')}</div>)}</div>
            <div><div className="dash-lbl" style={{ color: 'var(--down)' }}>HIGH RISK</div>{high.map((m) => <div className="dash-row" key={m.key} onClick={() => onNav('market')}><span className="dash-nm">{m.name}</span>{num(m.lev, 'var(--down)')}</div>)}</div>
          </div>
        ) : <div className="dash-empty">No leverage data.</div>
      }
      case 'trends-custom': {
        const rows = rowsForTrends(t.config)
        return rows.length ? rows.map((x) => <div className="dash-row" key={x.key} onClick={() => onNav('trends')}><span className="dash-nm">{x.name} {stagePill(x.stage)}</span>{num(x.det, 'var(--det)')}{num(x.conf, 'var(--conf)')}</div>) : <div className="dash-empty">No matches.</div>
      }
      case 'market-custom': {
        const rows = rowsForMarket(t.config)
        return rows.length ? rows.map((x) => <div className="dash-row" key={x.key} onClick={() => onNav('market')}><span className="dash-nm">{x.name}</span>{num(x.det, 'var(--det)')}{t.config?.rankBy === 'leverage' ? num(x.lev ?? 0, 'var(--text-2)') : pill(x.tier, 'var(--st-t)', 'var(--st-b)')}</div>) : <div className="dash-empty">No matches.</div>
      }
      case 'track-topic':
        return <TrackTile topicKey={t.config?.topic_key} display={t.config?.topic_display} onNav={onNav} onNavHistory={onNavHistory} />
      default:
        return <div className="dash-empty">Unknown tile.</div>
    }
  }

  function tileHead(t: DashTile) {
    const bi = BUILTIN_META[t.type]
    if (bi) { const Icon = bi.icon; return <><Icon size={17} color={bi.color} /> {bi.title}</> }
    if (t.type === 'trends-custom') return <><TrendingUp size={17} color="var(--det)" /> {t.title || 'Custom trends'}</>
    if (t.type === 'market-custom') return <><DollarSign size={17} color="var(--conf)" /> {t.title || 'Custom market'}</>
    if (t.type === 'track-topic') return <><LineChart size={17} color="var(--early)" /> {t.title || `Track: ${t.config?.topic_display || ''}`}</>
    return <>{t.title}</>
  }
  const tileNav = (t: DashTile): NavKey => (t.type.includes('market') ? 'market' : t.type === 'track-topic' ? 'history' : 'trends')

  if (loading) return <div className="center-state"><div className="spinner" />Loading dashboard…</div>

  return (
    <div className="dash">
      <div className="dash-head">
        <span className="h">Dashboard</span>
        <span className="s">· {edit ? 'edit mode — drag to reorder, ✕ to remove' : 'at a glance'}</span>
        <button className="dash-edit" onClick={() => { setEdit(!edit); setBuilding(false) }}>
          {edit ? <><Check size={14} /> Done</> : <><Pencil size={14} /> Edit dashboard</>}
        </button>
      </div>

      <div className="dash-grid">
        {tiles.map((t, i) => (
          <div className={'dash-tile' + (edit ? ' editing' : '')} key={t.id}
            draggable={edit} onDragStart={() => setDrag(i)} onDragOver={(e) => e.preventDefault()} onDrop={() => drop(i)}>
            {edit && <div className="dash-tile-ctrls"><span className="dash-grip" title="Drag to reorder"><GripVertical size={15} /></span><span className="dash-del" title="Remove" onClick={() => removeTile(t.id)}><X size={15} /></span></div>}
            <h3>{tileHead(t)}{!edit && <span className="sub" onClick={() => onNav(tileNav(t))}>view all →</span>}</h3>
            {renderTileBody(t)}
          </div>
        ))}

        {edit && (
          <div className="dash-tile dash-addtile" onClick={() => setBuilding(true)}>
            <Plus size={22} /><span>Create new metric</span>
          </div>
        )}
      </div>

      {building && <TileBuilder topics={T} onAdd={addTile} onCancel={() => setBuilding(false)} />}
    </div>
  )
}

// ── Track-a-topic tile — self-fetches the topic's trajectory ──────
function TrackTile({ topicKey, display, onNav, onNavHistory }: { topicKey?: string; display?: string; onNav: (k: NavKey) => void; onNavHistory?: (q: string) => void }) {
  const [d, setD] = useState<any[] | null>(null)
  useEffect(() => {
    if (!topicKey) return
    api.scoreHistory(topicKey).then((x) => setD((x.rows || []).slice().reverse())).catch(() => setD([]))
  }, [topicKey])
  if (!topicKey) return <div className="dash-empty">No topic set.</div>
  if (d === null) return <div className="dash-empty">Loading…</div>
  if (d.length < 2) return <div className="dash-empty">Not enough history.</div>
  const det = d.map((r) => r0(r.detection)), conf = d.map((r) => r0(r.confidence))
  const slope = det[det.length - 1] - det[0]
  const trend = slope >= 3 ? 'Rising' : slope <= -3 ? 'Falling' : 'Flat'
  const tcol = slope >= 3 ? 'var(--bk-t)' : slope <= -3 ? 'var(--down)' : 'var(--text-3)'
  const W = 240, H = 70, pad = 5
  const xs = (i: number) => pad + i * (W - 2 * pad) / (d.length - 1)
  const ys = (v: number) => H - pad - (Math.max(0, Math.min(100, v)) / 100) * (H - 2 * pad)
  const ln = (a: number[]) => a.map((v, i) => `${xs(i).toFixed(1)},${ys(v).toFixed(1)}`).join(' ')
  return (
    <div onClick={() => onNavHistory ? onNavHistory(display || topicKey || '') : onNav('history')} style={{ cursor: 'pointer' }}>
      <div className="dash-row" style={{ borderTop: 'none', paddingTop: 0 }}>
        <span className="dash-nm" style={{ fontWeight: 600 }}>{display || topicKey}</span>
        <span className="dash-pill" style={{ color: tcol, background: 'var(--line-2)' }}>{trend}</span>
        <span className="dash-row-v" style={{ color: 'var(--det)' }}>{det[det.length - 1]}</span>
        <span className="dash-row-v" style={{ color: 'var(--conf)' }}>{conf[conf.length - 1]}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto', display: 'block', marginTop: 6 }}>
        <polyline points={ln(det)} style={{ stroke: 'var(--det)', fill: 'none' }} strokeWidth={2} />
        <polyline points={ln(conf)} style={{ stroke: 'var(--conf)', fill: 'none' }} strokeWidth={2} />
      </svg>
    </div>
  )
}

// ── Tile builder ──────────────────────────────────────────────────
function TileBuilder({ topics, onAdd, onCancel }: { topics: { key: string; name: string }[]; onAdd: (t: DashTile) => void; onCancel: () => void }) {
  const [section, setSection] = useState<'trends' | 'market' | 'track'>('trends')
  const [rankBy, setRankBy] = useState('n')
  const [stage, setStage] = useState('')
  const [tier, setTier] = useState('')
  const [topic, setTopic] = useState('')
  const [topicKey, setTopicKey] = useState('')
  const [name, setName] = useState('')

  const TREND_RANK = [['n', 'N'], ['det', 'Detection'], ['conf', 'Confidence'], ['mingap', 'Min gap']]
  const MKT_RANK = [['det', 'Money Movement'], ['leverage', 'Leverage']]
  const STAGES = ['', 'BREAKOUT', 'STRONG', 'EMERGING', 'WATCHING', 'MONITORING']
  const TIERS = ['', 'ELEVATED', 'ACTIVE', 'MODERATE', 'ROUTINE', 'DORMANT']
  // Verified typeahead (same as the watchlist): filter the live topic universe as
  // the user types; a tile can only track a topic that exists in our database.
  const tq = topic.trim().toLowerCase()
  const matches = !topicKey && tq.length >= 2
    ? topics.filter((s) => s.name.toLowerCase().includes(tq) || s.key.toLowerCase().includes(tq)).slice(0, 8)
    : []

  const add = () => {
    if (section === 'track') {
      if (!topicKey) return  // hard gate — must be a verified DB topic
      onAdd({ id: newId(), type: 'track-topic', title: name || `Track: ${topic.trim()}`, config: { topic_key: topicKey, topic_display: topic.trim() } })
    } else if (section === 'trends') {
      onAdd({ id: newId(), type: 'trends-custom', title: name || 'Custom trends', config: { rankBy, stage: stage || undefined } })
    } else {
      onAdd({ id: newId(), type: 'market-custom', title: name || 'Custom market', config: { rankBy: rankBy === 'n' || rankBy === 'conf' || rankBy === 'mingap' ? 'det' : rankBy, tier: tier || undefined } })
    }
  }
  const chip = (on: boolean, label: string, fn: () => void) => <button className={'al-chip' + (on ? ' on' : '')} onClick={fn} style={{ textTransform: 'capitalize' }}>{label}</button>

  return (
    <div className="dash-builder">
      <div className="dash-builder-h">New metric tile <span className="dash-builder-x" onClick={onCancel}><X size={16} /></span></div>
      <label className="al-lbl">Section</label>
      <div className="al-chips">
        {chip(section === 'trends', 'Trends', () => { setSection('trends'); setRankBy('n') })}
        {chip(section === 'market', 'Market', () => { setSection('market'); setRankBy('det') })}
        {chip(section === 'track', 'Track a topic', () => setSection('track'))}
      </div>

      {section === 'track' ? (
        <>
          <label className="al-lbl">Topic — search and select a verified topic</label>
          <input className="al-input" value={topic} placeholder="Search a topic…" onChange={(e) => { setTopic(e.target.value); setTopicKey('') }} />
          {topicKey ? (
            <div className="al-verified">✓ {topic} <button className="al-verified-x" onClick={() => { setTopic(''); setTopicKey('') }} title="Clear">✕</button></div>
          ) : matches.length > 0 ? (
            <div className="al-chips">{matches.map((s) => <button key={s.key} className="al-chip" onClick={() => { setTopic(s.name); setTopicKey(s.key) }}>{s.name}</button>)}</div>
          ) : tq.length >= 2 ? (
            <div className="al-hint">Not in our database — only existing topics can be tracked.</div>
          ) : null}
        </>
      ) : (
        <>
          <label className="al-lbl">Rank by</label>
          <div className="al-chips">{(section === 'trends' ? TREND_RANK : MKT_RANK).map(([k, l]) => chip(rankBy === k, l, () => setRankBy(k)))}</div>
          <label className="al-lbl">Filter</label>
          <div className="al-chips">
            {section === 'trends'
              ? STAGES.map((s) => chip(stage === s, (s === 'EMERGING' ? 'INDICATING' : s) || 'Any stage', () => setStage(s)))
              : TIERS.map((t) => chip(tier === t, t || 'Any tier', () => setTier(t)))}
          </div>
        </>
      )}

      <div className="dash-builder-foot">
        <input className="al-input" style={{ flex: 1, marginBottom: 0 }} value={name} placeholder="Tile name" onChange={(e) => setName(e.target.value)} />
        <button className="al-create" style={{ width: 'auto', marginTop: 0, padding: '0 18px', height: 36 }} onClick={add} disabled={section === 'track' && !topicKey}>Add tile</button>
      </div>
    </div>
  )
}
