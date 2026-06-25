import { useEffect, useState, useCallback } from 'react'
import { X } from 'lucide-react'
import { grade as gradeApi, gradeHistory, gradedAll, type User } from '../lib/auth'
import { api } from '../lib/api'
import { MC, stageColor, marketTierColor, GAP_BANDS, gapBandIndex } from '../lib/mobileTheme'
import { Disclaimer } from '../components/Disclaimer'

// GRADE — the AI Grade tool, web parity with the mobile GradeTool. Three tabs:
// New Grade (token-metered AI proposed score), History (this member's grades,
// free), Graded (all members' graded topics, free). The result page carries the
// three required reads: AI Context definition, Signal Quality analysis, N score.

const GOLD = '#D4A017'
type Tab = 'new' | 'history' | 'graded'

function timeAgo(iso: string) {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (isNaN(mins)) return ''
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const h = Math.floor(mins / 60); if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24); return d < 30 ? `${d}d ago` : new Date(iso).toLocaleDateString()
}

function ring(val: number, color: string) {
  const r = 22, c = 2 * Math.PI * r, off = c * (1 - Math.max(0, Math.min(100, val)) / 100)
  return (
    <svg width="60" height="60" viewBox="0 0 60 60">
      <circle cx="30" cy="30" r={r} fill="none" stroke="var(--line)" strokeWidth="5" />
      <circle cx="30" cy="30" r={r} fill="none" stroke={color} strokeWidth="5" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={off} transform="rotate(-90 30 30)" />
      <text x="30" y="34" textAnchor="middle" fontSize="15" fontWeight="800" fill={color}>{Math.round(val)}</text>
    </svg>
  )
}

