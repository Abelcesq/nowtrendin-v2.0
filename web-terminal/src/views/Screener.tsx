import { useEffect, useMemo, useState } from 'react'
import { Star, Bell, Download } from 'lucide-react'
import { api, type TopicRow } from '../lib/api'
import { pullTrends } from '../lib/auth'
import { addToWatchlist, exportEntityCsv } from '../lib/actions'
import { MC, stageColor, maturityColor, GAP_BANDS, gapBandIndex, SCORE_ROLES } from '../lib/mobileTheme'

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
  // Stage-coherent tiers — each filter shows ONLY topics whose Detection-derived
  // stage matches, so the Stage badge always agrees with the selected filter.
  { k: 'breakout', label: 'Breakout ≥85', test: (r) => r.det >= 85 },
  { k: 'strong', label: 'Strong ≥70', test: (r) => r.det >= 70 && r.det < 85 },
  { k: 'emerging', label: 'Emerging', test: (r) => r.det >= 55 && r.det < 70 },
  { k: 'marginal', label: 'Marginal', test: (r) => r.det >= 35 && r.det < 55 },
  // Anomalies = DETECTION running ahead of CONFIRMATION (signed gap ≥ 16) — the
  // "future arriving" shape. NOT |gap| (also caught lagging conf>det topics) and
  // NOT the engine is_anomaly flag (which fires on accelerating already-confirmed
  // topics — 126 of 131 were conf>det). Orthogonal to strength: an anomaly can be
  // STRONG or MARGINAL — what defines it is the early-edge lead, not the level.
  { k: 'anomalies', label: 'Anomalies', test: (r) => (r.det - r.conf) >= 16 },
]

interface Row extends TopicRow { det: number; conf: number; n: number; gap: number; stage: string; ageMin: number }
type SortKey = 'topic_display' | 'det' | 'conf' | 'n' | 'gap' | 'stage' | 'category' | 'total_mentions' | 'ageMin'

