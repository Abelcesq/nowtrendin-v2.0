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

        {/* The N factor — separate from the Gradient Score */}
        <section className="mth-sec">
          <h3>The N factor — Now Trending (community demand)</h3>
          <div className="mth-card" style={{ borderColor: '#EE6A2A55', background: '#EE6A2A0C' }}>
            <div className="mth-tag" style={{ color: '#EE6A2A' }}>● N · Now Trending</div>
            <p className="mth-p">
              <b>N</b> is our on-platform <b>demand</b> signal — how often Now TrendIn users
              themselves query, open, or grade a topic. It captures real institutional curiosity
              that no public source can see, and it is shown alongside every score.
            </p>
            <p className="mth-p" style={{ marginTop: 10 }}>
              <b>N is deliberately NOT part of the Gradient Score.</b> Detection and Confidence are
              composed only from the six <b>external</b> components above (G·I·M·D·C·P) — measured
              from the outside world. N is reported as a <b>separate, parallel number</b> and is never
              folded into the official Gradient Score.
            </p>
            <p className="mth-p" style={{ marginTop: 10 }}>
              <b>Why it's kept separate (the integrity reason):</b> if our own users' demand fed the
              score, the instrument would measure itself — popular topics would look "trending" because
              we surfaced them, a reflexive feedback loop. That violates the no-circular-metrics rule:
              a validator must never use inputs derived from what it validates. Keeping N external-only
              guarantees the Gradient Score stays an <b>objective measure of the outside world</b>, not
              of our platform.
            </p>
            <p className="mth-p" style={{ marginTop: 10 }}>
              The signal-detail page also shows a clearly-labelled, demand-inclusive
              <b> "Now Trending Gradient Score"</b> as a what-if read — what the score would be if N
              were folded in. That view is informational only; the headline Gradient Score always
              remains N-free.
            </p>
          </div>
        </section>

        {/* Anomalies */}
        <section className="mth-sec">
          <h3>Anomalies</h3>
          <div className="mth-card" style={{ borderColor: '#8B5CF655', background: '#8B5CF60C' }}>
            <div className="mth-tag" style={{ color: '#8B5CF6' }}>● Anomaly</div>
            <p className="mth-p">
              An <b>anomaly</b> is a topic whose <b>Detection score is running ahead of its Confidence
              score</b> by a clear margin (a signed lead of <b>16+ points</b>) — strong early-edge
              evidence the engine sees <b>before</b> broad confirmation has caught up. It is the
              clearest expression of the product thesis: <i>the future arriving before it's obvious</i>.
              Some are the real thing early; some are noise that never confirms.
            </p>
            <p className="mth-p" style={{ marginTop: 10 }}>
              <b>It is a separate axis from the signal stage.</b> Stage (Breakout / Strong / Indicating /
              Marginal) measures <b>strength</b> — how high Detection is. An anomaly measures <b>shape</b>
              — how far Detection LEADS Confirmation. So an anomaly can appear at any stage: a Strong
              topic with a wide lead is a strong early anomaly; a Marginal one with a wide lead is an
              early-stage anomaly. A topic where Confidence exceeds Detection is the opposite —
              already-confirmed or lagging — and is <b>not</b> an anomaly.
            </p>
            <p className="mth-p" style={{ marginTop: 10 }}>
              True anomalies are deliberately rare. We define them by the signed Detection-minus-
              Confidence lead, not by an absolute gap (which would also catch lagging topics) and not by
              raw acceleration alone (a heavily-covered topic can accelerate without being early).
            </p>
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

        {/* The Money Gradient */}
        <section className="mth-sec">
          <h3>The Money Gradient — where money is moving</h3>
          <div className="mth-card">
            <p className="mth-p">Alongside the Attention Gradient, Now TrendIn runs a parallel <b>Money Gradient</b> on the same Dark-Matter→Mainstream pattern. <b>Money Movement</b> measures early/informed money — congressional trades, insider Form-4, smart-money 13F, and quality finance analysts (the Dark-Matter layer). <b>Market Confirmation</b> measures the broad market + economic data (the Mainstream layer). The <b>flow</b> (IN/OUT) is a fact read straight from the filings, and an objective <b>leverage</b> read states balance-sheet facts. It is a measurement of movement and a leverage-facts read — never a buy/sell recommendation, a price prediction, or investment advice.</p>
          </div>
        </section>

        {/* Accuracy ledgers */}
        <section className="mth-sec">
          <h3>The Accuracy Ledgers</h3>
          <div className="mth-card">
            <p className="mth-p">Every notable detection is time-stamped and later validated against what actually happened — a permanent, auditable record, denominator included. We report it as it is; we do not market a number we cannot defend. There are <b>two</b> ledgers, one per Gradient, with two different ground truths: the <b>Attention</b> ledger validates against the topic's <b>Google Trends breakout</b> (did attention arrive?); the <b>Money</b> ledger validates against the realized <b>EOD price direction</b> (did the market move the way the detected flow indicated?). Both are retrospective measurements of our own accuracy — see the <b>Accuracy Ledger</b> tab (toggle Attention / Money) for the live record.</p>
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
