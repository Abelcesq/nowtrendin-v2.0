import { useEffect, useMemo, useState } from 'react'
import { Star, Bell, Download, X } from 'lucide-react'
import { api, type RiskRow } from '../lib/api'
import { pullMarket } from '../lib/auth'
import { addToWatchlist, exportEntityCsv } from '../lib/actions'
import { MC, marketTierColor, FEEDS_COLOR, MARKET_TIERS, RISK_PIPELINE, BASELINE_META } from '../lib/mobileTheme'
import { Disclaimer } from '../components/Disclaimer'

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
  raw: RiskRow   // full payload for the comprehensive detail rail (mobile parity)
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
    comps, raw: r,
  }
}

function bar(label: string, val: number | null, color: string) {
  return (
    <div className="comp-row" key={label}>
      <span className="cl">{label}</span>
      <span className="comp-bar"><i style={{ width: `${Math.max(0, Math.min(100, val ?? 0))}%`, background: color }} /></span>
      <span className="cv">{val == null ? 'n/a' : Math.round(val)}</span>
    </div>
  )
}

function MarketRail({ row, onClose }: { row: MRow; onClose: () => void }) {
  const raw = row.raw
  const [act, setAct] = useState('')
  const onWatch = async () => setAct(await addToWatchlist(row.key, row.name, 'market'))
  const onAlert = () => setAct('Alerts are arriving soon — noted your interest in this instrument.')
  const onExport = () => exportEntityCsv(`${row.key}_market.csv`, [
    ['Instrument', row.name], ['Detection', row.det], ['Confidence', row.conf], ['Gap', row.gap],
    ['Tier', row.tier], ['Leverage health', row.lev ?? ''], ['Signals', row.sigs], ['Updated (min ago)', row.ageMin],
  ])
  const tcol = marketTierColor(row.tier)
  const mg = raw.market_gradient || {}
  const sust = raw.sustainability
  const av = raw.alpha_vantage
  const cc = raw.creator_coverage
  const bc = raw.broadcast_coverage
  const si = raw.short_interest
  const macro = raw.macro_leverage
  const inst = raw.institutional_holdings
  const sustTone = (v: number) => v >= 75 ? MC.confidence : v >= 50 ? MC.detection : v >= 30 ? MC.gold : MC.red
  const sources = String(raw.source_provenance || '').split('·').map((s) => s.trim()).filter(Boolean)
  const diffusion: any = raw.diffusion || {}
  const stageCount = (k: string) => {
    const x = diffusion[k]; return typeof x === 'number' ? x : (x?.count ?? null)
  }
  const hasPipeline = RISK_PIPELINE.some((s) => stageCount(s.key) != null)
  const maxStage = Math.max(1, ...RISK_PIPELINE.map((s) => stageCount(s.key) ?? 0))

  return (
    <aside className="rail">
      <div className="detail-head">
        <div className="detail-top">
          <div>
            <div className="detail-name">{row.name}</div>
            <div className="detail-cat">Market Signal · <span style={{ color: tcol, fontWeight: 700 }}>{row.tier}</span>{row.calibrating && <span className="cal-chip">calibrating</span>}</div>
          </div>
          <div className="x" onClick={onClose}>✕</div>
        </div>
        <div className="detail-asof">
          {row.cls ? `vs baseline: ${row.cls}` : ''}{row.pct != null ? ` · ${row.pct > 0 ? '+' : ''}${Math.round(row.pct)}% vs baseline` : ''} · updated {ageLabel(row.ageMin)} ago
        </div>
      </div>

      {/* Legal disclaimer — top, above the score */}
      <Disclaimer style={{ marginBottom: 10 }} />
      {/* Market Gradient — dual score, mobile colors */}
      <div className="gauges" style={mg.data_coverage === 'insufficient' ? { opacity: 0.55 } : undefined}>
        <div className="gauge det">{ring(row.det, MC.detection)}<div className="gv" style={{ marginTop: -50, color: MC.detection }}>{row.det}</div><div className="gl" style={{ marginTop: 28 }}>Detection</div><div className="gf">analysts + positioning</div></div>
        <div className="gauge conf">{ring(row.conf, MC.confidence)}<div className="gv" style={{ marginTop: -50, color: MC.confidence }}>{row.conf}</div><div className="gl" style={{ marginTop: 28 }}>Confidence</div><div className="gf">fundamentals + price</div></div>
      </div>
      <div className="sect">
        {mg.data_coverage === 'insufficient' && (
          <div className="narr" style={{ marginBottom: 8, background: '#FFF4E5', border: '1px solid #F0C27B', color: '#8A5A00', borderRadius: 8, padding: '8px 10px' }}>
            ⚠ <b>Insufficient positioning data.</b> Smart-money / short-interest sources (FINRA short interest · 13F holdings) aren’t populated for this instrument yet{mg.absent_inputs != null ? ` (${mg.absent_inputs}/${mg.total_inputs} inputs absent)` : ''}, so it sits near baseline by default — <i>not</i> a confirmed quiet market.
          </div>
        )}
        <div className="mkt-gapband" style={{ borderColor: tcol + '55', background: tcol + '10' }}>
          <b style={{ color: tcol, fontSize: 12 }}>{mg.calibrating ? 'CALIBRATING' : (mg.gap_state || `${Math.abs(row.gap)}-pt gap`)}{!mg.calibrating && ` · ${Math.abs(row.gap)}-pt gap`}</b>
          {row.interp && <div className="narr" style={{ marginTop: 6, background: 'transparent', padding: 0 }}>{row.interp}</div>}
          {row.interp && <div className="disc" style={{ marginTop: 8 }}>AI-generated overview · qualitative context are computer generated. All information contained herein may not be accurate including any figures are approximate and the measured score and velocity and should not be construed as financial, investment, or legal advice.</div>}
        </div>
        <div className="disc"><b>What Market Signal measures:</b> is this stock’s <i>positioning</i> unusual versus its <b>own</b> baseline — a different question from a Trend/Attention score. Detection = analysts + smart-money positioning (leading); Confidence = fundamentals + price (hard data). Measurement only — not financial advice.</div>
      </div>

      {/* Market factors — colored by which score they feed */}
      {row.comps.length > 0 && (
        <div className="sect">
          <h4>Market Factors</h4>
          {Object.entries(mg.components || {}).map(([label, c]: [string, any]) => {
            const col = FEEDS_COLOR[c?.feeds] ?? MC.muted
            return (
              <div className="comp-row" key={label} title={label}>
                <span className="cl" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span style={{ width: 6, height: 6, borderRadius: 3, background: col, flex: '0 0 auto' }} />
                  {label.replace(/\s*\(.*\)$/, '')}{c?.baseline_relative ? ' ✓' : ''}
                </span>
                <span className="comp-bar"><i style={{ width: `${Math.max(4, Math.min(100, c?.score ?? 0))}%`, background: col }} /></span>
                <span className="cv">{Math.round(c?.score ?? 0)}</span>
              </div>
            )
          })}
          <div className="div-legend"><span style={{ color: MC.detection }}>●</span> leading · <span style={{ color: MC.confidence }}>●</span> confirming · <span style={{ color: MC.purple }}>●</span> both · ✓ = scored vs own history</div>
        </div>
      )}

      {/* Tier legend */}
      <div className="sect">
        <h4>What the Tiers Mean</h4>
        <div className="tier-legend">
          {MARKET_TIERS.map((t) => {
            const c = marketTierColor(t.key)
            return (
              <div key={t.key} className="tier-cell" style={{ borderColor: c + '55', background: c + '12' }}>
                <div style={{ color: c, fontWeight: 800, fontSize: 11 }}>{t.key}</div>
                <div style={{ fontSize: 9.5, color: 'var(--text-3)' }}>{t.range}</div>
                <div style={{ color: c, fontSize: 10, fontWeight: 600 }}>{t.desc}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Financial Sustainability */}
      {sust && (() => {
        const sc = sustTone(sust.score)
        const hasAdj = sust.sector_adjusted_score != null && sust.sector_adjusted_score !== sust.score
        const adj = sust.sector_adjusted_score ?? sust.score
        const m = sust.metrics || {}
        return (
          <div className="sect">
            <h4>Financial Sustainability</h4>
            <div className="sust-pair">
              <div className="sust-cell" style={{ background: sc + '12' }}><div className="sust-k">SCORE</div><div className="sust-n" style={{ color: sc }}>{sust.score}<span className="sust-u">/100</span></div><div style={{ color: sc, fontSize: 10.5, fontWeight: 700 }}>{sust.label}</div><div className="sust-vs">vs all companies</div></div>
              <div className="sust-cell" style={{ background: sustTone(adj) + '12' }}><div className="sust-k">SECTOR-ADJ</div><div className="sust-n" style={{ color: sustTone(adj) }}>{adj}<span className="sust-u">/100</span></div><div style={{ color: sustTone(adj), fontSize: 10.5, fontWeight: 700 }}>{sust.sector_adjusted_label || sust.label}</div><div className="sust-vs">vs {sust.sector || 'sector'}</div></div>
            </div>
            {sust.sector_explanation && <div className="narr" style={{ margin: '8px 0' }}>{sust.sector_explanation}</div>}
            {bar('Profitability (margin · ROE)', sust.profitability, sc)}
            {bar('Cash & liquidity', sust.liquidity, sc)}
            {bar(hasAdj ? 'Leverage health (raw)' : 'Leverage health', sust.leverage_health, sc)}
            {hasAdj && bar(`Leverage health (vs ${sust.sector || 'sector'})`, sust.leverage_health_sector, sc)}
            <div className="metrics">
              {m.net_profit_margin_pct != null && <span>Net margin {m.net_profit_margin_pct}%</span>}
              {m.roe_pct != null && <span>ROE {m.roe_pct}%</span>}
              {m.current_ratio != null && <span>Current ratio {m.current_ratio}</span>}
              {m.debt_to_equity != null && <span>Debt/equity {m.debt_to_equity}</span>}
            </div>
            <div className="disc">From {sust.ticker}'s reported financials. Descriptive only — not a recommendation.</div>
          </div>
        )
      })()}

      {/* Retail & media coverage */}
      {(av || cc || bc) && (
        <div className="sect">
          <h4>Retail &amp; Media Coverage</h4>
          {av && (
            <div className="cov-block">
              <div className="cov-h">{av.article_count} news article{av.article_count === 1 ? '' : 's'}{av.sentiment_label ? ` · ${av.sentiment_label}` : ''}</div>
              {(av.recent || []).slice(0, 3).map((a: any, i: number) => <div className="cov-i" key={i}>▸ {a.title}<span className="cov-m"> {a.source}</span></div>)}
            </div>
          )}
          {(cc?.creators || []).map((cr: any) => (
            <div className="cov-block" key={cr.handle}>
              <div className="cov-h" style={{ color: MC.red }}>{cr.name}: {cr.covered ? `${cr.count} recent video${cr.count === 1 ? '' : 's'}` : 'not in recent uploads'}</div>
              {cr.covered && (cr.recent || []).slice(0, 2).map((vd: any, i: number) => <div className="cov-i" key={i}>▸ {vd.title}</div>)}
            </div>
          ))}
          {bc && bc.channels?.length > 0 && (
            <div className="cov-block">
              <div className="cov-h">Broadcast media ({bc.channels.length}/{bc.total_channels} channels)</div>
              {bc.channels.slice(0, 4).map((ch: any) => <div className="cov-i" key={ch.handle}>▸ {ch.name}{ch.region ? ` · ${ch.region}` : ''}: {ch.count} video{ch.count === 1 ? '' : 's'}</div>)}
            </div>
          )}
        </div>
      )}

      {/* Leverage & funding */}
      {(si || macro || inst) && (
        <div className="sect">
          <h4>Leverage &amp; Funding</h4>
          {si && (
            <div className="cov-block">
              <div className="cov-h">{si.label}</div>
              <div className="metrics">
                {si.short_position != null && <span>Short {(si.short_position / 1e6).toFixed(1)}M sh</span>}
                {si.change_pct != null && <span>{si.change_pct >= 0 ? '+' : ''}{si.change_pct}% vs prior</span>}
                {si.days_to_cover != null && <span>{si.days_to_cover} days to cover</span>}
              </div>
              <div className="disc">FINRA short interest{si.settlement_date ? ` · ${si.settlement_date}` : ''}</div>
            </div>
          )}
          {macro && (
            <div className="cov-block">
              <div className="kv"><span>Market funding</span><b>{macro.leverage?.label}{macro.funding_stress?.label ? ` · ${macro.funding_stress.label}` : ''}</b></div>
              <div className="disc">OFR Short-Term Funding Monitor (repo){macro.as_of ? ` · ${macro.as_of}` : ''}</div>
            </div>
          )}
          {inst && (
            <div className="cov-block">
              <div className="cov-h">{inst.label || 'Institutional positioning'}</div>
              <div className="metrics">
                {inst.holders_count != null && <span>{inst.holders_count} holders</span>}
                {inst.shares_change_pct != null && <span>{inst.shares_change_pct >= 0 ? '+' : ''}{inst.shares_change_pct}% avg change</span>}
              </div>
              {inst.top_holders?.length > 0 && <div className="disc">Top: {inst.top_holders.slice(0, 4).map((h: any) => h.name).join(', ')}</div>}
              <div className="disc">WhaleWisdom 13F institutional holdings</div>
            </div>
          )}
        </div>
      )}

      {/* Market tenure */}
      {!!raw.maturity && (
        <div className="sect"><h4>Market Tenure</h4>
          <div className="kv"><span>Maturity</span><b>{raw.maturity}</b></div>
          {raw.maturity_note && <div className="narr" style={{ marginTop: 6 }}>{raw.maturity_note}</div>}
        </div>
      )}

      {/* Vs own baseline */}
      {!!raw.baseline_status && (() => {
        const bm = BASELINE_META[raw.baseline_status!] ?? BASELINE_META.INSUFFICIENT_HISTORY
        const insuff = raw.baseline_status === 'INSUFFICIENT_HISTORY'
        const abn = raw.abnormality ?? 0
        return (
          <div className="sect"><h4>Vs. Its Own Baseline</h4>
            <div className="mkt-gapband" style={{ borderColor: bm.color + '55' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <b style={{ color: bm.color, fontSize: 12 }}>{bm.label}</b>
                {!insuff && <b style={{ color: bm.color, fontSize: 15 }}>{abn > 0 ? '+' : ''}{abn}%</b>}
              </div>
              {!insuff && <div className="disc" style={{ marginTop: 4 }}>Now {row.sigs} signals vs a {raw.baseline_signals}-signal baseline over {raw.baseline_cycles} prior cycles.</div>}
              {raw.baseline_note && <div className="narr" style={{ marginTop: 6, background: 'transparent', padding: 0 }}>{raw.baseline_note}</div>}
            </div>
          </div>
        )
      })()}

      {/* Diffusion pipeline */}
      {hasPipeline && (
        <div className="sect"><h4>Diffusion Pipeline</h4>
          {RISK_PIPELINE.map((s) => {
            const cnt = stageCount(s.key) ?? 0
            return (
              <div className="comp-row" key={s.key} title={s.desc}>
                <span className="cl">{s.label}{s.detect ? ' ●' : ''}</span>
                <span className="comp-bar"><i style={{ width: `${Math.round((cnt / maxStage) * 100)}%`, background: cnt > 0 ? tcol : 'var(--line)' }} /></span>
                <span className="cv">{cnt}</span>
              </div>
            )
          })}
        </div>
      )}

      {/* Score components */}
      {raw.components && Object.keys(raw.components).length > 0 && (
        <div className="sect"><h4>Score Components</h4>
          {Object.entries(raw.components).map(([k, val]) => bar(k.replace(/_/g, ' '), Number(val), tcol))}
        </div>
      )}

      {/* Sources */}
      {sources.length > 0 && (
        <div className="sect"><h4>Sources</h4>
          <div className="src-row">{sources.map((s) => <span className="src-chip" key={s}>{s}</span>)}</div>
          <div className="disc">Public filings, government data, or official APIs. Results proprietary to Now TrendIn.</div>
        </div>
      )}

      <div className="disc" style={{ padding: '0 16px 14px', textAlign: 'center' }}>Positioning analysis for informational purposes only — not financial, investment, or legal advice, and not a risk rating.</div>

      {/* Legal disclaimer — bottom, above the actions */}
      <Disclaimer style={{ margin: '0 16px 10px' }} />
      <div className="detail-actions">
        <button className="btn" onClick={onWatch}><Star size={17} color="var(--early)" /> Add to Watchlist</button>
        <button className="btn" onClick={onAlert}><Bell size={17} color="var(--early)" /> Add to Alert</button>
        <button className="btn" onClick={onExport}><Download size={17} color="var(--early)" /> Export</button>
      </div>
      {act && <div className="detail-act-msg">{act}</div>}
    </aside>
  )
}

export function MarketSignal({ onRail, preset, focus }: { onRail: (node: React.ReactNode | null) => void; preset?: { filter: string; n: number } | null; focus?: { key: string; display: string; n: number } | null }) {
  const [rows, setRows] = useState<MRow[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')
  const [q, setQ] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('det')
  const [sortDir, setSortDir] = useState(-1)
  const [sel, setSel] = useState<string | null>(null)
  const [pulling, setPulling] = useState(false)
  const [pullMsg, setPullMsg] = useState<string | null>(null)

  const doPull = async () => {
    setPulling(true); setPullMsg(null)
    try {
      const r = await pullMarket()
      setPullMsg(r?.message || 'Market pull queued — fresh positioning arrives next cycle.')
    } catch (e: any) {
      setPullMsg(e?.data?.detail || e?.message || 'Pull failed.')
    } finally { setPulling(false) }
  }

  // Progressive load — 100 instruments at a time so the table paints on the first
  // page instead of blocking on the whole rich payload (engine serves O(1) slices
  // from its prewarmed superset).
  useEffect(() => {
    let alive = true; setLoading(true); setErr(null)
    api.riskAll((batch) => { if (alive) { setRows(batch.map(toRow)); setLoading(false) } })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  // Favorite (market) click → apply the saved tier/leverage filter. Nonce-keyed.
  useEffect(() => {
    if (!preset) return
    setQ('')             // clear any leftover instrument filter from a prior "track-topic" focus
    setSel(null); onRail(null)
    if (FILTERS.some((f) => f.k === preset.filter)) setFilter(preset.filter)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset?.n])

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

  // Focus = filter the list to a SPECIFIC instrument AND open its detail rail
  // (from a favorite / watchlist / alert), so the user lands on the filtered word.
  // The market detail needs the full payload, so the rail opens once the row is in
  // the loaded set.
  useEffect(() => {
    if (!focus) return
    setFilter('all')        // clear any tier filter that could hide it
    setQ(focus.display)     // narrow the list to the focused instrument
    const row = rows.find((r) => r.key === focus.key)
    if (row) { setSel(focus.key); onRail(<MarketRail row={row} onClose={() => { setSel(null); onRail(null) }} />) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus?.n, rows])

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
          <div className="main-sub"><b>{view.length}</b> instruments · finance-native dual score · baseline-relative{pullMsg ? ` · ${pullMsg}` : ''}</div>
          <div className="main-actions">
            <button className="btn primary" onClick={doPull} disabled={pulling} title="Enterprise — fresh FINRA/OFR/WhaleWisdom/creator/news pull, costs 1 token">
              {pulling ? '⟳ Pulling…' : '⚡ Pull Market · 1 token'}
            </button>
            <button className="btn" onClick={csv}>↧ Export CSV</button>
          </div>
        </div>
        <div className="chips">
          <span className="chip-label">Tier</span>
          {FILTERS.map((f) => (
            <div key={f.k} className={'chip' + (filter === f.k ? ' active' : '')} onClick={() => setFilter(f.k)}>{f.label}</div>
          ))}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input className="chip-search" placeholder="Filter instruments…" value={q} onChange={(e) => setQ(e.target.value)} style={{ paddingRight: q ? 22 : undefined }} />
            {q && <button onClick={() => setQ('')} title="Clear" style={{ position: 'absolute', right: 4, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', padding: '2px', display: 'flex', alignItems: 'center' }}><X size={12} /></button>}
          </div>
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
