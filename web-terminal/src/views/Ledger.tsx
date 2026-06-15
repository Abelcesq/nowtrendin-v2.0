import { useEffect, useMemo, useState } from 'react'
import { api, type LedgerSummary, type LedgerRow } from '../lib/api'

type SortKey = 'topic_display' | 'detection_score' | 'lead_time_days' | 'verdict' | 'validated_at'

const VERDICTS = ['', 'LED', 'SAME_DAY', 'LAGGED', 'FALSE_POSITIVE'] as const
const VLABEL: Record<string, string> = {
  '': 'All', LED: 'Led', SAME_DAY: 'Same day', LAGGED: 'Lagged', FALSE_POSITIVE: 'False positive',
}

function fmtDate(s?: string) {
  if (!s) return '—'
  const d = new Date(s)
  return isNaN(+d) ? s.slice(0, 10) : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })
}

export function Ledger() {
  const [summary, setSummary] = useState<LedgerSummary | null>(null)
  const [rows, setRows] = useState<LedgerRow[]>([])
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

  const sort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => -d)
    else { setSortKey(k); setSortDir(k === 'topic_display' ? 1 : -1) }
  }
  const arrow = (k: SortKey) => (k === sortKey ? (sortDir < 0 ? '▼' : '▲') : '▼')

  const hit = summary?.hitRate ?? 0
  const med = summary?.medianLead ?? 0
  const resolved = summary?.total ?? 0

  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Accuracy Ledger</div>
          <div className="main-sub">
            Timestamped detections validated against observed breakouts ·{' '}
            <b>{resolved}</b> resolved · <b>{summary?.pending ?? 0}</b> pending
          </div>
          <div className="main-actions">
            <button className="btn">▦ Columns</button>
            <button className="btn primary">↧ Export</button>
          </div>
        </div>
        <div className="chips">
          {VERDICTS.map((v) => (
            <div key={v || 'all'} className={'chip' + (filter === v ? ' active' : '')} onClick={() => setFilter(v)}>
              {VLABEL[v]}
            </div>
          ))}
        </div>
      </div>

      {/* headline stat strip — the proof asset, up front */}
      <div className="statstrip">
        <div className="statcard"><div className="sl">Honest hit rate</div><div className="sv good">{hit.toFixed(1)}%</div><div className="sf">LED ÷ all resolved (misses counted)</div></div>
        <div className="statcard"><div className="sl">Median lead time</div><div className="sv early">{med}d</div><div className="sf">days ahead of Google Trends breakout</div></div>
        <div className="statcard"><div className="sl">Max lead</div><div className="sv det">{summary?.maxLead ?? 0}d</div><div className="sf">best documented early call</div></div>
        <div className="statcard"><div className="sl">Led / Same / Lagged / FP</div><div className="sv">{summary?.led ?? 0}/{summary?.sameDay ?? 0}/{summary?.lagged ?? 0}/{summary?.falsePositives ?? 0}</div><div className="sf">outcome breakdown</div></div>
        <div className="statcard"><div className="sl">Resolved · pending</div><div className="sv">{resolved}·{summary?.pending ?? 0}</div><div className="sf">{summary?.smallSample ? 'small sample — interpret with care' : 'sample sufficient'}</div></div>
      </div>

      <div className="grid-wrap">
        {loading ? (
          <div className="center-state"><div className="spinner" />Loading the ledger…</div>
        ) : err ? (
          <div className="center-state">Could not load the ledger.<div className="muted">{err}</div></div>
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
