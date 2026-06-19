import { useState } from 'react'
import { TIER_LABEL, updateProfile, changePassword, updateNotifyPrefs, sendPhoneCode, verifyPhone, type User } from '../lib/auth'

// Plan pricing (authority: constants/tiers.ts / CLAUDE.md §6). Billing is a UI
// shell — Stripe is deferred; "Manage billing" activates when Stripe lands.
const PLAN_PRICE: Record<string, number> = { consumer: 49, business: 499, enterprise: 250_000 }

// Account — the web equivalent of the mobile Profile flow (edit profile, change
// password, etc.). The one web-specific difference: "Membership" is replaced by
// "Authorized Users" (the Enterprise account is multi-seat), and the account
// admin is identified. Edit Profile + Change Password hit the SAME Django
// endpoints the mobile app uses, so changes sync across every surface.

// Enterprise entitlement (authority: constants/tiers.ts / CLAUDE.md §6):
// up to 5 users under one account share a single 100,000 query-token pool.
const ENT_SEATS = 5
const ENT_TOKEN_POOL = 100_000

const card: React.CSSProperties = {
  background: 'var(--surface)', border: '1px solid var(--line)',
  borderRadius: 12, padding: 18, marginBottom: 16,
}
const lbl: React.CSSProperties = {
  fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
  color: 'var(--text-3)', marginBottom: 10,
}
const inp: React.CSSProperties = {
  width: '100%', height: 40, padding: '0 12px', marginBottom: 10,
  border: '1px solid var(--line)', borderRadius: 8, fontSize: 13,
  color: 'var(--text)', background: 'var(--canvas)', boxSizing: 'border-box',
}
const btn: React.CSSProperties = {
  height: 38, padding: '0 18px', border: 'none', borderRadius: 8,
  background: 'var(--det)', color: '#fff', fontWeight: 700, fontSize: 13, cursor: 'pointer',
}
const btnGhost: React.CSSProperties = {
  ...btn, background: 'transparent', color: 'var(--det)', border: '1px solid var(--det)',
}

function Msg({ m }: { m: { ok: boolean; text: string } | null }) {
  if (!m) return null
  return <div style={{ fontSize: 12.5, marginTop: 6, color: m.ok ? 'var(--conf)' : 'var(--down)' }}>
    {m.ok ? '✓ ' : '• '}{m.text}</div>
}

