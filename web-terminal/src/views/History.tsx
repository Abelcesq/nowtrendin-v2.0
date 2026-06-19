import { useEffect, useMemo, useState } from 'react'
import { TrendingUp, TrendingDown, Minus, RotateCcw, Sparkles } from 'lucide-react'
import { api, type HistoryRow } from '../lib/api'

// History — consistent with the mobile app (windowed list of recently-scored
// topics) PLUS the trajectory redesign: a sparkline + rising/falling/flat trend per
// row, and a featured line chart of the selected topic's score over time. One call
// (/history/recent) powers the list; the detail uses /scores/{key}/score-history.
const WINDOWS = ['12h', '24h', '7d']

function trendMeta(t: string): [JSX.Element, string, string] {
  if (t === 'up') return [<TrendingUp size={15} />, 'Rising', 'var(--bk-t)']
  if (t === 'down') return [<TrendingDown size={15} />, 'Falling', 'var(--down)']
  return [<Minus size={15} />, 'Flat', 'var(--text-3)']
}

function Spark({ pts, color }: { pts: number[]; color: string }) {
  if (pts.length < 2) return <svg width={84} height={26} />
  const max = Math.max(...pts), min = Math.min(...pts), rng = (max - min) || 1
  const P = pts.map((v, i) => `${(i * 84 / (pts.length - 1)).toFixed(1)},${(24 - ((v - min) / rng) * 20).toFixed(1)}`).join(' ')
  return <svg width={84} height={26} style={{ display: 'block', flex: '0 0 auto' }}><polyline points={P} style={{ stroke: color, fill: 'none' }} strokeWidth={2} /></svg>
}

