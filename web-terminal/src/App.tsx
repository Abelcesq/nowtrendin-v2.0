import { useEffect, useState, type ReactNode } from 'react'
import { Shell, type NavKey } from './components/Shell'
import { Ledger } from './views/Ledger'
import { Screener } from './views/Screener'
import { MarketSignal } from './views/MarketSignal'
import { Watchlists } from './views/Watchlists'
import { Methodology } from './views/Methodology'
import { Account } from './views/Account'
import { Grade } from './views/Grade'
import { Dashboard } from './views/Dashboard'
import { Alerts } from './views/Alerts'
import { History } from './views/History'
import { Login } from './views/Login'
import { fetchMe, logout, listWatchlists, type User } from './lib/auth'
import { api } from './lib/api'

function Placeholder({ title }: { title: string }) {
  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">{title}</div>
          <div className="main-sub">Coming next in the institutional build.</div>
        </div>
      </div>
      <div className="center-state">
        {title} view is queued.
        <div className="muted">Shipped: Signal Screener · Accuracy Ledger · Auth. Next: Market Signal, Grade, Watchlists, Methodology.</div>
      </div>
    </>
  )
}

export function App() {
  const [user, setUser] = useState<User | null>(null)
  const [booting, setBooting] = useState(true)
  const [nav, setNav] = useState<NavKey>('dashboard')   // land on the at-a-glance dashboard
  const [rail, setRail] = useState<ReactNode | null>(null)
  const [q, setQ] = useState('')   // top-bar search → filters the Trends grid
  const [account, setAccount] = useState(false)   // avatar → account view
  // Saved-screen click → jump to Trends with a preset filter (nonce so re-clicking
  // the same screen re-applies even after navigating away).
  const [screen, setScreen] = useState<{ filter: string; n: number } | null>(null)
  const [counts, setCounts] = useState<{ early?: number; breakout?: number; watchlist?: number }>({})

  // Enterprise-only web build: a restored session must be Enterprise tier, else
  // clear it (Consumer/Business belong on the mobile app). The Login screen
  // enforces the same gate on sign-in.
  useEffect(() => {
    fetchMe().then((u) => {
      if (u && u.tier !== 'enterprise') { logout(); u = null }
      setUser(u); setBooting(false)
    })
  }, [])

  // Live counts for the Saved Screens (so the section reflects real activity, not
  // hardcoded numbers). Buckets match the Screener's filter tests.
  useEffect(() => {
    if (!user) return
    api.topics(200).then((t) => {
      let early = 0, breakout = 0
      for (const x of (t.topics || [])) {
        const d = Math.round(x.detection_score ?? 0)
        if (d >= 85) breakout++
        else if (d >= 55 && d < 70) early++
      }
      setCounts((c) => ({ ...c, early, breakout }))
    }).catch(() => {})
    listWatchlists().then((ws) => {
      const n = (ws || []).reduce((a: number, w: any) => a + (w.items?.length || 0), 0)
      setCounts((c) => ({ ...c, watchlist: n }))
    }).catch(() => {})
  }, [user])

  if (booting) {
    return <div style={{ display: 'grid', placeItems: 'center', height: '100vh' }}><div className="spinner" /></div>
  }
  if (!user) return <Login onAuthed={setUser} />

  const go = (k: NavKey) => { setRail(null); setAccount(false); setNav(k) }
  const onScreen = (filter: string) => { setRail(null); setAccount(false); setNav('trends'); setScreen((s) => ({ filter, n: (s?.n ?? 0) + 1 })) }
  const signOut = () => { logout(); setUser(null) }

  let body: ReactNode
  if (account) body = <Account user={user} onSignOut={signOut} onClose={() => setAccount(false)} onUserUpdate={setUser} />
  else if (nav === 'dashboard') body = <Dashboard onNav={go} />
  else if (nav === 'trends') body = <Screener onRail={setRail} query={q} preset={screen} />
  else if (nav === 'market') body = <MarketSignal onRail={setRail} />
  else if (nav === 'watchlists') body = <Watchlists />
  else if (nav === 'grade') body = <Grade user={user} onUser={setUser} />
  else if (nav === 'ledger') body = <Ledger />
  else if (nav === 'alerts') body = <Alerts />
  else if (nav === 'history') body = <History />
  else if (nav === 'methodology') body = <Methodology />
  else body = <Placeholder title={titleFor(nav)} />

  return (
    <Shell nav={nav} onNav={go} rail={!account && (nav === 'trends' || nav === 'market') ? rail : null}
      user={user} onSignOut={signOut} onAccount={() => { setRail(null); setAccount(true) }}
      search={q} onSearch={setQ} alertCount={0} onScreen={onScreen} screenCounts={counts}>
      {body}
    </Shell>
  )
}

function titleFor(k: NavKey): string {
  return ({
    dashboard: 'Dashboard', trends: 'Signal Screener', market: 'Market Signal',
    grade: 'Grade', watchlists: 'Watchlists', alerts: 'Alerts', history: 'History',
    ledger: 'Accuracy Ledger', methodology: 'Methodology',
  } as Record<NavKey, string>)[k]
}