function ProposedCard({ result, topic }: { result: any; topic: string }) {
  const det = Math.round(result.detection_score ?? 0)
  const conf = Math.round(result.confidence_score ?? 0)
  const gap = Math.abs(Math.round(result.heisenberg_gap ?? (det - conf)))
  const band = GAP_BANDS[gapBandIndex(gap)]
  const ms = result.market_signal?.market_gradient
  const scol = stageColor(result.stage)
  // Measured topics carry their components under measured_row (with _score suffixes);
  // AI-proposed topics carry them at the top level — read both so the bars aren't 0.
  const _qc = result.measured_row || result
  const quality: [string, number][] = [
    ['Niche Concentration', _qc.gradient_strength],
    ['Platform Diversity', _qc.platform_diversity],
    ['Momentum', _qc.inertia_score ?? _qc.inertia],
    ['Dark Matter', _qc.dark_matter_score ?? _qc.dark_matter],
    ['Persistence', _qc.persistence_score ?? _qc.persistence],
  ]
  const measured = result.source === 'measured'
  // N score comes straight from the Grade Agent now (live engine value).
  const nScore = result.n_score != null ? Math.round(result.n_score) : null
  // AI Context — source-aware definition for the graded topic (best-effort).
  const [ctx, setCtx] = useState<string | null>(null)
  useEffect(() => {
    let alive = true
    const key = (result.topic_key || topic).trim().toLowerCase().replace(/\s+/g, '_')
    api.explainer(key).then((x) => alive && setCtx(x?.available ? (x.full || x.short || null) : null)).catch(() => {})
    return () => { alive = false }
  }, [topic, result.topic_key])

  const gradedName = result.topic_display || result.topic || topic || (result.topic_key || '').replace(/_/g, ' ')
  return (
    <div className="grade-result">
      {/* Graded topic name + how it was graded — so the user always sees WHAT was
          graded and understands the (up to) three independent reads below. */}
      <div className="g-graded-title" style={{ fontSize: 22, fontWeight: 800, color: MC.text, marginBottom: 4, textTransform: 'capitalize' }}>{gradedName}</div>
      <div className="g-grade-explain" style={{ fontSize: 12.5, lineHeight: 1.5, color: MC.textSec, background: '#F7F8FA', border: '1px solid #E4E7EC', borderRadius: 10, padding: '10px 12px', marginBottom: 14 }}>
        <div style={{ marginBottom: 6 }}>
          <b style={{ color: MC.text }}>How this topic is graded.</b>{' '}
          {measured
            ? <>This topic is already in NowTrendIn’s live data pool, so the scores below are the engine’s <b>MEASURED</b> read — no AI estimate, no grade credit charged.</>
            : <>This topic isn’t in the pool yet, so the AI researched the open web and <b>PROPOSED</b> a score from the evidence (1 grade credit).</>}
        </div>
        <div style={{ marginBottom: 4 }}>You may see up to three <b>independent reads</b> — they answer different questions, so they can legitimately differ:</div>
        <div style={{ paddingLeft: 2 }}>
          <div>• <b style={{ color: MC.detection }}>Attention (Gradient Score)</b> — how much human attention is moving toward this, and how early. <i>The headline read.</i></div>
          <div>• <b style={{ color: MC.amber }}>Market Signal</b> (companies only) — whether market positioning is unusual vs this stock’s <i>own</i> baseline. Not attention.</div>
          <div>• <b style={{ color: MC.orange }}>N · Now Trending</b> — how often this topic is triggered + surfaced as a tracked topic across the platform. A separate signal, never folded into the Gradient.</div>
        </div>
      </div>
      {/* Legal disclaimer — top, above the Market Signal score */}
      <Disclaimer style={{ marginBottom: 12 }} />
      {/* Market read first (companies) */}
      {ms && (() => {
        const tc = marketTierColor(ms.tier)
        const msV2 = !!((ms as any).model_version || (ms as any).flow || (ms as any).money_movement)
        const flow = (ms as any).flow as string | undefined
        const mAnalysis = result.market_analysis?.text as string | undefined
        return (
          <div className="g-card" style={{ borderColor: tc + '44' }}>
            <div className="g-kicker" style={{ color: MC.amber }}>Market Signal · {msV2 ? 'money movement' : 'market positioning'}
              <span className="g-tier" style={{ background: tc + '1A', color: tc }}>{ms.calibrating ? 'CALIBRATING' : ms.data_coverage === 'insufficient' ? 'LIMITED DATA' : ms.tier}</span>
              {msV2 && flow && <span className="g-tier" style={{ background: (flow === 'inflow' ? MC.confidence : flow === 'outflow' ? MC.red : MC.muted) + '1A', color: flow === 'inflow' ? MC.confidence : flow === 'outflow' ? MC.red : MC.muted }}>{flow === 'inflow' ? '▲ inflow' : flow === 'outflow' ? '▼ outflow' : '• neutral'}</span>}</div>
            <div className="g-rings" style={ms.data_coverage === 'insufficient' ? { opacity: 0.55 } : undefined}>
              <div className="g-ring">{ring(ms.detection, MC.detection)}<div className="g-rl">{msV2 ? 'MONEY MOVEMENT' : 'DETECTION'}</div><div className="g-rf">{msV2 ? 'informed money · D' : 'analysts + positioning'}</div></div>
              <div className="g-ring">{ring(ms.confidence, MC.confidence)}<div className="g-rl">{msV2 ? 'MARKET CONFIRMATION' : 'CONFIDENCE'}</div><div className="g-rf">{msV2 ? 'broad market · M' : 'fundamentals + price'}</div></div>
            </div>
            {ms.leverage_health != null && <div className="g-lev">Leverage Health {Math.round(ms.leverage_health)}/100 (high = lower debt)</div>}
            {ms.data_coverage === 'insufficient' ? (
              <div className="narr" style={{ background: '#FFF4E5', border: '1px solid #F0C27B', color: '#8A5A00', borderRadius: 8, padding: '8px 10px' }}>
                ⚠ <b>Insufficient positioning data.</b> Smart-money &amp; short-interest sources (FINRA short interest / 13F holdings) aren’t populated for this instrument yet{ms.absent_inputs != null ? ` (${ms.absent_inputs}/${ms.total_inputs} inputs absent)` : ''}, so this sits near baseline. Treat as limited coverage — <i>not</i> a confirmed quiet market.
              </div>
            ) : (ms.interpretation && <div className="narr">{ms.interpretation}</div>)}
            {mAnalysis && <div className="narr" style={{ marginTop: 6 }}><b style={{ color: MC.amber }}>AI analysis</b> — {mAnalysis}<div className="disc" style={{ marginTop: 6 }}>AI measurement of money movement, market confirmation &amp; leverage from our scores — computer-generated, not financial advice.</div></div>}
            <div className="disc">Measured MARKET read — is positioning unusual vs this stock’s <i>own</i> baseline? Same data as the Market section. The Attention/Gradient read below is a separate question.</div>
          </div>
        )
      })()}

      {/* Gradient read — MEASURED (from data pool) or AI-PROPOSED */}
      <div className="g-card">
        <div className="g-kicker" style={{ color: MC.detection }}>
          {measured ? 'Attention · Gradient Score · measured' : 'Attention · Gradient Score · AI estimate'}
          <span className="g-tier" style={{ background: (measured ? MC.confidence : GOLD) + '1A', color: measured ? MC.confidence : GOLD }}>
            {measured ? 'IN DATA POOL' : 'AI ESTIMATE'}</span>
          <span className="g-tier" style={{ background: scol + '1A', color: scol }}>{result.stage}</span>
        </div>
        <div className="disc" style={{ marginTop: -2, marginBottom: 8 }}>
          How much human attention is moving toward this topic — <b style={{ color: MC.detection }}>Detection</b> = how early/strong, <b style={{ color: MC.confidence }}>Confidence</b> = how broadly confirmed.
        </div>
        {result.note && <div className="disc" style={{ marginTop: -4, marginBottom: 8 }}>{result.note}</div>}
        <div className="g-rings">
          <div className="g-ring">{ring(det, MC.detection)}<div className="g-rl">DETECTION</div></div>
          <div className="g-ring">{ring(conf, MC.confidence)}<div className="g-rl">CONFIDENCE</div></div>
        </div>
        <div className="g-gapband" style={{ borderColor: band.color + '55', background: band.color + '0F' }}>
          <b style={{ color: band.color }}>{gap}-point gap — {band.label}</b>
        </div>
        {result.action && <div className="g-action" style={{ color: scol }}>{result.action}</div>}
        {result.reasoning && <div className="narr" style={{ marginBottom: 10 }}>{result.reasoning}</div>}

        {/* Mainstream vs Niche — engine (in pool) or open-web research (off pool) */}
        {result.mainstream_vs_niche && (() => {
          const mv = result.mainstream_vs_niche
          const col = mv.label === 'mainstream' ? MC.confidence : mv.label === 'emerging' ? MC.gold
            : mv.label === 'fading' ? MC.slate : MC.detection
          return (
            <>
              <h4 className="g-h">Mainstream vs Niche</h4>
              <div className="kv"><span>Reach</span><b style={{ textTransform: 'capitalize', color: col }}>{mv.label}</b></div>
              {mv.note && <div className="disc">{mv.note}</div>}
              <div className="disc">Determined from: {mv.source}{result.consulted ? ` · consulted ${result.consulted.length} data agents` : ''}</div>
            </>
          )
        })()}

        {/* (1) AI Context definition */}
        <h4 className="g-h">AI Context</h4>
        <div className="narr">{ctx || result.research || 'A source-aware definition generates on first view; the AI reasoning above summarizes what this topic is and why it scores here.'}</div>

        {/* (2) Signal Quality analysis */}
        <h4 className="g-h">Signal Quality Analysis</h4>
        {quality.map(([label, val]) => {
          const v = Math.max(0, Math.min(100, Math.round(val ?? 0)))
          return (
            <div className="comp-row" key={label}>
              <span className="cl">{label}</span>
              <span className="comp-bar"><i style={{ width: `${v}%`, background: GOLD }} /></span>
              <span className="cv">{v}</span>
            </div>
          )
        })}

        {/* (3) N score — Now Trending (platform tracking, NOT user demand) */}
        <h4 className="g-h" style={{ color: MC.orange }}>N Score · Now Trending</h4>
        <div className="kv"><span>N (platform tracking)</span><b style={{ color: MC.orange }}>{nScore != null && nScore > 0 ? nScore : 'not yet registered'}</b></div>
        <div className="disc">N — how often a topic is triggered + surfaced as a tracked topic across the Now TrendIn platform (feeds, queries, grades) — is a SEPARATE signal, never folded into the Gradient (no feedback loop). {measured ? 'Measured live from the engine.' : 'Registers once platform tracking accrues; this grade query logs it.'}</div>

        {Array.isArray(result.citations) && result.citations.length > 0 && (
          <>
            <h4 className="g-h">Sources</h4>
            {result.citations.slice(0, 8).map((c: string, i: number) => <div className="g-cite" key={i}>• {c}</div>)}
          </>
        )}
        <div className="disc">Proposed score — an AI estimate from public web evidence, not a measured engine score.</div>
      </div>
      {/* Legal disclaimer — bottom of the grade result */}
      <Disclaimer style={{ marginTop: 12 }} />
    </div>
  )
}

