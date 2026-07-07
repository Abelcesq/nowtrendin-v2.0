import { Fragment, useEffect, useMemo, useState } from 'react'
import { api, type LedgerSummary, type LedgerRow, type MarketLedgerSummary, type MarketLedgerRow } from '../lib/api'
import { SignalAnalysisPanel } from '../components/SignalAnalysis'

type SortKey = 'topic_display' | 'detection_score' | 'lead_time_days' | 'verdict' | 'validated_at'

const VERDICTS = ['', 'LED', 'SAME_DAY', 'LAGGED_NEAR', 'PRE_BROKEN', 'FALSE_POSITIVE'] as const
const VLABEL: Record<string, string> = {
  '': 'All', LED: 'Led', SAME_DAY: 'Same day', LAGGED_NEAR: 'Lagged · near miss',
  PRE_BROKEN: 'Pre-broken', FALSE_POSITIVE: 'False positive',
}

// PRE-BROKEN = a LAGGED row whose Google breakout happened more than the grace window
// (server default 7d) BEFORE our first sighting — the topic entered tracking already
// post-breakout, so it was never a race. Server-computed (r.pre_broken); the lead-based
// fallback only covers a cached/older API response.
const isPreBroken = (r: { pre_broken?: boolean; verdict?: string; lead_time_days?: number | null }) =>
  r.pre_broken === true || (r.pre_broken == null && (r.verdict || '').toUpperCase() === 'LAGGED'
    && r.lead_time_days != null && r.lead_time_days < -7)

// Money-ledger verdicts (distinct: validated by realized EOD price direction, not Trends).
const MVERDICTS = ['', 'CONFIRMED', 'NOT_CONFIRMED', 'NO_MOVE'] as const
const MVLABEL: Record<string, string> = {
  '': 'All', CONFIRMED: 'Confirmed', NOT_CONFIRMED: 'Not confirmed', NO_MOVE: 'No move',
}
const flowCol = (f?: string) => f === 'inflow' ? 'var(--conf, #00C896)' : f === 'outflow' ? '#DC2626' : '#94A3B8'
const flowLabel = (f?: string) => f === 'inflow' ? '▲ inflow' : f === 'outflow' ? '▼ outflow' : '• neutral'

function fmtDate(s?: string) {
  if (!s) return '—'
  const d = new Date(s)
  return isNaN(+d) ? s.slice(0, 10) : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })
}

