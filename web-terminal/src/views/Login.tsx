import { useState } from 'react'
import { login, type User } from '../lib/auth'

export function Login({ onAuthed }: { onAuthed: (u: User) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true); setErr(null)
    try { onAuthed(await login(email.trim(), password)) }
    catch (e: any) { setErr(e?.data?.detail || e?.message || 'Sign-in failed. Check your credentials.') }
    finally { setBusy(false) }
  }

  return (
    <div className="login">
      {/* Left: sign-in */}
      <div className="login-left">
        <div className="login-brand">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="7" fill="#13233a" />
            <path d="M9 21c2-1 3-3 3-6 1 2 2 3 4 3 0-3 1-5 3-7-1 5 4 6 4 10 0 3-3 5-7 5s-8-2-7-6 1-3 0-5z" fill="#df7a36" />
            <path d="M19 9l4-3-1 5z" fill="#2f6fed" />
          </svg>
          <div><div className="lb-name">Now<b>TrendIn</b></div><div className="lb-tag">Attention Intelligence Terminal</div></div>
        </div>

        <div className="login-form-wrap">
          <h1 className="login-h1">Sign in</h1>
          <p className="login-sub">Institutional access to the attention-intelligence terminal.</p>

          <form onSubmit={submit}>
            <label className="fld-label">Email</label>
            <input className="fld" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@fund.com" required />
            <label className="fld-label">Password</label>
            <input className="fld" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
            {err && <div className="login-err">{err}</div>}
            <button className="login-btn" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign In'}</button>
          </form>

          <div className="login-or"><span>or</span></div>
          <button className="login-google" onClick={() => setErr('Google sign-in for web is provisioned at deploy (web client ID). Use email + password for now.')}>
            Continue with Google
          </button>

          <p className="login-foot">Measurement, not investment advice. © Now TrendIn LLC.</p>
        </div>
      </div>

      {/* Right: value proposition */}
      <div className="login-right">
        <div className="lr-inner">
          <div className="lr-eyebrow">THE INSTRUMENT</div>
          <h2 className="lr-h2">Measure where attention is moving — before it arrives.</h2>
          <ul className="lr-list">
            <li><b>Dual-score detection.</b> Early-signal Detection vs. confirmed Confidence — the gap is the lead time.</li>
            <li><b>Diffusion-calibrated.</b> Baseline-relative scoring separates a genuine breakout from a household name's ambient noise.</li>
            <li><b>Auditable track record.</b> A timestamped Accuracy Ledger — documented lead time vs. observed breakouts.</li>
            <li><b>Screen &amp; export.</b> Sortable signal grid, saved screens, technical history, CSV/API.</li>
          </ul>
          <div className="lr-stat-row">
            <div className="lr-stat"><div className="lr-sv">200+</div><div className="lr-sl">topics scored / cycle</div></div>
            <div className="lr-stat"><div className="lr-sv">12+</div><div className="lr-sl">independent sources</div></div>
            <div className="lr-stat"><div className="lr-sv">6h</div><div className="lr-sl">scan cadence</div></div>
          </div>
        </div>
      </div>
    </div>
  )
}
