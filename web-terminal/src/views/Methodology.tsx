// Methodology — the institutional transparency page. Explains the Gradient Score
// honestly (no performance claims), documents data + integrity, and hosts the
// legal documents / disclaimer. Static content; no data wiring.

const LEGAL = [
  { title: 'Terms & Conditions', sub: 'Terms of service', url: 'https://nowtrendin.com/terms/' },
  { title: 'Privacy Policy', sub: 'How we handle your data', url: 'https://nowtrendin.com/privacy/' },
  { title: 'Disclaimer', sub: 'Important information & limitations', url: 'https://nowtrendin.com/disclaimer/' },
]

const COMPONENTS = [
  ['G', 'Gradient strength', 'Niche/expert concentration vs. mainstream — how much runway is left.'],
  ['I', 'Inertia', 'Acceleration sustained across consecutive scoring windows.'],
  ['M', 'Platform diversity', 'How many independent surfaces carry the signal.'],
  ['D', 'Dark matter', 'First-timer asymmetry — inferred pre-public, insider activity.'],
  ['C', 'Confidence decay', 'Signal freshness and directional momentum.'],
  ['P', 'Persistence', 'Sustained elevation across cycles — has it held.'],
]

export function Methodology() {
  return (
    <>
      <div className="main-head">
        <div className="main-title-row">
          <div className="main-title">Methodology</div>
          <div className="main-sub">How the Gradient Score measures where attention is moving — before it arrives.</div>
        </div>
      </div>

      <div className="mth">
        <p className="mth-lede">
          The Gradient Score is an <b>instrument</b>, not a recommendation. It measures the
          movement of public attention across independent sources and reports two numbers per
          topic. Everything below is how those numbers are produced — and what they do and do
          not claim.
        </p>

        {/* The two scores */}
        <section className="mth-sec">
          <h3>The two scores</h3>
          <div className="mth-two">
            <div className="mth-card">
              <div className="mth-tag" style={{ color: 'var(--det)' }}>● Detection</div>
              <p className="mth-p">Reads the <b>early signal</b> — how strongly a topic is emerging right now. Higher = earlier. It moves first, with less certainty.</p>
            </div>
            <div className="mth-card">
              <div className="mth-tag" style={{ color: 'var(--conf)' }}>● Confidence</div>
              <p className="mth-p">Reads the <b>confirmation</b> — how much corroborating evidence has accumulated. It moves later, with more certainty.</p>
            </div>
          </div>
          <div className="mth-card mth-gapnote">
            <b>The gap is the lead time.</b> A wide Detection-over-Confidence gap means the engine
            sees a topic moving before the evidence has caught up — the window where being early
            has value. As a topic matures the two scores converge.
          </div>
        </section>

        {/* How detection is computed */}
        <section className="mth-sec">
          <h3>How detection is computed</h3>
          <div className="mth-list">
            <div className="mth-card">
              <div className="mth-ch">Dual-pathway detection</div>
              <p className="mth-p">Two legitimate trend shapes, one number. <b>Expert-origin</b> topics (tech, research) are scored on the niche-concentration gradient — the moat. <b>Mainstream-origin</b> topics (consumer culture, news) are scored on real attention magnitude + cross-source breadth, because a niche ratio is structurally meaningless for them.</p>
            </div>
            <div className="mth-card">
              <div className="mth-ch">Baseline-relative (fame vs. diffusion)</div>
              <p className="mth-p">Mainstreaming is measured as deviation from a topic's <b>own</b> baseline footprint — not absolute size. A household name's permanent visibility reads as neutral; only expansion past its norm counts as movement. A perennial topic in the news every day is its baseline, not news.</p>
            </div>
            <div className="mth-card">
              <div className="mth-ch">News-outlet corroboration</div>
              <p className="mth-p">One reputable outlet can still be niche; corroboration across many distinct reputable outlets is what marks a topic <b>mainstream-confirmed</b>. Outlet breadth is counted explicitly so a story carried widely — even with modest per-article reach — surfaces correctly.</p>
            </div>
            <div className="mth-card">
              <div className="mth-ch">Community-level tiers &amp; tier-migration</div>
              <p className="mth-p">"Expert" vs "mainstream" is a property of the community, not the platform — the same entity is early in a specialist forum and arrived on a general feed. A topic crossing from expert communities into mainstream ones is the highest-confidence mainstreaming signal.</p>
            </div>
          </div>
        </section>

        {/* Components */}
        <section className="mth-sec">
          <h3>Score components</h3>
          <p className="mth-p">Detection and Confidence are composites of the same measured components, weighted differently:</p>
          <div className="mth-comp">
            {COMPONENTS.map(([k, name, desc]) => (
              <div className="mth-cc" key={k}>
                <span className="mth-cb">{k}</span>
                <div><div className="mth-cn">{name}</div><div className="mth-cd">{desc}</div></div>
              </div>
            ))}
          </div>
        </section>

        {/* Data & integrity */}
        <section className="mth-sec">
          <h3>Data &amp; integrity</h3>
          <div className="mth-card">
            <p className="mth-p">Signals are collected from independent public sources — developer and research surfaces (GitHub, Hacker News, dev blogs), general discovery (Wikipedia, Google Trends), broad coverage (GDELT + reputable news wires), and market data (Finnhub). Topics are scored every 6 hours.</p>
            <p className="mth-p" style={{ marginTop: 10 }}>Integrity rules are enforced in the engine: only vetted, reputable publishers carry full weight; unverified sources are quarantined and admitted only when independently corroborated; a validator never uses inputs derived from what it validates (no circular metrics); and the score reflects <b>external</b> attention, never our own users' demand.</p>
          </div>
        </section>

        {/* Accuracy ledger */}
        <section className="mth-sec">
          <h3>The Accuracy Ledger</h3>
          <div className="mth-card">
            <p className="mth-p">Every notable detection is time-stamped and later validated against what actually broke out — a permanent, auditable record of lead time vs. observed reality. This is the honest measure of the instrument, denominator included. We report it as it is; we do not market a number we cannot defend. The ledger is young and grows with every cycle — see the <b>Accuracy Ledger</b> tab for the live record.</p>
          </div>
        </section>

        {/* Legal */}
        <section className="mth-sec">
          <h3>Legal &amp; disclaimer</h3>
          <div className="mth-legal">
            {LEGAL.map((d) => (
              <a className="mth-doc" key={d.url} href={d.url} target="_blank" rel="noopener noreferrer">
                <div className="mth-doc-t">{d.title}</div>
                <div className="mth-doc-s">{d.sub}</div>
                <span className="mth-doc-x">↗</span>
              </a>
            ))}
          </div>
          <p className="mth-fine">
            Measurement, not investment advice — the Gradient Score is not a recommendation, solicitation,
            or risk rating. All Gradient Scores, analyses, and signal data are proprietary to Now TrendIn LLC;
            users have no ownership rights to any data, scores, analyses, or results obtained through the platform.
          </p>
        </section>
      </div>
    </>
  )
}
