import { useEffect, useState } from 'react'
import { Bitcoin, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'
import { api, type CryptoFeed, type CryptoCoin } from '../lib/api'

// Per-coin flow chip styling (factual IN/OUT direction — never advice).
const FLOW_META: Record<string, { label: string; color: string; Icon: typeof Minus }> = {
  inflow:    { label: 'Inflow',    color: 'var(--up)',    Icon: ArrowUpRight },
  outflow:   { label: 'Outflow',   color: 'var(--down)',  Icon: ArrowDownRight },
  neutral:   { label: 'Neutral',   color: 'var(--text-3)', Icon: Minus },
  no_data:   { label: 'No data',   color: 'var(--text-3)', Icon: Minus },
  mixed:     { label: 'Mixed',     color: 'var(--warn, #D4A017)', Icon: Minus },
  divergent: { label: 'Divergent', color: 'var(--warn, #D4A017)', Icon: Minus },
}

function Bar({ label, value, color, level }: { label: string; value?: number; color: string; level?: string }) {
  const v = Math.max(0, Math.min(100, value ?? 0))
  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, color: 'var(--text-2)', marginBottom: 5 }}>
        <span>{label}</span>
        <span style={{ fontWeight: 700, color }}>{value ?? '—'}{level ? ` · ${level}` : ''}</span>
      </div>
      <div style={{ height: 8, background: 'var(--line-2)', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ width: `${v}%`, height: '100%', background: color, borderRadius: 6 }} />
      </div>
    </div>
  )
}

function CoinCard({ c }: { c: CryptoCoin }) {
  const flow = FLOW_META[c.flow || 'neutral'] || FLOW_META.neutral
  const Icon = flow.Icon
  const comps = Object.entries(c.components || {})
  const p = c.price
  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 11, padding: 16, display: 'flex', flexDirection: 'column', gap: 13 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Bitcoin size={22} color="#f7931a" strokeWidth={2} />
        <div style={{ fontWeight: 700, fontSize: 16 }}>{c.item_name}<span style={{ color: 'var(--text-3)', fontWeight: 500 }}> · {c.coin}</span></div>
        <span style={{ marginLeft: 'auto', fontSize: 10.5, fontWeight: 700, letterSpacing: '.04em', padding: '3px 9px', borderRadius: 999, background: 'var(--canvas)', color: 'var(--text-2)' }}>{c.tier}</span>
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        <Bar label="Money Movement" value={c.money_movement} color="var(--det)" level={c.detection_level} />
        <Bar label="Market Confirmation" value={c.market_confirmation} color="var(--conf)" level={c.confidence_level} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 12, fontWeight: 700, color: flow.color }}>
          <Icon size={14} /> {flow.label}
        </span>
        {p && p.change_7d_pct != null && (
          <span className="muted" style={{ fontSize: 11.5 }}>
            {p.last_close != null ? `$${p.last_close.toLocaleString()} · ` : ''}7d {p.change_7d_pct}% · 30d {p.change_30d_pct ?? '—'}%
          </span>
        )}
        {c.calibrating && <span style={{ marginLeft: 'auto', fontSize: 10.5, fontWeight: 700, letterSpacing: '.06em', color: 'var(--warn, #D4A017)' }}>CALIBRATING</span>}
      </div>

      {c.gap_state && (
        <div style={{ fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.5 }}>
          <b style={{ color: 'var(--text)' }}>{c.gap_state.replace(/_/g, ' ')}</b>{c.interpretation ? ` — ${c.interpretation}` : ''}
        </div>
      )}

      {/* §17 source-display: only components that contributed; real value or explicit n/a (never NaN). */}
      {comps.length > 0 && (
        <div style={{ borderTop: '1px solid var(--line-2)', paddingTop: 10, display: 'grid', gap: 6 }}>
          {comps.map(([label, comp]) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 12 }}>
              <span style={{ color: 'var(--text-3)' }}>{label}</span>
              <span style={{ fontWeight: 600, fontFamily: 'var(--mono)' }}>
                {comp.score == null ? 'n/a' : comp.score}
                {comp.baseline_relative && comp.z != null ? <span style={{ color: 'var(--text-3)', fontWeight: 400 }}> (z {comp.z})</span> : null}
              </span>
            </div>
          ))}
        </div>
      )}

      {c.dark_matter && (
        <div className="muted" style={{ fontSize: 11 }}>
          Dark Matter: {c.dark_matter.flow} · intensity {c.dark_matter.intensity} · {c.dark_matter.coverage} coverage ({c.dark_matter.proxies_covered} proxies)
        </div>
      )}
    </div>
  )
}

export function Crypto() {
  const [feed, setFeed] = useState<CryptoFeed | null>(null)
  const [err, setErr] = useState('')
  useEffect(() => { api.crypto().then(setFeed).catch((e) => setErr(String(e))) }, [])

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
      </div>

      {!feed && !err && <div className="center-state"><div className="spinner" /></div>}
      {err && <div className="center-state">Couldn't load the crypto feed.<div className="muted">{err}</div></div>}
      {feed && !feed.available && (
        <div className="center-state">
          Crypto Money Gradient is in held-out research.
          <div className="muted">{feed.note || 'Enable CRYPTO_SIGNAL to activate the live feed.'}</div>
        </div>
      )}
      {feed && feed.available && (
        <div style={{ padding: '16px 20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(330px, 1fr))', gap: 16 }}>
            {(feed.coins || []).map((c) => <CoinCard key={c.coin} c={c} />)}
          </div>
          {(feed.coins || []).length === 0 && <div className="center-state">No coins in the feed yet.</div>}
          {feed.disclaimer && <div className="muted" style={{ marginTop: 18, fontSize: 11, lineHeight: 1.5, maxWidth: 760 }}>{feed.disclaimer}</div>}
        </div>
      )}
    </>
  )
}
