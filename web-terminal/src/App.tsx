import { useEffect, useState, type ReactNode } from 'react'
import { Shell, type NavKey } from './components/Shell'
import { Ledger } from './views/Ledger'
import { Screener } from './views/Screener'
import { MarketSignal } from './views/MarketSignal'
import { Methodology } from './views/Methodology'
import { Login } from './views/Login'
import { fetchMe, logout, type User } from './lib/auth'

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
  const [nav, setNav] = useState<NavKey>('trends')
  const [rail, setRail] = useState<ReactNode | null>(null)

  // Enterprise-only web build: a restored session must be Enterprise tier, else
  // clear it (Consumer/Business belong on the mobile app). The Login screen
  // enforces the same gate on sign-in.
  useEffect(() => {
    fetchMe().then((u) => {
      if (u && u.tier !== 'enterprise') { logout(); u = null }
      setUser(u); setBooting(false)
    })
  }, [])

  if (booting) {
    return <div style={{ display: 'grid', placeItems: 'center', height: '100vh' }}><div className="spinner" /></div>
  }
  if (!user) return <Login onAuthed={setUser} />

  const go = (k: NavKey) => { setRail(null); setNav(k) }
  const signOut = () => { logout(); setUser(null) }

  let body: ReactNode
  if (nav === 'trends') body = <Screener onRail={setRail} />
  else if (nav === 'market') body = <MarketSignal onRail={setRail} />
  else if (nav === 'ledger') body = <Ledger />
  else if (nav === 'methodology') body = <Methodology />
  else body = <Placeholder title={titleFor(nav)} />

  return (
    <Shell nav={nav} onNav={go} rail={nav === 'trends' || nav === 'market' ? rail : null} user={user} onSignOut={signOut}>
      {body}
    </Shell>
  )
}

function titleFor(k: NavKey): string {
  return ({
    dashboard: 'Dashboard', trends: 'Signal Screener', market: 'Market Signal',
    grade: 'Grade', watchlists: 'Watchlists', alerts: 'Alerts',
    ledger: 'Accuracy Ledger', methodology: 'Methodology',
  } as Record<NavKey, string>)[k]
}
