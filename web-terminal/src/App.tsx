import { useState, type ReactNode } from 'react'
import { Shell, type NavKey } from './components/Shell'
import { Ledger } from './views/Ledger'
import { Screener } from './views/Screener'

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
        <div className="muted">Shipped: Signal Screener + Accuracy Ledger. Next: Market Signal, Grade, Watchlists, Methodology, auth.</div>
      </div>
    </>
  )
}

export function App() {
  const [nav, setNav] = useState<NavKey>('trends')
  const [rail, setRail] = useState<ReactNode | null>(null)

  const go = (k: NavKey) => { setRail(null); setNav(k) }

  let body: ReactNode
  if (nav === 'trends') body = <Screener onRail={setRail} />
  else if (nav === 'ledger') body = <Ledger />
  else body = <Placeholder title={titleFor(nav)} />

  return (
    <Shell nav={nav} onNav={go} rail={nav === 'trends' ? rail : null}>
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