function stageOf(d: number) {
  return d >= 85 ? 'BREAKOUT' : d >= 70 ? 'STRONG' : d >= 55 ? 'EMERGING' : d >= 35 ? 'MARGINAL' : 'MONITORING'
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

  // Lazy panels (same endpoints the mobile signal page uses).
  const [conv, setConv] = useState<any>(null)
  const [xsig, setXsig] = useState<any>(null)
  const [hist, setHist] = useState<any>(null)
  const [research, setResearch] = useState<any>(null)
  useEffect(() => {
    let alive = true
    api.convergence(row.topic_key).then((x) => alive && setConv(x)).catch(() => {})
    api.xsignal(row.topic_display).then((x) => alive && setXsig(x?.available ? x : null)).catch(() => {})
    api.scoreHistory(row.topic_key).then((x) => alive && setHist(x)).catch(() => {})
    api.researchHistory(row.topic_key).then((x) => alive && setResearch(x)).catch(() => {})
    return () => { alive = false }
  }, [row.topic_key])

  const v = d?.velocity_scores || {}
  const r = d?.rich || {}   // rich parity row (mobile /scores shape)
  // Round to whole numbers so the gauge shows a clean "94" like the mobile app —
  // the detail endpoint returns the raw float (e.g. 69.35), which renders cramped
  // ("69.35") inside the ring and reads as pixelated next to the app's "27".
  const det = Math.round(v.detection ?? row.det), conf = Math.round(v.confidence ?? row.conf), gap = det - conf
  const [gs, tight, gt] = gapInterp(gap)
  const groups: BGroup[] = d?.components ? deriveGroups(d.components) : []
  const diverge = d?.components ? deriveDivergence(d.components, gap) : null
  const platforms: string[] = Array.isArray(r.platforms_active) ? r.platforms_active
    : (Array.isArray(d?.components?.M_platform_diversity?.platforms) ? d.components.M_platform_diversity.platforms : [])
  const why = r.why_this_matters || d?.why_this_matters || ''
  const watch = r.what_to_watch || d?.what_to_watch || ''
  const scol = stageColor(row.stage)

  // mobile field reads (rich parity payload)
  const matClass = r.calibration?.maturity_class ?? r.maturity_class
  const matBadge = r.calibration?.maturity_badge ?? matClass
  const matReason = r.calibration?.maturity_reason ?? r.maturity_reason
  const N = Math.round(r.nowtrendin_score ?? row.n ?? 0)
  const [act, setAct] = useState('')
  const onWatch = async () => setAct(await addToWatchlist(row.topic_key, row.topic_display || row.topic_key, 'topic'))
  const onAlert = () => setAct('Alerts are arriving soon — noted your interest in this topic.')
  const onExport = () => exportEntityCsv(`${row.topic_key}_nowtrendin.csv`, [
    ['Topic', row.topic_display], ['Detection', det], ['Confidence', conf], ['Gap', gap],
    ['N (Now Trending)', N], ['Stage', row.stage], ['Category', row.category || ''],
    ['Mentions', row.total_mentions ?? ''], ['Updated (min ago)', row.ageMin],
  ])
  const ntgD = r.nowtrending_gradient_detection, ntgC = r.nowtrending_gradient_confidence
  const dm = Math.round(r.dark_matter_score ?? d?.components?.D_dark_matter?.score ?? 0)
  const ftPct = r.first_timer_ratio != null ? Math.round(r.first_timer_ratio * 100) : null
  const asym = r.engagement_asymmetry != null ? Boolean(Number(r.engagement_asymmetry)) : null
  const variations: any[] = Array.isArray(r.variations) ? r.variations : []
  const scoreExpl = r.score_explanation
  const tcol = (n?: string) => (({ green: MC.confidence, blue: MC.detection, gold: MC.gold, gray: MC.slate, grey: MC.slate } as any)[(n || '').toLowerCase()] || MC.textSec)
  const gbi = gapBandIndex(gap)

  return (
    <aside className="rail">
      <div className="detail-head">
        <div className="detail-top">
          <div>
            <div className="detail-name">{row.topic_display}</div>
            <div className="detail-cat">{row.category || '—'} · <span style={{ color: scol, fontWeight: 700 }}>{row.stage}</span></div>
          </div>
          <div className="x" onClick={onClose}>✕</div>
        </div>
        <div className="detail-asof">
          {r.total_mentions ?? row.total_mentions ?? 0} signals · {platforms[0] || 'multi-platform'} · updated {ageLabel(row.ageMin)} ago
        </div>
      </div>

      {/* Topic maturity — live calibration lifecycle (mobile parity) */}
      {!!matClass && (
        <div className="m-card" style={{ borderColor: maturityColor(matClass) + '55' }}>
          <div className="m-row">
            <span className="m-badge" style={{ background: maturityColor(matClass) + '1A', color: maturityColor(matClass) }}>{matBadge || matClass}</span>
            <span className="m-kicker">Topic maturity</span>
          </div>
          <div className="m-reason">{matReason || ''}</div>
          <div className="m-foot">Lifecycle stage from the calibration engine · re-evaluated each scoring cycle</div>
        </div>
      )}

      {/* AI tier badge */}
      {!!r.ai_tier_label && (
        <div style={{ margin: '0 16px 4px' }}>
          <span className="m-badge" style={{ background: tcol(r.ai_tier_colour) + '1A', color: tcol(r.ai_tier_colour) }}>
            {r.ai_tier_label}{r.ai_velocity_signal ? ` · ${r.ai_velocity_signal}` : ''}
          </span>
        </div>
      )}

      {/* Dual Gradient Score — mobile colors (Detection blue / Confidence green) */}
      <div className="gauges">
        <div className="gauge det">{ring(det, MC.detection)}<div className="gv" style={{ marginTop: -50, color: MC.detection }}>{det}</div><div className="gl" style={{ marginTop: 28 }}>Detection</div><div className="gf">speed · ~22% FP</div></div>
        <div className="gauge conf">{ring(conf, MC.confidence)}<div className="gv" style={{ marginTop: -50, color: MC.confidence }}>{conf}</div><div className="gl" style={{ marginTop: 28 }}>Confidence</div><div className="gf">precision · &lt;9% FP</div></div>
      </div>

      {/* AI Context */}
      <div className="sect">
        <h4>AI Context</h4>
        {ex?.short ? (
          <div className="ai-ctx">
            <div className="ai-preview">{ex.short}</div>
            {ex.full && ex.full.trim() !== ex.short.trim() && (
              showFull ? <div className="ai-full">{ex.full}</div>
                : <button className="ai-more" onClick={() => setShowFull(true)}>Read full definition ↓</button>
            )}
          </div>
        ) : (
          <div className="narr muted">{exLoading ? 'Generating a source-aware definition…' : 'No AI definition yet — it generates on first view and is cached.'}</div>
        )}
      </div>

      {/* Now TrendIn (N) + Now Trending Gradient (demand-inclusive) + Convergence */}
      <div className="sect">
        <div className="n-card">
          <div className="n-head">
            <span className="n-flame">🔥</span>
            <span className="n-brand"><b style={{ color: MC.orange }}>Now</b><b style={{ color: MC.maroon }}>TrendIn</b> · N component</span>
            <span className="n-val">{N}</span>
          </div>
          <div className="n-desc">The on-platform demand signal — how often Now TrendIn users have asked the engine about this topic. Real institutional curiosity no public source can see.</div>
          {N > 0 && ntgD != null && ntgC != null ? (
            <div className="ntg">
              <div className="ntg-head"><span style={{ color: MC.orange, fontWeight: 800, fontSize: 9, letterSpacing: '.1em' }}>NOW TRENDING GRADIENT SCORE</span><span className="ntg-tag">SEPARATE · DEMAND-INCLUSIVE</span></div>
              <div className="ntg-sub">A what-if read — where the score lands if on-platform demand (N) is folded in. The headline Detection/Confidence stay N-free (external world only).</div>
              <div className="ntg-pair">
                <div className="ntg-cell" style={{ borderColor: MC.detection + '33', background: MC.detection + '0A' }}><div className="ntg-l">DETECTION + N</div><div className="ntg-n" style={{ color: MC.detection }}>{Math.round(ntgD)}</div></div>
                <div className="ntg-cell" style={{ borderColor: MC.confidence + '33', background: MC.confidence + '0A' }}><div className="ntg-l">CONFIDENCE + N</div><div className="ntg-n" style={{ color: MC.confidence }}>{Math.round(ntgC)}</div></div>
              </div>
              {r.nowtrending_gradient_demand_driven && <div className="ntg-warn">⚠ Substantially demand-driven — external confirmation is limited; N's weight is reduced so demand alone can't lift the score.</div>}
            </div>
          ) : (
            <div className="n-empty">No on-platform demand registered yet — N rises as users query this topic.</div>
          )}
          {conv?.status === 'ok' && (
            <div className="conv" style={{ borderColor: (conv.convergence === 'CONFIRMED' ? MC.confidence : conv.convergence === 'CONFLICTING' ? MC.red : MC.gold) + '55' }}>
              <b style={{ color: conv.convergence === 'CONFIRMED' ? MC.confidence : conv.convergence === 'CONFLICTING' ? MC.red : MC.gold }}>Signal Convergence: {conv.direction} · {conv.convergence}</b>
              {conv.vsGradient?.text && <div className="conv-t">{conv.vsGradient.text}</div>}
              {conv.vsNiche?.text && <div className="conv-t">{conv.vsNiche.text}</div>}
            </div>
          )}
        </div>
      </div>

      {/* Detection–Confidence Gap */}
      <div className="sect">
        <h4>Detection–Confidence Gap</h4>
        <div className={'gapband' + (tight ? ' tight' : '')}>
          <div className="gbs">{gs}</div>
          <div className="gbv">{gap > 0 ? '+' : ''}{gap} pts</div>
          <div className="gbt">{gt}</div>
        </div>
      </div>

      {/* Dual Score Analysis — gap interpretation bands + who uses which score */}
      <div className="sect">
        <h4>Dual Score Analysis</h4>
        <div className="narr" style={{ marginBottom: 8 }}>The same measurements run once. Two threshold rule-sets produce two scores; the gap tells you how early this signal is.</div>
        <div className="gapbands">
          {GAP_BANDS.map((b, i) => (
            <div className="gb-row" key={b.range} style={{ opacity: i === gbi ? 1 : 0.45 }}>
              <span className="gb-bar" style={{ background: b.color }} />
              <span className="gb-range">{b.range}</span>
              <span className="gb-label">{b.label}</span>
            </div>
          ))}
        </div>
        <div className="who">
          <div className="who-cell" style={{ borderColor: SCORE_ROLES.detection.color + '55', background: SCORE_ROLES.detection.color + '0D' }}>
            <div style={{ color: SCORE_ROLES.detection.color, fontWeight: 700, fontSize: 12 }}>Detection {det} · {SCORE_ROLES.detection.tag}</div>
            <div className="who-t">{SCORE_ROLES.detection.who}</div>
          </div>
          <div className="who-cell" style={{ borderColor: SCORE_ROLES.confidence.color + '55', background: SCORE_ROLES.confidence.color + '0D' }}>
            <div style={{ color: SCORE_ROLES.confidence.color, fontWeight: 700, fontSize: 12 }}>Confidence {conf} · {SCORE_ROLES.confidence.tag}</div>
            <div className="who-t">{SCORE_ROLES.confidence.who}</div>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
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
                  <span className="comp-bar"><i style={{ width: `${Math.min(100, it.value)}%`, background: grp.title === 'Community Demand' ? MC.orange : MC.detection }} /></span>
                  <span className="cv">{it.value}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Why the Scores Diverge */}
      {diverge && diverge.rows.length > 0 && (
        <div className="sect">
          <h4>Why the Scores Diverge</h4>
          <div className="narr" style={{ marginBottom: 8 }}>{diverge.summary}</div>
          <div className="div-grid">
            {diverge.rows.map((dr) => (
              <div className="div-cell" key={dr.label}>
                <div className="div-label">{dr.label}</div>
                <div className="div-val" style={{ color: dr.favors === 'DET' ? MC.detection : MC.confidence }}>
                  <span className="div-dot" style={{ background: dr.favors === 'DET' ? MC.detection : MC.confidence }} />{dr.value}
                </div>
                <div className="div-note">{dr.note}</div>
              </div>
            ))}
          </div>
          <div className="div-legend"><span style={{ color: MC.detection }}>● Blue</span> lifts Detection · <span style={{ color: MC.confidence }}>● Green</span> lifts Confidence</div>
        </div>
      )}

      {/* Dark Matter signatures */}
      {dm > 0 && (
        <div className="sect">
          <h4>Dark Matter</h4>
          <div className="narr" style={{ marginBottom: 8 }}>Inferred private-conversation activity — early movement that hasn't surfaced publicly yet.</div>
          <div className="comp-row"><span className="cl">Dark matter score</span><span className="comp-bar"><i style={{ width: `${Math.min(100, dm)}%`, background: MC.purple }} /></span><span className="cv">{dm}</span></div>
          {ftPct != null && <div className="comp-row"><span className="cl">First-timer ratio</span><span className="comp-bar"><i style={{ width: `${Math.min(100, ftPct)}%`, background: MC.detection }} /></span><span className="cv">{ftPct}%</span></div>}
          {asym != null && <div className="kv"><span>Engagement asymmetry</span><b style={{ color: asym ? MC.detection : MC.muted }}>{asym ? 'Detected' : 'Normal'}</b></div>}
        </div>
      )}

      {/* AI score explanation */}
      {!!scoreExpl && (
        <div className="sect"><h4>Why It Scores Here</h4><div className="narr">{scoreExpl}</div></div>
      )}

      {/* Variation map */}
      {variations.length > 0 && (
        <div className="sect">
          <h4>Topic Variations</h4>
          {variations.slice(0, 8).map((vr: any, i: number) => (
            <div className="var-row" key={i} style={{ opacity: vr.is_queried ? 1 : 0.85 }}>
              <span className="var-name">{vr.display || vr.topic_key}{vr.is_queried ? ' ◆' : ''}</span>
              {vr.tier_label && <span className="var-tier" style={{ color: tcol(vr.tier_colour) }}>{vr.tier_label}</span>}
              <span className="var-sc">{Math.round(vr.typical_detection ?? 0)}/{Math.round(vr.typical_confidence ?? 0)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Source & Why */}
      {(platforms.length > 0 || why) && (
        <div className="sect">
          <h4>Source &amp; Why</h4>
          {platforms.length > 0 && <div className="src-row">{platforms.map((p) => <span className="src-chip" key={p}>{p}</span>)}</div>}
          {why && <div className="narr">{why}</div>}
          {watch && <div className="narr" style={{ marginTop: 8 }}>{watch}</div>}
        </div>
      )}

      {/* Research history (lazy) */}
      {research && (research.trajectory_label || research.summary_short) && (
        <div className="sect">
          <h4>Research History</h4>
          {research.trajectory_label && <div className="kv"><span>Trajectory</span><b>{research.trajectory_label}</b></div>}
          {research.years_discussed != null && <div className="kv"><span>Years discussed</span><b>{research.years_discussed}</b></div>}
          {research.summary_short && <div className="narr" style={{ marginTop: 6 }}>{research.summary_short}</div>}
        </div>
      )}

      {/* X dual-role signal (lazy) */}
      {xsig && (
        <div className="sect">
          <h4>X Signal</h4>
          <div className="kv"><span>Role · Stage</span><b>{xsig.x_role || xsig.diffusion?.role || '—'} · {xsig.x_stage || xsig.diffusion?.stage || '—'}</b></div>
          {xsig.diffusion?.interpretation && <div className="narr" style={{ marginTop: 6 }}>{xsig.diffusion.interpretation}</div>}
          {xsig.signal_integrity && <div className="kv"><span>Integrity</span><b>{xsig.signal_integrity.classification} ({Math.round(xsig.signal_integrity.score)})</b></div>}
        </div>
      )}

      {/* Signal Read */}
      <div className="sect">
        <h4>Signal Read</h4>
        <div className="narr">
          {loading ? 'Loading live score…'
            : gap >= 20 ? `${row.topic_display} shows a wide ${gap}-point gap — leading indicators run ahead of confirmation. Detected, not yet broadly confirmed.`
              : gap < 0 ? `${row.topic_display} reads with confidence above detection — the hard signal arrived after the early window; the topic is maturing.`
                : `${row.topic_display} has detection and confidence closely aligned (${gap > 0 ? '+' : ''}${gap}) — a high-conviction read at the ${row.stage} level.`}
        </div>
        <div className="disc">Signal analysis only — not financial, investment, or legal advice.</div>
      </div>

      {/* Scoring history (lazy) */}
      {Array.isArray(hist?.rows) && hist.rows.length > 1 && (() => {
        const pts = hist.rows.slice(0, 24).slice().reverse()   // oldest → newest
        const W = 300, H = 92, pad = 6
        const xs = (i: number) => pad + i * (W - 2 * pad) / (pts.length - 1)
        const ys = (v: number) => H - pad - (Math.max(0, Math.min(100, v)) / 100) * (H - 2 * pad)
        const ln = (k: string) => pts.map((h: any, i: number) => `${xs(i).toFixed(1)},${ys(Math.round(h[k] ?? 0)).toFixed(1)}`).join(' ')
        return (
          <div className="sect">
            <h4>Scoring History</h4>
            <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
              <line x1={0} y1={H - pad} x2={W} y2={H - pad} style={{ stroke: 'var(--line)' }} strokeWidth={1} />
              <polyline points={ln('detection')} style={{ stroke: MC.detection, fill: 'none' }} strokeWidth={2} />
              <polyline points={ln('confidence')} style={{ stroke: MC.confidence, fill: 'none' }} strokeWidth={2} />
            </svg>
            <div className="div-legend"><span style={{ color: MC.detection }}>● Detection</span> · <span style={{ color: MC.confidence }}>● Confidence</span> · oldest → newest</div>
          </div>
        )
      })()}

      {/* Methodology */}
      <div className="sect">
        <h4>How the Gradient Score Works</h4>
        <div className="narr">Two scores from one engine. <b style={{ color: MC.detection }}>Detection</b> weights early-edge components (niche concentration, dark matter, acceleration) — speed. <b style={{ color: MC.confidence }}>Confidence</b> weights cross-platform confirmation — precision. The gap between them is how early you are. The N (Now Trending) demand signal is shown separately and never feeds the Gradient (objectivity).</div>
      </div>

      <div className="detail-actions">
        <button className="btn" onClick={onWatch}><Star size={17} color="var(--early)" /> Add to Watchlist</button>
        <button className="btn" onClick={onAlert}><Bell size={17} color="var(--early)" /> Add to Alert</button>
        <button className="btn" onClick={onExport}><Download size={17} color="var(--early)" /> Export</button>
      </div>
      {act && <div className="detail-act-msg">{act}</div>}
    </aside>
  )
}

export function Screener({ onRail, query = '', preset }: { onRail: (node: React.ReactNode | null) => void; query?: string; preset?: { filter: string; n: number } | null }) {
  const [rows, setRows] = useState<Row[]>([])
  const [cats, setCats] = useState<{ key: string; label: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState('nowtrendin')   // mobile default = Now TrendIn
  // Default sort MUST match the default filter: "Now TrendIn" ranks by N (the
  // proprietary demand signal), "All Signals" by Detection. Defaulting to 'det'
  // while the Now TrendIn chip is highlighted showed All-Signals-sorted data under
  // the wrong active tab (selectSignal only synced the sort on a later click).
  const [sortKey, setSortKey] = useState<SortKey>('n')
  const [sortDir, setSortDir] = useState(-1)
  const [sel, setSel] = useState<string | null>(null)
  const [pulling, setPulling] = useState(false)
  const [pullMsg, setPullMsg] = useState<string | null>(null)
  // Inline topic filter — same UI as Market Signal's "Filter instruments…", for
  // cross-section consistency (combines with the top-bar global search).
  const [topicFilter, setTopicFilter] = useState('')

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

  // Saved-screen preset (Early Signals / Breakouts) → apply the matching signal
  // filter + its ranking. Nonce-keyed so re-clicking the same screen re-applies.
  useEffect(() => {
    if (!preset) return
    const f = SIGNAL_FILTERS.find((x) => x.k === preset.filter)
    if (f) { setFilter(f.k); if (f.sort) { setSortKey(f.sort); setSortDir(-1) } }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset?.n])

  const view = useMemo(() => {
    let r = rows.slice()
    const sig = SIGNAL_FILTERS.find((f) => f.k === filter)
    if (sig) { if (sig.test) r = r.filter(sig.test) }     // nowtrendin/all = no filter
    // category rows already filtered server-side (catParam) — no client re-filter
    const ql = query.trim().toLowerCase()
    if (ql) r = r.filter((x) => (x.topic_display || '').toLowerCase().includes(ql) || (x.topic_key || '').toLowerCase().includes(ql))
    const tl = topicFilter.trim().toLowerCase()
    if (tl) r = r.filter((x) => (x.topic_display || '').toLowerCase().includes(tl) || (x.topic_key || '').toLowerCase().includes(tl))
    r.sort((a, b) => {
      const va = a[sortKey] as any, vb = b[sortKey] as any
      if (typeof va === 'string') return String(va).localeCompare(String(vb)) * sortDir
      return ((va ?? -1) - (vb ?? -1)) * sortDir
    })
    return r
  }, [rows, filter, sortKey, sortDir, query, topicFilter])

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

  // Export the current (filtered + sorted) view to CSV — same UX as Market Signal.
  const csv = () => {
    const hdr = ['topic', 'topic_key', 'detection', 'confidence', 'gap', 'n', 'stage', 'category', 'mentions', 'updated_min']
    const lines = [hdr.join(',')].concat(view.map((r) =>
      [`"${(r.topic_display || '').replace(/"/g, '""')}"`, r.topic_key, r.det, r.conf, r.gap, r.n, r.stage, r.category || '', r.total_mentions ?? '', r.ageMin].join(',')))
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' }))
    a.download = 'nowtrendin_trends.csv'; a.click()
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
            <button className="btn primary" onClick={doPull} disabled={pulling} title="Enterprise — fresh attention pull, costs 1 token">
              {pulling ? '⟳ Pulling…' : '⚡ Pull Trends · 1 token'}
            </button>
            <button className="btn" onClick={csv}>↧ Export CSV</button>
          </div>
        </div>
        {/* Row 1 — TRENDS (signal) filters — EXACT mobile parity (CATEGORY_DEFS) */}
        <div className="chips tight">
          <span className="chip-label">Trends</span>
          {SIGNAL_FILTERS.map((f) => (
            <div key={f.k} className={'chip' + (filter === f.k ? ' active' : '')}
              onClick={() => selectSignal(f)}>{f.label}</div>
          ))}
          <input className="chip-search" placeholder="Filter topics…" value={topicFilter}
            onChange={(e) => setTopicFilter(e.target.value)} />
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
