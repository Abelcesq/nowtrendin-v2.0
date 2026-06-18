import { useEffect, useState, type ReactNode } from 'react'
import {
  LayoutGrid, TrendingUp, DollarSign, Activity, Star, Bell, CheckCircle, Sparkles,
  Search, type LucideIcon,
} from 'lucide-react'
import { TIER_LABEL, type User } from '../lib/auth'

export type NavKey =
  | 'dashboard' | 'trends' | 'market' | 'grade'
  | 'watchlists' | 'alerts' | 'ledger' | 'methodology'

// Phase 2 of the 3-platform UI migration (Charter §0.6): nav icons now come from
// lucide-react (the web sibling of the mobile app's lucide-react-native), one icon =
// one meaning across surfaces — replacing the ad-hoc Unicode glyphs (▦ ▲ $ ◎ ★ ⚑ ✓ ❋).
const NAV: { key: NavKey; icon: LucideIcon; label: string }[] = [
  { key: 'dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { key: 'trends', icon: TrendingUp, label: 'Trends' },
  { key: 'market', icon: DollarSign, label: 'Market Signal' },
  { key: 'grade', icon: Activity, label: 'Grade' },
  { key: 'watchlists', icon: Star, label: 'Watchlists' },
  { key: 'alerts', icon: Bell, label: 'Alerts' },
  { key: 'ledger', icon: CheckCircle, label: 'Accuracy Ledger' },
  { key: 'methodology', icon: Sparkles, label: 'Methodology' },
]

function useEtClock() {
  const [t, setT] = useState('')
  useEffect(() => {
    const tick = () =>
      setT(new Date().toLocaleTimeString('en-US', {
        hour: 'numeric', minute: '2-digit', second: '2-digit',
        hour12: true, timeZone: 'America/New_York',
      }) + ' ET')
    tick(); const id = setInterval(tick, 1000); return () => clearInterval(id)
  }, [])
  return t
}

export function Shell({
  nav, onNav, children, rail, user, onSignOut, onAccount, search, onSearch, alertCount = 0,
}: {
  nav: NavKey
  onNav: (k: NavKey) => void
  children: ReactNode
  rail?: ReactNode
  user?: User | null
  onSignOut?: () => void
  onAccount?: () => void
  search?: string
  onSearch?: (v: string) => void
  alertCount?: number
}) {
  const clock = useEtClock()
  const initials = (user?.name || user?.email || 'NT').split(/[\s@.]+/).filter(Boolean).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'NT'
  const plan = user?.tier ? TIER_LABEL[user.tier].toUpperCase() : 'GUEST'
  return (
    <div className="app">
      {/* TOP BAR */}
      <header className="topbar">
        <div className="brand">
          <svg className="mark" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="7" fill="#13233a" />
            <path d="M9 21c2-1 3-3 3-6 1 2 2 3 4 3 0-3 1-5 3-7-1 5 4 6 4 10 0 3-3 5-7 5s-8-2-7-6 1-3 0-5z" fill="#df7a36" />
            <path d="M19 9l4-3-1 5z" fill="#2f6fed" />
          </svg>
          <div>
            <div className="name">Now<b>TrendIn</b></div>
            <div className="tag">Attention Intelligence</div>
          </div>
        </div>
        <div className="search">
          <Search className="ico" size={14} strokeWidth={2} />
          <input id="search" type="text" placeholder="Search topics, tickers, screens…" autoComplete="off"
            value={search ?? ''} onChange={(e) => onSearch?.(e.target.value)}
            onFocus={() => nav !== 'trends' && onNav('trends')} />
          <span className="kbd">⌘K</span>
        </div>
        <div className="top-right">
          <div className="asof"><span className="live">●</span> Live · as of<br /><b>{clock}</b></div>
          <div className="bell" title={alertCount > 0 ? `${alertCount} alert${alertCount === 1 ? '' : 's'}` : 'Alerts'}
            onClick={() => onNav('alerts')} style={{ cursor: 'pointer' }}>
            <Bell size={18} strokeWidth={1.8} />
            {alertCount > 0 && <span className="dot">{alertCount}</span>}
          </div>
          <span className="plan">{plan}</span>
          <div className="avatar" title={`${user?.name || ''} — account`} onClick={onAccount} style={{ cursor: 'pointer' }}>{initials}</div>
        </div>
      </header>

      {/* BODY */}
      <div className={'body' + (rail ? ' with-rail' : '')}>
        <aside className="sidebar">
          <div>
            {NAV.map((n) => {
              const Icon = n.icon
              return (
                <div key={n.key}
                  className={'nav-item' + (nav === n.key ? ' active' : '')}
                  onClick={() => onNav(n.key)}>
                  <span className="ni"><Icon size={16} strokeWidth={2} /></span> {n.label}
                  {n.key === 'alerts' && alertCount > 0 && <span className="badge">{alertCount}</span>}
                </div>
              )
            })}
          </div>
          <div className="nav-label">Saved Screens</div>
          <div className="screen-item" onClick={() => onNav('trends')}><span className="sd" style={{ background: 'var(--early)' }} /> Early Signals <span className="cnt">—</span></div>
          <div className="screen-item" onClick={() => onNav('trends')}><span className="sd" style={{ background: 'var(--bk-t)' }} /> Breakouts <span className="cnt">—</span></div>
          <div className="screen-item" onClick={() => onNav('watchlists')}><span className="sd" style={{ background: 'var(--conf)' }} /> My Watchlist <span className="cnt">6</span></div>
        </aside>

        <main className="main">{children}</main>

        {rail}
      </div>

      {/* FOOTER */}
      <footer className="footer">
        <span className="live">●</span>
        <span>Measurement, not investment advice — not a recommendation or risk rating.</span>
        <span className="sep">|</span>
        <a className="foot-link" href="https://nowtrendin.com/terms/" target="_blank" rel="noopener noreferrer">Terms</a>
        <a className="foot-link" href="https://nowtrendin.com/privacy/" target="_blank" rel="noopener noreferrer">Privacy</a>
        <a className="foot-link" href="https://nowtrendin.com/disclaimer/" target="_blank" rel="noopener noreferrer">Disclaimer</a>
        <span className="sep">|</span>
        <span>Sources: GitHub · HackerNews · GDELT · Wikipedia · Google Trends · Finnhub</span>
        <span className="right">Engine v2.0 · as of {clock}</span>
      </footer>
    </div>
  )
}
