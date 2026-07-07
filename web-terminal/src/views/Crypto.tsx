import { useEffect, useState, type ReactNode } from 'react'
import { MC, marketTierColor } from '../lib/mobileTheme'
import { Disclaimer } from '../components/Disclaimer'
import { SignalAnalysisPanel } from '../components/SignalAnalysis'
import { api, type CryptoFeed, type CryptoCoin } from '../lib/api'

// Crypto Money Gradient — master/detail, mirroring the Market Signal stock detail page.
// Coin list (master) + a side panel (CryptoRail) with the SAME dual-ring layout, interpretation,
// factors, and CSS as MarketRail. Measurement, not advice.
const MM_LABEL = 'Money Movement'
const MC_LABEL = 'Market Confirmation'

function ring(val: number, color: string) {
  const r = 26, c = 2 * Math.PI * r, off = c * (1 - Math.max(0, Math.min(100, val)) / 100)
  return (
    <svg width="72" height="72" viewBox="0 0 72 72">
      <circle cx="36" cy="36" r={r} fill="none" stroke="var(--line)" strokeWidth="6" />
      <circle cx="36" cy="36" r={r} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={off} transform="rotate(-90 36 36)" />
    </svg>
  )
}

// Factual flow direction chip (proxy Dark Matter vs price) — a measurement, not a buy/sell call.
function flowChip(flow?: string) {
  if (!flow || flow === 'no_data') return null
  const meta = flow === 'inflow' ? { t: '▲ inflow', c: MC.confidence }
    : flow === 'outflow' ? { t: '▼ outflow', c: MC.red }
    : flow === 'divergent' ? { t: '◆ divergent', c: MC.gold }
    : { t: '• ' + flow, c: MC.muted }
  return <span className="cal-chip" title="Net money-flow direction (informed proxies vs the coin's price) — a measurement, not advice" style={{ background: meta.c + '1A', color: meta.c, fontWeight: 700 }}>{meta.t}</span>
}

