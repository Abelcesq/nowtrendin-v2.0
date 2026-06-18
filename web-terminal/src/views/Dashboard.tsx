import { useEffect, useState } from 'react'
import { TrendingUp, Flame, DollarSign, Scale } from 'lucide-react'
import { api, type TopicRow, type RiskRow } from '../lib/api'
import type { NavKey } from '../components/Shell'

// Phase 4 of the 3-platform UI migration (Charter §0.6): the at-a-glance intro page.
// Four large tiles, all wired to LIVE engine data — top high-conviction trends,
// top N (demand) leaders, top market signals, and the leverage spread (low- vs
// high-leverage-risk companies). Icons from lucide-react; colors from the shared
// mobile tokens (var(--det)/--conf + stage tokens).

const r0 = (v: any) => Math.round(Number(v || 0))

function stagePill(stage?: string) {
  const s = (stage || '').toUpperCase()
  const cls = ['BREAKOUT', 'STRONG', 'EMERGING', 'WATCHING', 'MARGINAL', 'MONITORING'].includes(s) ? s : 'MONITORING'
  return <span className={'stage ' + cls}>{s || '—'}</span>
}

export function Dashboard({ onNav, onPick }: { onNav: (k: NavKey) => void; onPick?: (key: string) => void }) {
  const [topics, setTopics] = useState<TopicRow[]>([])
  const [risks, setRisks] = useState<RiskRow[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    Promise.all([api.topics(200), api.risk(200).catch(() => ({ count: 0, results: [] as RiskRow[] }))])
      .then(([t, r]) => { if (!alive) return; setTopics(t.topics || []); setRisks(r.results || []) })
      .catch((e) => alive && setErr(String(e?.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const T = topics.map((t) => ({
    key: t.topic_key, name: t.topic_display || t.topic_key,
    det: r0(t.detection_score), conf: r0(t.confidence_score), n: r0(t.nowtrendin_score),
    stage: t.current_stage,
  }))
  // Tile 1 — top trends, minimal gap (high conviction: strong score AND det≈conf)
  const conv = T.filter((t) => t.det >= 70).sort((a, b) => Math.abs(a.det - a.conf) - Math.abs(b.det - b.conf)).slice(0, 5)
  // Tile 2 — top N (on-platform demand leaders)
  const nlead = [...T].sort((a, b) => b.n - a.n).slice(0, 5)

  const M = risks.map((r) => {
    const mg = r.market_gradient || {}
    return {
      key: r.risk_topic, name: r.risk_display || r.risk_topic,
      det: r0(mg.detection ?? r.detection_score), tier: mg.tier || r.risk_stage || '—',
      lev: mg.leverage_health == null ? null : r0(mg.leverage_health),
    }
  })
  // Tile 3 — top market signals (by market detection)
  const mkt = [...M].sort((a, b) => b.det - a.det).slice(0, 5)
  // Tile 4 — leverage spread: leverage_health high = healthy/low risk, low = high risk
  const withLev = M.filter((m) => m.lev != null) as (typeof M[number] & { lev: number })[]
  const low = [...withLev].sort((a, b) => b.lev - a.lev).slice(0, 4)
  const high = [...withLev].sort((a, b) => a.lev - b.lev).slice(0, 4)

  const pick = (key: string, nav: NavKey) => { onNav(nav); onPick?.(key) }

  if (loading) return <div className="center-state"><div className="spinner" />Loading dashboard…</div>
  if (err) return <div className="center-state">Could not load dashboard.<div className="muted">{err}</div></div>

  return (
    <div className="dash">
      <div className="dash-head">
        <span className="h">Dashboard</span>
        <span className="s">· at a glance</span>
      </div>
      <div className="dash-grid">

        <div className="dash-tile">
          <h3><TrendingUp size={17} color="var(--det)" /> Top trends · minimal gap
            <span className="sub" onClick={() => onNav('trends')}>view all →</span></h3>
          {conv.length === 0 ? <div className="dash-empty">No high-conviction trends right now.</div> :
            conv.map((t) => (
              <div className="dash-row" key={t.key} onClick={() => pick(t.key, 'trends')}>
                <span className="nm">{t.name}</span>
                <span className="v" style={{ color: 'var(--det)' }}>{t.det}</span>
                <span className="v" style={{ color: 'var(--conf)' }}>{t.conf}</span>
                <span className="pill" style={{ color: 'var(--em-t)', background: 'var(--em-b)' }}>gap {Math.abs(t.det - t.conf)}</span>
              </div>
            ))}
        </div>

        <div className="dash-tile">
          <h3><Flame size={17} color="var(--early)" /> Top N · demand leaders
            <span className="sub" onClick={() => onNav('trends')}>view all →</span></h3>
          {nlead.map((t) => (
            <div className="dash-row" key={t.key} onClick={() => pick(t.key, 'trends')}>
              <span className="nm">{t.name}</span>
              <span className="pill" style={{ color: 'var(--early)', background: 'var(--early-soft)' }}>N {t.n}</span>
              <span className="v" style={{ color: 'var(--text-3)' }}>det {t.det}</span>
            </div>
          ))}
        </div>

        <div className="dash-tile">
          <h3><DollarSign size={17} color="var(--conf)" /> Top market signals
            <span className="sub" onClick={() => onNav('market')}>view all →</span></h3>
          {mkt.length === 0 ? <div className="dash-empty">Market signals unavailable.</div> :
            mkt.map((m) => (
              <div className="dash-row" key={m.key} onClick={() => pick(m.key, 'market')}>
                <span className="nm">{m.name}</span>
                <span className="v" style={{ color: 'var(--det)' }}>{m.det}</span>
                <span className="pill" style={{ color: 'var(--st-t)', background: 'var(--st-b)' }}>{m.tier}</span>
              </div>
            ))}
        </div>

        <div className="dash-tile">
          <h3><Scale size={17} color="var(--text-2)" /> Leverage spread
            <span className="sub" onClick={() => onNav('market')}>view all →</span></h3>
          {withLev.length === 0 ? <div className="dash-empty">No leverage data yet.</div> : (
            <div className="dash-split">
              <div>
                <div className="lbl" style={{ color: 'var(--conf)' }}>LOW RISK</div>
                {low.map((m) => (
                  <div className="dash-row" key={m.key} onClick={() => pick(m.key, 'market')}>
                    <span className="nm">{m.name}</span>
                    <span className="v" style={{ color: 'var(--conf)' }}>{m.lev}</span>
                  </div>
                ))}
              </div>
              <div>
                <div className="lbl" style={{ color: 'var(--down)' }}>HIGH RISK</div>
                {high.map((m) => (
                  <div className="dash-row" key={m.key} onClick={() => pick(m.key, 'market')}>
                    <span className="nm">{m.name}</span>
                    <span className="v" style={{ color: 'var(--down)' }}>{m.lev}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
