import { useState } from 'react'
import { login, logout, type User } from '../lib/auth'

// ── gap micro-viz — identical semantics to the terminal grid (det•conf dots,
// amber connector when the gap is wide). The signature mark tying login to the
// product. ──
function GapMicro({ det, conf }: { det: number; conf: number }) {
  const lo = Math.min(det, conf), hi = Math.max(det, conf), W = 78
  const x = (v: number) => 4 + (v / 100) * (W - 8)
  const wide = Math.abs(det - conf) >= 20
  const col = wide ? '#E8551C' : '#6F7FA8'
  return (
    <svg width={W} height="16" viewBox={`0 0 ${W} 16`} aria-hidden="true">
      <line x1={x(lo)} y1="8" x2={x(hi)} y2="8" stroke={col} strokeWidth={wide ? 2.5 : 1.5} />
      <circle cx={x(det)} cy="8" r="3.2" fill="#2A5B9E" />
      <circle cx={x(conf)} cy="8" r="3.2" fill="#2E7D5B" />
    </svg>
  )
}

// Illustrative sample for the value panel — clearly labelled "Illustrative" (NOT
// "Live"), and it makes NO performance claims. Real top-widest-gap /scores +
// honest, denominator-backed ledger numbers get wired in once the ledger matures.
const SAMPLE = [
  { name: 'neuromorphic inference', cat: 'ML Research', det: 69, conf: 31, stage: 'early', label: 'Early signal' },
  { name: 'world models', cat: 'ML Research', det: 72, conf: 41, stage: 'early', label: 'Early signal' },
  { name: 'RISC-V datacenter', cat: 'AI Infra', det: 66, conf: 44, stage: 'early', label: 'Early signal' },
  { name: 'agentic coding', cat: 'Dev Tools', det: 95, conf: 93, stage: 'aligned', label: 'Aligned' },
]

const EyeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" /><circle cx="12" cy="12" r="3" />
  </svg>
)
const EyeOffIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M2 2l20 20" /><path d="M6.7 6.7C3.6 8.6 1 12 1 12s4 7 11 7c2 0 3.8-.5 5.3-1.3" />
    <path d="M9.9 5.2A11 11 0 0 1 12 5c7 0 11 7 11 7a18 18 0 0 1-3.2 4" />
  </svg>
)

