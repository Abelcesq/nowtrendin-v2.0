// SignalAnalysisPanel — the per-item Signal Analysis side-panel section, shared by the trend,
// market, and crypto rails (3-platform parity: this is the web surface). It POSTs the item the
// rail already rendered to /analysis/{kind}; the engine attaches the matching accuracy-ledger
// report and returns a held-out, reproducible, formula-confidential narrative (measurement, not
// advice). Render-only — it adds no data of its own. §17 compliant: if the engine returns no
// sections (nothing to say), the panel renders nothing rather than an empty shell.
import { useEffect, useState } from 'react'
import { api, type SignalAnalysis } from '../lib/api'
import { MC } from '../lib/mobileTheme'

const SURFACE = '#FFFFFF', BORDER = '#ECECEC', BG = '#F4F5F8'

// Render **bold** spans (the descriptor bolds each metric name).
function renderBody(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith('**') && p.endsWith('**')
      ? <strong key={i} style={{ color: MC.text }}>{p.slice(2, -2)}</strong>
      : <span key={i}>{p}</span>)
}

export function SignalAnalysisPanel({ kind, item }: { kind: 'trend' | 'market' | 'crypto' | 'ledger'; item: any }) {
  const [a, setA] = useState<SignalAnalysis | null>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'empty'>('loading')
  const sig = JSON.stringify(item || {})
  useEffect(() => {
    let alive = true
    setState('loading')
    api.analysis(kind, item)
      .then(r => {
        if (!alive) return
        if (r && Array.isArray(r.sections) && r.sections.length) { setA(r); setState('ready') }
        else setState('empty')
      })
      .catch(() => { if (alive) setState('empty') })
    return () => { alive = false }
  }, [kind, sig])

  if (state === 'empty') return null
  return (
    <div style={{ marginTop: 18, padding: 14, border: `1px solid ${BORDER}`, borderRadius: 10, background: SURFACE }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: MC.text, letterSpacing: 0.3 }}>SIGNAL ANALYSIS</span>
        {a?.headline && <span style={{ fontSize: 11, color: MC.textSec }}>· {a.headline}</span>}
      </div>
      {state === 'loading' && <div style={{ fontSize: 12, color: MC.textSec }}>Composing analysis…</div>}
      {state === 'ready' && a && (
        <>
          {a.facts && a.facts.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
              {a.facts.map((f, i) => (
                <span key={i} style={{ fontSize: 11, padding: '3px 8px', borderRadius: 6, background: BG, border: `1px solid ${BORDER}`, color: MC.textSec }}>
                  <b style={{ color: MC.text }}>{f.label}</b> {f.value}
                </span>
              ))}
            </div>
          )}
          {a.sections!.map((s, i) => (
            <div key={i} style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 10.5, fontWeight: 700, color: MC.textSec, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 3 }}>{s.heading}</div>
              <div style={{ fontSize: 12.5, lineHeight: 1.5, color: MC.text }}>{renderBody(s.body)}</div>
            </div>
          ))}
          {a.disclaimer && (
            <div style={{ fontSize: 10.5, lineHeight: 1.45, color: MC.muted, marginTop: 10, fontStyle: 'italic' }}>{a.disclaimer}</div>
          )}
        </>
      )}
    </div>
  )
}
