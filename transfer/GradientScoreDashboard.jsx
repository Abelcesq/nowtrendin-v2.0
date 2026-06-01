import { useState, useEffect, useCallback, useRef, Component } from "react";
import {
  MaturityBadge,
  CalibratedScoreDisplay,
  CalibratedComponentBreakdown,
  WhatToDoPanel,
  MaturityMiniTag,
} from "./CalibrationDisplayFixes";
import ResearchHistoryPanel from "./ResearchHistoryPanel";
import {
  AIVariationMap,
  AIResearchSection,
  AITierBadge,
  AIScoreWithContext,
} from "./AIVariationMap";

// ── ERROR BOUNDARY ────────────────────────────────────────────────
// Catches any render-time JS exception and shows a recovery UI instead
// of a blank white screen. Without this, a single bad data field in one
// TopicCard unmounts the entire app with no feedback.
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { err: null }; }
  static getDerivedStateFromError(err) { return { err }; }
  componentDidCatch(err, info) { console.error("NowTrendIn render error:", err, info); }
  render() {
    if (this.state.err) {
      return (
        <div style={{ padding: 32, textAlign: "center", fontFamily: "sans-serif" }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}>⚠️</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#0F172A", marginBottom: 8 }}>
            Something went wrong rendering this section.
          </div>
          <div style={{ fontSize: 11, color: "#6B7280", marginBottom: 16 }}>
            {this.state.err.message}
          </div>
          <button
            onClick={() => this.setState({ err: null })}
            style={{ padding: "8px 20px", borderRadius: 8, border: "1px solid #CBD5E1",
              background: "#F1F5F9", cursor: "pointer", fontSize: 12 }}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── API BASE ─────────────────────────────────────────────────────
const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env)
    ? (import.meta.env.VITE_API_URL ?? (import.meta.env.PROD ? "" : "http://localhost:8000"))
    : "http://localhost:8000";

// No mock data — the app only ever shows real collected signals.
// On first load the list is empty until handleRefresh() returns live data.

// ── DESIGN TOKENS — LIGHT THEME ─────────────────────────────────
const T = {
  bg: "#F1F5F9",
  surface: "#FFFFFF",
  card: "#FFFFFF",
  cardBorder: "#E2E8F0",
  detection: "#1D4ED8",
  detectionMid: "#3B82F6",
  detectionLight: "#EFF6FF",
  detectionBorder: "#BFDBFE",
  confidence: "#047857",
  confidenceMid: "#10B981",
  confidenceLight: "#ECFDF5",
  confidenceBorder: "#A7F3D0",
  gold: "#92400E",
  goldMid: "#D97706",
  goldLight: "#FFFBEB",
  goldBorder: "#FCD34D",
  orange: "#9A3412",
  orangeLight: "#FFF7ED",
  purple: "#5B21B6",
  purpleLight: "#F5F3FF",
  flame: "#D94F0A",
  flameMid: "#FF6820",
  flameLight: "#FFF3ED",
  flameBorder: "#FDBF9A",
  red: "#B91C1C",
  textPrimary: "#0F172A",
  textSecondary: "#374151",
  textMuted: "#6B7280",
  textFaint: "#9CA3AF",
  navy: "#1E3A8A",
};

// ── FORMULA WEIGHTS (G·I·M·D·C·P·N — seven components) ──────────
// P = Persistence: historical longevity across scoring cycles
// N = NowTrendIn: internal query frequency (demand-side signal)
// Low weight for Detection (speed > history), high for Confidence (history = precision)
const DET_W  = { G: 0.33, I: 0.16, M: 0.09, D: 0.19, C: 0.05, P: 0.06, N: 0.12 };
const CONF_W = { G: 0.11, I: 0.25, M: 0.20, D: 0.04, C: 0.06, P: 0.24, N: 0.10 };
const OVR_W  = { G: 0.22, I: 0.20, M: 0.15, D: 0.12, C: 0.07, P: 0.14, N: 0.10 };
// Visual anchor for DualBar normalisation (unchanged from original so bars stay readable)
const DET_ANCHOR  = 0.40;
const CONF_ANCHOR = 0.35;

// ── UTILITIES ────────────────────────────────────────────────────
function gapMeta(gap) {
  if (gap <= 15) return { label: "High conviction",         color: T.confidence,  bg: T.confidenceLight,  border: T.confidenceBorder };
  if (gap <= 35) return { label: "Early stage",             color: T.goldMid,     bg: T.goldLight,        border: T.goldBorder };
  if (gap <= 60) return { label: "Very early",              color: T.orange,      bg: T.orangeLight,      border: "#FDBA74" };
  return            { label: "Speculative — dark matter",   color: T.purple,      bg: T.purpleLight,      border: "#C4B5FD" };
}

// Plain-English action instruction per signal stage — Level 3: Action Clarity (Section 04)
// The most important and most neglected output: the user must know WHAT TO DO, not just see a number.
function stageActionLine(stage, gap) {
  if (stage === "BREAKOUT") return "Act now — breakout confirmed";
  if (stage === "STRONG")   return "Act with confidence — strong signal";
  if (stage === "EMERGING") return gap > 35 ? "First-mover window — very early signal" : "Emerging — creators act now";
  if (stage === "WATCHING" || stage === "WATCH") return "Building — monitor this topic closely";
  return "Monitoring — wait for stronger signal";
}

// Maps a signal_stage string to a display color. Used in TopicCard, HistoryPanel, and any
// component that needs a color for a stage label. Defined at module level so all components share it.
function stageColor(stage) {
  const map = {
    BREAKOUT:   T.confidence,
    STRONG:     T.detection,
    EMERGING:   T.goldMid,
    WATCHING:   T.orange,
    WATCH:      T.orange,
    MONITORING: T.textFaint,
    DECAY:      T.textFaint,
  };
  return map[(stage || "").toString().toUpperCase().trim()] || T.textFaint;
}

function detLabel(s) {
  if (s >= 85) return "Breakout signal";
  if (s >= 70) return "Strong signal";
  if (s >= 55) return "Early signal";
  if (s >= 40) return "Watch signal";
  return "Weak signal";
}

function confLabel(s) {
  if (s >= 70) return "Confirmed";
  if (s >= 50) return "Building";
  if (s >= 30) return "Needs confirmation";
  return "Unconfirmed";
}

function patternLabel(p) {
  const m = {
    A_builder_to_buyer: "Pattern A · Builder → Buyer",
    B_enthusiast_to_mainstream: "Pattern B · Enthusiast → Mainstream",
    C_research_to_commerce: "Pattern C · Research → Commerce",
    multi_platform_unclassified: "Multi-Platform",
    single_platform: "Single Platform",
  };
  return m[p] || (p || "Emerging");
}

// Platform icons — covers all 10 possible sources (3 core + 7 blog)
const PLATFORM_ICONS = {
  reddit:     "⬡",
  github:     "◈",
  hackernews: "▲",
  arxiv:      "◎",
  devto:      "✦",
  hashnode:   "◆",
  discourse:  "❋",
  wordpress:  "⊕",
  blogger:    "✿",
  medium:     "○",
  ghost:      "◇",
};

// Human-readable platform display names
const PLATFORM_NAMES = {
  reddit:     "Reddit",
  github:     "GitHub",
  hackernews: "Hacker News",
  arxiv:      "arXiv",
  devto:      "DEV.to",
  hashnode:   "Hashnode",
  discourse:  "Discourse",
  wordpress:  "WordPress",
  blogger:    "Blogger",
  medium:     "Medium",
  ghost:      "Ghost",
};

function srcIcon(s) { return PLATFORM_ICONS[s] || "·"; }
function platformName(s) { return PLATFORM_NAMES[s] || (s ? s.charAt(0).toUpperCase() + s.slice(1) : "Unknown"); }

function timeAgo(iso) {
  const ms = Date.now() - new Date(iso).getTime();
  const m = Math.floor(ms / 60000);
  if (m < 1)  return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return h < 24 ? `${h}h ago` : `${Math.floor(h / 24)}d ago`;
}

// ── SCROLLABLE PANE — custom slim scrollbar (track + draggable thumb) ──
// Hides the native browser scrollbar and replaces it with a thin 8px
// track on the right edge.  Dragging the thumb, clicking the track, and
// normal mouse-wheel / touch scrolling all work as expected.
// scrollRef — optional external ref that is wired to the inner scroll div
//             (used by HistoryPanel's scrollUp / scrollDown helpers).
function ScrollablePane({ children, style, scrollRef }) {
  const innerRef  = useRef(null);
  const thumbHRef = useRef(0);          // pixel height of thumb (for drag math)

  const [thumbH,   setThumbH]   = useState(0);
  const [thumbTop, setThumbTop] = useState(0);
  const [showBar,  setShowBar]  = useState(false);

  // Merge the external scrollRef with our own innerRef
  const setRef = useCallback((node) => {
    innerRef.current = node;
    if (scrollRef) scrollRef.current = node;
  }, [scrollRef]);

  // Recompute thumb size + position
  const update = useCallback(() => {
    const el = innerRef.current;
    if (!el) return;
    const trackH   = el.clientHeight;
    const contentH = el.scrollHeight;
    const maxScroll = contentH - trackH;
    if (contentH <= trackH + 4) { setShowBar(false); return; }
    const rawH  = (trackH / contentH) * trackH;
    const th    = Math.max(rawH, 36);           // never shorter than 36px
    const maxTT = trackH - th;
    const tt    = maxScroll > 0 ? (el.scrollTop / maxScroll) * maxTT : 0;
    thumbHRef.current = th;
    setThumbH(th);
    setThumbTop(Math.max(0, Math.min(maxTT, tt)));
    setShowBar(true);
  }, []);

  useEffect(() => {
    const el = innerRef.current;
    if (!el) return;
    update();
    el.addEventListener("scroll", update, { passive: true });
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => { el.removeEventListener("scroll", update); ro.disconnect(); };
  }, [update]);

  // Drag the thumb
  const onThumbMouseDown = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    const el = innerRef.current;
    if (!el) return;
    const startY      = e.clientY;
    const startScroll = el.scrollTop;
    const trackH      = el.clientHeight;
    const th          = thumbHRef.current;
    const maxThumbTop = trackH - th;
    const maxScroll   = el.scrollHeight - el.clientHeight;

    const onMove = (ev) => {
      const delta       = ev.clientY - startY;
      const scrollDelta = maxThumbTop > 0 ? (delta / maxThumbTop) * maxScroll : 0;
      el.scrollTop = Math.max(0, Math.min(maxScroll, startScroll + scrollDelta));
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup",   onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup",   onUp);
  }, []);

  // Click on the track (not the thumb) to jump
  const onTrackClick = useCallback((e) => {
    const el = innerRef.current;
    if (!el) return;
    const rect      = e.currentTarget.getBoundingClientRect();
    const clickY    = e.clientY - rect.top;
    const trackH    = el.clientHeight;
    const th        = thumbHRef.current;
    const maxThumbTop = trackH - th;
    const ratio     = maxThumbTop > 0
      ? Math.max(0, Math.min(1, (clickY - th / 2) / maxThumbTop))
      : 0;
    el.scrollTop = ratio * (el.scrollHeight - el.clientHeight);
  }, []);

  return (
    <div style={{ position: "relative", overflow: "hidden", minHeight: 0, ...style }}>
      {/* Inner scrollable div — native scrollbar hidden via class */}
      <div
        ref={setRef}
        className="nt-scrollpane"
        style={{
          height: "100%",
          overflowY: "scroll",
          scrollbarWidth: "none",      /* Firefox */
          msOverflowStyle: "none",     /* IE/Edge */
          paddingRight: showBar ? 8 : 0,
          boxSizing: "border-box",
        }}
      >
        {children}
      </div>

      {/* Custom scrollbar track */}
      {showBar && (
        <div
          onClick={onTrackClick}
          style={{
            position: "absolute", right: 0, top: 0, bottom: 0, width: 8,
            background: T.bg,
            borderLeft: `1px solid ${T.cardBorder}`,
            cursor: "pointer",
            userSelect: "none",
            zIndex: 20,
          }}
        >
          {/* Thumb */}
          <div
            onMouseDown={onThumbMouseDown}
            style={{
              position: "absolute",
              left: 2, right: 2,
              top:    thumbTop,
              height: thumbH,
              borderRadius: 4,
              background: "#B0BEC5",
              cursor: "grab",
              transition: "background 0.15s",
            }}
            onMouseEnter={e => e.currentTarget.style.background = T.detectionMid}
            onMouseLeave={e => e.currentTarget.style.background = "#B0BEC5"}
          />
        </div>
      )}
    </div>
  );
}

// ── FLAME LOGO ───────────────────────────────────────────────────
function FlameLogo({ size = 36 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ display: "block", flexShrink: 0 }}>
      <defs>
        <linearGradient id="nt-flame-body" x1="30%" y1="0%" x2="70%" y2="100%">
          <stop offset="0%"   stopColor="#FF8020" />
          <stop offset="100%" stopColor="#C81400" />
        </linearGradient>
        <radialGradient id="nt-flame-glow" cx="50%" cy="60%" r="40%">
          <stop offset="0%"   stopColor="#FFD878" stopOpacity="0.75" />
          <stop offset="100%" stopColor="#FF8020" stopOpacity="0"   />
        </radialGradient>
      </defs>
      {/* Flame body — clean teardrop with upward point */}
      <path
        d="M50 7
           C54 16, 66 24, 70 38
           C74 52, 70 66, 62 75
           C57 81, 53 85, 50 87
           C47 85, 43 81, 38 75
           C30 66, 26 52, 30 38
           C34 24, 46 16, 50 7Z"
        fill="url(#nt-flame-body)"
      />
      {/* Inner warm highlight */}
      <path
        d="M50 30
           C53 37, 58 44, 59 53
           C60 62, 56 70, 50 74
           C44 70, 40 62, 41 53
           C42 44, 47 37, 50 30Z"
        fill="url(#nt-flame-glow)"
      />
      {/* Trending-up chart line (white) */}
      <polyline
        points="26,74 38,58 50,65 70,42"
        fill="none" stroke="white" strokeWidth="6"
        strokeLinecap="round" strokeLinejoin="round"
      />
      <circle cx="70" cy="42" r="4.5" fill="white" />
    </svg>
  );
}