export function Login({ onAuthed }: { onAuthed: (u: User) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [remember, setRemember] = useState(false)
  const [busy, setBusy] = useState(false)
  const [ok, setOk] = useState(false)
  const [emailErr, setEmailErr] = useState('')
  const [pwErr, setPwErr] = useState('')
  const [formErr, setFormErr] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailErr(''); setPwErr(''); setFormErr('')
    const em = email.trim()
    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)
    let bad = false
    if (!em) { setEmailErr('Enter your work email.'); bad = true }
    else if (!emailOk) { setEmailErr('Enter a valid email address.'); bad = true }
    if (!password) { setPwErr('Enter your password.'); bad = true }
    if (bad) return

    setBusy(true)
    try {
      const u = await login(em, password)
      // ── Enterprise-only web build. The institutional terminal is for Enterprise
      // clients; Consumer & Business members use the Now TrendIn mobile app. The
      // backend/engine remain the source of truth for entitlements — this gate is
      // the front door. ──
      if (u.tier !== 'enterprise') {
        logout()
        setBusy(false)
        setFormErr('This terminal is for Enterprise clients. Consumer and Business members — please use the Now TrendIn mobile app.')
        return
      }
      setOk(true)
      setTimeout(() => onAuthed(u), 450) // brief "Verified" state, then route in
    } catch (e: any) {
      setBusy(false)
      setPwErr(e?.data?.detail || e?.message || "Those credentials didn't match. Try again.")
    }
  }

  return (
    <div className="lg">
      {/* ============ LEFT: SIGN-IN ============ */}
      <section className="lg-auth">
        <a className="lg-brand" href="#" aria-label="Now TrendIn home">
          <svg className="lg-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect width="32" height="32" rx="7" fill="#0C1B3A" />
            <path d="M9 21c2-1 3-3 3-6 1 2 2 3 4 3 0-3 1-5 3-7-1 5 4 6 4 10 0 3-3 5-7 5s-8-2-7-6 1-3 0-5z" fill="#E8551C" />
            <path d="M19 9l4-3-1 5z" fill="#2A5B9E" />
          </svg>
          <div>
            <div className="lg-name">Now<b>TrendIn</b></div>
            <div className="lg-tag">Attention Intelligence</div>
          </div>
        </a>

        <form className="lg-body" onSubmit={submit} noValidate>
          <h1>Sign in to your terminal</h1>
          <p className="lg-sub">Institutional access to the Gradient Score engine — Enterprise clients.</p>

          <div className={`lg-field${emailErr ? ' err' : ''}`}>
            <label htmlFor="lg-email">Work email</label>
            <div className="lg-wrap">
              <input id="lg-email" type="email" inputMode="email" autoComplete="username"
                placeholder="you@firm.com" value={email}
                onChange={(e) => { setEmail(e.target.value); if (emailErr) setEmailErr('') }} />
            </div>
            <div className="lg-msg">{emailErr}</div>
          </div>

          <div className={`lg-field${pwErr ? ' err' : ''}`}>
            <label htmlFor="lg-pw">Password</label>
            <div className="lg-wrap">
              <input id="lg-pw" type={showPw ? 'text' : 'password'} autoComplete="current-password"
                placeholder="••••••••••" value={password}
                onChange={(e) => { setPassword(e.target.value); if (pwErr) setPwErr('') }} />
              <button type="button" className="lg-pw-btn" onClick={() => setShowPw((v) => !v)}
                aria-label={showPw ? 'Hide password' : 'Show password'}>
                {showPw ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
            <div className="lg-msg">{pwErr}</div>
          </div>

          <div className="lg-rowb">
            <label className="lg-rem">
              <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
              <span className="lg-check">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5"><path d="M5 13l4 4L19 7" /></svg>
              </span>
              Remember this device
            </label>
            <a className="lg-link" href="#">Forgot password?</a>
          </div>

          {formErr && <div className="lg-err">{formErr}</div>}

          <button type="submit" className={`lg-btn${ok ? ' ok' : ''}`} disabled={busy} style={{ marginTop: 12 }}>
            {busy && !ok && <span className="lg-spin" />}
            {ok ? 'Verified — opening terminal' : busy ? 'Authenticating' : 'Sign in'}
          </button>
        </form>

        <div className="lg-foot">
          {/* Enterprise is sales-led — no self-serve signup on this build.
              Update the mailto to the real sales alias before launch. */}
          <span className="req">Enterprise access only.</span>{' '}
          <a className="lg-link" href="mailto:enterprise@nowtrendin.com?subject=Terminal%20access%20request">Request access</a>
          <div className="lg-legal">
            By signing in you agree that all Gradient Scores, analyses, and signal data are
            proprietary to Now TrendIn LLC.{' '}
            <a href="https://nowtrendin.com/terms/" target="_blank" rel="noopener noreferrer">Terms</a> ·{' '}
            <a href="https://nowtrendin.com/privacy/" target="_blank" rel="noopener noreferrer">Privacy</a> ·{' '}
            <a href="https://nowtrendin.com/disclaimer/" target="_blank" rel="noopener noreferrer">Disclaimer</a>
          </div>
        </div>
      </section>

      {/* ============ RIGHT: THE INSTRUMENT ============ */}
      <section className="lg-value">
        <div className="lg-vin">
          <div className="lg-veb eyebrow">The Gradient Score</div>
          <h2 className="lg-vh">The first instrument that measures where human attention is moving <em>before it arrives.</em></h2>
          <p className="lg-vs">Two scores per topic. Detection reads the early signal; Confidence reads the confirmation. The gap between them is how early you are.</p>

          <div className="lg-demo" aria-label="Illustrative signal sample">
            <div className="lg-dh">
              <span className="t">Early signals · widest gap</span>
              <span className="s">Illustrative</span>
            </div>
            {SAMPLE.map((r) => {
              const gap = r.det - r.conf, wide = Math.abs(gap) >= 20
              return (
                <div className="lg-srow" key={r.name}>
                  <div><div className="nm">{r.name}</div><div className="ct">{r.cat}</div></div>
                  <div className="lg-gv"><GapMicro det={r.det} conf={r.conf} /><span className={`lg-gn${wide ? ' wide' : ''}`}>{gap > 0 ? '+' : ''}{gap}</span></div>
                  <span className={`lg-stg ${r.stage}`}>{r.label}</span>
                </div>
              )
            })}
            <div className="lg-leg">
              <span><span className="lg-dot det" /> Detection</span>
              <span><span className="lg-dot conf" /> Confidence</span>
              <span className="gk">gap = lead time</span>
            </div>
          </div>
        </div>

        <div className="lg-vfoot">
          <span>Measurement, not investment advice.</span>
          <span className="sep">|</span>
          <span className="src">Sources: GitHub · Hacker News · GDELT · news wires · Finnhub</span>
          <span className="sep">|</span>
          <span className="src">Engine v2.0</span>
        </div>
      </section>
    </div>
  )
}
