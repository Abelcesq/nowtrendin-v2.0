import { useEffect, useState, type ReactNode } from 'react'
import { Shell, type NavKey } from './components/Shell'
import { Ledger } from './views/Ledger'
import { Screener } from './views/Screener'
import { MarketSignal } from './views/MarketSignal'
import { Watchlists } from './views/Watchlists'
import { Methodology } from './views/Methodology'
import { Account } from './views/Account'
import { Grade } from './views/Grade'
import { Crypto } from './views/Crypto'
import { Dashboard } from './views/Dashboard'
import { Alerts } from './views/Alerts'
import { History } from './views/History'
import { Login } from './views/Login'
import { fetchMe, logout, getDashboard, saveFavorites, type User, type Favorite } from './lib/auth'

const DEFAULT_FAVORITES: Favorite[] = [
  { id: 'f_break', label: 'Breakouts', section: 'trends', filter: 'breakout', color: 'var(--bk-t)' },
  { id: 'f_anom', label: 'Anomalies', section: 'trends', filter: 'anomalies', color: '#6B4FA0' },
  { id: 'f_elev', label: 'Elevated risk', section: 'market', filter: 'elevated', color: 'var(--down)' },
]

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
  // Favorite click → jump to its section with the filter applied (nonce so
  // re-clicking re-applies even after navigating away).
  const [screen, setScreen] = useState<{ filter: string; n: number } | null>(null)
  const [marketScreen, setMarketScreen] = useState<{ filter: string; n: number } | null>(null)
  // Open a SPECIFIC entity's detail rail (from a favorite / watchlist / alert /
  // history click) — nonce-keyed so re-opening the same one re-fires.
  const [trendFocus, setTrendFocus] = useState<{ key: string; display: string; n: number } | null>(null)
  const [marketFocus, setMarketFocus] = useState<{ key: string; display: string; n: number } | null>(null)
  const [favorites, setFavorites] = useState<Favorite[]>(DEFAULT_FAVORITES)
  const [historyInitQ, setHistoryInitQ] = useState('')
  const [historyNavKey, setHistoryNavKey] = useState(0)

  // Enterprise-only web build: a restored session must be Enterprise tier, else
  // clear it (Consumer/Business belong on the mobile app). The Login screen
  // enforces the same gate on sign-in.
  useEffect(() => {
    fetchMe().then((u) => {
      if (u && u.tier !== 'enterprise') { logout(); u = null }
      setUser(u); setBooting(false)
    })
  }, [])

  // Load the member's saved Favorites (falls back to sensible defaults).
  useEffect(() => {
    if (!user) return
    getDashboard().then((d) => { if (d.favorites && d.favorites.length) setFavorites(d.favorites) }).catch(() => {})
  }, [user])

  if (booting) {
    return <div style={{ display: 'grid', placeItems: 'center', height: '100vh' }}><div className="spinner" /></div>
  }
  if (!user) return <Login onAuthed={setUser} />

  const go = (k: NavKey) => { setRail(null); setAccount(false); setNav(k); if (k === 'history') setHistoryNavKey((n) => n + 1) }
  const signOut = () => { logout(); setUser(null) }
  // Open a specific entity's detail rail. Trends → Screener focus; market →
  // MarketSignal focus. The view auto-opens the matching row's rail once loaded.
  const openDetail = (key: string, kind: 'topic' | 'market' = 'topic', display = key) => {
    setRail(null); setAccount(false)
    if (kind === 'market') { setNav('market'); setMarketFocus((s) => ({ key, display, n: (s?.n ?? 0) + 1 })) }
    else { setNav('trends'); setTrendFocus((s) => ({ key, display, n: (s?.n ?? 0) + 1 })) }
  }
  const onFav = (f: Favorite) => {
    setRail(null); setAccount(false)
    // A "Track topic" favorite pins a specific HISTORY topic — clicking it opens the
    // History section with that topic pre-filtered (so the user lands on its scoring
    // trajectory). Track-topic = History only; the Trends/Market sections are saved
    // filter-views. (Filter by display label — History matches display OR key, and
    // falls back to a direct score lookup for topics below the top-list cutoff.)
    if (f.section === 'history') { setTrendFocus(null); setMarketFocus(null); setHistoryInitQ(f.label); setNav('history'); setHistoryNavKey((n) => n + 1) }
    else if (f.section === 'market') { setTrendFocus(null); setMarketFocus(null); setNav('market'); setMarketScreen((s) => ({ filter: f.filter || 'all', n: (s?.n ?? 0) + 1 })) }
    else if (f.section === 'watchlist') setNav('watchlists')
    else { setTrendFocus(null); setMarketFocus(null); setNav('trends'); setScreen((s) => ({ filter: f.filter || 'all', n: (s?.n ?? 0) + 1 })) }
  }
  const onFavChange = (next: Favorite[]) => { setFavorites(next); saveFavorites(next).catch(() => {}) }

  let body: ReactNode
  const onNavHistory = (q: string) => { go('history'); setHistoryInitQ(q) }

  if (account) body = <Account user={user} onSignOut={signOut} onClose={() => setAccount(false)} onUserUpdate={setUser} />
  else if (nav === 'dashboard') body = <Dashboard onNav={go} onNavHistory={onNavHistory} />
  else if (nav === 'trends') body = <Screener onRail={setRail} query={q} preset={screen} focus={trendFocus} />
  else if (nav === 'market') body = <MarketSignal onRail={setRail} preset={marketScreen} focus={marketFocus} />
  else if (nav === 'watchlists') body = <Watchlists onOpenDetail={openDetail} />
  else if (nav === 'grade') body = <Grade user={user} onUser={setUser} />
  else if (nav === 'crypto') body = <Crypto onRail={setRail} />
  else if (nav === 'ledger') body = <Ledger />
  else if (nav === 'alerts') body = <Alerts onOpenDetail={openDetail} />
  else if (nav === 'history') body = <History key={historyNavKey} initialQ={historyInitQ} />
  else if (nav === 'methodology') body = <Methodology />
  else body = <Placeholder title={titleFor(nav)} />

  return (
    <Shell nav={nav} onNav={go} rail={!account && (nav === 'trends' || nav === 'market' || nav === 'crypto') ? rail : null}
      user={user} onSignOut={signOut} onAccount={() => { setRail(null); setAccount(true) }}
      search={q} onSearch={setQ} alertCount={0} favorites={favorites} onFav={onFav} onFavChange={onFavChange}>
      {body}
    </Shell>
  )
}

function titleFor(k: NavKey): string {
  return ({
    dashboard: 'Dashboard', trends: 'Signal Screener', market: 'Market Signal',
    crypto: 'Crypto', grade: 'Grade', watchlists: 'Watchlists', alerts: 'Alerts', history: 'History',
    ledger: 'Accuracy Ledger', methodology: 'Methodology',
  } as Record<NavKey, string>)[k]
}