// ── SCORE CIRCLE ─────────────────────────────────────────────────
function ScoreCircle({ score, color, trackColor, size = 100 }) {
  const r = size / 2 - 10;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(score || 0, 0), 100) / 100;
  const offset = circ * (1 - pct);
  return (
    <svg width={size} height={size} style={{ overflow: "visible", display: "block" }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={trackColor || "#E2E8F0"} strokeWidth={9} />
      <circle
        cx={size/2} cy={size/2} r={r}
        fill="none" stroke={color} strokeWidth={9}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
        style={{ transition: "stroke-dashoffset 1s ease" }}
      />
      <text x={size/2} y={size/2 - 5} textAnchor="middle" dominantBaseline="middle"
        fill={color} fontSize={size >= 90 ? 28 : 16} fontWeight="800"
        fontFamily="'DM Mono', monospace">
        {Math.round(score || 0)}
      </text>
      <text x={size/2} y={size/2 + 16} textAnchor="middle" dominantBaseline="middle"
        fill={T.textFaint} fontSize={10} fontFamily="'DM Mono', monospace">
        /100
      </text>
    </svg>
  );
}

// ── DUAL COMPONENT BAR ───────────────────────────────────────────
// Shows how much each G·I·M·D·C·P·N component contributes to each mode
// Anchored to 0.40 for detection, 0.35 for confidence (visual normalisation)
// highlight: pass a CSS color string for special badge color (e.g. T.purple or T.flame)
function DualBar({ letter, name, weight, score, dw, cw, highlight, desc }) {
  const s = Math.max(score || 0, 0);
  const detVal  = Math.round(s * dw / DET_ANCHOR);
  const confVal = Math.round(s * cw / CONF_ANCHOR);
  const badgeColor = highlight || T.navy;
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <div style={{
          width: 22, height: 22, borderRadius: 5, flexShrink: 0,
          background: badgeColor,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 9, fontWeight: 800, color: "white", fontFamily: "'DM Mono', monospace",
        }}>{letter}</div>
        <span style={{ fontSize: 12, color: T.textSecondary, flex: 1 }}>
          {name} <span style={{ color: T.textFaint, fontSize: 10 }}>{Math.round(weight * 100)}%</span>
        </span>
        <span style={{ fontSize: 12, fontFamily: "'DM Mono', monospace" }}>
          <span style={{ color: T.detection, fontWeight: 700 }}>{detVal}</span>
          <span style={{ color: T.textFaint }}> / </span>
          <span style={{ color: T.confidence, fontWeight: 700 }}>{confVal}</span>
        </span>
      </div>
      <div style={{ height: 4, background: T.detectionLight, borderRadius: 2, overflow: "hidden", marginBottom: 3 }}>
        <div style={{ height: "100%", width: `${Math.min(detVal, 100)}%`, background: T.detection, borderRadius: 2, transition: "width 1s ease" }} />
      </div>
      <div style={{ height: 4, background: T.confidenceLight, borderRadius: 2, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${Math.min(confVal, 100)}%`, background: T.confidence, borderRadius: 2, transition: "width 1s ease" }} />
      </div>
      {desc && (
        <div style={{ fontSize: 9, color: T.textFaint, lineHeight: 1.5, marginTop: 4, fontStyle: "italic" }}>
          {desc}
        </div>
      )}
    </div>
  );
}

// ── GAP WARNING BOX ──────────────────────────────────────────────
function GapWarning({ gap }) {
  const { label } = gapMeta(gap);
  const msg = gap > 35
    ? "The engine sees it. Confirmation data hasn't arrived yet. High potential, not yet proven."
    : gap > 15
    ? "Signal is building. Multiple windows of evidence are accumulating."
    : "Both scores agree — this is a high-conviction signal in either direction.";
  return (
    <div style={{
      padding: "12px 14px", borderRadius: 10,
      background: T.goldLight, border: `1px solid ${T.goldBorder}`,
      display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 16,
    }}>
      <span style={{ fontSize: 15, flexShrink: 0, marginTop: 1 }}>⚠</span>
      <div>
        <div style={{ fontSize: 12, fontWeight: 700, color: T.gold, marginBottom: 3 }}>
          {gap}-point gap = {label.toLowerCase()}
        </div>
        <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.5 }}>{msg}</div>
      </div>
    </div>
  );
}

// ── WHY SCORES DIVERGE ───────────────────────────────────────────
function WhyDiverge({ data }) {
  const inertia = data.inertia_score || 0;
  const medium  = data.medium_sequence_score || data.platform_diversity || 0;
  const ftr     = Math.round((data.first_timer_ratio || 0) * 100);
  const niche   = data.niche_signal_count || data.niche_mentions || 0;
  const mainstream = data.mainstream_signal_count || data.mainstream_mentions || 0;
  const rows = [
    { label: "Inertia window",       det: inertia >= 50 ? "2 windows"     : "1 window",    conf: inertia >= 70 ? "4 windows" : "2 windows" },
    { label: "Platform pattern",     det: medium  >= 50 ? "Partial match" : "No match",    conf: medium  >= 70 ? "Full match" : "Partial match" },
    { label: "First-timer trigger",  det: `≥ ${ftr}%`,                                     conf: `≥ ${Math.min(ftr + 10, 90)}%` },
    { label: "Mainstream penalty",   det: niche > mainstream ? "Gradual"   : "Applied",     conf: "Strict" },
  ];
  return (
    <div>
      <div style={{ fontSize: 10, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700, marginBottom: 10 }}>
        WHY THE SCORES DIVERGE
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {rows.map(row => (
          <div key={row.label} style={{
            padding: "8px 10px", borderRadius: 8,
            background: T.bg, border: `1px solid ${T.cardBorder}`,
          }}>
            <div style={{ fontSize: 9, color: T.textFaint, marginBottom: 5, letterSpacing: 0.5, textTransform: "uppercase" }}>
              {row.label}
            </div>
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              <span style={{ fontSize: 11, color: T.detection, fontWeight: 600 }}>{row.det}</span>
              <span style={{ fontSize: 10, color: T.textFaint }}>/</span>
              <span style={{ fontSize: 11, color: T.confidence, fontWeight: 600 }}>{row.conf}</span>
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, fontSize: 10, color: T.textFaint }}>
        Blue = Detection mode · Green = Confidence mode
      </div>
    </div>
  );
}

// ── TOPIC DETAIL CARD (left half of detail view) ─────────────────
function TopicDetailCard({ data }) {
  const gap    = Math.abs(Math.round((data.detection_score || 0) - (data.confidence_score || 0)));
  const plats  = data.active_platforms || [];
  const det    = Math.round(data.detection_score  || 0);
  const stage  = data.signal_stage || "MONITORING";
  const fpr    = data.false_positive_risk || "high";
  const lead   = Math.round(data.lead_time_estimate_days || 0);

  return (
    <div style={{ padding: "20px 22px" }}>
      {/* Header */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 9, color: T.textFaint, letterSpacing: 1.5, marginBottom: 4, textTransform: "uppercase" }}>
          Now TrendIn · Signal Intel
        </div>
        <h2 style={{
          fontSize: 22, fontWeight: 800, color: T.textPrimary, lineHeight: 1.2,
          textTransform: "lowercase", letterSpacing: -0.3, marginBottom: 6,
        }}>
          {data.topic}
        </h2>
        <div style={{ fontSize: 11, color: T.textMuted }}>
          {data.signal_count} signals · {plats.map(p => `${srcIcon(p)} ${platformName(p)}`).join(" · ")} · {timeAgo(data.computed_at)}
        </div>
      </div>

      {/* Tagline */}
      <div style={{
        padding: "10px 12px", borderRadius: 8,
        background: T.bg, border: `1px solid ${T.cardBorder}`,
        display: "flex", gap: 8, alignItems: "flex-start", marginBottom: 14,
      }}>
        <span style={{ fontSize: 14, flexShrink: 0 }}>⚖</span>
        <span style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.5 }}>
          <strong>Two scores, one engine.</strong> Earlier detection = lower certainty. You choose.
        </span>
      </div>

      {/* ── MATURITY BADGE — explains WHY the score is what it is ────
           Shown when calibration data is present (backend v2+).
           Without this, a permanently-ESTABLISHED topic at D:48 looks
           identical to a genuinely new topic — very misleading. */}
      {data.calibration && <MaturityBadge calibration={data.calibration} />}

      {/* ── AI SCORE WITH CONTEXT — tier headline + score pair ────────
           Shown only for topics in the AI taxonomy (ai_tier present).
           Explains immediately whether this is VIRAL/STRONG/ESTABLISHED/
           MAINSTREAM and what that means for interpretation.
           'AI (generic)' scores 26 AND shows "Mainstream — Already Arrived"
           so the low score is never confusing. */}
      <AIScoreWithContext signal={data} />

      {/* ── RESEARCH HISTORY — how long has this been discussed? ──────
           Provides context critical for interpreting the Gradient Score.
           'ai agent' scoring 84 could mean genuine emergence (new term)
           OR permanent expert-community home (3+ years established).
           This panel resolves that ambiguity. Lazy-fetched on expand. */}
      <ResearchHistoryPanel
        topicKey={data.topic_key || (data.topic || "").toLowerCase().replace(/\s+/g, "_")}
        topicDisplay={data.topic || data.topic_key}
      />

      {/* ── WHAT TO DO — calibrated action (or legacy fallback) ──────
           WhatToDoPanel is driven by backend apply_calibration():
           - what_to_do_action / urgency / instruction / detail
           If those fields aren't present (pre-calibration data),
           the legacy score-based heuristic renders instead. */}
      {data.what_to_do_action
        ? <WhatToDoPanel signal={data} />
        : (() => {
            const actionMap = det >= 85
              ? { title: "Act now",                      sub: "Breakout confirmed. Move before mainstream. Both scores signal high conviction.", c: T.confidence, bg: T.confidenceLight, border: T.confidenceBorder }
              : det >= 70
              ? { title: "Act with confidence",           sub: "Strong signal from multiple sources. Creators & marketers: act now. Institutions: 24–48h to confirm.", c: T.detection, bg: T.detectionLight, border: T.detectionBorder }
              : det >= 55 && gap > 35
              ? { title: "First-mover window open",       sub: "Very early detection — highest lead time available. Ideal for content creators who want maximum head start.", c: T.orange, bg: T.orangeLight, border: "#FDBA74" }
              : det >= 55
              ? { title: "Emerging — creators act now",   sub: "Signal building toward confirmation. Creators: this is your window. Institutions: wait for Confidence Score to catch up.", c: T.goldMid, bg: T.goldLight, border: T.goldBorder }
              : det >= 35
              ? { title: "Monitor — signal building",     sub: "Not yet confirmed. The engine is watching — check back after the next collection run.", c: T.textMuted, bg: T.bg, border: T.cardBorder }
              : { title: "Wait — insufficient signal",    sub: "Below action threshold. Act only when the score reaches EMERGING (55+) or higher.", c: T.textFaint, bg: T.bg, border: T.cardBorder };
            const { title, sub, c, bg, border } = actionMap;
            return (
              <div style={{ padding: "14px 16px", borderRadius: 10, marginBottom: 16, background: bg, border: `1px solid ${border}` }}>
                <div style={{ fontSize: 9, letterSpacing: 1.2, fontWeight: 700, color: c, marginBottom: 6 }}>WHAT TO DO</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: c, marginBottom: 5, lineHeight: 1.2 }}>{title}</div>
                <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.6 }}>{sub}</div>
                <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
                  <span style={{
                    fontSize: 8, fontWeight: 700, padding: "2px 8px", borderRadius: 4,
                    color: fpr === "low" ? T.confidence : fpr === "medium" ? T.goldMid : T.textFaint,
                    background: fpr === "low" ? T.confidenceLight : fpr === "medium" ? T.goldLight : T.bg,
                    border: `1px solid ${fpr === "low" ? T.confidenceBorder : fpr === "medium" ? T.goldBorder : T.cardBorder}`,
                  }}>
                    {fpr === "low" ? "Low false-positive risk — act with confidence" : fpr === "medium" ? "Medium false-positive risk" : "High false-positive risk — wait for confirmation"}
                  </span>
                  {lead > 0 && (
                    <span style={{ fontSize: 9, color: c, fontWeight: 700 }}>
                      Est. {lead} days before Google Trends breakout
                    </span>
                  )}
                </div>
              </div>
            );
          })()
      }

      {/* ── Score display — calibrated (CalibratedScoreDisplay) or legacy ──
           CalibratedScoreDisplay is used when calibration data is present:
           - directional gap label (not just a size number)
           - lead time HIDDEN when inertia = 0
           - first-run notice instead of confusing zeroes
           Legacy two-box grid is the fallback for pre-calibration data. */}
      {data.component_groups
        ? <CalibratedScoreDisplay signal={data} />
        : (
          <>
            {/* Legacy score circles side by side */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 4 }}>
              <div style={{ padding: "16px 10px", borderRadius: 12, textAlign: "center", background: T.detectionLight, border: `1px solid ${T.detectionBorder}` }}>
                <div style={{ fontSize: 9, letterSpacing: 1.5, color: T.detection, fontWeight: 700, marginBottom: 10 }}>DETECTION SCORE</div>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 10 }}>
                  <ScoreCircle score={data.detection_score} color={T.detection} trackColor={T.detectionBorder} size={96} />
                </div>
                <div style={{ display: "inline-block", padding: "3px 10px", borderRadius: 20, border: `1px solid ${T.detectionBorder}`, background: "white", fontSize: 10, color: T.detection, fontWeight: 600, marginBottom: 8 }}>
                  {detLabel(data.detection_score || 0)}
                </div>
                <div style={{ fontSize: 9, color: T.textFaint }}>False positive risk</div>
                <div style={{ fontSize: 12, color: T.textSecondary, fontWeight: 700 }}>~22% false positive</div>
              </div>
              <div style={{ padding: "16px 10px", borderRadius: 12, textAlign: "center", background: T.confidenceLight, border: `1px solid ${T.confidenceBorder}` }}>
                <div style={{ fontSize: 9, letterSpacing: 1.5, color: T.confidence, fontWeight: 700, marginBottom: 10 }}>CONFIDENCE SCORE</div>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 10 }}>
                  <ScoreCircle score={data.confidence_score} color={T.confidence} trackColor={T.confidenceBorder} size={96} />
                </div>
                <div style={{ display: "inline-block", padding: "3px 10px", borderRadius: 20, border: `1px solid ${T.confidenceBorder}`, background: "white", fontSize: 10, color: T.confidence, fontWeight: 600, marginBottom: 8 }}>
                  {confLabel(data.confidence_score || 0)}
                </div>
                <div style={{ fontSize: 9, color: T.textFaint }}>False positive risk</div>
                <div style={{ fontSize: 12, color: T.textSecondary, fontWeight: 700 }}>&lt;9% false positive</div>
              </div>
            </div>
            {gap > 5 && <GapWarning gap={gap} />}
          </>
        )
      }

      {/* ── Why This Matters + What To Watch ──────────────────────────
           Moved to appear EARLY — per Master Analysis Section 04:
           "These are not optional UX features — they ARE the product."
           Showing them at the top means every user sees them immediately. */}
      {(data.is_gravitational_anomaly || data.why_this_matters || data.what_to_watch) && (
        <div style={{ marginBottom: 20 }}>
          {data.is_gravitational_anomaly && (
            <div style={{
              padding: "10px 12px", borderRadius: 8, marginBottom: 8,
              background: T.confidenceLight, border: `1px solid ${T.confidenceBorder}`,
              display: "flex", alignItems: "flex-start", gap: 8,
            }}>
              <span style={{ fontSize: 14, flexShrink: 0 }}>★</span>
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, color: T.confidence, marginBottom: 3 }}>
                  Gravitational Anomaly confirmed
                </div>
                <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.5 }}>
                  {data.anomaly_reason || "Multiple anomaly indicators fired simultaneously."}
                </div>
              </div>
            </div>
          )}
          {data.why_this_matters && (
            <div style={{ padding: "10px 12px", borderRadius: 8, marginBottom: 8, background: T.bg, border: `1px solid ${T.cardBorder}` }}>
              <div style={{ fontSize: 9, color: T.textFaint, fontWeight: 700, letterSpacing: 0.8, marginBottom: 4 }}>WHY THIS MATTERS</div>
              <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.6 }}>{data.why_this_matters}</div>
            </div>
          )}
          {data.what_to_watch && (
            <div style={{ padding: "10px 12px", borderRadius: 8, background: T.bg, border: `1px solid ${T.cardBorder}` }}>
              <div style={{ fontSize: 9, color: T.textFaint, fontWeight: 700, letterSpacing: 0.8, marginBottom: 4 }}>WHAT TO WATCH</div>
              <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.6 }}>{data.what_to_watch}</div>
            </div>
          )}
        </div>
      )}

      {/* ── Score breakdown — 3 calibrated groups or legacy 7-bar flat ──
           CalibratedComponentBreakdown shows when component_groups is present:
           - 3 expandable buckets: Signal Quality / Momentum / Context
           - Inertia shows "Pending" (not confusing zero) on first run
           - Gradient Strength shows raw→calibrated note for ESTABLISHED topics
           Legacy DualBar rows are the fallback. */}
      <div style={{ marginBottom: 20 }}>
        {(data.component_groups && Object.keys(data.component_groups).length > 0)
          ? <CalibratedComponentBreakdown signal={data} />
          : (
            <>
              <div style={{ fontSize: 10, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700, marginBottom: 12 }}>
                SCORE BREAKDOWN — BOTH MODES
              </div>
              {[
                { letter: "G", name: "Gradient strength",  weight: OVR_W.G, score: data.gradient_strength,       dw: DET_W.G, cw: CONF_W.G, desc: "Niche vs mainstream concentration — high means experts discussing before the public knows." },
                { letter: "I", name: "Inertia",             weight: OVR_W.I, score: data.inertia_score,           dw: DET_W.I, cw: CONF_W.I, desc: "Acceleration sustained across multiple time windows — rules out one-day spikes." },
                { letter: "M", name: "Platform diversity",  weight: OVR_W.M, score: data.medium_sequence_score,   dw: DET_W.M, cw: CONF_W.M, desc: "Cross-platform spread matches known diffusion pattern (GitHub → HN → Reddit = Pattern A)." },
                { letter: "D", name: "Dark matter",         weight: OVR_W.D, score: data.dark_matter_score,       dw: DET_W.D, cw: CONF_W.D, desc: "First-timer ratio — many new voices entering a community signals hidden demand overflowing." },
                { letter: "C", name: "Confidence decay",    weight: OVR_W.C, score: data.confidence_decay,        dw: DET_W.C, cw: CONF_W.C, desc: "Signal freshness — drops as trend matures and mainstream platforms pick it up." },
                { letter: "P", name: "Persistence",         weight: OVR_W.P, score: data.persistence_score || 0, dw: DET_W.P, cw: CONF_W.P, highlight: T.purple, desc: "Sustained elevation across scoring cycles — not a spike but a genuine lasting trend." },
                { letter: "N", name: "NowTrendIn",          weight: OVR_W.N, score: data.nowtrendin_score || 0,  dw: DET_W.N, cw: CONF_W.N, highlight: T.flame,  desc: "Internal demand signal — how often this topic appears in user result sets within the app." },
              ].map(c => (
                <DualBar key={c.letter} {...c} />
              ))}
            </>
          )
        }
      </div>

      {/* Persistence / lifecycle summary */}
      {(data.persistence_cycles > 0 || data.persistence_streak > 0) && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 10, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700, marginBottom: 10 }}>
            TREND LIFECYCLE — P COMPONENT
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {[
              {
                label: "Scoring cycles",
                val: data.persistence_cycles || 0,
                sub: "times measured",
                color: T.textSecondary,
              },
              {
                label: "Current streak",
                val: data.persistence_streak || 0,
                sub: "consecutive above threshold",
                color: data.persistence_streak >= 3 ? T.confidence : T.textSecondary,
              },
              {
                label: "Persistence rate",
                val: `${Math.round((data.persistence_rate || 0) * 100)}%`,
                sub: "cycles above emerging",
                color: (data.persistence_rate || 0) >= 0.7 ? T.confidence : T.textSecondary,
              },
              {
                label: "Active for",
                val: (() => {
                  const h = data.trend_age_hours || 0;
                  return h < 24 ? `${Math.round(h)}h` : `${Math.round(h / 24)}d`;
                })(),
                sub: "since first detection",
                color: T.textSecondary,
              },
            ].map(row => (
              <div key={row.label} style={{
                padding: "8px 10px", borderRadius: 8,
                background: T.bg, border: `1px solid ${T.cardBorder}`,
              }}>
                <div style={{ fontSize: 9, color: T.textFaint, marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
                  {row.label}
                </div>
                <div style={{ fontSize: 18, fontWeight: 800, color: row.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                  {row.val}
                </div>
                <div style={{ fontSize: 9, color: T.textFaint, marginTop: 2 }}>{row.sub}</div>
              </div>
            ))}
          </div>
          {data.confirmed_trend && (
            <div style={{
              marginTop: 8, padding: "8px 12px", borderRadius: 8,
              background: T.confidenceLight, border: `1px solid ${T.confidenceBorder}`,
              display: "flex", alignItems: "center", gap: 8,
            }}>
              <span style={{ fontSize: 14 }}>✓</span>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: T.confidence }}>Confirmed sustained trend</div>
                <div style={{ fontSize: 10, color: T.textSecondary }}>
                  Reached STRONG level in 2+ scoring cycles. Institutional-grade signal.
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* NowTrendIn / N component summary */}
      {(data.nowtrendin_score > 0 || data.nowtrendin_queries_30d > 0) && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 10, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700, marginBottom: 10 }}>
            INTERNAL DEMAND — N COMPONENT
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {[
              {
                label: "Total appearances",
                val: data.nowtrendin_queries_30d || 0,
                sub: "in user results (30 days)",
                color: (data.nowtrendin_queries_30d || 0) >= 20 ? T.flame : T.textSecondary,
              },
              {
                label: "Last 24 hours",
                val: data.nowtrendin_queries_24h || 0,
                sub: "recent query events",
                color: (data.nowtrendin_queries_24h || 0) > (data.nowtrendin_daily_rate || 0)
                  ? T.flame : T.textSecondary,
              },
              {
                label: "Daily avg (7d)",
                val: `${Math.round(data.nowtrendin_daily_rate || 0)}/day`,
                sub: "baseline query rate",
                color: T.textSecondary,
              },
              {
                label: "N score",
                val: Math.round(data.nowtrendin_score || 0),
                sub: "internal demand score",
                color: (data.nowtrendin_score || 0) >= 40 ? T.flame : T.textSecondary,
              },
            ].map(row => (
              <div key={row.label} style={{
                padding: "8px 10px", borderRadius: 8,
                background: T.bg, border: `1px solid ${T.cardBorder}`,
              }}>
                <div style={{ fontSize: 9, color: T.textFaint, marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
                  {row.label}
                </div>
                <div style={{ fontSize: 18, fontWeight: 800, color: row.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                  {row.val}
                </div>
                <div style={{ fontSize: 9, color: T.textFaint, marginTop: 2 }}>{row.sub}</div>
              </div>
            ))}
          </div>
          {(data.nowtrendin_queries_24h || 0) > (data.nowtrendin_daily_rate || 0) && (data.nowtrendin_daily_rate || 0) > 0 && (
            <div style={{
              marginTop: 8, padding: "8px 12px", borderRadius: 8,
              background: T.flameLight, border: `1px solid ${T.flameBorder}`,
              display: "flex", alignItems: "center", gap: 8,
            }}>
              <span style={{ fontSize: 14 }}>🔥</span>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: T.flame }}>Rising user demand</div>
                <div style={{ fontSize: 10, color: T.textSecondary }}>
                  Last 24h queries above 7-day baseline — users are actively seeking this topic.
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Why scores diverge */}
      <WhyDiverge data={data} />

      {/* ── AI VARIATION MAP — shows all related AI topics ranked ─────
           The core answer to "why does 'AI' score 26 when AI is viral?"
           For any AI topic this shows the full spectrum: agentic coding
           at DET 97 / CONF 95 (VIRAL) down to 'ai' at DET 26 (MAINSTREAM).
           Shows ONLY when the backend has classified this as an AI topic.
           The variation list is collapsible to avoid UX bloat. */}
      <AIVariationMap signal={data} />

      {/* Engine Analysis (Why This Matters / What To Watch) has been moved
           to appear immediately after the gap warning — above the score
           breakdown — so every user sees the plain-English explanation
           before reaching the technical detail. */}
    </div>
  );
}

// ── HEISENBERG PANEL (right half of detail view) ─────────────────
// All data displayed here is fetched live from the backend.
// No projections or estimates — only actual recorded scoring events.
function HeisenbergPanel({ data }) {
  const gap   = Math.abs(Math.round((data.detection_score || 0) - (data.confidence_score || 0)));
  const meta  = gapMeta(gap);
  const det   = Math.round(data.detection_score || 0);
  const conf  = Math.round(data.confidence_score || 0);
  const topicKey = data.topic_key || (data.topic || "").toLowerCase().replace(/\s+/g, "_");

  // ── Live score history fetched from /history/{topic_key} ──────
  const [history,     setHistory]     = useState([]);
  const [histLoading, setHistLoading] = useState(false);
  const [histFetched, setHistFetched] = useState(false);

  useEffect(() => {
    if (!topicKey) return;
    setHistLoading(true);
    setHistFetched(false);
    fetch(`${API_BASE}/history/${topicKey}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d && d.history) setHistory(d.history.slice(0, 10)); // last 10 scoring events
        setHistFetched(true);
      })
      .catch(() => setHistFetched(true))
      .finally(() => setHistLoading(false));
  }, [topicKey]);

  const gapRows = [
    { range: "0–15 pts",  desc: "Both agree — high conviction either way",   color: T.confidence, bg: T.confidenceLight },
    { range: "16–35 pts", desc: "Early stage — confirmation building",        color: T.goldMid,   bg: T.goldLight },
    { range: "36–60 pts", desc: "Very early — detected, not confirmed",       color: T.orange,    bg: T.orangeLight },
    { range: "60+ pts",   desc: "Speculative — dark matter signal only",      color: T.purple,    bg: T.purpleLight },
  ];

  return (
    <div style={{ padding: "24px 24px" }}>
      <h3 style={{ fontSize: 20, fontWeight: 800, color: T.textPrimary, marginBottom: 10 }}>
        Dual Score Analysis
      </h3>
      <p style={{ fontSize: 13, color: T.textSecondary, lineHeight: 1.65, marginBottom: 18 }}>
        The same measurements run once. Two different threshold rule-sets produce two scores. The gap between them tells you how early this signal is.
      </p>

      {/* Legend */}
      <div style={{ display: "flex", gap: 16, marginBottom: 22 }}>
        {[{ color: T.detection, label: "Detection" }, { color: T.confidence, label: "Confidence" }].map(l => (
          <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: l.color }} />
            <span style={{ fontSize: 12, color: T.textSecondary }}>{l.label}</span>
          </div>
        ))}
      </div>

      {/* Gap interpretation */}
      <div style={{ border: `1px solid ${T.cardBorder}`, borderRadius: 12, overflow: "hidden", marginBottom: 16 }}>
        <div style={{ padding: "10px 16px", background: T.bg, borderBottom: `1px solid ${T.cardBorder}` }}>
          <div style={{ fontSize: 9, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700 }}>GAP INTERPRETATION</div>
        </div>
        <div style={{ padding: "14px 16px" }}>
          {gapRows.map(row => (
            <div key={row.range} style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 10 }}>
              <div style={{ width: 4, borderRadius: 2, alignSelf: "stretch", background: row.color, flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: T.textPrimary, fontFamily: "'DM Mono', monospace", marginBottom: 1 }}>
                  {row.range}
                </div>
                <div style={{ fontSize: 11, color: T.textSecondary }}>{row.desc}</div>
              </div>
            </div>
          ))}
          <div style={{
            marginTop: 10, padding: "8px 12px", borderRadius: 8,
            background: meta.bg, border: `1px solid ${meta.border}`,
          }}>
            <div style={{ fontSize: 12, color: meta.color, fontWeight: 700 }}>
              This signal: {gap}-point gap — {meta.label}
            </div>
          </div>
        </div>
      </div>

      {/* Who uses which score */}
      <div style={{ border: `1px solid ${T.cardBorder}`, borderRadius: 12, overflow: "hidden", marginBottom: 16 }}>
        <div style={{ padding: "10px 16px", background: T.bg, borderBottom: `1px solid ${T.cardBorder}` }}>
          <div style={{ fontSize: 9, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700 }}>WHO USES WHICH SCORE</div>
        </div>
        <div style={{ padding: "12px 16px", display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ padding: "12px", borderRadius: 8, background: T.detectionLight, border: `1px solid ${T.detectionBorder}` }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: T.detection, marginBottom: 4 }}>
              Detection score: {det}
            </div>
            <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.5 }}>
              Content creators, brand managers, trend-forward marketers. Speed creates value. Accepts ~1 in 5 false alarms — confirmed by engine backtesting.
            </div>
          </div>
          <div style={{ padding: "12px", borderRadius: 8, background: T.confidenceLight, border: `1px solid ${T.confidenceBorder}` }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: T.confidence, marginBottom: 4 }}>
              Confidence score: {conf}
            </div>
            <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.5 }}>
              Institutional analysts, strategic planners, investors. Precision over speed. Requires 4+ sustained evidence windows — confirmed by engine backtesting.
            </div>
          </div>
        </div>
      </div>

      {/* ── REAL scoring history — fetched live from /history/{topic_key} ── */}
      <div style={{ border: `1px solid ${T.cardBorder}`, borderRadius: 12, overflow: "hidden" }}>
        <div style={{ padding: "10px 16px", background: T.bg, borderBottom: `1px solid ${T.cardBorder}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 9, letterSpacing: 1.2, color: T.textFaint, fontWeight: 700 }}>
            ACTUAL SCORING HISTORY
          </div>
          <div style={{ fontSize: 9, color: T.textFaint }}>live from database</div>
        </div>
        <div style={{ padding: "14px 16px" }}>
          {histLoading && (
            <div style={{ fontSize: 11, color: T.textFaint, textAlign: "center", padding: "12px 0" }}>
              Loading history…
            </div>
          )}
          {histFetched && !histLoading && history.length === 0 && (
            <div style={{ fontSize: 11, color: T.textFaint, textAlign: "center", padding: "12px 0" }}>
              Only one scoring event recorded so far.
              <br />
              <span style={{ fontSize: 10 }}>Run more collections to build a history.</span>
            </div>
          )}
          {history.length > 0 && (
            <>
              {/* Column headers */}
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <div style={{ flex: 1, fontSize: 8, color: T.textFaint, fontWeight: 700, letterSpacing: 0.8 }}>SCORED AT</div>
                <div style={{ width: 34, textAlign: "center", fontSize: 8, color: T.detection, fontWeight: 700, letterSpacing: 0.5 }}>DET</div>
                <div style={{ width: 34, textAlign: "center", fontSize: 8, color: T.confidence, fontWeight: 700, letterSpacing: 0.5 }}>CONF</div>
                <div style={{ width: 34, textAlign: "center", fontSize: 8, color: T.textFaint, fontWeight: 700, letterSpacing: 0.5 }}>GAP</div>
              </div>
              {history.map((h, i) => {
                const hDet  = Math.round(h.detection_score  || 0);
                const hConf = Math.round(h.confidence_score || 0);
                const hGap  = Math.abs(hDet - hConf);
                const isLatest = i === 0;
                const ts = h.scored_at
                  ? new Date(h.scored_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: true })
                  : "—";
                return (
                  <div key={i} style={{
                    display: "flex", alignItems: "center", gap: 10,
                    padding: "6px 0",
                    borderBottom: i < history.length - 1 ? `1px solid ${T.cardBorder}` : "none",
                    background: isLatest ? T.detectionLight + "60" : "none",
                    borderRadius: isLatest ? 4 : 0,
                  }}>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: 10, color: isLatest ? T.detection : T.textMuted, fontFamily: "'DM Mono', monospace" }}>
                        {ts}
                      </span>
                      {isLatest && (
                        <span style={{ marginLeft: 6, fontSize: 8, color: T.detection, fontWeight: 700, letterSpacing: 0.5 }}>LATEST</span>
                      )}
                    </div>
                    <div style={{ width: 34, textAlign: "center", fontSize: 13, fontWeight: 800, color: T.detection, fontFamily: "'DM Mono', monospace" }}>{hDet}</div>
                    <div style={{ width: 34, textAlign: "center", fontSize: 13, fontWeight: 800, color: T.confidence, fontFamily: "'DM Mono', monospace" }}>{hConf}</div>
                    <div style={{ width: 34, textAlign: "center" }}>
                      <span style={{
                        fontSize: 10, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                        color: hGap <= 15 ? T.confidence : hGap <= 35 ? T.goldMid : T.orange,
                      }}>{hGap}pt</span>
                    </div>
                  </div>
                );
              })}
              <div style={{ marginTop: 10, fontSize: 10, color: T.textFaint, lineHeight: 1.6 }}>
                Each row is a real scoring event from a collection run. Scores change as new signals are collected.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── TOPIC LIST CARD ───────────────────────────────────────────────
function TopicCard({ data, onClick, isSelected }) {
  const gap   = Math.abs(Math.round((data.detection_score || 0) - (data.confidence_score || 0)));
  const plats = data.active_platforms || [];
  const meta  = gapMeta(gap);

  return (
    <div
      onClick={() => onClick(data)}
      style={{
        padding: "14px 16px", borderRadius: 12, cursor: "pointer", marginBottom: 8,
        background: isSelected ? T.detectionLight : T.card,
        border: `1px solid ${isSelected ? T.detection : T.cardBorder}`,
        transition: "all 0.15s",
      }}
      onMouseEnter={e => !isSelected && (e.currentTarget.style.borderColor = "#CBD5E1")}
      onMouseLeave={e => !isSelected && (e.currentTarget.style.borderColor = T.cardBorder)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <div style={{ flex: 1, paddingRight: 12 }}>
          <div style={{ fontSize: 9, color: T.textFaint, marginBottom: 4 }}>
            {plats.map(p => `${srcIcon(p)} ${platformName(p)}`).join(" · ")} · {data.signal_count} signals · {timeAgo(data.computed_at)}
          </div>
          <div style={{
            fontSize: 15, fontWeight: 800, color: T.textPrimary,
            textTransform: "lowercase", marginBottom: 5, lineHeight: 1.3,
          }}>
            {data.topic}
          </div>
          <div style={{ fontSize: 10, color: T.textMuted }}>{patternLabel(data.diffusion_pattern)}</div>
          {/* Action instruction — Level 3: Action Clarity. Answers "what should I do?" */}
          <div style={{
            fontSize: 10, fontWeight: 700, marginTop: 4,
            color: stageColor(data.signal_stage || "MONITORING"),
          }}>
            → {stageActionLine(data.signal_stage || "MONITORING", gap)}
          </div>
        </div>

        {/* Detection | Confidence + stage label */}
        <div style={{ flexShrink: 0, textAlign: "center" }}>
          {/* Stage pill — the one-word answer to "how urgent is this?" */}
          {(() => {
            try {
              const raw = (data.signal_stage || "MONITORING").toString().toUpperCase().trim();
              const STAGE_STYLES = {
                BREAKOUT:   { color: T.confidence, bg: T.confidenceLight, border: T.confidenceBorder },
                STRONG:     { color: T.detection,  bg: T.detectionLight,  border: T.detectionBorder },
                EMERGING:   { color: T.goldMid,    bg: T.goldLight,       border: T.goldBorder },
                WATCHING:   { color: T.orange,     bg: T.orangeLight,     border: "#FDBA74" },
                WATCH:      { color: T.orange,     bg: T.orangeLight,     border: "#FDBA74" },
                MONITORING: { color: T.textFaint,  bg: T.bg,              border: T.cardBorder },
              };
              const style = STAGE_STYLES[raw] || STAGE_STYLES.MONITORING;
              const label = raw === "WATCH" ? "WATCHING" : (STAGE_STYLES[raw] ? raw : "MONITORING");
              return (
                <div style={{
                  marginBottom: 5, padding: "2px 10px", borderRadius: 20,
                  background: style.bg, border: `1px solid ${style.border}`,
                  fontSize: 9, fontWeight: 800, color: style.color,
                  letterSpacing: 0.6, whiteSpace: "nowrap",
                }}>
                  {label}
                </div>
              );
            } catch { return null; }
          })()}

          <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 8, color: T.detection, fontWeight: 700, letterSpacing: 0.5, marginBottom: 1 }}>DET</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: T.detection, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                {Math.round(data.detection_score || 0)}
              </div>
            </div>
            <div style={{ fontSize: 14, color: T.textFaint, paddingBottom: 2 }}>|</div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 8, color: T.confidence, fontWeight: 700, letterSpacing: 0.5, marginBottom: 1 }}>CONF</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: T.confidence, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                {Math.round(data.confidence_score || 0)}
              </div>
            </div>
          </div>

          {/* Gap sentence — full plain-English interpretation */}
          {gap > 5 && (
            <div style={{
              marginTop: 5, fontSize: 9, color: meta.color, fontWeight: 700,
              background: meta.bg, padding: "2px 7px", borderRadius: 4,
              border: `1px solid ${meta.border}`, whiteSpace: "nowrap",
            }}>
              {gap}pt gap
            </div>
          )}
          {data.is_gravitational_anomaly && (
            <div style={{
              marginTop: 4, fontSize: 9, color: T.confidence, fontWeight: 700,
              background: T.confidenceLight, padding: "1px 7px", borderRadius: 4,
              border: `1px solid ${T.confidenceBorder}`, whiteSpace: "nowrap",
            }}>
              ★ ANOMALY
            </div>
          )}
          {/* Maturity mini tag — shown only when calibration data is present */}
          {data.calibration && <MaturityMiniTag calibration={data.calibration} />}
          {/* AI tier badge — shown when topic is in the AI taxonomy */}
          <AITierBadge signal={data} />
        </div>
      </div>

      {/* 7-component mini bars (G I M D C P N) */}
      <div style={{ display: "flex", gap: 3 }}>
        {[
          { val: data.gradient_strength,      color: T.detection },
          { val: data.inertia_score,           color: T.confidence },
          { val: data.medium_sequence_score,   color: T.detection },
          { val: data.dark_matter_score,       color: T.confidence },
          { val: data.confidence_decay,        color: T.detection },
          { val: data.persistence_score || 0,  color: T.purple },    // P — purple
          { val: data.nowtrendin_score  || 0,  color: T.flameMid },   // N — flame
        ].map((bar, i) => (
          <div key={i} style={{ flex: 1, height: 3, background: T.bg, borderRadius: 2, overflow: "hidden" }}>
            <div style={{
              height: "100%", width: `${Math.max(bar.val || 0, 0)}%`,
              background: bar.color, borderRadius: 2,
            }} />
          </div>
        ))}
      </div>

      {/* Gap sentence — Step 1.3: full plain-English interpretation of the gap */}
      {gap > 5 && (
        <div style={{
          marginTop: 6, padding: "5px 10px", borderRadius: 6,
          background: meta.bg, border: `1px solid ${meta.border}`,
          fontSize: 10, color: meta.color,
        }}>
          <span style={{ fontWeight: 700 }}>{gap}-point gap: </span>
          {gap <= 15
            ? "Both scores agree — high conviction signal"
            : gap <= 35
            ? "Confirmation building — 24–72h to alignment"
            : gap <= 60
            ? "Detected, not yet confirmed — act early or wait"
            : "Speculative — dark matter signal, confirmation pending"}
        </div>
      )}

      {/* Persistence + NowTrendIn meta row */}
      {(data.persistence_streak >= 2 || data.confirmed_trend || (data.nowtrendin_score || 0) >= 20) && (
        <div style={{ marginTop: 6, display: "flex", gap: 5, alignItems: "center", flexWrap: "wrap" }}>
          {data.confirmed_trend && (
            <div style={{
              fontSize: 8, color: T.confidence, fontWeight: 700,
              background: T.confidenceLight, padding: "1px 6px", borderRadius: 4,
              border: `1px solid ${T.confidenceBorder}`,
            }}>✓ CONFIRMED</div>
          )}
          {data.persistence_streak >= 2 && (
            <div style={{ fontSize: 9, color: T.purple }}>
              {data.persistence_streak} cycle streak · {Math.round((data.persistence_rate || 0) * 100)}% persistent
            </div>
          )}
          {(data.nowtrendin_score || 0) >= 20 && (
            <div style={{
              fontSize: 8, color: T.flame, fontWeight: 700,
              background: T.flameLight, padding: "1px 6px", borderRadius: 4,
              border: `1px solid ${T.flameBorder}`,
            }}>
              N·{Math.round(data.nowtrendin_score || 0)} demand
            </div>
          )}
          {(data.trend_age_hours || 0) > 0 && (
            <div style={{ fontSize: 9, color: T.textFaint, marginLeft: "auto" }}>
              {(data.trend_age_hours || 0) < 24
                ? `${Math.round(data.trend_age_hours)}h active`
                : `${Math.round(data.trend_age_hours / 24)}d active`}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── HEADER ───────────────────────────────────────────────────────
function Header({ lastUpdated, onRefresh, onCollect, loading, collecting, collectMsg, topicCount, scores }) {
  const [narrow, setNarrow] = useState(() => typeof window !== "undefined" && window.innerWidth < 600);
  useEffect(() => {
    const h = () => setNarrow(window.innerWidth < 600);
    window.addEventListener("resize", h);
    return () => window.removeEventListener("resize", h);
  }, []);

  const isLive = scores && scores.length > 0;

  if (narrow) {
    // ── MOBILE HEADER: two compact rows ──────────────────────────
    return (
      <div style={{
        borderBottom: `1px solid ${T.cardBorder}`, background: T.surface,
        position: "sticky", top: 0, zIndex: 100,
        boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
      }}>
        {/* Row 1: logo + action buttons */}
        <div style={{
          padding: "8px 12px", display: "flex", alignItems: "center",
          justifyContent: "space-between", gap: 8,
        }}>
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: 7, flexShrink: 0 }}>
            <FlameLogo size={28} />
            <div style={{ fontSize: 15, fontWeight: 800, color: T.textPrimary, whiteSpace: "nowrap" }}>
              Now <span style={{ color: T.detection }}>TrendIn</span>
            </div>
          </div>
          {/* Buttons */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
            <button onClick={onCollect} disabled={collecting || loading} style={{
              padding: "6px 13px", borderRadius: 7,
              border: `1px solid ${collecting ? T.goldBorder : T.cardBorder}`,
              background: collecting ? T.goldLight : T.bg,
              color: collecting ? T.gold : T.textMuted,
              cursor: (collecting || loading) ? "wait" : "pointer",
              fontSize: 11, fontWeight: 700, fontFamily: "inherit",
              whiteSpace: "nowrap",
            }}>
              {collecting ? (collectMsg || "…") : "+ COLLECT"}
            </button>
            <button onClick={onRefresh} disabled={loading} style={{
              padding: "6px 13px", borderRadius: 7,
              border: `1px solid ${T.detectionBorder}`,
              background: loading ? T.bg : T.detectionLight,
              color: T.detection, cursor: loading ? "wait" : "pointer",
              fontSize: 11, fontWeight: 700, fontFamily: "inherit",
              whiteSpace: "nowrap",
            }}>
              {loading ? "…" : "↻ REFRESH"}
            </button>
          </div>
        </div>
        {/* Row 2: live status bar */}
        <div style={{
          padding: "3px 12px 7px", display: "flex", alignItems: "center", gap: 6,
        }}>
          {isLive && (
            <div style={{
              width: 6, height: 6, borderRadius: "50%", background: T.confidence,
              boxShadow: `0 0 4px ${T.confidence}80`, animation: "pulse 2s infinite", flexShrink: 0,
            }} />
          )}
          <span style={{ fontSize: 10, color: T.detection, fontWeight: 700 }}>
            {topicCount} SIGNALS ACTIVE
          </span>
          <span style={{ fontSize: 9, color: T.textFaint }}>
            · {lastUpdated ? timeAgo(lastUpdated) : "—"}
          </span>
          {isLive && (
            <div style={{
              fontSize: 8, color: T.confidence, fontWeight: 700, letterSpacing: 0.8,
              background: T.confidenceLight, padding: "1px 6px", borderRadius: 4,
              border: `1px solid ${T.confidenceBorder}`, marginLeft: "auto",
            }}>LIVE DATA</div>
          )}
        </div>
      </div>
    );
  }

  // ── DESKTOP HEADER: single row ────────────────────────────────
  return (
    <div style={{
      padding: "10px 20px", borderBottom: `1px solid ${T.cardBorder}`,
      background: T.surface, display: "flex", alignItems: "center",
      justifyContent: "space-between", gap: 8,
      position: "sticky", top: 0, zIndex: 100,
      boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
      minHeight: 56,
    }}>
      {/* Left: logo + name */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        <FlameLogo size={34} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 800, color: T.textPrimary, lineHeight: 1.2, whiteSpace: "nowrap" }}>
            Now <span style={{ color: T.detection }}>TrendIn</span>
          </div>
          <div style={{ fontSize: 8, color: T.textFaint, letterSpacing: 1.4 }}>ATTENTION INTELLIGENCE ENGINE</div>
        </div>
        {isLive && (
          <div style={{
            fontSize: 8, color: T.confidence, fontWeight: 700, letterSpacing: 0.8,
            background: T.confidenceLight, padding: "2px 7px", borderRadius: 4,
            border: `1px solid ${T.confidenceBorder}`, whiteSpace: "nowrap", flexShrink: 0,
          }}>LIVE DATA</div>
        )}
      </div>
      {/* Right: status + buttons */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        <div style={{ textAlign: "right", lineHeight: 1.3 }}>
          <div style={{ fontSize: 10, color: T.detection, fontWeight: 700, whiteSpace: "nowrap" }}>
            {topicCount} SIGNALS ACTIVE
          </div>
          <div style={{ fontSize: 9, color: T.textFaint, whiteSpace: "nowrap" }}>
            {lastUpdated ? timeAgo(lastUpdated) : "—"}
          </div>
        </div>
        <div style={{
          width: 7, height: 7, borderRadius: "50%", background: T.confidence,
          boxShadow: `0 0 5px ${T.confidence}80`, animation: "pulse 2s infinite", flexShrink: 0,
        }} />
        <button onClick={onCollect} disabled={collecting || loading} style={{
          padding: "6px 11px", borderRadius: 7,
          border: `1px solid ${collecting ? T.goldBorder : T.cardBorder}`,
          background: collecting ? T.goldLight : T.bg,
          color: collecting ? T.gold : T.textMuted,
          cursor: (collecting || loading) ? "wait" : "pointer",
          fontSize: 10, fontWeight: 700, letterSpacing: 0.3, fontFamily: "inherit",
          whiteSpace: "nowrap", flexShrink: 0,
        }}>
          {collecting ? (collectMsg || "COLLECTING...") : "+ COLLECT"}
        </button>
        <button onClick={onRefresh} disabled={loading} style={{
          padding: "6px 12px", borderRadius: 7,
          border: `1px solid ${T.detectionBorder}`,
          background: loading ? T.bg : T.detectionLight,
          color: T.detection, cursor: loading ? "wait" : "pointer",
          fontSize: 10, fontWeight: 700, fontFamily: "inherit",
          whiteSpace: "nowrap", flexShrink: 0,
        }}>
          {loading ? "..." : "↻ REFRESH"}
        </button>
      </div>
    </div>
  );
}

// ── FILTER BAR (search + FILTERS/SORT toggle + directional sort) ──
function FilterBar({ filter, setFilter, sortBy, setSortBy, sortDir, setSortDir, searchQuery, setSearchQuery }) {
  const [mode, setMode] = useState("filters"); // "filters" | "sort"

  const filters = [
    { id: "all",       label: "All Signals" },
    { id: "breakout",  label: "Breakout ≥85" },
    { id: "strong",    label: "Strong ≥70" },
    { id: "emerging",  label: "Emerging" },
    { id: "low-risk",  label: "Low Risk" },
  ];

  const sorts = [
    { id: "score",       label: "Score" },
    { id: "detection",   label: "Detection" },
    { id: "confidence",  label: "Confidence" },
    { id: "persistence", label: "Persistence" },
  ];

  const handleSortClick = (id) => {
    if (sortBy === id) {
      setSortDir(d => d === "desc" ? "asc" : "desc");
    } else {
      setSortBy(id);
      setSortDir("desc");
    }
  };

  // Active sort label for the toggle button subtitle
  const activeSortLabel = sorts.find(s => s.id === sortBy)?.label || "Score";
  const activeFilterLabel = filter === "all" ? "All" : filters.find(f => f.id === filter)?.label || "All";

  return (
    <div style={{ background: T.surface, borderBottom: `1px solid ${T.cardBorder}` }}>

      {/* ── Search input (always visible) ── */}
      <div style={{ padding: "10px 14px 8px" }}>
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          background: T.bg, border: `1px solid ${T.cardBorder}`,
          borderRadius: 10, padding: "7px 12px",
        }}>
          <span style={{ fontSize: 13, color: T.textFaint, flexShrink: 0 }}>🔍</span>
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search trends…"
            style={{
              flex: 1, border: "none", background: "none", outline: "none",
              fontSize: 13, color: T.textPrimary, fontFamily: "inherit",
              caretColor: T.detection,
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              style={{
                background: "none", border: "none", cursor: "pointer",
                fontSize: 16, color: T.textFaint, padding: 0, lineHeight: 1, flexShrink: 0,
              }}
            >×</button>
          )}
        </div>
      </div>

      {/* ── FILTERS / SORT toggle tabs ── */}
      <div style={{
        padding: "0 14px 8px",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        {/* Toggle pill */}
        <div style={{
          display: "flex", borderRadius: 8, overflow: "hidden",
          border: `1px solid ${T.cardBorder}`, flexShrink: 0,
        }}>
          <button
            onClick={() => setMode("filters")}
            style={{
              padding: "5px 13px",
              background: mode === "filters" ? T.detection : T.surface,
              color: mode === "filters" ? "white" : T.textMuted,
              border: "none", cursor: "pointer",
              fontSize: 10, fontWeight: 700, letterSpacing: 0.4,
              fontFamily: "inherit", transition: "all 0.15s",
              borderRight: `1px solid ${T.cardBorder}`,
            }}
          >
            ⊞ Filters
          </button>
          <button
            onClick={() => setMode("sort")}
            style={{
              padding: "5px 13px",
              background: mode === "sort" ? T.detection : T.surface,
              color: mode === "sort" ? "white" : T.textMuted,
              border: "none", cursor: "pointer",
              fontSize: 10, fontWeight: 700, letterSpacing: 0.4,
              fontFamily: "inherit", transition: "all 0.15s",
            }}
          >
            ⇅ Sort
          </button>
        </div>

        {/* Active selection summary — tappable shortcut to switch mode */}
        {mode === "filters" ? (
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ fontSize: 9, color: T.textFaint, letterSpacing: 0.5 }}>active:</span>
            <span style={{
              fontSize: 10, color: T.detection, fontWeight: 700,
              background: T.detectionLight, padding: "2px 8px",
              borderRadius: 10, border: `1px solid ${T.detectionBorder}`,
            }}>{activeFilterLabel}</span>
            <button
              onClick={() => setMode("sort")}
              style={{
                marginLeft: 4, fontSize: 9, color: T.textMuted, background: "none",
                border: `1px solid ${T.cardBorder}`, borderRadius: 6,
                padding: "2px 7px", cursor: "pointer", fontFamily: "inherit",
                fontWeight: 600,
              }}
            >
              Sort: {activeSortLabel} {sortDir === "desc" ? "↓" : "↑"}
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ fontSize: 9, color: T.textFaint, letterSpacing: 0.5 }}>sorting by:</span>
            <span style={{
              fontSize: 10, color: T.detection, fontWeight: 700,
              background: T.detectionLight, padding: "2px 8px",
              borderRadius: 10, border: `1px solid ${T.detectionBorder}`,
            }}>{activeSortLabel} {sortDir === "desc" ? "↓" : "↑"}</span>
            <button
              onClick={() => setMode("filters")}
              style={{
                marginLeft: 4, fontSize: 9, color: T.textMuted, background: "none",
                border: `1px solid ${T.cardBorder}`, borderRadius: 6,
                padding: "2px 7px", cursor: "pointer", fontFamily: "inherit",
                fontWeight: 600,
              }}
            >
              Filter: {activeFilterLabel}
            </button>
          </div>
        )}
      </div>

      {/* ── FILTER chips panel ── */}
      {mode === "filters" && (
        <div style={{
          padding: "0 14px 10px",
          display: "flex", alignItems: "center", gap: 6, overflowX: "auto",
          scrollbarWidth: "none",
        }}>
          {filters.map(f => (
            <button key={f.id} onClick={() => setFilter(f.id)} style={{
              padding: "5px 13px", borderRadius: 20, flexShrink: 0,
              border: `1px solid ${filter === f.id ? T.detection : T.cardBorder}`,
              background: filter === f.id ? T.detection : "none",
              color: filter === f.id ? "white" : T.textSecondary,
              cursor: "pointer", whiteSpace: "nowrap",
              fontSize: 11, fontWeight: 600, letterSpacing: 0.2,
              transition: "all 0.15s", fontFamily: "inherit",
            }}>
              {f.label}
            </button>
          ))}
        </div>
      )}

      {/* ── SORT buttons panel ── */}
      {mode === "sort" && (
        <div style={{
          padding: "0 14px 10px",
          display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap",
        }}>
          {sorts.map(s => {
            const active = sortBy === s.id;
            return (
              <button
                key={s.id}
                onClick={() => handleSortClick(s.id)}
                title={active ? (sortDir === "desc" ? "Click to sort ascending" : "Click to sort descending") : `Sort by ${s.label}`}
                style={{
                  padding: "6px 14px", borderRadius: 20, flexShrink: 0,
                  border: `1px solid ${active ? T.detection : T.cardBorder}`,
                  background: active ? T.detection : "none",
                  color: active ? "white" : T.textSecondary,
                  cursor: "pointer", fontSize: 11, fontWeight: 600,
                  fontFamily: "inherit", display: "flex", alignItems: "center", gap: 5,
                  transition: "all 0.15s",
                }}
              >
                {s.label}
                <span style={{
                  fontSize: 12, lineHeight: 1, fontWeight: 800,
                  color: active ? "white" : T.textFaint,
                  opacity: active ? 1 : 0.5,
                }}>
                  {active ? (sortDir === "desc" ? "↓" : "↑") : "↕"}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── SCORE GUIDE STRIP ────────────────────────────────────────────
// Always-visible horizontal threshold strip — directly answers the 10-second test.
// A new user sees this immediately and knows what every score level means before
// they look at a single topic. Replaces the collapsed accordion (ScoreLegend).
function ScoreGuideStrip() {
  const levels = [
    { score: "85–100", label: "BREAKOUT", meaning: "Act now",          color: T.confidence, bg: T.confidenceLight, border: T.confidenceBorder },
    { score: "70–84",  label: "STRONG",   meaning: "Window open",      color: T.detection,  bg: T.detectionLight,  border: T.detectionBorder },
    { score: "55–69",  label: "EMERGING", meaning: "Begin planning",   color: T.goldMid,    bg: T.goldLight,       border: T.goldBorder },
    { score: "35–54",  label: "WATCHING", meaning: "Too early to act", color: T.orange,     bg: T.orangeLight,     border: "#FDBA74" },
  ];
  return (
    <div style={{ margin: "8px 16px 4px", padding: "10px 12px", background: T.card, borderRadius: 10, border: `1px solid ${T.cardBorder}` }}>
      <div style={{ fontSize: 9, color: T.textFaint, fontWeight: 700, letterSpacing: 1.2, marginBottom: 8 }}>
        WHAT DO THESE SCORES MEAN?
      </div>
      <div style={{ display: "flex", gap: 6 }}>
        {levels.map(lv => (
          <div key={lv.label} style={{
            flex: "1 1 0", padding: "7px 8px", borderRadius: 8,
            background: lv.bg, border: `1px solid ${lv.border}`,
            textAlign: "center",
          }}>
            <div style={{ fontSize: 10, fontWeight: 800, color: lv.color, letterSpacing: 0.4 }}>{lv.label}</div>
            <div style={{ fontSize: 9, color: T.textFaint, margin: "2px 0 3px" }}>{lv.score}</div>
            <div style={{ fontSize: 9, fontWeight: 700, color: lv.color }}>{lv.meaning}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── SUMMARY BAR ──────────────────────────────────────────────────
// ── VIEW TOGGLE (Trends / History) ───────────────────────────────
function ViewToggle({ view, setView, historyCount }) {
  return (
    <div style={{
      display: "flex", alignItems: "center",
      background: T.surface, borderBottom: `1px solid ${T.cardBorder}`,
      overflowX: "auto", overflowY: "hidden",
      scrollbarWidth: "none", msOverflowStyle: "none",
      flexShrink: 0,
    }}>
      {[
        { id: "trends",   label: "🔥 Trends" },
        { id: "history",  label: `🕐 History${historyCount > 0 ? ` · ${historyCount}` : ""}` },
        { id: "accuracy", label: "⭐ Accuracy" },
      ].map((tab) => (
        <button
          key={tab.id}
          onClick={() => setView(tab.id)}
          style={{
            padding: "11px 16px",
            background: "none", border: "none",
            borderBottom: view === tab.id ? `2px solid ${T.detection}` : "2px solid transparent",
            color: view === tab.id ? T.detection : T.textMuted,
            cursor: "pointer", fontSize: 12, fontWeight: 700,
            letterSpacing: 0.3, fontFamily: "inherit",
            transition: "all 0.15s",
            marginBottom: -1,
            whiteSpace: "nowrap", flexShrink: 0,
          }}
        >{tab.label}</button>
      ))}
    </div>
  );
}

// ── ACCURACY LEADERBOARD ─────────────────────────────────────────
// The "trust mechanism" — shows the engine's prediction track record.
// Every signal ≥55 that was detected is listed with its detection date, scores,
// and stage. This is the HexClad /science page equivalent: proof > claim.
function AccuracyView() {
  const [records, setRecords]   = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error,   setError]     = useState(null);
  const [health,  setHealth]    = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`${API_BASE}/accuracy`).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API_BASE}/health/detailed`).then(r => r.ok ? r.json() : null).catch(() => null),
    ]).then(([acc, h]) => {
      if (acc) setRecords(acc.predictions || []);
      if (h)   setHealth(h);
      if (!acc) setError("Accuracy endpoint not yet available.");
    }).finally(() => setLoading(false));
  }, []);

  const stageCol = (s) => ({
    BREAKOUT: T.confidence, STRONG: T.detection, EMERGING: T.goldMid, WATCHING: T.orange,
  }[s] || T.textMuted);

  const stageBg = (s) => ({
    BREAKOUT: T.confidenceLight, STRONG: T.detectionLight, EMERGING: T.goldLight, WATCHING: T.orangeLight,
  }[s] || T.bg);

  const stageBorder = (s) => ({
    BREAKOUT: T.confidenceBorder, STRONG: T.detectionBorder, EMERGING: T.goldBorder, WATCHING: "#FDBA74",
  }[s] || T.cardBorder);

  return (
    <div style={{ padding: "16px 16px 40px" }}>
      {/* Mission header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 800, color: T.textPrimary, marginBottom: 6 }}>
          Prediction Track Record
        </div>
        <div style={{ fontSize: 11, color: T.textMuted, lineHeight: 1.6 }}>
          Every topic with a score ≥55 detected by the engine. Proof that the signal leads mainstream awareness.
          Detection score = speed. Confidence score = precision.
        </div>
      </div>

      {/* Data source health */}
      {health && (
        <div style={{
          marginBottom: 16, padding: "10px 14px", borderRadius: 10,
          background: T.card, border: `1px solid ${T.cardBorder}`,
        }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: T.textFaint, letterSpacing: 1.2, marginBottom: 8 }}>
            DATA SOURCE STATUS
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {(health.sources || []).map(src => (
              <div key={src.platform} style={{
                padding: "5px 10px", borderRadius: 20,
                background: src.signals_24h > 0 ? T.confidenceLight : T.bg,
                border: `1px solid ${src.signals_24h > 0 ? T.confidenceBorder : T.cardBorder}`,
                fontSize: 10,
              }}>
                <span style={{ fontWeight: 700, color: src.signals_24h > 0 ? T.confidence : T.textMuted }}>
                  {src.platform}
                </span>
                <span style={{ color: T.textFaint, marginLeft: 4 }}>
                  {src.signals_24h > 0 ? `${src.signals_24h} signals` : "no recent signals"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats summary */}
      {records.length > 0 && (
        <div style={{
          display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16,
        }}>
          {[
            { label: "Predictions tracked", value: records.length },
            { label: "BREAKOUT detected",   value: records.filter(r => r.stage === "BREAKOUT").length },
            { label: "Avg detection score", value: Math.round(records.reduce((a, r) => a + (r.detection_score || 0), 0) / records.length) },
          ].map(stat => (
            <div key={stat.label} style={{
              padding: "10px 12px", borderRadius: 10, textAlign: "center",
              background: T.card, border: `1px solid ${T.cardBorder}`,
            }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: T.detection }}>{stat.value}</div>
              <div style={{ fontSize: 9, color: T.textFaint, marginTop: 3, fontWeight: 600 }}>{stat.label.toUpperCase()}</div>
            </div>
          ))}
        </div>
      )}

      {/* Predictions list */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "40px 20px" }}>
          <div style={{ fontSize: 24, marginBottom: 10 }}>⭐</div>
          <div style={{ fontSize: 12, color: T.textMuted }}>Loading prediction history…</div>
        </div>
      ) : error ? (
        <div style={{
          padding: "20px", borderRadius: 10, textAlign: "center",
          background: T.goldLight, border: `1px solid ${T.goldBorder}`,
        }}>
          <div style={{ fontSize: 12, color: T.gold, marginBottom: 6 }}>⚠ {error}</div>
          <div style={{ fontSize: 10, color: T.textMuted, lineHeight: 1.6 }}>
            Pull Trends first to collect signals. Once topics are scored at ≥55, they appear here.
          </div>
        </div>
      ) : records.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px 20px" }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}>📊</div>
          <div style={{ fontSize: 13, color: T.textMuted, marginBottom: 8 }}>No predictions logged yet.</div>
          <div style={{ fontSize: 11, color: T.textFaint, lineHeight: 1.7 }}>
            Collect and score topics. Any signal reaching EMERGING (55+) will appear here as a tracked prediction.
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {records.map((rec, i) => {
            const gap = Math.round((rec.detection_score || 0) - (rec.confidence_score || 0));
            const gm  = gapMeta(gap);
            return (
              <div key={rec.topic_key || i} style={{
                padding: "12px 14px", borderRadius: 12,
                background: T.card, border: `1px solid ${T.cardBorder}`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: T.textPrimary, marginBottom: 2 }}>
                      {rec.topic_display || rec.topic}
                    </div>
                    <div style={{ fontSize: 10, color: T.textFaint }}>
                      Detected {rec.detected_at ? new Date(rec.detected_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "—"}
                    </div>
                  </div>
                  <div style={{
                    padding: "3px 10px", borderRadius: 20, flexShrink: 0, marginLeft: 10,
                    background: stageBg(rec.stage), border: `1px solid ${stageBorder(rec.stage)}`,
                    fontSize: 9, fontWeight: 800, color: stageCol(rec.stage), letterSpacing: 0.5,
                  }}>
                    {rec.stage || "MONITORING"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <div style={{
                    flex: 1, padding: "6px 10px", borderRadius: 8,
                    background: T.detectionLight, border: `1px solid ${T.detectionBorder}`,
                    textAlign: "center",
                  }}>
                    <div style={{ fontSize: 16, fontWeight: 800, color: T.detection }}>{Math.round(rec.detection_score || 0)}</div>
                    <div style={{ fontSize: 8, color: T.detection, fontWeight: 600, letterSpacing: 0.5 }}>DETECTION</div>
                  </div>
                  <div style={{
                    flex: 1, padding: "6px 10px", borderRadius: 8,
                    background: T.confidenceLight, border: `1px solid ${T.confidenceBorder}`,
                    textAlign: "center",
                  }}>
                    <div style={{ fontSize: 16, fontWeight: 800, color: T.confidence }}>{Math.round(rec.confidence_score || 0)}</div>
                    <div style={{ fontSize: 8, color: T.confidence, fontWeight: 600, letterSpacing: 0.5 }}>CONFIDENCE</div>
                  </div>
                  <div style={{
                    flex: 1, padding: "6px 10px", borderRadius: 8,
                    background: gm.bg, border: `1px solid ${gm.border}`,
                    textAlign: "center",
                  }}>
                    <div style={{ fontSize: 16, fontWeight: 800, color: gm.color }}>{gap}pt</div>
                    <div style={{ fontSize: 8, color: gm.color, fontWeight: 600, letterSpacing: 0.5 }}>GAP</div>
                  </div>
                </div>
                {rec.lead_time_est_days > 0 && (
                  <div style={{ marginTop: 6, fontSize: 10, color: T.textFaint }}>
                    Est. lead time: <span style={{ color: T.confidence, fontWeight: 700 }}>{rec.lead_time_est_days}d ahead of mainstream</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── HISTORY PANEL ────────────────────────────────────────────────
function HistoryPanel({ onSelectTopic, onCountChange }) {
  const [items,     setItems]     = useState([]);
  const [loading,   setLoading]   = useState(false);
  const [hours,     setHours]     = useState(24);
  const [lastFetch, setLastFetch] = useState(null);
  const [search,    setSearch]    = useState("");
  const listRef = useRef(null);

  const load = useCallback(async (h) => {
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/history/recent?hours=${h}&limit=300`);
      if (r.ok) {
        const data = await r.json();
        const topics = data.topics || [];
        setItems(topics);
        setLastFetch(new Date().toISOString());
        if (onCountChange) onCountChange(topics.length);
      }
    } catch (e) {
      console.log("History fetch error:", e.message);
    } finally {
      setLoading(false);
    }
  }, [onCountChange]);

  useEffect(() => { load(hours); }, [load, hours]);

  // Scroll helpers — jump ±300px in the list
  const scrollUp   = () => listRef.current?.scrollBy({ top: -300, behavior: "smooth" });
  const scrollDown = () => listRef.current?.scrollBy({ top:  300, behavior: "smooth" });
  const scrollTop  = () => listRef.current?.scrollTo({ top: 0,    behavior: "smooth" });

  // stageColor is defined at module level — used here and in TopicCard

  // Filter by search query, then group by date
  const filtered = search.trim()
    ? items.filter(i =>
        (i.topic_display || i.topic_key || "").toLowerCase().includes(search.toLowerCase())
      )
    : items;

  const grouped = filtered.reduce((acc, item) => {
    const day = item.scored_at
      ? new Date(item.scored_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
      : "Unknown date";
    if (!acc[day]) acc[day] = [];
    acc[day].push(item);
    return acc;
  }, {});

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>

      {/* ── Row 1: Window selector + scroll buttons + refresh ── */}
      <div style={{
        padding: "8px 14px 8px",
        background: T.surface, borderBottom: `1px solid ${T.cardBorder}`,
        display: "flex", alignItems: "center", gap: 6,
        flexShrink: 0, flexWrap: "nowrap",
      }}>
        {/* Time window */}
        <span style={{ fontSize: 9, color: T.textFaint, fontWeight: 700, letterSpacing: 1, flexShrink: 0 }}>
          WINDOW:
        </span>
        {[
          { h: 24,  label: "24h" },
          { h: 48,  label: "48h" },
          { h: 168, label: "7d"  },
        ].map(w => (
          <button key={w.h} onClick={() => setHours(w.h)} style={{
            padding: "3px 10px", borderRadius: 6, flexShrink: 0,
            border: `1px solid ${hours === w.h ? T.detectionBorder : T.cardBorder}`,
            background: hours === w.h ? T.detectionLight : "none",
            color: hours === w.h ? T.detection : T.textMuted,
            cursor: "pointer", fontSize: 10, fontWeight: 700, fontFamily: "inherit",
          }}>{w.label}</button>
        ))}

        {/* Divider */}
        <div style={{ width: 1, height: 20, background: T.cardBorder, flexShrink: 0, marginLeft: 4, marginRight: 4 }} />

        {/* ↑ ↓ scroll toggle buttons */}
        <div style={{ display: "flex", borderRadius: 7, overflow: "hidden", border: `1px solid ${T.cardBorder}`, flexShrink: 0 }}>
          <button
            onClick={scrollUp}
            title="Scroll up"
            style={{
              padding: "4px 10px", background: T.bg, border: "none",
              borderRight: `1px solid ${T.cardBorder}`,
              color: T.textMuted, cursor: "pointer",
              fontSize: 13, lineHeight: 1, fontFamily: "inherit",
              transition: "background 0.12s",
            }}
            onMouseEnter={e => e.currentTarget.style.background = T.detectionLight}
            onMouseLeave={e => e.currentTarget.style.background = T.bg}
          >↑</button>
          <button
            onClick={scrollDown}
            title="Scroll down"
            style={{
              padding: "4px 10px", background: T.bg, border: "none",
              color: T.textMuted, cursor: "pointer",
              fontSize: 13, lineHeight: 1, fontFamily: "inherit",
              transition: "background 0.12s",
            }}
            onMouseEnter={e => e.currentTarget.style.background = T.detectionLight}
            onMouseLeave={e => e.currentTarget.style.background = T.bg}
          >↓</button>
        </div>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Last fetch + refresh */}
        {lastFetch && (
          <span style={{ fontSize: 9, color: T.textFaint, flexShrink: 0 }}>{timeAgo(lastFetch)}</span>
        )}
        <button
          onClick={() => load(hours)}
          disabled={loading}
          style={{
            padding: "4px 10px", borderRadius: 6, flexShrink: 0,
            border: `1px solid ${T.detectionBorder}`,
            background: T.detectionLight, color: T.detection,
            cursor: loading ? "wait" : "pointer",
            fontSize: 9, fontWeight: 700, fontFamily: "inherit",
          }}
        >{loading ? "…" : "↻"}</button>
      </div>

      {/* ── Row 2: Search input ── */}
      <div style={{
        padding: "8px 14px",
        background: T.surface, borderBottom: `1px solid ${T.cardBorder}`,
        flexShrink: 0,
      }}>
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          background: T.bg, border: `1px solid ${T.cardBorder}`,
          borderRadius: 10, padding: "6px 12px",
        }}>
          <span style={{ fontSize: 12, color: T.textFaint, flexShrink: 0 }}>🔍</span>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search history…"
            style={{
              flex: 1, border: "none", background: "none", outline: "none",
              fontSize: 12, color: T.textPrimary, fontFamily: "inherit",
              caretColor: T.detection,
            }}
          />
          {search && (
            <button onClick={() => setSearch("")} style={{
              background: "none", border: "none", cursor: "pointer",
              fontSize: 15, color: T.textFaint, padding: 0, lineHeight: 1, flexShrink: 0,
            }}>×</button>
          )}
        </div>
      </div>

      {/* ── Count summary ── */}
      {!loading && items.length > 0 && (
        <div style={{
          padding: "6px 14px", background: T.bg,
          borderBottom: `1px solid ${T.cardBorder}`, flexShrink: 0,
          display: "flex", alignItems: "center", gap: 6,
        }}>
          <span style={{ fontSize: 10, color: T.textMuted }}>
            {search.trim() ? (
              <><strong style={{ color: T.detection, fontFamily: "'DM Mono', monospace" }}>{filtered.length}</strong> of {items.length} topics match</>
            ) : (
              <><strong style={{ color: T.textPrimary, fontFamily: "'DM Mono', monospace" }}>{items.length}</strong> topics scored in the last {hours === 168 ? "7 days" : `${hours}h`}</>
            )}
          </span>
          {filtered.length > 0 && (
            <button onClick={scrollTop} style={{
              marginLeft: "auto", fontSize: 9, color: T.textFaint, background: "none",
              border: "none", cursor: "pointer", fontFamily: "inherit",
            }}>↑ top</button>
          )}
        </div>
      )}

      {/* ── List ── */}
      <ScrollablePane style={{ flex: 1 }} scrollRef={listRef}>
        <div style={{ padding: "0 0 24px" }}>
        {loading && (
          <div style={{ padding: "60px 20px", textAlign: "center", color: T.textMuted, fontSize: 12 }}>
            Loading history…
          </div>
        )}
        {!loading && items.length === 0 && (
          <div style={{ padding: "60px 20px", textAlign: "center", color: T.textMuted, fontSize: 12 }}>
            No scoring events in the last {hours}h.
            <br /><br />
            <span style={{ fontSize: 11, color: T.textFaint }}>
              Click ↻ Pull Trends to collect and score topics — they'll appear here.
            </span>
          </div>
        )}
        {!loading && Object.entries(grouped).map(([day, dayItems]) => (
          <div key={day}>
            {/* Day header */}
            <div style={{
              padding: "8px 16px 5px", position: "sticky", top: 0, zIndex: 5,
              background: T.bg, borderBottom: `1px solid ${T.cardBorder}`,
            }}>
              <span style={{ fontSize: 9, color: T.textFaint, fontWeight: 700, letterSpacing: 1.2 }}>
                {day.toUpperCase()} · {dayItems.length} topic{dayItems.length !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Topic rows */}
            {dayItems.map((item, idx) => {
              const sc   = Math.round(item.overall_score   || 0);
              const det  = Math.round(item.detection_score || 0);
              const conf = Math.round(item.confidence_score || 0);
              const stage = item.signal_stage || "MONITORING";
              const ts = item.scored_at
                ? new Date(item.scored_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true })
                : "—";

              return (
                <div
                  key={idx}
                  onClick={() => onSelectTopic && onSelectTopic(item)}
                  style={{
                    padding: "10px 16px", cursor: "pointer",
                    borderBottom: `1px solid ${T.cardBorder}`,
                    background: T.surface,
                    transition: "background 0.12s",
                    display: "flex", alignItems: "center", gap: 10,
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = T.detectionLight}
                  onMouseLeave={e => e.currentTarget.style.background = T.surface}
                >
                  {/* Stage color bar */}
                  <div style={{
                    width: 3, height: 38, borderRadius: 2, flexShrink: 0,
                    background: stageColor(stage),
                  }} />

                  {/* Topic name + timestamp */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: 13, fontWeight: 700, color: T.textPrimary,
                      textTransform: "lowercase", whiteSpace: "nowrap",
                      overflow: "hidden", textOverflow: "ellipsis",
                      marginBottom: 3,
                    }}>
                      {item.topic_display || (item.topic_key || "").replace(/_/g, " ")}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{
                        fontSize: 8, fontWeight: 700, letterSpacing: 0.5,
                        color: stageColor(stage),
                        background: stageColor(stage) + "18",
                        padding: "1px 6px", borderRadius: 4,
                      }}>
                        {stage}
                      </span>
                      {item.is_gravitational_anomaly === 1 && (
                        <span style={{
                          fontSize: 8, fontWeight: 700, color: T.confidence,
                          background: T.confidenceLight, padding: "1px 5px",
                          borderRadius: 4, border: `1px solid ${T.confidenceBorder}`,
                        }}>★ ANOMALY</span>
                      )}
                      <span style={{ fontSize: 9, color: T.textFaint }}>{ts}</span>
                    </div>
                  </div>

                  {/* Scores */}
                  <div style={{ display: "flex", gap: 10, flexShrink: 0, alignItems: "center" }}>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 8, color: T.textFaint, letterSpacing: 0.5, marginBottom: 1 }}>OVR</div>
                      <div style={{ fontSize: 16, fontWeight: 800, color: T.textPrimary, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{sc}</div>
                    </div>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 8, color: T.detection, letterSpacing: 0.5, marginBottom: 1 }}>DET</div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: T.detection, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{det}</div>
                    </div>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 8, color: T.confidence, letterSpacing: 0.5, marginBottom: 1 }}>CONF</div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: T.confidence, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{conf}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ))}
        </div>
      </ScrollablePane>
    </div>
  );
}

function SummaryBar({ scores }) {
  const stats = [
    { label: "BREAKOUT", count: scores.filter(s => s.overall_score >= 85).length,                                   color: T.confidence },
    { label: "STRONG",   count: scores.filter(s => s.overall_score >= 70 && s.overall_score < 85).length,           color: T.detection },
    { label: "EMERGING", count: scores.filter(s => s.overall_score >= 55 && s.overall_score < 70).length,           color: T.goldMid },
    { label: "ANOMALIES",count: scores.filter(s => s.is_gravitational_anomaly).length,                              color: T.purple },
  ];
  return (
    <div style={{ padding: "6px 20px 10px", display: "flex", gap: 8 }}>
      {stats.map(s => (
        <div key={s.label} style={{
          flex: 1, padding: "8px 6px", borderRadius: 8, textAlign: "center",
          background: T.card, border: `1px solid ${T.cardBorder}`,
        }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: s.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
            {s.count}
          </div>
          <div style={{ fontSize: 8, color: T.textFaint, letterSpacing: 1, marginTop: 3 }}>{s.label}</div>
        </div>
      ))}
    </div>
  );
}

// ── TRENDS SECTION HEADER ────────────────────────────────────────
// Styled like the "Trends" tab header in the Android app
function TrendsSectionHeader({ count, filtered, onCollect, collecting, collectMsg }) {
  return (
    <div style={{
      padding: "12px 16px 8px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      background: T.surface,
    }}>
      {/* Left: section title + count pill */}
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        {/* Flame accent bar */}
        <div style={{
          width: 3, height: 20, borderRadius: 2, flexShrink: 0,
          background: `linear-gradient(to bottom, ${T.flameMid}, ${T.detection})`,
        }} />
        <span style={{
          fontSize: 17, fontWeight: 800, color: T.textPrimary, letterSpacing: -0.5,
          fontFamily: "'Syne', sans-serif",
        }}>
          Trends
        </span>
        {/* Count chip — shows filtered count if search/filter is active */}
        <div style={{
          fontSize: 10, color: T.textMuted, fontWeight: 700,
          background: T.bg, border: `1px solid ${T.cardBorder}`,
          padding: "2px 9px", borderRadius: 10, lineHeight: 1.4,
        }}>
          {filtered !== count ? `${filtered} / ${count}` : count}
        </div>
      </div>

      {/* Right: Pull / Collect button (app-style) */}
      <button
        onClick={onCollect}
        disabled={collecting}
        style={{
          display: "flex", alignItems: "center", gap: 5,
          padding: "6px 14px", borderRadius: 20,
          border: `1px solid ${collecting ? T.goldBorder : T.flameBorder}`,
          background: collecting ? T.goldLight : T.flameLight,
          color: collecting ? T.gold : T.flame,
          cursor: collecting ? "wait" : "pointer",
          fontSize: 10, fontWeight: 700, letterSpacing: 0.4,
          fontFamily: "inherit", transition: "all 0.2s",
          boxShadow: collecting ? "none" : `0 1px 4px ${T.flameBorder}60`,
        }}
      >
        <span style={{ fontSize: 13, lineHeight: 1 }}>
          {collecting ? "⏳" : "↻"}
        </span>
        {collecting ? (collectMsg || "Collecting…") : "Pull Trends"}
      </button>
    </div>
  );
}

// ── MAIN APP ─────────────────────────────────────────────────────
export default function GradientScoreDashboard() {
  const [scores,      setScores]      = useState([]);
  const [usingMock,   setUsingMock]   = useState(false); // never show fake data
  const [selected,    setSelected]    = useState(null);
  const [loading,     setLoading]     = useState(false);
  const [collecting,  setCollecting]  = useState(false);
  const [collectMsg,  setCollectMsg]  = useState("");
  const [lastUpdated, setLastUpdated] = useState(new Date().toISOString());
  const [filter,      setFilter]      = useState("all");
  const [sortBy,      setSortBy]      = useState("score");
  const [sortDir,     setSortDir]     = useState("desc");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode,    setViewMode]    = useState("trends"); // "trends" | "history"
  const [historyCount, setHistoryCount] = useState(0);
  const [mobileDetailTab, setMobileDetailTab] = useState("detail"); // "detail" | "analysis"
  const [isMobile, setIsMobile] = useState(() => typeof window !== "undefined" && window.innerWidth < 768);
  const pollRef = useRef(null);

  // Track viewport width for mobile layout switching
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  // Keyframe injection
  useEffect(() => {
    const s = document.createElement("style");
    s.textContent = `
      @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
      @keyframes fadeSlideIn { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:none;} }
      @keyframes slideInRight { from{transform:translateX(100%);opacity:0;} to{transform:translateX(0);opacity:1;} }
      .nt-scrollpane::-webkit-scrollbar { display: none; }
    `;
    document.head.appendChild(s);
    return () => document.head.removeChild(s);
  }, []);

  const parseScores = useCallback((data) => {
    const raw = Array.isArray(data) ? data : (data.scores || data.results || []);
    return raw.map(item => {
      // ── Normalize platforms (new API: platforms_active, old: active_platforms)
      const plats =
        Array.isArray(item.platforms_active) ? item.platforms_active :
        typeof item.platforms_active === "string" ? (() => { try { return JSON.parse(item.platforms_active); } catch { return []; } })() :
        Array.isArray(item.active_platforms) ? item.active_platforms :
        typeof item.active_platforms === "string" ? (() => { try { return JSON.parse(item.active_platforms); } catch { return []; } })() :
        [];

      // ── Derive diffusion_pattern from signal_stage when the old field is absent
      const diffusion = item.diffusion_pattern || (
        (item.signal_stage === "BREAKOUT" || item.signal_stage === "STRONG")
          ? "A_builder_to_buyer"
          : item.signal_stage === "EMERGING"
            ? "B_enthusiast_to_mainstream"
            : "multi_platform_unclassified"
      );

      // ── Derive false_positive_risk if not present
      const fpr = item.false_positive_risk || (
        (item.overall_score || 0) >= 70 ? "low" :
        (item.overall_score || 0) >= 50 ? "medium" : "high"
      );

      return {
        ...item,
        // Topic name — new API uses topic_display
        topic: item.topic_display || item.topic || (item.topic_key || "").replace(/_/g, " ") || "unknown",
        // Signal count — new API uses total_mentions
        signal_count: item.total_mentions ?? item.signal_count ?? 0,
        // Platforms array — normalised above
        active_platforms: plats,
        // M component — new API uses platform_diversity
        medium_sequence_score: item.platform_diversity ?? item.medium_sequence_score ?? 0,
        // Timestamps — new API uses scored_at
        computed_at: item.scored_at || item.computed_at || new Date().toISOString(),
        // Niche/mainstream breakdown
        niche_signal_count: item.niche_mentions ?? item.niche_signal_count ?? 0,
        mainstream_signal_count: item.mainstream_mentions ?? item.mainstream_signal_count ?? 0,
        // Engagement asymmetry
        engagement_asymmetry_detected:
          item.engagement_asymmetry === 1 ||
          item.engagement_asymmetry_detected === 1 ||
          item.engagement_asymmetry_detected === true,
        // Diffusion pattern / stage label
        diffusion_pattern: diffusion,
        // False positive risk
        false_positive_risk: fpr,
        // Anomaly flag — new API uses is_gravitational_anomaly (0/1) and is_anomaly (bool)
        is_gravitational_anomaly:
          item.is_gravitational_anomaly === 1 ||
          item.is_anomaly === true,
        // Persistence / lifecycle fields (P component)
        persistence_score:   item.persistence_score  ?? 0,
        persistence_cycles:  item.persistence_cycles ?? 0,
        persistence_streak:  item.persistence_streak ?? 0,
        persistence_rate:    item.persistence_rate   ?? 0,
        trend_age_hours:     item.trend_age_hours    ?? 0,
        confirmed_trend:     item.confirmed_trend    === true || item.confirmed_trend === 1,
        peak_score:          item.peak_score         ?? 0,
        // NowTrendIn internal demand fields (N component)
        nowtrendin_score:       item.nowtrendin_score        ?? 0,
        nowtrendin_queries_30d: item.nowtrendin_queries_30d  ?? 0,
        nowtrendin_queries_24h: item.nowtrendin_queries_24h  ?? 0,
        nowtrendin_daily_rate:  item.nowtrendin_daily_rate   ?? 0,
        // Lead time estimate — derive from heisenberg gap when not present
        lead_time_estimate_days:
          Math.abs(item.lead_time_estimate_days || 0) ||
          Math.round((item.heisenberg_gap || 0) / 7),
        // JSON array fields
        platform_sequence: typeof item.platform_sequence === "string"
          ? (() => { try { return JSON.parse(item.platform_sequence); } catch { return []; } })()
          : (item.platform_sequence || []),
        top_signals: typeof item.top_signals === "string"
          ? (() => { try { return JSON.parse(item.top_signals); } catch { return []; } })()
          : (item.top_signals || []),
      };
    });
  }, []);

  const handleRefresh = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/scores?limit=20`);
      if (resp.ok) {
        const data = await resp.json();
        const parsed = parseScores(data);
        if (parsed.length > 0) {
          setScores(parsed);
          setUsingMock(false);
          setLastUpdated(new Date().toISOString());
        }
      }
    } catch (e) {
      console.log("Backend not returning data:", e.message);
    } finally {
      setLoading(false);
    }
  }, [parseScores]);

  useEffect(() => { handleRefresh(); }, [handleRefresh]);

  // Stable ref that tracks current score count — avoids stale closure in poll loop
  const scoresLenRef = useRef(0);
  useEffect(() => { scoresLenRef.current = scores.length; }, [scores.length]);

  const handleCollect = useCallback(async () => {
    if (collecting) return;
    setCollecting(true);
    setCollectMsg("COLLECTING...");
    try {
      // /collect returns immediately; full pipeline runs in background on server.
      // We poll /scores every 12 s for up to 16 polls (~3 min) until data appears.
      await fetch(`${API_BASE}/collect`, { method: "POST" });
      setCollectMsg("PROCESSING...");

      const prevLen = scoresLenRef.current;
      let polls = 0;
      const doPoll = async () => {
        polls++;
        if (polls > 16) { setCollecting(false); setCollectMsg(""); return; }
        setCollectMsg(`SCANNING... (${polls}/16)`);
        await handleRefresh();
        // Stop early once new results appear
        if (scoresLenRef.current > prevLen) { setCollecting(false); setCollectMsg(""); return; }
        pollRef.current = setTimeout(doPoll, 12000);
      };
      pollRef.current = setTimeout(doPoll, 12000);
    } catch {
      setCollecting(false); setCollectMsg("");
    }
  }, [collecting, handleRefresh]);

  useEffect(() => () => clearTimeout(pollRef.current), []);

  const displayScores = scores
    .filter(s => {
      // Search filter — match against topic name
      if (searchQuery && !s.topic.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      // Category filter
      if (filter === "breakout") return s.overall_score >= 85;
      if (filter === "strong")   return s.overall_score >= 70;
      if (filter === "emerging") return s.overall_score >= 55 && s.overall_score < 70;
      if (filter === "low-risk") return s.false_positive_risk === "low";
      return true;
    })
    .sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      if (sortBy === "persistence")
        return dir * ((a.persistence_rate || 0) - (b.persistence_rate || 0)) ||
               dir * ((a.persistence_streak || 0) - (b.persistence_streak || 0));
      if (sortBy === "detection")   return dir * ((a.detection_score || 0)  - (b.detection_score || 0));
      if (sortBy === "confidence")  return dir * ((a.confidence_score || 0) - (b.confidence_score || 0));
      return dir * ((a.overall_score || 0) - (b.overall_score || 0));
    });

  return (
    <div style={{
      background: T.bg, color: T.textPrimary,
      fontFamily: "'Syne', sans-serif",
      /* Full-viewport flex column — header takes natural height, content fills the rest */
      display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden",
      overflowX: "hidden",
    }}>
      <Header
        lastUpdated={lastUpdated}
        onRefresh={handleRefresh}
        onCollect={handleCollect}
        loading={loading}
        collecting={collecting}
        collectMsg={collectMsg}
        topicCount={scores.length}
        scores={scores}
      />

      {/* Content row: fills whatever height remains after the header (1-row or 2-row) */}
      <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden" }}>
        {/* Left: signal list / history */}
        <div style={{
          width:    isMobile ? "100%" : (selected ? "380px" : "100%"),
          maxWidth: isMobile ? "100%" : (selected ? "380px" : "700px"),
          margin:   isMobile ? "0"    : (selected ? "0"     : "0 auto"),
          flexShrink: 0,
          display: "flex", flexDirection: "column",
          borderRight: (!isMobile && selected) ? `1px solid ${T.cardBorder}` : "none",
          transition: "all 0.3s ease",
          background: T.bg,
          overflow: "hidden",
          minHeight: 0,   /* critical: lets flex:1 children resolve to a pixel height */
        }}>
          {/* Trends/History view toggle — always visible */}
          <ViewToggle
            view={viewMode}
            setView={(v) => { setViewMode(v); setSelected(null); }}
            historyCount={historyCount}
          />

          {/* ── TRENDS VIEW ── */}
          {viewMode === "trends" && (
            <ScrollablePane style={{ flex: 1 }}>
              <FilterBar
                filter={filter}      setFilter={setFilter}
                sortBy={sortBy}      setSortBy={setSortBy}
                sortDir={sortDir}    setSortDir={setSortDir}
                searchQuery={searchQuery} setSearchQuery={setSearchQuery}
              />
              <TrendsSectionHeader
                count={scores.length}
                filtered={displayScores.length}
                onCollect={handleCollect}
                collecting={collecting}
                collectMsg={collectMsg}
              />
              <SummaryBar scores={scores} />
              <ScoreGuideStrip />
              <div style={{ padding: "0 20px 24px" }}>
                {displayScores.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "60px 20px" }}>
                    {loading ? (
                      <>
                        <div style={{ fontSize: 28, marginBottom: 12 }}>🔥</div>
                        <div style={{ fontSize: 13, color: T.textMuted, marginBottom: 8 }}>Loading live signals…</div>
                        <div style={{ fontSize: 11, color: T.textFaint }}>First load can take up to 30 seconds while the engine wakes up.</div>
                      </>
                    ) : searchQuery ? (
                      <>
                        <div style={{ fontSize: 13, color: T.textMuted, marginBottom: 8 }}>No trends match <strong>"{searchQuery}"</strong>.</div>
                        <div style={{ fontSize: 11, color: T.textFaint }}>Try a shorter search term or clear the search.</div>
                      </>
                    ) : scores.length === 0 ? (
                      <div style={{ maxWidth: 340, margin: "0 auto" }}>
                        <div style={{ fontSize: 28, marginBottom: 14 }}>📡</div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: T.textPrimary, marginBottom: 8, lineHeight: 1.5 }}>
                          The first instrument that measures where human attention is moving before it arrives.
                        </div>
                        <div style={{ fontSize: 11, color: T.textMuted, lineHeight: 1.7, marginBottom: 16 }}>
                          NowTrendIn detects expert-community signals 3–14 days before they reach Google Trends.
                          Two scores per topic: <span style={{ color: T.detection, fontWeight: 700 }}>Detection</span> (act early, ~22% FP)
                          and <span style={{ color: T.confidence, fontWeight: 700 }}>Confidence</span> (act precisely, &lt;9% FP).
                          The gap between them tells you how early the signal is.
                        </div>
                      </div>
                    ) : (
                      <>
                        <div style={{ fontSize: 13, color: T.textMuted, marginBottom: 8 }}>No signals match this filter.</div>
                        <div style={{ fontSize: 11, color: T.textFaint }}>Try a different filter or clear the search.</div>
                      </>
                    )}
                  </div>
                ) : (
                  <ErrorBoundary>
                    {displayScores.map(score => (
                      <div key={score.topic} style={{ animation: "fadeSlideIn 0.4s ease" }}>
                        <TopicCard
                          data={score}
                          onClick={(d) => { setSelected(d); setMobileDetailTab("detail"); }}
                          isSelected={selected?.topic === score.topic}
                        />
                      </div>
                    ))}
                  </ErrorBoundary>
                )}
              </div>
            </ScrollablePane>
          )}

          {/* ── ACCURACY VIEW ── */}
          {viewMode === "accuracy" && (
            <ScrollablePane style={{ flex: 1 }}>
              <ErrorBoundary><AccuracyView /></ErrorBoundary>
            </ScrollablePane>
          )}

          {/* ── HISTORY VIEW ── */}
          {viewMode === "history" && (
            <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
              <ErrorBoundary><HistoryPanel
                onSelectTopic={(item) => {
                  // Convert history item to the shape TopicDetailCard expects
                  const parsed = {
                    topic: item.topic_display || (item.topic_key || "").replace(/_/g, " "),
                    topic_key: item.topic_key,
                    overall_score:    item.overall_score    || 0,
                    detection_score:  item.detection_score  || 0,
                    confidence_score: item.confidence_score || 0,
                    persistence_score: item.persistence_score || 0,
                    gradient_strength: item.gradient_strength || 0,
                    inertia_score:    item.inertia_score    || 0,
                    nowtrendin_score: item.nowtrendin_score  || 0,
                    signal_count:     item.total_mentions    || 0,
                    active_platforms: Array.isArray(item.platforms_active)
                      ? item.platforms_active
                      : [],
                    computed_at:      item.scored_at || new Date().toISOString(),
                    is_gravitational_anomaly: item.is_gravitational_anomaly === 1,
                    diffusion_pattern: "multi_platform_unclassified",
                    false_positive_risk: (item.overall_score || 0) >= 70 ? "low" : "medium",
                  };
                  setSelected(parsed);
                  setMobileDetailTab("detail");
                }}
                onCountChange={setHistoryCount}
              /></ErrorBoundary>
            </div>
          )}
        </div>

        {/* ── MOBILE DETAIL OVERLAY ── full-screen slide-in when a card is tapped on mobile */}
        {isMobile && selected && (
          <div style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            zIndex: 300,
            display: "flex", flexDirection: "column",
            background: T.bg,
            animation: "slideInRight 0.25s ease",
          }}>
            {/* Mobile header: back + topic name + tab pills */}
            <div style={{
              background: T.surface, borderBottom: `1px solid ${T.cardBorder}`,
              flexShrink: 0,
            }}>
              {/* Top row: back + topic name */}
              <div style={{
                display: "flex", alignItems: "center", gap: 10,
                padding: "10px 16px 6px",
              }}>
                <button
                  onClick={() => setSelected(null)}
                  style={{
                    display: "flex", alignItems: "center", gap: 4,
                    background: T.bg, border: `1px solid ${T.cardBorder}`,
                    borderRadius: 8, padding: "5px 11px",
                    fontSize: 12, fontWeight: 700, color: T.detection,
                    cursor: "pointer", fontFamily: "inherit", flexShrink: 0,
                  }}
                >
                  ← Back
                </button>
                <div style={{
                  fontSize: 14, fontWeight: 800, color: T.textPrimary,
                  textTransform: "lowercase", letterSpacing: -0.3,
                  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                }}>
                  {selected.topic}
                </div>
              </div>
              {/* Tab switcher: Signal Detail | Analysis */}
              <div style={{ display: "flex", padding: "0 16px" }}>
                {[
                  { id: "detail",   label: "📊 Signal Detail" },
                  { id: "analysis", label: "⚡ Gap Analysis" },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setMobileDetailTab(tab.id)}
                    style={{
                      padding: "8px 14px", background: "none", border: "none",
                      borderBottom: mobileDetailTab === tab.id
                        ? `2px solid ${T.detection}`
                        : "2px solid transparent",
                      color: mobileDetailTab === tab.id ? T.detection : T.textMuted,
                      cursor: "pointer", fontSize: 12, fontWeight: 700,
                      letterSpacing: 0.3, fontFamily: "inherit",
                      marginBottom: -1, whiteSpace: "nowrap",
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Scrollable panel content */}
            <ScrollablePane style={{ flex: 1, background: mobileDetailTab === "detail" ? T.surface : T.bg }}>
              {mobileDetailTab === "detail"
                ? <ErrorBoundary><TopicDetailCard data={selected} /></ErrorBoundary>
                : <ErrorBoundary><HeisenbergPanel data={selected} /></ErrorBoundary>
              }
            </ScrollablePane>
          </div>
        )}

        {/* Right: Heisenberg detail (split 50/50) — desktop only */}
        {!isMobile && selected && (
          <div style={{
            flex: 1, display: "flex", overflow: "hidden",
            animation: "fadeSlideIn 0.25s ease",
          }}>
            {/* Left half: signal detail */}
            <div style={{ width: "50%", display: "flex", flexDirection: "column", overflow: "hidden", background: T.surface, borderRight: `1px solid ${T.cardBorder}` }}>
              {/* Fixed header */}
              <div style={{
                padding: "11px 18px", borderBottom: `1px solid ${T.cardBorder}`,
                display: "flex", justifyContent: "space-between", alignItems: "center",
                background: T.surface, flexShrink: 0,
              }}>
                <span style={{ fontSize: 10, color: T.textMuted, fontWeight: 700, letterSpacing: 1 }}>SIGNAL DETAIL</span>
                <button onClick={() => setSelected(null)} style={{
                  background: "none", border: "none", cursor: "pointer",
                  fontSize: 20, color: T.textMuted, lineHeight: 1, fontFamily: "inherit",
                }}>×</button>
              </div>
              {/* Scrollable content with custom scrollbar */}
              <ScrollablePane style={{ flex: 1 }}>
                <ErrorBoundary><TopicDetailCard data={selected} /></ErrorBoundary>
              </ScrollablePane>
            </div>

            {/* Right half: Dual Score Analysis */}
            <div style={{ width: "50%", display: "flex", flexDirection: "column", overflow: "hidden", background: T.bg }}>
              {/* Fixed header */}
              <div style={{
                padding: "11px 18px", borderBottom: `1px solid ${T.cardBorder}`,
                background: T.surface, flexShrink: 0,
              }}>
                <span style={{ fontSize: 10, color: T.textMuted, fontWeight: 700, letterSpacing: 1 }}>DUAL SCORE ANALYSIS</span>
              </div>
              {/* Scrollable content with custom scrollbar */}
              <ScrollablePane style={{ flex: 1 }}>
                <ErrorBoundary><HeisenbergPanel data={selected} /></ErrorBoundary>
              </ScrollablePane>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
