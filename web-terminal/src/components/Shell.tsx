import { useEffect, useState, type ReactNode } from 'react'
import {
  LayoutGrid, TrendingUp, DollarSign, Activity, Star, Bell, CheckCircle, Sparkles,
  Search, Clock, Pencil, Plus, X, type LucideIcon,
} from 'lucide-react'
import { TIER_LABEL, type User, type Favorite } from '../lib/auth'
import { api } from '../lib/api'

// Filter options a Favorite can target (label + key) per section.
const FAV_OPTIONS: Record<string, { k: string; label: string }[]> = {
  trends: [
    { k: 'nowtrendin', label: 'Now TrendIn' }, { k: 'all', label: 'All Signals' },
    { k: 'breakout', label: 'Breakout' }, { k: 'strong', label: 'Strong' },
    { k: 'emerging', label: 'Indicating' }, { k: 'marginal', label: 'Marginal' },
    { k: 'anomalies', label: 'Anomalies' },
  ],
  market: [
    { k: 'all', label: 'All' }, { k: 'elevated', label: 'Elevated' }, { k: 'active', label: 'Active' },
    { k: 'building', label: 'Building' }, { k: 'routine', label: 'Routine' },
    { k: 'dormant', label: 'Dormant' }, { k: 'leverage', label: 'Leverage ≥60' },
  ],
  watchlist: [{ k: '', label: 'My watchlists' }],
}
const FAV_COLORS = ['var(--bk-t)', '#8B5CF6', 'var(--down)', 'var(--det)', 'var(--em-t)', 'var(--conf)']
let _favc = 0