export function Ledger() {
  const [mode, setMode] = useState<'attention' | 'money' | 'crypto'>('attention')
  const [summary, setSummary] = useState<LedgerSummary | null>(null)
  const [rows, setRows] = useState<LedgerRow[]>([])
  const [msum, setMsum] = useState<MarketLedgerSummary | null>(null)
  const [mrows, setMrows] = useState<MarketLedgerRow[]>([])
  const [moneyLoaded, setMoneyLoaded] = useState(false)
  const [csum, setCsum] = useState<MarketLedgerSummary | null>(null)
  const [crows, setCrows] = useState<MarketLedgerRow[]>([])
  const [cryptoLoaded, setCryptoLoaded] = useState(false)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('')
  const [sortKey, setSortKey] = useState<SortKey>('validated_at')
  const [sortDir, setSortDir] = useState(-1)
  // Row → expanded Ledger Entry Analysis (the /analysis/ledger information panel).
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    setLoading(true); setErr(null)
    Promise.all([api.ledger(), api.ledgerDetail()])
      .then(([s, d]) => { if (!alive) return; setSummary(s); setRows(d.rows || []) })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  // Lazy-load the Money ledger the first time it's selected (distinct endpoints).
  useEffect(() => {
    if (mode !== 'money' || moneyLoaded) return
    let alive = true
    setLoading(true); setErr(null); setFilter('')
    Promise.all([api.marketAccuracy(), api.marketAccuracyDetail()])
      .then(([s, d]) => { if (!alive) return; setMsum(s); setMrows(d.rows || []); setMoneyLoaded(true) })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [mode, moneyLoaded])

  // Lazy-load the Crypto ledger the first time it's selected (coin-price-validated, distinct endpoints).
  useEffect(() => {
    if (mode !== 'crypto' || cryptoLoaded) return
    let alive = true
    setLoading(true); setErr(null); setFilter('')
    Promise.all([api.cryptoAccuracy(), api.cryptoAccuracyDetail()])
      .then(([s, d]) => { if (!alive) return; setCsum(s); setCrows(d.rows || []); setCryptoLoaded(true) })
      .catch((e) => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [mode, cryptoLoaded])

  const view = useMemo(() => {
    let r = rows.slice()
    if (filter === 'PRE_BROKEN') r = r.filter((x) => isPreBroken(x))
    else if (filter === 'LAGGED_NEAR') r = r.filter((x) => (x.verdict || '').toUpperCase() === 'LAGGED' && !isPreBroken(x))
    else if (filter) r = r.filter((x) => (x.verdict || '').toUpperCase() === filter)
    r.sort((a, b) => {
      const va = a[sortKey] as any, vb = b[sortKey] as any
      if (typeof va === 'string' || typeof vb === 'string')
        return String(va ?? '').localeCompare(String(vb ?? '')) * sortDir
      return ((va ?? -1) - (vb ?? -1)) * sortDir
    })
    return r
  }, [rows, filter, sortKey, sortDir])

  const mview = useMemo(() => {
    let r = mrows.slice()
    if (filter) r = r.filter((x) => (x.verdict || '').toUpperCase() === filter)
    return r.sort((a, b) => String(b.validated_at ?? '').localeCompare(String(a.validated_at ?? '')))
  }, [mrows, filter])

  const cview = useMemo(() => {
    let r = crows.slice()
    if (filter) r = r.filter((x) => (x.verdict || '').toUpperCase() === filter)
    return r.sort((a, b) => String(b.validated_at ?? '').localeCompare(String(a.validated_at ?? '')))
  }, [crows, filter])

  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'topic_display' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const hit = summary?.hitRate ?? 0
  const med = summary?.medianLead ?? 0
  const resolved = summary?.total ?? 0
  const money = mode === 'money'
  const crypto = mode === 'crypto'
  // Money + Crypto are BOTH realized-price-validated ledgers with the SAME shape — render one path.
  const priceMode = money || crypto
  const psum = crypto ? csum : msum
  const pview = crypto ? cview : mview

  const ModeToggle = (
    <div className="chips" style={{ marginBottom: 6 }}>
      <span className="chip-label">Ledger</span>
      <div className={'chip' + (mode === 'attention' ? ' active' : '')} onClick={() => { setMode('attention'); setFilter('') }}
           title="Attention Gradient — validated against Google Trends breakout">Attention · Trends</div>
      <div className={'chip' + (money ? ' active' : '')} onClick={() => { setMode('money'); setFilter('') }}
           title="Money Gradient — validated against realized EOD price direction (FMP)">Money · Market</div>
      <div className={'chip' + (crypto ? ' active' : '')} onClick={() => { setMode('crypto'); setFilter('') }}
           title="Crypto Money Gradient — validated against realized COIN price direction (FMP crypto + AV)">Crypto · Coin</div>
    </div>
  )

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Accuracy Ledger</div>
          <div className="main-sub">
            {priceMode ? (
              <>{crypto ? 'Crypto money-movement detections validated against realized ' : 'Money-movement detections validated against realized '}
                <b>{crypto ? 'coin price direction' : 'EOD price direction'}</b> ({crypto ? 'FMP crypto + AV' : 'FMP'}) ·{' '}
                <b>{psum?.resolved ?? 0}</b> resolved · <b>{psum?.pending ?? 0}</b> in flight</>
            ) : (
              <>Timestamped detections validated against observed breakouts ·{' '}
                <b>{resolved}</b> resolved · <b>{summary?.pending ?? 0}</b> pending</>
            )}
          </div>
          <div className="main-actions">
            <button className="btn">▦ Columns</button>
            <button className="btn primary">↧ Export</button>
          </div>
        </div>
        {ModeToggle}
        <div className="chips">
          {(priceMode ? MVERDICTS : VERDICTS).map((v) => (
            <div key={v || 'all'} className={'chip' + (filter === v ? ' active' : '')} onClick={() => setFilter(v)}>
              {priceMode ? MVLABEL[v] : VLABEL[v]}
            </div>
          ))}
        </div>
      </div>

      {priceMode ? (
        <>
          <div className="cal-banner">
            ◷ A <b>separate</b> ledger from the Attention one. Ground truth = the realized {crypto ? 'coin' : 'EOD'} close
            <b> direction</b> (inflow→up / outflow→down, past ±{psum?.move_threshold_pct ?? (crypto ? 8 : 5)}%), {crypto ? 'via FMP crypto + AV' : 'via FMP'} — not Google Trends.
            A <b>retrospective measurement</b> of whether our {crypto ? 'crypto ' : ''}money-movement read matched the {crypto ? 'coin' : 'market'} — not a
            forecast or advice.
          </div>
          <div className="statstrip">
            <div className="statcard"><div className="sl">Confirm rate</div><div className="sv good">{psum?.confirm_rate_pct != null ? psum.confirm_rate_pct.toFixed(1) + '%' : '—'}</div><div className="sf">CONFIRMED ÷ all resolved (misses counted)</div></div>
            <div className="statcard"><div className="sl">Median lead</div><div className="sv early">{psum?.median_lead_days != null ? psum.median_lead_days + 'd' : '—'}</div><div className="sf">days from detection to the confirming move</div></div>
            <div className="statcard"><div className="sl">Confirmed / Not / No-move</div><div className="sv">{psum?.confirmed ?? 0}/{psum?.not_confirmed ?? 0}/{psum?.no_move ?? 0}</div><div className="sf">directional outcome breakdown</div></div>
            <div className="statcard"><div className="sl">Inflow · outflow confirm</div><div className="sv">{psum?.by_flow?.inflow?.confirm_rate_pct != null ? psum.by_flow.inflow.confirm_rate_pct + '%' : '—'} · {psum?.by_flow?.outflow?.confirm_rate_pct != null ? psum.by_flow.outflow.confirm_rate_pct + '%' : '—'}</div><div className="sf">by detected flow direction</div></div>
            <div className="statcard"><div className="sl">Resolved · in flight</div><div className="sv">{psum?.resolved ?? 0}·{psum?.pending ?? 0}</div><div className="sf">{psum?.small_sample ? 'small sample — interpret with care' : 'sample sufficient'}</div></div>
          </div>
        </>
      ) : (
        <>
          <div className="cal-banner">
            ◷ <b>Pre-broken</b> = the Google breakout happened more than {' '}
            <b>7 days before our first sighting</b> — the topic entered tracking already
            post-breakout, so it was never a race we could win. Pre-broken rows stay {' '}
            <b>counted in the honest rate</b>; the <b>tracked-race rate</b> reports only the
            races actually run. LED wins additionally carry an <b>independent Wikipedia-pageviews
            referee</b> check (wins resolved before 2026-07-07 predate it and read "unchecked").
          </div>
          <div className="statstrip">
            <div className="statcard"><div className="sl">Honest hit rate</div><div className="sv good">{hit.toFixed(1)}%</div><div className="sf">LED ÷ all resolved (misses counted)</div></div>
            <div className="statcard"><div className="sl">Tracked-race hit rate</div><div className="sv early">{summary?.trackedRaceHitRate != null ? summary.trackedRaceHitRate.toFixed(1) + '%' : '—'}</div><div className="sf">LED ÷ races actually run ({summary?.trackedRaceSample ?? '—'}; pre-broken excluded)</div></div>
            <div className="statcard"><div className="sl">Median lead time</div><div className="sv early">{med}d</div><div className="sf">days ahead of Google Trends breakout</div></div>
            <div className="statcard"><div className="sl">Led / Same / Near / Pre-broken / FP</div><div className="sv">{summary?.led ?? 0}/{summary?.sameDay ?? 0}/{summary?.laggedNear ?? summary?.lagged ?? 0}/{summary?.preBroken ?? 0}/{summary?.falsePositives ?? 0}</div><div className="sf">outcome breakdown (near + pre-broken = lagged)</div></div>
            <div className="statcard"><div className="sl">LED referee check</div><div className="sv">{summary?.ledCorroborated ?? 0}✓ · {summary?.ledUncorroborated ?? 0}– · {summary?.ledUnchecked ?? 0}·</div><div className="sf">Wikipedia-corroborated · not corroborated · unchecked</div></div>
            <div className="statcard"><div className="sl">Resolved · pending</div><div className="sv">{resolved}·{summary?.pending ?? 0}</div><div className="sf">{summary?.smallSample ? 'small sample — interpret with care' : 'sample sufficient'}</div></div>
          </div>
        </>
      )}

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading the ledger…</div>
        ) : err ? (
          <div className="center-state">Could not load the ledger.<div className="muted">{err}</div></div>
        ) : priceMode ? (
          pview.length === 0 ? (
            <div className="center-state">
              No resolved {crypto ? 'crypto ' : ''}money-movement detections yet{filter ? ` for "${MVLABEL[filter]}"` : ''}.
              <div className="muted">{(psum?.pending ?? 0) > 0 ? `${psum!.pending} detection${psum!.pending === 1 ? '' : 's'} in flight — they resolve` : 'Detections resolve'} as the realized {crypto ? 'coin' : ''} price confirms (or the {psum?.timeout_days ?? (crypto ? 45 : 60)}-day window elapses).{(psum?.pending ?? 0) === 0 ? ` Populates once the ${crypto ? 'Crypto ' : ''}Money Gradient is live.` : ''}</div>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>{crypto ? 'Coin' : 'Instrument'}</th>
                  <th>Flow</th>
                  <th className="r">Money @ call</th>
                  <th className="r">Detected</th>
                  <th className="r">Price move</th>
                  <th className="r">Lead</th>
                  <th>Verdict</th>
                  <th className="r">Validated</th>
                </tr>
              </thead>
              <tbody>
                {pview.map((r, i) => (
                  <tr key={(r.ticker || r.coin || '') + i}>
                    <td><div className="topic-name">{r.name || r.ticker || r.coin}</div><div className="topic-cat">{r.ticker || r.coin}</div></td>
                    <td><span style={{ color: flowCol(r.flow), fontWeight: 700, fontSize: 12 }}>{flowLabel(r.flow)}</span></td>
                    <td className="r"><span className="score-cell det">{(r.detection_score ?? r.money_movement) != null ? Math.round((r.detection_score ?? r.money_movement)!) : '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.detection_date)}</span></td>
                    <td className="r"><span className={'gapnum ' + ((r.price_change_pct ?? 0) >= 0 ? 'wide' : 'neg')}>{r.price_change_pct != null ? `${r.price_change_pct > 0 ? '+' : ''}${r.price_change_pct}%` : '—'}</span></td>
                    <td className="r"><span className="muted">{r.lead_time_days != null ? `${r.lead_time_days}d` : '—'}</span></td>
                    <td><span className="verdict" style={{ color: r.verdict === 'CONFIRMED' ? 'var(--conf,#00C896)' : r.verdict === 'NOT_CONFIRMED' ? '#DC2626' : '#94A3B8' }}>{r.verdict || '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.validated_at)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : view.length === 0 ? (
          <div className="center-state">
            No resolved detections yet{filter ? ` for "${VLABEL[filter]}"` : ''}.
            <div className="muted">{summary?.pending ?? 0} detections in flight — they resolve as breakouts are observed.</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th onClick={() => sort('topic_display')} className={sortKey === 'topic_display' ? 'sorted' : ''}>Topic <span className="sort">{arrow('topic_display')}</span></th>
                <th onClick={() => sort('detection_score')} className={'r ' + (sortKey === 'detection_score' ? 'sorted' : '')}>Det @ call <span className="sort">{arrow('detection_score')}</span></th>
                <th className="r">Detected</th>
                <th className="r">Breakout</th>
                <th onClick={() => sort('lead_time_days')} className={'r ' + (sortKey === 'lead_time_days' ? 'sorted' : '')}>Lead <span className="sort">{arrow('lead_time_days')}</span></th>
                <th onClick={() => sort('verdict')} className={sortKey === 'verdict' ? 'sorted' : ''}>Verdict <span className="sort">{arrow('verdict')}</span></th>
                <th>Provider</th>
                <th onClick={() => sort('validated_at')} className={'r ' + (sortKey === 'validated_at' ? 'sorted' : '')}>Validated <span className="sort">{arrow('validated_at')}</span></th>
              </tr>
            </thead>
            <tbody>
              {view.map((r, i) => {
                const lead = r.lead_time_days
                const pre = isPreBroken(r)
                const win = r.verdict === 'LED' || r.verdict === 'SAME_DAY'
                const rowId = r.topic_key + '|' + (r.detection_date || i)
                const open = expanded === rowId
                return (
                  <Fragment key={rowId}>
                  <tr onClick={() => setExpanded(open ? null : rowId)}
                      style={{ cursor: 'pointer' }}
                      title="Click for the full entry analysis — what was recorded, how tracking works, and what this verdict means">
                    <td>
                      <div className="topic-name">{r.topic_display}</div>
                      <div className="topic-cat">
                        {r.topic_key}
                        {r.query_ambiguous === 1 && (
                          <span title="Broad/ambiguous search term — a Trends breakout on it is weaker evidence the matched surge is this specific signal"> · broad term</span>
                        )}
                      </div>
                    </td>
                    <td className="r"><span className="score-cell det">{r.detection_score ?? '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.detection_date)}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.breakout_date)}</span></td>
                    <td className="r"><span className={'gapnum ' + (lead != null && lead > 0 ? 'wide' : 'neg')}>{lead != null ? `${lead > 0 ? '+' : ''}${lead}d` : '—'}</span></td>
                    <td>
                      <span className={'verdict ' + (pre ? 'PRE_BROKEN' : (r.verdict || ''))}
                            style={pre ? { color: '#94A3B8', background: 'rgba(148,163,184,.12)' } : undefined}
                            title={pre ? 'Breakout occurred >7d before our first sighting — the topic entered tracking already post-breakout (never a race). Counted in the honest rate; excluded from the tracked-race rate.' : undefined}>
                        {pre ? 'PRE-BROKEN' : (r.verdict || '—')}
                      </span>
                      {win && (
                        <div className="topic-cat" style={{ marginTop: 2 }}
                             title="Independent second referee: Wikipedia pageviews showed attention arriving within ±14d of the Google breakout">
                          {r.referee_corroborated === 1 ? '✓ wiki-corroborated'
                            : r.referee_corroborated === 0 ? '– wiki: no arrival match'
                            : '· referee unchecked'}
                        </div>
                      )}
                    </td>
                    <td><span className="muted">{r.provider || '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.validated_at)}</span></td>
                  </tr>
                  {open && (
                    <tr>
                      <td colSpan={8} style={{ padding: '0 12px 12px' }}>
                        <SignalAnalysisPanel kind="ledger" item={{ ...r, pre_broken: pre }} />
                      </td>
                    </tr>
                  )}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