function Trajectory({ rows }: { rows: { detection: number; confidence: number }[] }) {
  if (rows.length < 2) return <div className="hv-empty">Not enough history yet for a trajectory.</div>
  const W = 560, H = 150, pad = 10
  const xs = (i: number) => pad + i * (W - 2 * pad) / (rows.length - 1)
  const ys = (v: number) => H - pad - (Math.max(0, Math.min(100, v)) / 100) * (H - 2 * pad)
  const line = (k: 'detection' | 'confidence') => rows.map((r, i) => `${xs(i).toFixed(1)},${ys(r[k]).toFixed(1)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
      <line x1={0} y1={H - pad} x2={W} y2={H - pad} style={{ stroke: 'var(--line)' }} strokeWidth={1} />
      <polyline points={line('detection')} style={{ stroke: 'var(--det)', fill: 'none' }} strokeWidth={2.5} />
      <polyline points={line('confidence')} style={{ stroke: 'var(--conf)', fill: 'none' }} strokeWidth={2.5} />
    </svg>
  )
}

export function History({ preset }: { preset?: { topic: string; n: number } | null }) {
  const [win, setWin] = useState('7d')
  const [rows, setRows] = useState<HistoryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [sel, setSel] = useState<HistoryRow | null>(null)
  const [traj, setTraj] = useState<{ detection: number; confidence: number }[] | null>(null)
  const [an, setAn] = useState<{ available: boolean; short?: string; full?: string; citations?: string[]; reason?: string } | null>(null)
  const [anLoad, setAnLoad] = useState(false)

  const load = (w: string) => {
    setLoading(true)
    api.historyRecent(w, 80).then((d) => setRows(d.results || [])).catch(() => setRows([])).finally(() => setLoading(false))
  }
  useEffect(() => load(win), [win])

  const pick = (r: HistoryRow) => {
    setSel(r); setTraj(null); setAn(null)
    api.scoreHistory(r.topic_key)
      .then((d) => setTraj((d.rows || []).slice().reverse()))
      .catch(() => setTraj([]))
  }
  const explain = () => {
    if (!sel) return
    setAnLoad(true)
    api.historyAnalysis(sel.topic_key, sel.topic_display)
      .then(setAn).catch(() => setAn({ available: false, reason: 'Analysis failed.' }))
      .finally(() => setAnLoad(false))
  }

  // A "Track topic" favorite → default to the 12h window and auto-select that topic
  // (loads its trajectory directly even if it's not in the windowed list).
  useEffect(() => {
    if (!preset?.topic) return
    setWin('12h')
    const key = preset.topic
    const found = rows.find((r) => r.topic_key === key || (r.topic_display || '').toLowerCase().replace(/\s+/g, '_') === key)
    pick(found || { topic_key: key, topic_display: key.replace(/_/g, ' '), overall: 0, det: 0, conf: 0, n: 0, series: [], trend: 'flat', slope: 0 })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset?.n])

  const view = useMemo(() => {
    const ql = q.trim().toLowerCase()
    return ql ? rows.filter((r) => (r.topic_display || '').toLowerCase().includes(ql) || (r.topic_key || '').toLowerCase().includes(ql)) : rows
  }, [rows, q])

  return (
    <div className="hv">
      <div className="main-head"><div className="main-title-row">
        <div className="main-title">History</div>
        <div className="main-sub">How a topic has scored over time — rising, falling, or flat</div>
      </div></div>

      <div className="hv-controls">
        <div className="hv-wins">{WINDOWS.map((w) => (
          <button key={w} className={'hv-win' + (win === w ? ' on' : '')} onClick={() => setWin(w)}>{w}</button>
        ))}</div>
        <input className="hv-search" value={q} placeholder="Search history…" onChange={(e) => setQ(e.target.value)} />
        <button className="hv-refresh" onClick={() => load(win)} title="Refresh"><RotateCcw size={15} /></button>
      </div>

      {sel && (() => {
        const [icon, label, color] = trendMeta(sel.trend)
        return (
          <div className="hv-feature">
            <div className="hv-feat-head">
              <span className="hv-feat-name">{sel.topic_display}</span>
              <span className="hv-trend" style={{ color, background: 'var(--line-2)' }}>{icon} {label}</span>
              <span className="hv-feat-scores"><b style={{ color: 'var(--det)' }}>DET {sel.det}</b> &nbsp; <b style={{ color: 'var(--conf)' }}>CONF {sel.conf}</b></span>
            </div>
            <div className="hv-chartslot">{traj === null ? <div className="hv-loading">Loading trajectory…</div> : <Trajectory rows={traj} />}</div>
            <div className="hv-legend"><span style={{ color: 'var(--det)' }}>● Detection</span> &nbsp; <span style={{ color: 'var(--conf)' }}>● Confidence</span></div>
            <div className="hv-ai">
              {an?.available ? (
                <>
                  <div className="hv-ai-short"><Sparkles size={13} color="var(--early)" /> {an.short}</div>
                  {an.full && <div className="hv-ai-full">{an.full}</div>}
                  {!!an.citations?.length && <div className="hv-ai-cite">Sources: {an.citations.slice(0, 4).map((c, i) => <a key={i} href={c} target="_blank" rel="noopener noreferrer">[{i + 1}]</a>)}</div>}
                  <div className="hv-ai-disc">AI analysis of attention movement — measurement is computer generated. All information contained herein may not be accurate and should not be construed as financial, investment, or legal advice.</div>
                </>
              ) : an ? <div className="hv-ai-note">{an.reason || 'Analysis unavailable.'}</div>
                : <button className="hv-ai-btn" onClick={explain} disabled={anLoad}><Sparkles size={14} /> {anLoad ? 'Analysing…' : 'Explain this move (AI)'}</button>}
            </div>
          </div>
        )
      })()}

      {loading ? <div className="center-state"><div className="spinner" />Loading…</div>
        : (
          <div className="hv-list">
            <div className="hv-count">{view.length} topics scored · last {win}</div>
            {view.map((r) => {
              const [icon, , color] = trendMeta(r.trend)
              return (
                <div className={'hv-row' + (sel?.topic_key === r.topic_key ? ' sel' : '')} key={r.topic_key} onClick={() => pick(r)}>
                  <span className="hv-nm">{r.topic_display}{r.is_anomaly && <span className="hv-anom">ANOMALY</span>}</span>
                  <Spark pts={r.series.map((p) => p.overall)} color={color} />
                  <span className="hv-v" style={{ color: 'var(--det)' }}>{r.det}</span>
                  <span className="hv-v" style={{ color: 'var(--conf)' }}>{r.conf}</span>
                  <span className="hv-arrow" style={{ color }}>{icon}</span>
                </div>
              )
            })}
            {view.length === 0 && <div className="hv-empty">No history in this window.</div>}
          </div>
        )}
    </div>
  )
}