function CryptoRail({ c, onClose }: { c: CryptoCoin; onClose: () => void }) {
  const tcol = marketTierColor(c.tier)
  const p = c.price
  const dm = c.dark_matter
  const comps = Object.entries(c.components || {})
  return (
    <aside className="rail">
      <div className="detail-head">
        <div className="detail-top">
          <div>
            <div className="detail-name">{c.item_name} <span style={{ color: 'var(--text-3)', fontWeight: 500 }}>· {c.coin}</span></div>
            <div className="detail-cat">Crypto · <span style={{ color: tcol, fontWeight: 700 }}>{c.tier}</span>{flowChip(c.flow)}{c.calibrating && <span className="cal-chip">calibrating</span>}</div>
          </div>
          <div className="x" onClick={onClose}>✕</div>
        </div>
        <div className="detail-asof">
          {p?.last_close != null ? `$${p.last_close.toLocaleString()}` : ''}{p?.as_of ? ` · price as of ${p.as_of}` : ''}
        </div>
      </div>

      <Disclaimer style={{ marginBottom: 10 }} />

      {/* Dual rings — Money Movement (D) / Market Confirmation (M), same layout as the stock page */}
      <div className="gauges">
        <div className="gauge det">{ring(c.money_movement ?? 0, MC.detection)}<div className="gv" style={{ marginTop: -50, color: MC.detection }}>{c.money_movement ?? '—'}</div><div className="gl" style={{ marginTop: 28 }}>{MM_LABEL}</div><div className="gf">informed money · D</div></div>
        <div className="gauge conf">{ring(c.market_confirmation ?? 0, MC.confidence)}<div className="gv" style={{ marginTop: -50, color: MC.confidence }}>{c.market_confirmation ?? '—'}</div><div className="gl" style={{ marginTop: 28 }}>{MC_LABEL}</div><div className="gf">coin price · M</div></div>
      </div>

      {(c.gap_state || c.interpretation) && (
        <div className="sect">
          <b style={{ color: tcol, fontSize: 12 }}>{c.calibrating ? 'CALIBRATING' : (c.gap_state || '').replace(/_/g, ' ')}{c.gap != null && !c.calibrating ? ` · ${Math.abs(c.gap)}-pt gap` : ''}</b>
          {c.interpretation && <div className="narr" style={{ marginTop: 6, background: 'transparent', padding: 0 }}>{c.interpretation}</div>}
          {c.interpretation && <div className="disc" style={{ marginTop: 8 }}>AI-generated overview · qualitative context are computer generated. All information contained herein may not be accurate including any and all figures indicated in this section and or site and may be an approximation and should not be construed as financial, investment, or legal advice.</div>}
        </div>
      )}

      {/* Signal Analysis — enterprise per-item narrative (held-out, reproducible, measurement-only) */}
      <SignalAnalysisPanel kind="crypto" item={{ item_name: c.item_name, detection: c.money_movement, confidence: c.market_confirmation, flow: c.flow, tier: c.tier, dark_matter: (c as any).dark_matter }} />

      {/* Market Factors — §17: real value or n/a, never NaN */}
      {comps.length > 0 && (
        <div className="sect">
          <h4>Market Factors</h4>
          {comps.map(([label, comp]: [string, any]) => {
            const na = comp?.not_applicable || comp?.score == null
            const col = na ? MC.muted : (comp?.feeds === 'money_movement' ? MC.detection : MC.confidence)
            return (
              <div className="comp-row" key={label} style={na ? { opacity: 0.5 } : undefined}>
                <span className="cl"><span style={{ width: 6, height: 6, borderRadius: 3, background: col, display: 'inline-block', marginRight: 5 }} />{label.replace(/\s*\(.*\)$/, '')}{!na && comp?.baseline_relative ? ' ✓' : ''}</span>
                <span className="comp-bar"><i style={{ width: na ? '0%' : `${Math.max(4, Math.min(100, comp?.score ?? 0))}%`, background: col }} /></span>
                <span className="cv">{na ? 'n/a' : Math.round(comp?.score ?? 0)}</span>
              </div>
            )
          })}
          <div className="div-legend"><span style={{ color: MC.detection }}>●</span> money movement · <span style={{ color: MC.confidence }}>●</span> market confirmation · ✓ = scored vs own history</div>
        </div>
      )}

      {/* Price & Dark Matter facts — only what contributed (§17) */}
      {(p?.change_7d_pct != null || dm) && (
        <div className="sect">
          <h4>Price &amp; Dark Matter</h4>
          {p?.change_7d_pct != null && <div className="comp-row"><span className="cl">Price trend</span><span className="cv" style={{ fontFamily: 'var(--mono)' }}>7d {p.change_7d_pct}% · 30d {p.change_30d_pct ?? '—'}%</span></div>}
          {dm && <div className="comp-row"><span className="cl">Dark Matter (proxies)</span><span className="cv" style={{ fontFamily: 'var(--mono)' }}>{dm.flow} · {dm.intensity} · {dm.coverage}</span></div>}
          <div className="disc">Price via FMP (coin) · Dark Matter via crypto-exposure proxy 13F / insider. Measurement only.</div>
        </div>
      )}

      <div className="disc"><b>What the Crypto signal measures:</b> The Crypto section tracks whether money is moving into or out of a coin. {MM_LABEL} “D” = informed / early money via crypto-exposure proxies (spot-ETF 13F + MSTR / COIN insider). {MC_LABEL} “M” = the coin's own price / volume confirmation. The flow (IN/OUT) is a measurement; whether an early read led realized price is recorded, after the fact, in the crypto accuracy ledger. Be advised that this summary may be inaccurate and is not intended to be financial, legal or investment advice.</div>
    </aside>
  )
}

// DIRECTION (flow) axis — net money-flow via crypto-exposure proxies (a measurement, not advice).
// Neutral covers anything without a clear in/out read (neutral, divergent, or unknown).
const CRYPTO_DIR_FILTERS: { k: string; label: string; test: (c: CryptoCoin) => boolean }[] = [
  { k: 'all', label: 'All', test: () => true },
  { k: 'inflow', label: 'Inflow', test: (c) => c.flow === 'inflow' },
  { k: 'outflow', label: 'Outflow', test: (c) => c.flow === 'outflow' },
  { k: 'neutral', label: 'Neutral', test: (c) => c.flow !== 'inflow' && c.flow !== 'outflow' },
]

