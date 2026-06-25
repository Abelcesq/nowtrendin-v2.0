import { useEffect, useMemo, useState } from 'react'
import { api, type LedgerSummary, type LedgerRow, type MarketLedgerSummary, type MarketLedgerRow } from '../lib/api'

type SortKey = 'topic_display' | 'detection_score' | 'lead_time_days' | 'verdict' | 'validated_at'

const VERDICTS = ['', 'LED', 'SAME_DAY', 'LAGGED', 'FALSE_POSITIVE'] as const
const VLABEL: Record<string, string> = {
  '': 'All', LED: 'Led', SAME_DAY: 'Same day', LAGGED: 'Lagged', FALSE_POSITIVE: 'False positive',
}

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
  const [mode, setMode] = useState<'attention' | 'money'>('attention')
  const [summary, setSummary] = useState<LedgerSummary | null>(null)
  const [rows, setRows] = useState<LedgerRow[]>([])
  const [msum, setMsum] = useState<MarketLedgerSummary | null>(null)
  const [mrows, setMrows] = useState<MarketLedgerRow[]>([])
  const [moneyLoaded, setMoneyLoaded] = useState(false)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('')
  const [sortKey, setSortKey] = useState<SortKey>('validated_at')
  const [sortDir, setSortDir] = useState(-1)

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

  const view = useMemo(() => {
    let r = rows.slice()
    if (filter) r = r.filter((x) => (x.verdict || '').toUpperCase() === filter)
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

  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'topic_display' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const hit = summary?.hitRate ?? 0
  const med = summary?.medianLead ?? 0
  const resolved = summary?.total ?? 0
  const money = mode === 'money'

  const ModeToggle = (
    <div className="chips" style={{ marginBottom: 6 }}>
      <span className="chip-label">Ledger</span>
      <div className={'chip' + (!money ? ' active' : '')} onClick={() => { setMode('attention'); setFilter('') }}
           title="Attention Gradient — validated against Google Trends breakout">Attention · Trends</div>
      <div className={'chip' + (money ? ' active' : '')} onClick={() => { setMode('money'); setFilter('') }}
           title="Money Gradient — validated against realized EOD price direction (FMP)">Money · Market</div>
    </div>
  )

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Accuracy Ledger</div>
          <div className="main-sub">
            {money ? (
              <>Money-movement detections validated against realized <b>EOD price direction</b> (FMP) ·{' '}
                <b>{msum?.resolved ?? 0}</b> resolved</>
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
          {(money ? MVERDICTS : VERDICTS).map((v) => (
            <div key={v || 'all'} className={'chip' + (filter === v ? ' active' : '')} onClick={() => setFilter(v)}>
              {money ? MVLABEL[v] : VLABEL[v]}
            </div>
          ))}
        </div>
      </div>

      {money ? (
        <>
          <div className="cal-banner">
            ◷ A <b>separate</b> ledger from the Attention one. Ground truth = the realized EOD close
            <b> direction</b> (inflow→up / outflow→down, past ±{msum?.move_threshold_pct ?? 5}%), not Google Trends.
            A <b>retrospective measurement</b> of whether our money-movement read matched the market — not a
            forecast or advice.
          </div>
          <div className="statstrip">
            <div className="statcard"><div className="sl">Confirm rate</div><div className="sv good">{msum?.confirm_rate_pct != null ? msum.confirm_rate_pct.toFixed(1) + '%' : '—'}</div><div className="sf">CONFIRMED ÷ all resolved (misses counted)</div></div>
            <div className="statcard"><div className="sl">Median lead</div><div className="sv early">{msum?.median_lead_days != null ? msum.median_lead_days + 'd' : '—'}</div><div className="sf">days from detection to the confirming move</div></div>
            <div className="statcard"><div className="sl">Confirmed / Not / No-move</div><div className="sv">{msum?.confirmed ?? 0}/{msum?.not_confirmed ?? 0}/{msum?.no_move ?? 0}</div><div className="sf">directional outcome breakdown</div></div>
            <div className="statcard"><div className="sl">Inflow · outflow confirm</div><div className="sv">{msum?.by_flow?.inflow?.confirm_rate_pct != null ? msum.by_flow.inflow.confirm_rate_pct + '%' : '—'} · {msum?.by_flow?.outflow?.confirm_rate_pct != null ? msum.by_flow.outflow.confirm_rate_pct + '%' : '—'}</div><div className="sf">by detected flow direction</div></div>
            <div className="statcard"><div className="sl">Resolved</div><div className="sv">{msum?.resolved ?? 0}</div><div className="sf">{msum?.small_sample ? 'small sample — interpret with care' : 'sample sufficient'}</div></div>
          </div>
        </>
      ) : (
        <div className="statstrip">
          <div className="statcard"><div className="sl">Honest hit rate</div><div className="sv good">{hit.toFixed(1)}%</div><div className="sf">LED ÷ all resolved (misses counted)</div></div>
          <div className="statcard"><div className="sl">Median lead time</div><div className="sv early">{med}d</div><div className="sf">days ahead of Google Trends breakout</div></div>
          <div className="statcard"><div className="sl">Max lead</div><div className="sv det">{summary?.maxLead ?? 0}d</div><div className="sf">best documented early call</div></div>
          <div className="statcard"><div className="sl">Led / Same / Lagged / FP</div><div className="sv">{summary?.led ?? 0}/{summary?.sameDay ?? 0}/{summary?.lagged ?? 0}/{summary?.falsePositives ?? 0}</div><div className="sf">outcome breakdown</div></div>
          <div className="statcard"><div className="sl">Resolved · pending</div><div className="sv">{resolved}·{summary?.pending ?? 0}</div><div className="sf">{summary?.smallSample ? 'small sample — interpret with care' : 'sample sufficient'}</div></div>
        </div>
      )}

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading the ledger…</div>
        ) : err ? (
          <div className="center-state">Could not load the ledger.<div className="muted">{err}</div></div>
        ) : money ? (
          mview.length === 0 ? (
            <div className="center-state">
              No resolved money-movement detections yet{filter ? ` for "${MVLABEL[filter]}"` : ''}.
              <div className="muted">Detections resolve as the realized price confirms (or the {msum?.timeout_days ?? 60}-day window elapses). Populates once the Money Gradient is live.</div>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Instrument</th>
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
                {mview.map((r, i) => (
                  <tr key={(r.ticker || '') + i}>
                    <td><div className="topic-name">{r.name || r.ticker}</div><div className="topic-cat">{r.ticker}</div></td>
                    <td><span style={{ color: flowCol(r.flow), fontWeight: 700, fontSize: 12 }}>{flowLabel(r.flow)}</span></td>
                    <td className="r"><span className="score-cell det">{r.detection_score != null ? Math.round(r.detection_score) : '—'}</span></td>
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
                return (
                  <tr key={r.topic_key + i}>
                    <td><div className="topic-name">{r.topic_display}</div><div className="topic-cat">{r.topic_key}</div></td>
                    <td className="r"><span className="score-cell det">{r.detection_score ?? '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.detection_date)}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.breakout_date)}</span></td>
                    <td className="r"><span className={'gapnum ' + (lead != null && lead > 0 ? 'wide' : 'neg')}>{lead != null ? `${lead > 0 ? '+' : ''}${lead}d` : '—'}</span></td>
                    <td><span className={'verdict ' + (r.verdict || '')}>{r.verdict || '—'}</span></td>
                    <td><span className="muted">{r.provider || '—'}</span></td>
                    <td className="r"><span className="muted">{fmtDate(r.validated_at)}</span></td>
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