function GradeList({ kind }: { kind: 'history' | 'graded' }) {
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [sel, setSel] = useState<any | null>(null)
  const load = useCallback(async (query: string) => {
    setLoading(true)
    try {
      const d = kind === 'history' ? await gradeHistory(query) : await gradedAll(query)
      setRows(Array.isArray(d?.grades) ? d.grades : [])
    } catch { setRows([]) } finally { setLoading(false) }
  }, [kind])
  useEffect(() => { const t = setTimeout(() => load(q.trim()), 350); return () => clearTimeout(t) }, [q, load])

  if (sel) {
    const hasResult = sel.result && Object.keys(sel.result).length > 0
    return (
      <div>
        <button className="btn" onClick={() => setSel(null)} style={{ marginBottom: 14 }}>← Back</button>
        {hasResult
          ? <ProposedCard result={sel.result} topic={sel.topic} />
          : <div className="center-state">Full grade detail was not saved for this entry.</div>}
      </div>
    )
  }

  return (
    <div>
      <div className="add-row" style={{ margin: '0 0 10px', position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input value={q} onChange={(e) => setQ(e.target.value)}
          placeholder={kind === 'history' ? 'Search your graded topics…' : 'Search all graded topics…'}
          style={{ flex: 1, paddingRight: q ? 24 : undefined }} />
        {q && <button onClick={() => setQ('')} title="Clear" style={{ position: 'absolute', right: 6, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', padding: '2px', display: 'flex', alignItems: 'center' }}><X size={13} /></button>}
      </div>
      <div className="disc" style={{ marginBottom: 10 }}>
        {kind === 'history' ? 'Your AI grades from the last 12 months. No token charge to view.'
          : 'Topics graded by Now TrendIn members across all plans. No token charge to view.'}
      </div>
      {loading ? <div className="center-state"><div className="spinner" />Loading…</div>
        : rows.length === 0 ? <div className="center-state">{q ? 'No graded topics match.' : (kind === 'history' ? "You haven't graded any topics yet." : 'No topics graded yet.')}</div>
          : rows.map((g) => {
            const col = stageColor(g.stage)
            return (
              <div className="g-row" key={g.id} onClick={() => setSel(g)} style={{ cursor: 'pointer' }}>
                <div className="g-row-top"><span className="g-row-name">{g.topic}</span>
                  {g.stage && <span className="g-tier" style={{ background: col + '1A', color: col }}>{g.stage}</span>}</div>
                <div className="g-row-sc">
                  <span style={{ color: MC.detection }}>DET {Math.round(g.detection)}</span>
                  <span style={{ color: MC.confidence }}>CONF {Math.round(g.confidence)}</span>
                  <span className="g-row-age">{timeAgo(g.createdAt)}</span>
                </div>
              </div>
            )
          })}
    </div>
  )
}

export function Grade({ user, onUser }: { user: User; onUser?: (u: User) => void }) {
  const [tab, setTab] = useState<Tab>('new')
  const [topic, setTopic] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)
  const [tokens, setTokens] = useState(user.gradeTokens ?? 0)
  const canGrade = !!user.tier

  const doGrade = async () => {
    setMsg(null); setResult(null); setBusy(true)
    try {
      const d: any = await gradeApi(topic.trim())
      if (d?.gradeTokens != null) { setTokens(d.gradeTokens); onUser?.({ ...user, gradeTokens: d.gradeTokens }) }
      if (d?.available && d?.proposed) setResult(d)
      else setMsg(d?.detail ?? d?.reason ?? 'AI grading is not available yet.')
    } catch (e: any) { setMsg(e?.data?.detail ?? 'Grade failed. Try again.') }
    finally { setBusy(false) }
  }

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Grade</div>
          <div className="main-sub">Propose a Gradient Score for any topic — AI researches the open web and returns a score with the evidence</div>
        </div>
        <div className="chips tight">
          <span className="chip-label">Grade</span>
          <div className={'chip' + (tab === 'new' ? ' active' : '')} onClick={() => setTab('new')}>+ New Grade</div>
          <div className={'chip' + (tab === 'history' ? ' active' : '')} onClick={() => setTab('history')}>My History</div>
          <div className={'chip' + (tab === 'graded' ? ' active' : '')} onClick={() => setTab('graded')}>Graded Library</div>
        </div>
      </div>

      <div className="grid-wrap" style={{ maxWidth: 760 }}>
        {tab === 'new' && (
          !canGrade ? (
            <div className="center-state">Choose a plan<div className="muted">AI grading is included on every plan with a monthly credit allowance.</div></div>
          ) : (
            <>
              <div className="g-grade-box">
                <div className="add-row" style={{ margin: '0 0 10px' }}>
                  <input value={topic} onChange={(e) => setTopic(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && topic.trim() && tokens > 0) doGrade() }}
                    placeholder="Enter any word or topic to grade…" />
                </div>
                <div className="g-grade-meta">
                  <span>Researches the open web and proposes a score with citations — uses 1 grade token.</span>
                  <span className="g-tok">{tokens} grade tokens left</span>
                </div>
                <button className="btn primary g-pull" disabled={busy || !topic.trim() || tokens <= 0} onClick={doGrade}>
                  {busy ? '⟳ Researching… ~20–40s' : tokens <= 0 ? 'No grade tokens remaining this month' : '⚡ Pull Grade · 1 token'}
                </button>
                {msg && <div className="g-err">{msg}</div>}
              </div>
              {result && <ProposedCard result={result} topic={topic.trim()} />}
            </>
          )
        )}
        {tab === 'history' && <GradeList kind="history" />}
        {tab === 'graded' && <GradeList kind="graded" />}
      </div>
    </>
  )
}
