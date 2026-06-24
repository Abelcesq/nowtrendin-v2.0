// Single source of truth for the legal disclaimer shown across Trends, Market Signal,
// History, and Grade. Keep the wording identical everywhere — change it here only.
export const LEGAL_DISCLAIMER =
  '*All information contained herein may not be accurate including any figures are approximate and the measured score and velocity and should not be construed as financial, investment, or legal advice.'

export function Disclaimer({ style }: { style?: any }) {
  return (
    <div className="disc legal-disc" style={{ fontStyle: 'italic', ...(style || {}) }}>
      {LEGAL_DISCLAIMER}
    </div>
  )
}