export function Account({ user, onSignOut, onClose, onUserUpdate }: {
  user: User
  onSignOut: () => void
  onClose: () => void
  onUserUpdate: (u: User) => void
}) {
  const initials = (user.name || user.email || 'NT').split(/[\s@.]+/).filter(Boolean)
    .slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'NT'
  const plan = user.tier ? TIER_LABEL[user.tier].toUpperCase() : 'GUEST'
  const isEnterprise = user.tier === 'enterprise'

  // edit profile
  const [name, setName] = useState(user.name ?? '')
  const [email, setEmail] = useState(user.email ?? '')
  const [savingP, setSavingP] = useState(false)
  const [pMsg, setPMsg] = useState<{ ok: boolean; text: string } | null>(null)
  const saveProfile = async () => {
    setPMsg(null); setSavingP(true)
    try {
      const u = await updateProfile({ name: name.trim(), email: email.trim() })
      onUserUpdate(u); setPMsg({ ok: true, text: 'Profile updated.' })
    } catch (e: any) {
      setPMsg({ ok: false, text: e?.data?.email?.[0] ?? e?.data?.detail ?? 'Could not update profile.' })
    } finally { setSavingP(false) }
  }

  // change password
  const [cur, setCur] = useState(''); const [nw, setNw] = useState(''); const [cf, setCf] = useState('')
  const [savingPw, setSavingPw] = useState(false)
  const [pwMsg, setPwMsg] = useState<{ ok: boolean; text: string } | null>(null)
  const savePw = async () => {
    setPwMsg(null)
    if (nw.length < 8) return setPwMsg({ ok: false, text: 'New password must be at least 8 characters.' })
    if (nw !== cf) return setPwMsg({ ok: false, text: "Passwords don't match." })
    setSavingPw(true)
    try {
      await changePassword(cur, nw)
      setCur(''); setNw(''); setCf(''); setPwMsg({ ok: true, text: 'Password updated.' })
    } catch (e: any) {
      setPwMsg({ ok: false, text: e?.data?.detail ?? 'Could not change password.' })
    } finally { setSavingPw(false) }
  }

  // notification channels + text-alert phone capture
  const [nEmail, setNEmail] = useState(user.notifyEmail ?? true)
  const [nSms, setNSms] = useState(user.notifySms ?? false)
  const [phone, setPhone] = useState(user.phone ?? '')
  const [verified, setVerified] = useState(user.phoneVerified ?? false)
  const [codeSent, setCodeSent] = useState(false)
  const [code, setCode] = useState('')
  const [nMsg, setNMsg] = useState<{ ok: boolean; text: string } | null>(null)

  const saveChannels = async (next: { notifyEmail?: boolean; notifySms?: boolean }) => {
    setNMsg(null)
    try { const u = await updateNotifyPrefs(next); onUserUpdate(u) }
    catch { setNMsg({ ok: false, text: 'Could not save notification preferences.' }) }
  }
  const onEmailToggle = (v: boolean) => { setNEmail(v); saveChannels({ notifyEmail: v }) }
  const onSmsToggle = (v: boolean) => {
    if (v && !verified) { setNMsg({ ok: false, text: 'Verify a phone number first to enable text alerts.' }); return }
    setNSms(v); saveChannels({ notifySms: v })
  }
  const sendCode = async () => {
    setNMsg(null)
    if (phone.trim().length < 7) { setNMsg({ ok: false, text: 'Enter a valid phone number (with country code).' }); return }
    try { const r = await sendPhoneCode(phone.trim()); setCodeSent(true); setNMsg({ ok: true, text: r.detail || 'Verification code sent.' }) }
    catch (e: any) { setNMsg({ ok: false, text: e?.data?.detail ?? 'Could not send the code. SMS may not be configured yet.' }) }
  }
  const confirmCode = async () => {
    setNMsg(null)
    try {
      const u = await verifyPhone(code.trim())
      onUserUpdate(u); setVerified(true); setCodeSent(false); setCode('')
      setNMsg({ ok: true, text: 'Phone verified. You can now enable text alerts.' })
    } catch (e: any) { setNMsg({ ok: false, text: e?.data?.detail ?? 'Incorrect or expired code.' }) }
  }

  // authorized users — the account admin is the signed-in account holder. Seats
  // beyond the admin are shown as available; we do NOT fabricate other users.
  const used = Math.max(0, ENT_TOKEN_POOL - (user.tokensRemaining ?? 0))
  const usedPct = Math.min(100, Math.round((used / ENT_TOKEN_POOL) * 100))

  return (
    <>
      <div className="main-head" style={{ paddingBottom: 0 }}>
        <div className="main-title-row">
          <div className="main-title">Account</div>
          <div className="main-sub">Profile, security, and authorized users · synced across your devices</div>
        </div>
        <div className="wl-tabs">
          <div className="wl-tab" onClick={onClose}>← Back to terminal</div>
        </div>
      </div>

      <div className="grid-wrap" style={{ maxWidth: 720 }}>
        {/* Identity */}
        <div style={{ ...card, display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 54, height: 54, borderRadius: '50%', background: 'var(--det)', color: '#fff',
            display: 'grid', placeItems: 'center', fontWeight: 800, fontSize: 18, flexShrink: 0,
          }}>{initials}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 17, fontWeight: 800, color: 'var(--text)' }}>{user.name || 'Member'}</div>
            <div style={{ fontSize: 13, color: 'var(--text-2)' }}>{user.email}</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span style={{ fontSize: 11, fontWeight: 800, padding: '4px 9px', borderRadius: 6, background: 'var(--conf-soft)', color: 'var(--conf)' }}>ADMIN</span>
            <span style={{ fontSize: 11, fontWeight: 800, padding: '4px 9px', borderRadius: 6, background: 'var(--ink-2)', color: '#fff' }}>{plan}</span>
          </div>
        </div>

        {/* Edit Profile */}
        <div style={card}>
          <div style={lbl}>Edit Profile</div>
          <input style={inp} value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" />
          <input style={inp} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email address" type="email" />
          <button style={btn} onClick={saveProfile} disabled={savingP}>{savingP ? 'Saving…' : 'Save Changes'}</button>
          <Msg m={pMsg} />
        </div>

        {/* Change Password */}
        <div style={card}>
          <div style={lbl}>Change Password</div>
          <input style={inp} value={cur} onChange={(e) => setCur(e.target.value)} placeholder="Current password" type="password" />
          <input style={inp} value={nw} onChange={(e) => setNw(e.target.value)} placeholder="New password (min 8 chars)" type="password" />
          <input style={inp} value={cf} onChange={(e) => setCf(e.target.value)} placeholder="Confirm new password" type="password" />
          <button style={btnGhost} onClick={savePw} disabled={savingPw}>{savingPw ? 'Updating…' : 'Update Password'}</button>
          <Msg m={pwMsg} />
        </div>

        {/* Notifications + Text Alerts (phone capture) */}
        <div style={card}>
          <div style={lbl}>Notifications</div>
          <div style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 12 }}>
            Choose how your alert and watchlist notifications are delivered.
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10, fontSize: 13, color: 'var(--text)', cursor: 'pointer' }}>
            <input type="checkbox" checked={nEmail} onChange={(e) => onEmailToggle(e.target.checked)} />
            Email — alerts and account updates by email
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text)', cursor: verified ? 'pointer' : 'not-allowed', opacity: verified ? 1 : 0.6 }}>
            <input type="checkbox" checked={nSms} disabled={!verified} onChange={(e) => onSmsToggle(e.target.checked)} />
            Text (SMS) — alerts to your verified phone
          </label>

          <div style={{ borderTop: '1px solid var(--line-2)', margin: '14px 0' }} />
          <div style={lbl}>Cell phone for text alerts</div>
          {verified ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text)' }}>
              <span style={{ fontWeight: 700 }}>{phone}</span>
              <span style={{ fontSize: 11, fontWeight: 800, padding: '3px 8px', borderRadius: 5, background: 'var(--conf-soft)', color: 'var(--conf)' }}>VERIFIED</span>
              <button style={{ ...btnGhost, height: 30, padding: '0 12px', fontSize: 12 }} onClick={() => { setVerified(false); setCodeSent(false) }}>Change</button>
            </div>
          ) : (
            <>
              <input style={inp} value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+1 555 123 4567" type="tel" />
              {!codeSent ? (
                <button style={btn} onClick={sendCode}>Send verification code</button>
              ) : (
                <div style={{ display: 'flex', gap: 8 }}>
                  <input style={{ ...inp, marginBottom: 0, width: 140 }} value={code} onChange={(e) => setCode(e.target.value)} placeholder="6-digit code" inputMode="numeric" />
                  <button style={btn} onClick={confirmCode}>Verify</button>
                  <button style={btnGhost} onClick={sendCode}>Resend</button>
                </div>
              )}
            </>
          )}
          <Msg m={nMsg} />
          <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 8 }}>
            Standard message rates may apply. We only text a phone you've verified.
          </div>
        </div>

        {/* Billing (UI shell — Stripe deferred) */}
        <div style={card}>
          <div style={lbl}>Billing</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
            <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text)' }}>{plan} Plan</span>
            <span style={{ fontSize: 22, fontWeight: 900, color: 'var(--text)' }}>
              ${(PLAN_PRICE[user.tier ?? 'consumer'] ?? 0).toLocaleString()}
              <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-3)' }}>/mo</span>
            </span>
          </div>
          <div style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 14 }}>
            Your plan renews monthly. Payment management arrives with the upcoming billing release.
          </div>
          <button style={{ ...btnGhost, cursor: 'default', opacity: 0.55 }} disabled>Manage billing — coming soon</button>
        </div>

        {/* Authorized Users (replaces Membership on web) */}
        <div style={card}>
          <div style={lbl}>Authorized Users</div>
          {isEnterprise ? (
            <>
              <div style={{ fontSize: 13, color: 'var(--text-2)', marginBottom: 14 }}>
                Enterprise — up to <b style={{ color: 'var(--text)' }}>{ENT_SEATS} authorized users</b> under one
                account, sharing a single pool of <b style={{ color: 'var(--text)' }}>{ENT_TOKEN_POOL.toLocaleString()} query tokens</b> per month.
              </div>

              {/* Shared token pool */}
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-2)', marginBottom: 6 }}>
                  <span>Shared query tokens</span>
                  <span><b style={{ color: 'var(--text)' }}>{(user.tokensRemaining ?? 0).toLocaleString()}</b> of {ENT_TOKEN_POOL.toLocaleString()} remaining</span>
                </div>
                <div style={{ height: 8, borderRadius: 4, background: 'var(--line-2)', overflow: 'hidden' }}>
                  <div style={{ width: `${usedPct}%`, height: '100%', background: usedPct > 85 ? 'var(--early)' : 'var(--det)' }} />
                </div>
              </div>

              {/* Seat roster — admin is real; remaining seats shown as available */}
              <div style={lbl}>Seats · 1 of {ENT_SEATS} used</div>
              <div style={{ border: '1px solid var(--line)', borderRadius: 8, overflow: 'hidden' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', borderBottom: '1px solid var(--line-2)' }}>
                  <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'var(--det)', color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 800, fontSize: 12 }}>{initials}</div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{user.name || user.email}</div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{user.email}</div>
                  </div>
                  <span style={{ fontSize: 10.5, fontWeight: 800, padding: '3px 8px', borderRadius: 5, background: 'var(--conf-soft)', color: 'var(--conf)' }}>ADMIN</span>
                </div>
                {Array.from({ length: ENT_SEATS - 1 }).map((_, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', borderBottom: i < ENT_SEATS - 2 ? '1px solid var(--line-2)' : 'none' }}>
                    <div style={{ width: 30, height: 30, borderRadius: '50%', border: '1px dashed var(--line)', display: 'grid', placeItems: 'center', color: 'var(--text-3)', fontSize: 14 }}>+</div>
                    <div style={{ flex: 1, fontSize: 13, color: 'var(--text-3)' }}>Available seat</div>
                    <span style={{ fontSize: 10.5, fontWeight: 700, color: 'var(--text-3)' }}>OPEN</span>
                  </div>
                ))}
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 10 }}>
                You are the account administrator. Seat provisioning for additional authorized users is
                managed with your account manager.
              </div>
            </>
          ) : (
            <div style={{ fontSize: 13, color: 'var(--text-2)' }}>
              Multi-user authorization is an Enterprise capability. Your current plan is {plan}.
            </div>
          )}
        </div>

        {/* Legal */}
        <div style={card}>
          <div style={lbl}>Legal</div>
          <div style={{ display: 'flex', gap: 18, fontSize: 13 }}>
            <a className="foot-link" href="https://nowtrendin.com/terms/" target="_blank" rel="noopener noreferrer">Terms</a>
            <a className="foot-link" href="https://nowtrendin.com/privacy/" target="_blank" rel="noopener noreferrer">Privacy</a>
            <a className="foot-link" href="https://nowtrendin.com/disclaimer/" target="_blank" rel="noopener noreferrer">Disclaimer</a>
          </div>
        </div>

        {/* Sign out */}
        <button style={{ ...btn, background: 'transparent', color: 'var(--down)', border: '1px solid var(--down)', width: '100%', height: 42, marginBottom: 28 }}
          onClick={onSignOut}>Sign Out</button>
      </div>
    </>
  )
}
