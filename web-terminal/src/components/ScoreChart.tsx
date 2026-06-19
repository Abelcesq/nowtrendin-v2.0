import { useEffect, useRef, useState } from 'react'
import { MC } from '../lib/mobileTheme'

// A real, axed score chart for a topic's scoring history. X = time (each scoring
// run), Y = score 0–100. Plots Detection (blue) + Confidence (green) with a dot at
// every actual data point, gridlines + axis labels, and a hover tooltip that shows
// the exact values AND the factors driving the move (mentions, platforms, stage,
// and the Δ vs the previous run). Every point is a REAL scoring event — nothing
// is interpolated or invented.

export interface ChartPoint {
  t: string                       // ISO timestamp of the scoring run
  det: number; conf: number
  overall?: number; gap?: number
  mentions?: number; platforms?: number; stage?: string
  inertia?: number; dark_matter?: number
}

const DET = MC.detection, CONF = MC.confidence

function fmtTime(iso: string): string {
  const d = new Date(iso)
  if (isNaN(+d)) return ''
  const mo = d.toLocaleString('en-US', { month: 'short' })
  let h = d.getHours(); const ap = h >= 12 ? 'p' : 'a'; h = h % 12 || 12
  return `${mo} ${d.getDate()}, ${h}:${d.getMinutes().toString().padStart(2, '0')}${ap}`
}
function fmtAxis(iso: string): string {
  const d = new Date(iso)
  if (isNaN(+d)) return ''
  let h = d.getHours(); const ap = h >= 12 ? 'p' : 'a'; h = h % 12 || 12
  return `${d.getMonth() + 1}/${d.getDate()} ${h}${ap}`
}

export function ScoreChart({ points }: { points: ChartPoint[] }) {
  const pts = [...points].filter((p) => p.t).sort((a, b) => +new Date(a.t) - +new Date(b.t))
  const wrapRef = useRef<HTMLDivElement>(null)
  const [w, setW] = useState(680)
  const [hover, setHover] = useState<number | null>(null)

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setW(Math.max(280, el.clientWidth)))
    ro.observe(el); setW(Math.max(280, el.clientWidth))
    return () => ro.disconnect()
  }, [])

  if (pts.length === 0) return <div className="sc-empty">No scoring history yet — points appear as the engine scores this topic.</div>
  if (pts.length === 1) {
    const p = pts[0]
    return <div className="sc-empty">Only one scoring run so far ({fmtTime(p.t)}: Det {p.det} · Conf {p.conf}). A trajectory appears after the next cycle.</div>
  }

  const W = w, H = 280
  const mL = 30, mR = 12, mT = 12, mB = 30
  const plotW = W - mL - mR, plotH = H - mT - mB
  const n = pts.length
  const x = (i: number) => mL + (i * plotW) / (n - 1)
  const y = (v: number) => mT + plotH - (Math.max(0, Math.min(100, v)) / 100) * plotH
  const path = (k: 'det' | 'conf') => pts.map((p, i) => `${x(i).toFixed(1)},${y(p[k]).toFixed(1)}`).join(' ')

  const yticks = [0, 25, 50, 75, 100]
  const xtickIdx = n <= 6 ? pts.map((_, i) => i)
    : [0, Math.round((n - 1) * 0.25), Math.round((n - 1) * 0.5), Math.round((n - 1) * 0.75), n - 1]

  const onMove = (e: React.MouseEvent) => {
    const rect = wrapRef.current?.getBoundingClientRect()
    if (!rect) return
    const px = e.clientX - rect.left
    let best = 0, bd = Infinity
    for (let i = 0; i < n; i++) { const d = Math.abs(x(i) - px); if (d < bd) { bd = d; best = i } }
    setHover(best)
  }

  const hp = hover != null ? pts[hover] : null
  const prev = hover != null && hover > 0 ? pts[hover - 1] : null
  const delta = (cur: number, p?: number) => (p == null ? '' : ` (${cur - p >= 0 ? '+' : ''}${cur - p})`)
  // tooltip left clamped within the wrap
  const tipLeft = hp ? Math.min(Math.max(x(hover!), 70), W - 70) : 0

  return (
    <div className="sc-wrap" ref={wrapRef} onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
      <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
        {/* Y grid + labels */}
        {yticks.map((t) => (
          <g key={t}>
            <line x1={mL} y1={y(t)} x2={W - mR} y2={y(t)} stroke="var(--line-2)" strokeWidth={1} strokeDasharray={t === 0 ? '0' : '3 3'} />
            <text x={mL - 6} y={y(t) + 3} textAnchor="end" fontSize="9" fill="var(--text-3)">{t}</text>
          </g>
        ))}
        {/* X labels + ticks */}
        {xtickIdx.map((i) => (
          <text key={i} x={x(i)} y={H - 10} textAnchor="middle" fontSize="9" fill="var(--text-3)">{fmtAxis(pts[i].t)}</text>
        ))}
        {/* lines */}
        <polyline points={path('conf')} fill="none" stroke={CONF} strokeWidth={2.25} />
        <polyline points={path('det')} fill="none" stroke={DET} strokeWidth={2.25} />
        {/* data-point dots */}
        {pts.map((p, i) => (
          <g key={i}>
            <circle cx={x(i)} cy={y(p.conf)} r={hover === i ? 4 : 2.6} fill={CONF} />
            <circle cx={x(i)} cy={y(p.det)} r={hover === i ? 4 : 2.6} fill={DET} />
          </g>
        ))}
        {/* hover guide */}
        {hover != null && <line x1={x(hover)} y1={mT} x2={x(hover)} y2={mT + plotH} stroke="var(--text-3)" strokeWidth={1} strokeDasharray="3 3" />}
      </svg>

      {hp && (
        <div className="sc-tip" style={{ left: tipLeft }}>
          <div className="sc-tip-t">{fmtTime(hp.t)}{hp.stage ? ` · ${hp.stage}` : ''}</div>
          <div className="sc-tip-r"><span style={{ color: DET }}>● Detection</span><b>{hp.det}<i>{delta(hp.det, prev?.det)}</i></b></div>
          <div className="sc-tip-r"><span style={{ color: CONF }}>● Confidence</span><b>{hp.conf}<i>{delta(hp.conf, prev?.conf)}</i></b></div>
          {hp.overall != null && <div className="sc-tip-r"><span>Overall</span><b>{hp.overall}</b></div>}
          {hp.gap != null && <div className="sc-tip-r"><span>Det–Conf gap</span><b>{hp.gap}</b></div>}
          {(hp.mentions != null || hp.platforms != null) && (
            <div className="sc-tip-fac">
              {hp.mentions != null && <span>{hp.mentions.toLocaleString()} mentions{delta(hp.mentions, prev?.mentions)}</span>}
              {hp.platforms != null && <span>{hp.platforms} platform{hp.platforms === 1 ? '' : 's'}</span>}
              {hp.dark_matter ? <span>dark-matter {hp.dark_matter}</span> : null}
            </div>
          )}
        </div>
      )}

      <div className="sc-legend">
        <span style={{ color: DET }}>● Detection</span>
        <span style={{ color: CONF }}>● Confidence</span>
        <span className="sc-legend-hint">{n} scoring runs · hover a point for the driving factors</span>
      </div>
    </div>
  )
}
