import { useEffect, useState } from 'react'
import { Bell, Trash2, Plus, Minus } from 'lucide-react'
import { api } from '../lib/api'
import { listAlerts, createAlert, updateAlert, removeAlert, type AlertT } from '../lib/auth'

// Web Alerts — same flow + same backend (/api/alerts/) as the mobile app, so an
// alert set here fires for the same member on mobile (UI-consistency mandate §0.6).
const SCORE_TYPES = ['detection', 'confidence', 'overall'] as const

export function Alerts() {
  const [alerts, setAlerts] = useState<AlertT[]>([])
  const [loading, setLoading] = useState(true)
  const [suggest, setSuggest] = useState<{ key: string; display: string }[]>([])
  const [topicDisplay, setTopicDisplay] = useState('')
  const [topicKey, setTopicKey] = useState('')
  const [scoreType, setScoreType] = useState<string>('detection')
  const [threshold, setThreshold] = useState(75)
  const [push, setPush] = useState(true)
  const [email, setEmail] = useState(true)
  const [sms, setSms] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const reload = () => listAlerts().then(setAlerts).catch(() => {})
  useEffect(() => {
    let alive = true
    Promise.all([
      listAlerts().catch(() => [] as AlertT[]),
      api.topics(500).then((t) => (t.topics || []).map((x) => ({ key: x.topic_key, display: x.topic_display || x.topic_key }))).catch(() => []),
    ]).then(([a, s]) => { if (!alive) return; setAlerts(a); setSuggest(s) }).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  // Verified-only: an alert can be created only for a topic that exists in our
  // live data (topicKey is set by picking a match, never by free text).
  const q = topicDisplay.trim().toLowerCase()
  const matches = !topicKey && q.length >= 2
    ? suggest.filter((s) => s.display.toLowerCase().includes(q) || s.key.toLowerCase().includes(q)).slice(0, 8)
    : []

  const bump = (d: number) => setThreshold((t) => Math.max(0, Math.min(100, t + d)))
  const create = async () => {
    if (!topicKey) return  // hard gate — must be a verified topic
    setBusy(true); setErr('')
    try {
      await createAlert({
        topic_key: topicKey,
        topic_display: topicDisplay.trim(), score_type: scoreType, threshold,
        notify_push: push, notify_email: email, notify_sms: sms,
      })
      setTopicDisplay(''); setTopicKey(''); reload()
    } catch (e: any) { setErr(e?.data?.detail || e?.message || 'Could not create alert — please sign in again.') }
    finally { setBusy(false) }
  }
  const toggle = async (a: AlertT) => { try { await updateAlert(a.id, { active: !a.active }); reload() } catch {} }
  const remove = async (a: AlertT) => { try { await removeAlert(a.id); reload() } catch {} }

  return (
    <div className="al">
      <div className="main-head"><div className="main-title-row">
        <div className="main-title">Alerts</div>
        <div className="main-sub">Score-threshold alerts — fire on web, desktop, and mobile</div>
      </div></div>

      <div className="al-sect">Active alerts</div>
      {loading ? <div className="center-state"><div className="spinner" />Loading…</div>
        : alerts.length === 0 ? <div className="al-empty">No alerts yet. Create one below.</div>
          : alerts.map((a) => (
            <div className="al-card" key={a.id}>
              <span className="al-ico"><Bell size={16} color="var(--conf)" /></span>
              <div className="al-body">
                <div className="al-topic">{a.topic_display || a.topic_key}</div>
                <div className="al-meta">When {a.score_type} ≥ {a.threshold} · {[a.notify_push && 'Push', a.notify_email && 'Email', a.notify_sms && 'Text'].filter(Boolean).join(' + ') || 'No channel'}</div>
                {a.last_triggered_at && <div className="al-fired">🔔 Triggered {new Date(a.last_triggered_at).toLocaleDateString()}</div>}
              </div>
              <button className={'al-toggle' + (a.active ? ' on' : '')} onClick={() => toggle(a)} title={a.active ? 'Active' : 'Paused'} />
              <button className="al-del" onClick={() => remove(a)} title="Delete alert"><Trash2 size={16} color="var(--down)" /></button>
            </div>
          ))}

      <div className="al-sect" style={{ marginTop: 18 }}>Create new alert</div>
      <div className="al-form">
        <label className="al-lbl">Topic — search and select a verified topic</label>
        <input className="al-input" value={topicDisplay} placeholder="Type a topic to search…"
          onChange={(e) => { setTopicDisplay(e.target.value); setTopicKey('') }} />
        {topicKey ? (
          <div className="al-verified">✓ {topicDisplay} <button className="al-verified-x" onClick={() => { setTopicKey(''); setTopicDisplay('') }} title="Clear">✕</button></div>
        ) : matches.length > 0 ? (
          <div className="al-chips">{matches.map((s) => (
            <button key={s.key} className="al-chip" onClick={() => { setTopicDisplay(s.display); setTopicKey(s.key) }}>{s.display}</button>
          ))}</div>
        ) : q.length >= 2 ? (
          <div className="al-hint">Not in our database — only existing topics can be alerted on.</div>
        ) : null}

        <label className="al-lbl">Score type</label>
        <div className="al-chips">{SCORE_TYPES.map((st) => (
          <button key={st} className={'al-chip' + (scoreType === st ? ' on' : '')} onClick={() => setScoreType(st)} style={{ textTransform: 'capitalize' }}>{st}</button>
        ))}</div>

        <label className="al-lbl">Alert when score reaches</label>
        <div className="al-step">
          <button onClick={() => bump(-5)} title="−5"><Minus size={16} /></button>
          <span className="al-thr">{threshold}</span>
          <button onClick={() => bump(5)} title="+5"><Plus size={16} /></button>
        </div>

        <div className="al-row"><span>Push notification</span>
          <button className={'al-toggle' + (push ? ' on' : '')} onClick={() => setPush(!push)} /></div>
        <div className="al-row"><span>Email</span>
          <button className={'al-toggle' + (email ? ' on' : '')} onClick={() => setEmail(!email)} /></div>
        <div className="al-row"><span>Text (SMS)<span style={{ color: 'var(--text-3)', fontSize: 11, marginLeft: 6 }}>needs a verified phone (Account)</span></span>
          <button className={'al-toggle' + (sms ? ' on' : '')} onClick={() => setSms(!sms)} /></div>

        {err && <div className="al-err">{err}</div>}
        <button className="al-create" disabled={!topicKey || busy} onClick={create}>{busy ? 'Creating…' : topicKey ? 'Create Alert' : 'Select a topic first'}</button>
      </div>

      <div className="disc" style={{ textAlign: 'center', marginTop: 14 }}>Now TrendIn provides signal analysis for informational purposes only — not financial, investment, or legal advice.</div>
    </div>
  )
}
