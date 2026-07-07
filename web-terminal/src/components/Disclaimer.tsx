// Single source of truth for the legal disclaimer shown across Trends, Market Signal,
// History, and Grade. Keep the wording identical everywhere — change it here only.
// Founder-approved legal copy (2026-07-07) — verbatim; do not edit without founder sign-off.
export const LEGAL_DISCLAIMER =
  '*All information contained herein may not be accurate including any and all figures indicated in this section and or site and may be an approximation and should not be construed as financial, investment, or legal advice.'

export function Disclaimer({ style }: { style?: any }) {
  return (
    <div className="disc legal-disc" style={{ fontStyle: 'italic', ...(style || {}) }}>
      {LEGAL_DISCLAIMER}
    </div>
  )
}