export type NavKey =
  | 'dashboard' | 'trends' | 'market' | 'grade'
  | 'watchlists' | 'alerts' | 'history' | 'ledger' | 'methodology'

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
  { key: 'history', icon: Clock, label: 'History' },
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
  favorites = [], onFav, onFavChange,
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
  favorites?: Favorite[]
  onFav?: (f: Favorite) => void
  onFavChange?: (next: Favorite[]) => void
}) {
  const clock = useEtClock()
  const initials = (user?.name || user?.email || 'NT').split(/[\s@.]+/).filter(Boolean).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'NT'
  const plan = user?.tier ? TIER_LABEL[user.tier].toUpperCase() : 'GUEST'
  const [favEdit, setFavEdit] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [favSection, setFavSection] = useState<'trends' | 'market' | 'history'>('trends')
  const [favFilter, setFavFilter] = useState('breakout')
  const [favQuery, setFavQuery] = useState('')
  const [favEnts, setFavEnts] = useState<{ key: string; display: string }[] | null>(null)
  const [favPicked, setFavPicked] = useState<{ key: string; display: string } | null>(null)
  // Lazy-load the searchable universe — TREND/HISTORY topics ONLY. "Track topic"
  // pins a topic that lands you in the History section (its scoring trajectory).
  // Market instruments belong to the Market section's filter-views, not here.
  useEffect(() => {
    if (favSection !== 'history' || favEnts !== null) return
    setFavEnts([])
    api.topics(500)
      .then((t) => setFavEnts((t.topics || []).map((x) => ({ key: x.topic_key, display: x.topic_display || x.topic_key }))))
      .catch(() => setFavEnts([]))
  }, [favSection, favEnts])
  const favMatches = (favEnts || []).filter((e) => favQuery.trim().length >= 2 && e.display.toLowerCase().includes(favQuery.trim().toLowerCase())).slice(0, 6)
  const resetFav = () => { setShowAdd(false); setFavQuery(''); setFavPicked(null) }
  const addFavorite = () => {
    let fav: Favorite
    if (favSection === 'history') {
      if (!favPicked) return
      fav = { id: `fav_${Date.now()}_${_favc++}`, label: favPicked.display, section: 'history', filter: favPicked.key, kind: 'topic', color: FAV_COLORS[favorites.length % FAV_COLORS.length] }
    } else {
      const opt = FAV_OPTIONS[favSection].find((o) => o.k === favFilter) || FAV_OPTIONS[favSection][0]
      fav = { id: `fav_${Date.now()}_${_favc++}`, label: opt.label, section: favSection, filter: favFilter, color: FAV_COLORS[favorites.length % FAV_COLORS.length] }
    }
    onFavChange?.([...favorites, fav]); resetFav()
  }
  const removeFavorite = (id: string) => onFavChange?.(favorites.filter((f) => f.id !== id))
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
          {search ? (
            <button onClick={() => onSearch?.('')} title="Clear" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', padding: '2px 4px', display: 'flex', alignItems: 'center' }}><X size={13} /></button>
          ) : (
            <span className="kbd">⌘K</span>
          )}
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
          <div className="nav-label fav-label">
            Favorites
            {favEdit ? (
              <button className="fav-savebtn" onClick={() => { setFavEdit(false); setShowAdd(false); resetFav() }} title="Save and exit editing">Save</button>
            ) : (
              <button className="fav-editbtn" onClick={() => setFavEdit(true)} title="Edit favorites"><Pencil size={11} /> Edit</button>
            )}
          </div>
          {favorites.map((f) => (
            <div className="screen-item" key={f.id} onClick={() => !favEdit && onFav?.(f)}>
              <span className="sd" style={{ background: f.color || 'var(--det)' }} /> {f.label}
              {favEdit && <span className="fav-del" onClick={(e) => { e.stopPropagation(); removeFavorite(f.id) }}><X size={13} /></span>}
            </div>
          ))}
          {favEdit && !showAdd && (
            <div className="screen-item fav-add" onClick={() => setShowAdd(true)}><Plus size={14} /> Add favorite</div>
          )}
          {favEdit && showAdd && (
            <div className="fav-form">
              <div className="fav-frow fav-sections">
                {([['trends', 'Trends'], ['market', 'Market'], ['history', 'Track topic']] as const).map(([s, label]) => (
                  <button key={s} className={'fav-chip' + (favSection === s ? ' on' : '')} onClick={() => { setFavSection(s); setFavPicked(null); setFavQuery(''); if (s !== 'history') setFavFilter(FAV_OPTIONS[s][0].k) }}>{label}</button>
                ))}
              </div>
              {favSection === 'history' ? (
                favPicked ? (
                  <div className="fav-picked" onClick={() => setFavPicked(null)} title="Clear">{favPicked.display} <span>· History</span> <X size={12} /></div>
                ) : (
                  <>
                    <input className="fav-input" value={favQuery} placeholder="Search a topic…" onChange={(e) => setFavQuery(e.target.value)} />
                    {favEnts === null ? <div className="fav-hint">Loading…</div>
                      : favQuery.trim().length >= 2 && favMatches.length === 0 ? <div className="fav-hint">Not in our database — only existing topics can be tracked.</div>
                        : favMatches.map((e) => <div key={e.key} className="fav-sugg" onClick={() => { setFavPicked(e); setFavQuery('') }}>{e.display}<span>History</span></div>)}
                  </>
                )
              ) : (
                <select className="fav-select" value={favFilter} onChange={(e) => setFavFilter(e.target.value)}>
                  {FAV_OPTIONS[favSection].map((o) => <option key={o.k} value={o.k}>{o.label}</option>)}
                </select>
              )}
              <div className="fav-frow">
                <button className="fav-save" onClick={addFavorite} disabled={favSection === 'history' && !favPicked} style={favSection === 'history' && !favPicked ? { opacity: 0.5 } : undefined}>Add</button>
                <button className="fav-cancel" onClick={resetFav}>Cancel</button>
              </div>
            </div>
          )}
        </aside>

        <main className="main">{children}</main>

        {rail}
      </div>

      {/* FOOTER */}
      <footer className="footer">
        <span className="live">●</span>
        <span>All information contained herein may not be accurate including any figures are approximate and the measured score and velocity and should not be construed as financial, investment, or legal advice.</span>
        <span className="sep">|</span>
        <a className="foot-link" href="https://nowtrendin.com/terms/" target="_blank" rel="noopener noreferrer">Terms</a>
        <a className="foot-link" href="https://nowtrendin.com/privacy/" target="_blank" rel="noopener noreferrer">Privacy</a>
        <a className="foot-link" href="https://nowtrendin.com/disclaimer/" target="_blank" rel="noopener noreferrer">Disclaimer</a>
        <span className="right">Engine v2.0 · as of {clock}</span>
      </footer>
    </div>
  )
}