export function Crypto({ onRail }: { onRail: (node: ReactNode | null) => void }) {
  const [feed, setFeed] = useState<CryptoFeed | null>(null)
  const [err, setErr] = useState('')
  const [sel, setSel] = useState<string | null>(null)
  const [dirFilter, setDirFilter] = useState('all')
  // The engine serves /crypto from a prewarmed cache. On a cold boot it returns status:'warming'
  // (coins:[]) while the prewarm fills the roster — poll until the coins arrive.
  useEffect(() => {
    let stop = false; let tries = 0
    const load = () => {
      api.crypto().then((f) => {
        if (stop) return
        setFeed(f)
        if (f.status === 'warming' && tries++ < 15) setTimeout(load, 4000)
      }).catch((e) => { if (!stop) setErr(String(e)) })
    }
    load()
    return () => { stop = true }
  }, [])

  const select = (c: CryptoCoin) => {
    if (c.coin === sel) { setSel(null); onRail(null); return }
    setSel(c.coin)
    onRail(<CryptoRail c={c} onClose={() => { setSel(null); onRail(null) }} />)
  }

  const coins = feed?.coins || []
  const anyCalibrating = coins.some((c) => c.calibrating)
  const dfl = CRYPTO_DIR_FILTERS.find((x) => x.k === dirFilter)
  const shown = dfl?.test ? coins.filter(dfl.test) : coins
  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Crypto</div>
          <div className="main-sub">
            Crypto <b>Money Gradient</b> — Money Movement (informed money via crypto-exposure proxies)
            vs Market Confirmation (the coin's own price). Measurement, not advice.
          </div>
        </div>
        <div className="chips">
          <span className="chip-label">Direction</span>
          {CRYPTO_DIR_FILTERS.map((f) => (
            <div key={f.k} className={'chip' + (dirFilter === f.k ? ' active' : '')} onClick={() => setDirFilter(f.k)}
                 title="Net money-flow via crypto-exposure proxies: Inflow = informed buying · Outflow = selling · Neutral = no clear net direction">{f.label}</div>
          ))}
        </div>
      </div>

      {anyCalibrating && feed?.available && (
        <div className="cal-banner">
          ◷ Crypto Money Gradient is <b>baseline-relative</b>. Coins with limited history read “calibrating” —
          tiers settle as each coin's baseline accumulates over the coming cycles. Measurement only — not advice.
        </div>
      )}

      <div className="grid-wrap">
        {!feed && !err ? (
          <div className="center-state"><div className="spinner" />Loading the crypto money gradient…</div>
        ) : err ? (
          <div className="center-state">Couldn't load the crypto feed.<div className="muted">{err}</div></div>
        ) : feed && !feed.available ? (
          <div className="center-state">Crypto Money Gradient is in held-out research.<div className="muted">{feed.note || ''}</div></div>
        ) : feed?.status === 'warming' ? (
          <div className="center-state"><div className="spinner" />Warming the crypto money gradient…<div className="muted">Loading the roster — one moment.</div></div>
        ) : coins.length === 0 ? (
          <div className="center-state">No coins in the feed yet.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Coin</th>
                <th className="r">{MM_LABEL}</th>
                <th className="r">{MC_LABEL}</th>
                <th className="r">Lead</th>
                <th>Tier</th>
                <th className="r">Price 7d</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((c) => {
                const ch7 = c.price?.change_7d_pct
                return (
                  <tr key={c.coin} className={c.coin === sel ? 'sel' : ''} onClick={() => select(c)}>
                    <td>
                      <div className="topic-name">{c.item_name} <span style={{ color: 'var(--text-3)' }}>· {c.coin}</span>{c.calibrating && <span className="cal-chip">cal</span>}{flowChip(c.flow)}</div>
                      <div className="topic-cat">crypto</div>
                    </td>
                    <td className="r"><span className="score-cell det">{c.money_movement}</span></td>
                    <td className="r"><span className="score-cell conf">{c.market_confirmation}</span></td>
                    <td className="r"><span className="muted">{c.gap != null ? `${c.gap > 0 ? '+' : ''}${c.gap}` : '—'}</span></td>
                    <td><span className="tier" style={{ color: marketTierColor(c.tier), background: marketTierColor(c.tier) + '18', padding: '2px 8px', borderRadius: 6, fontWeight: 700, fontSize: 11 }}>{c.tier}</span></td>
                    <td className="r"><span className={'pct ' + (ch7 == null ? 'na' : ch7 > 0 ? 'up' : ch7 < 0 ? 'down' : 'flat')}>{ch7 == null ? '—' : `${ch7 > 0 ? '+' : ''}${ch7}%`}</span></td>
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
