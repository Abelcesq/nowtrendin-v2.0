import { useEffect, useMemo, useState } from 'react'
import { TrendingUp, TrendingDown, Minus, RotateCcw, Sparkles } from 'lucide-react'
import { api, type HistoryRow } from '../lib/api'
import { ScoreChart, type ChartPoint } from '../components/ScoreChart'

// History — windowed list of recently-scored topics, plus a featured axed chart of
// the selected topic's full scoring trajectory (Detection/Confidence over time, with
// the driving factors per point). The list uses /history/recent; the featured chart
// uses /scores/{key}/score-history (real per-cycle events), clipped to the window.
const WINDOWS = ['12h', '24h', '7d']
const WIN_MS: Record<string, number> = { '12h': 12 * 3600e3, '24h': 24 * 3600e3, '7d': 7 * 24 * 3600e3 }

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

export function History({ initialQ }: { initialQ?: string }) {
  const [win, setWin] = useState('7d')
  const [rows, setRows] = useState<HistoryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState(initialQ ?? '')
  const [selKey, setSelKey] = useState<string | null>(null)
  const [hist, setHist] = useState<ChartPoint[] | null>(null)   // enriched per-cycle history for the selected topic
  const [an, setAn] = useState<{ available: boolean; short?: string; full?: string; citations?: string[]; reason?: string } | null>(null)
  const [anLoad, setAnLoad] = useState(false)
  // Direct-lookup hit: used when the search term matches nothing in the top-80 list
  // (e.g. a low-scoring topic like SpaceX at ~40 that doesn't rank in the top 80).
  const [directHit, setDirectHit] = useState<HistoryRow | null>(null)

  const load = (w: string) => {
    setLoading(true)
    api.historyRecent(w, 80).then((d) => setRows(d.results || [])).catch(() => setRows([])).finally(() => setLoading(false))
  }
  useEffect(() => load(win), [win])
  // When a dashboard tile navigates here with a topic pre-set, apply the filter.
  useEffect(() => { if (initialQ) { setQ(initialQ); setSelKey(null) } }, [initialQ])

  // Fetch the full per-cycle scoring history (with driving factors) for the picked
  // topic; the chart clips it to the selected window below.
  const pick = (r: HistoryRow) => {
    setSelKey(r.topic_key); setAn(null); setHist(null)
    api.scoreHistory(r.topic_key)
      .then((d) => setHist((d.rows || []).map((x: any) => ({
        t: x.scored_at, det: Math.round(x.detection ?? 0), conf: Math.round(x.confidence ?? 0),
        overall: x.overall, gap: x.gap, mentions: x.mentions, platforms: x.platforms,
        stage: x.stage, inertia: x.inertia, dark_matter: x.dark_matter,
      }))))
      .catch(() => setHist([]))
  }

  const view = useMemo(() => {
    const ql = q.trim().toLowerCase()
    return ql ? rows.filter((r) => (r.topic_display || '').toLowerCase().includes(ql) || (r.topic_key || '').toLowerCase().includes(ql)) : rows
  }, [rows, q])

  // When the search has text but yields nothing from the top-80 list, try a direct
  // topic lookup so low-scoring topics (below the top-80 cutoff) are still findable.
  useEffect(() => {
    const ql = q.trim().toLowerCase()
    if (!ql || view.length > 0) { setDirectHit(null); return }
    const key = ql.replace(/\s+/g, '_')
    api.score(key)
      .then((d: any) => {
        if (!d?.topic_key) { setDirectHit(null); return }
        setDirectHit({
          topic_key: d.topic_key,
          topic_display: d.topic_display || d.topic_key,
          overall: Math.round(d.overall_score ?? 0),
          det: Math.round(d.detection_score ?? 0),
          conf: Math.round(d.confidence_score ?? 0),
          n: Math.round(d.nowtrendin_score ?? 0),
          stage: d.signal_stage,
          is_anomaly: !!d.is_gravitational_anomaly,
          scored_at: d.scored_at,
          series: [],
          trend: 'flat',
          slope: 0,
        })
      })
      .catch(() => setDirectHit(null))
  }, [q, view.length])

  const effectiveView = view.length > 0 ? view : (directHit ? [directHit] : [])

  // sel must also check directHit so the featured chart works for direct-lookup results.
  const sel = useMemo(() => {
    if (!selKey) return null
    return rows.find((r) => r.topic_key === selKey) ?? (directHit?.topic_key === selKey ? directHit : null)
  }, [rows, selKey, directHit])

  // Clip the per-cycle history to the selected window so the chart reflects 12h/24h/7d.
  const chartPoints = useMemo(() => {
    const cutoff = Date.now() - (WIN_MS[win] ?? WIN_MS['7d'])
    return (hist ?? []).filter((p) => +new Date(p.t) >= cutoff)
  }, [hist, win])
  const explain = () => {
    if (!sel) return
    setAnLoad(true)
    api.historyAnalysis(sel.topic_key, sel.topic_display)
      .then(setAn).catch(() => setAn({ available: false, reason: 'Analysis failed.' }))
      .finally(() => setAnLoad(false))
  }

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
            <div className="hv-chartslot">{hist === null ? <div className="hv-loading">Loading trajectory…</div> : <ScoreChart points={chartPoints} />}</div>
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
            <div className="hv-count">{effectiveView.length} topics scored · last {win}</div>
            {effectiveView.map((r) => {
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
            {effectiveView.length === 0 && <div className="hv-empty">No history in this window.</div>}
          </div>
        )}
    </div>
  )
}
