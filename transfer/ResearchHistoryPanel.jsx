/**
 * ResearchHistoryPanel
 * ────────────────────────────────────────────────────────────────
 * Shows HOW LONG a topic has been discussed online so users can
 * tell the difference between genuine emergence and a topic that
 * has lived in expert communities for years.
 *
 * Appears in TopicDetailCard after the MaturityBadge.
 * Lazy-fetched on first expand — does NOT block initial render.
 *
 * API: GET /scores/{topic_key}/history
 * ────────────────────────────────────────────────────────────────
 */

import { useState, useEffect, useRef } from "react";

// ── API Base (mirrors GradientScoreDashboard) ─────────────────────
const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env)
    ? (import.meta.env.VITE_API_BASE || "https://nowtrendin-e62dcb9ecb69.herokuapp.com")
    : "https://nowtrendin-e62dcb9ecb69.herokuapp.com";

// ── Light theme tokens (must match GradientScoreDashboard T object) ─
const T = {
  bg:              "#F1F5F9",
  surface:         "#FFFFFF",
  cardBorder:      "#E2E8F0",
  textPrimary:     "#0F172A",
  textSecondary:   "#374151",
  textMuted:       "#6B7280",
  textFaint:       "#9CA3AF",
  confidence:      "#047857",
  confidenceLight: "#D1FAE5",
  confidenceBorder:"#6EE7B7",
  detection:       "#1D4ED8",
  detectionLight:  "#DBEAFE",
  detectionBorder: "#93C5FD",
  goldMid:         "#D97706",
  goldLight:       "#FEF3C7",
  goldBorder:      "#FDE68A",
  purple:          "#5B21B6",
  purpleLight:     "#EDE9FE",
  purpleBorder:    "#C4B5FD",
  orange:          "#9A3412",
  orangeLight:     "#FFEDD5",
};

// ── Trajectory colours ────────────────────────────────────────────
function trajectoryStyle(traj) {
  switch (traj) {
    case "fully_mainstream":
    case "established_mainstream":
      return { color: T.textMuted,    bg: T.bg,              border: T.cardBorder,      icon: "◉", label: "Established mainstream" };
    case "established_expert":
      return { color: T.purple,       bg: T.purpleLight,     border: T.purpleBorder,    icon: "◉", label: "Established expert" };
    case "emerging":
      return { color: T.goldMid,      bg: T.goldLight,       border: T.goldBorder,      icon: "▲", label: "Actively emerging" };
    case "recently_emerged":
      return { color: T.detection,    bg: T.detectionLight,  border: T.detectionBorder, icon: "↑", label: "Recently emerged" };
    case "new":
      return { color: T.confidence,   bg: T.confidenceLight, border: T.confidenceBorder,icon: "★", label: "New term" };
    default:
      return { color: T.textFaint,    bg: T.bg,              border: T.cardBorder,      icon: "?", label: "Unknown" };
  }
}

// ── Credibility dot ───────────────────────────────────────────────
function CredDot({ level }) {
  const c = level === "HIGH" ? T.confidence : T.goldMid;
  return (
    <span style={{
      display: "inline-block", width: 6, height: 6, borderRadius: "50%",
      background: c, marginRight: 4, verticalAlign: "middle",
    }} />
  );
}

// ── Source icon by type ───────────────────────────────────────────
function sourceIcon(type) {
  switch (type) {
    case "forum":           return "💬";
    case "encyclopedia":    return "📖";
    case "code_repository": return "⌨";
    case "search_interest": return "📈";
    case "internal":        return "◎";
    case "curated":         return "✓";
    default:                return "·";
  }
}

// ── Main panel ────────────────────────────────────────────────────
export default function ResearchHistoryPanel({ topicKey, topicDisplay }) {
  const [data,       setData]       = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [expanded,   setExpanded]   = useState(false);
  const [error,      setError]      = useState(null);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showSources,  setShowSources]  = useState(false);
  const fetchedRef = useRef(false);

  // Lazy-fetch on first expand
  useEffect(() => {
    if (!expanded || fetchedRef.current || !topicKey) return;
    fetchedRef.current = true;
    setLoading(true);
    setError(null);

    fetch(`${API_BASE}/scores/${encodeURIComponent(topicKey)}/history`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [expanded, topicKey]);

  const tStyle = data ? trajectoryStyle(data.trajectory) : null;

  return (
    <div style={{ marginBottom: 20 }}>
      {/* ── Section header — always visible ─── */}
      <button
        onClick={() => setExpanded(v => !v)}
        style={{
          width: "100%", textAlign: "left", cursor: "pointer",
          background: "none", border: "none", padding: 0,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          marginBottom: expanded ? 10 : 0,
        }}
      >
        <div style={{
          fontSize: 10, letterSpacing: 1.2, color: T.textFaint,
          fontWeight: 700, textTransform: "uppercase",
        }}>
          Research History — How long has this been discussed?
        </div>
        <span style={{ fontSize: 10, color: T.textFaint, fontWeight: 700, marginLeft: 8 }}>
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {/* ── Collapsed state: brief trajectory pill if data already loaded ─ */}
      {!expanded && data && tStyle && (
        <div
          onClick={() => setExpanded(true)}
          style={{
            display: "inline-flex", alignItems: "center", gap: 5,
            padding: "3px 10px", borderRadius: 20, cursor: "pointer",
            background: tStyle.bg, border: `1px solid ${tStyle.border}`,
          }}
        >
          <span style={{ fontSize: 10 }}>{tStyle.icon}</span>
          <span style={{ fontSize: 10, fontWeight: 700, color: tStyle.color }}>{tStyle.label}</span>
          {data.years_discussed !== null && data.years_discussed !== undefined && (
            <span style={{ fontSize: 9, color: T.textFaint }}>
              — {data.years_discussed < 1
                ? `${Math.round(data.years_discussed * 12)}mo`
                : `${data.years_discussed.toFixed(1)}yr`} online
            </span>
          )}
        </div>
      )}

      {/* ── Expanded body ──────────────────────────────────────────── */}
      {expanded && (
        <div>
          {/* Loading */}
          {loading && (
            <div style={{
              padding: "16px", borderRadius: 10, textAlign: "center",
              background: T.bg, border: `1px solid ${T.cardBorder}`,
            }}>
              <div style={{ fontSize: 11, color: T.textFaint, fontStyle: "italic" }}>
                Researching history for "{topicDisplay || topicKey}"…
              </div>
              <div style={{ fontSize: 9, color: T.textFaint, marginTop: 4 }}>
                Checking Hacker News, Wikipedia, GitHub, Google Trends
              </div>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div style={{
              padding: "12px 14px", borderRadius: 10,
              background: T.orangeLight, border: `1px solid #FDBA74`,
            }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: T.orange, marginBottom: 3 }}>
                Research unavailable
              </div>
              <div style={{ fontSize: 10, color: T.textSecondary }}>
                History lookup failed for this topic. The engine continues to score normally.
              </div>
            </div>
          )}

          {/* Data loaded */}
          {data && !loading && (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>

              {/* ── Trajectory badge ── */}
              <div style={{
                padding: "12px 14px", borderRadius: 10,
                background: tStyle.bg, border: `1px solid ${tStyle.border}`,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: 16 }}>{tStyle.icon}</span>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 800, color: tStyle.color }}>
                      {data.trajectory_label}
                    </div>
                    <div style={{ fontSize: 9, color: T.textFaint }}>
                      {data.first_known_date
                        ? `First recorded: ${data.first_known_date}`
                        : "First recorded: unknown"}
                      {data.years_discussed !== null && data.years_discussed !== undefined
                        ? ` · ${data.years_discussed < 1
                            ? `${Math.round(data.years_discussed * 12)} months`
                            : `${data.years_discussed.toFixed(1)} years`} of documented discussion`
                        : ""}
                    </div>
                  </div>
                </div>
                <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.6 }}>
                  {data.summary_short}
                </div>
              </div>

              {/* ── Gradient implication — the key insight ── */}
              <div style={{
                padding: "12px 14px", borderRadius: 10,
                background: T.surface, border: `1px solid ${T.cardBorder}`,
              }}>
                <div style={{
                  fontSize: 9, letterSpacing: 1.2, fontWeight: 700,
                  color: T.textFaint, marginBottom: 6, textTransform: "uppercase",
                }}>
                  What this means for the Gradient Score
                </div>
                <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.7 }}>
                  {data.gradient_implication}
                </div>
              </div>

              {/* ── Summary long ── */}
              {data.summary_long && data.summary_long !== data.summary_short && (
                <div style={{
                  padding: "10px 12px", borderRadius: 8,
                  background: T.bg, border: `1px solid ${T.cardBorder}`,
                }}>
                  <div style={{ fontSize: 10, color: T.textSecondary, lineHeight: 1.7 }}>
                    {data.summary_long}
                  </div>
                </div>
              )}

              {/* ── Key milestones (from KNOWN_TOPICS) ── */}
              {data.milestones && data.milestones.length > 0 && (
                <div style={{
                  padding: "10px 14px", borderRadius: 10,
                  background: T.surface, border: `1px solid ${T.cardBorder}`,
                }}>
                  <div style={{
                    fontSize: 9, letterSpacing: 1.2, fontWeight: 700,
                    color: T.textFaint, marginBottom: 8, textTransform: "uppercase",
                  }}>
                    Key milestones
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {data.milestones.map((m, i) => (
                      <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                        <span style={{
                          fontSize: 9, fontWeight: 700, color: T.detection,
                          fontFamily: "'DM Mono', monospace", minWidth: 44, flexShrink: 0,
                        }}>
                          {m.year}
                        </span>
                        <span style={{ fontSize: 10, color: T.textSecondary, lineHeight: 1.5 }}>
                          {m.event}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Full timeline (collapsible) ── */}
              {data.timeline && data.timeline.length > 0 && (
                <div>
                  <button
                    onClick={() => setShowTimeline(v => !v)}
                    style={{
                      background: "none", border: `1px solid ${T.cardBorder}`,
                      borderRadius: 8, padding: "6px 12px", cursor: "pointer",
                      fontSize: 10, color: T.textMuted, width: "100%", textAlign: "left",
                      display: "flex", justifyContent: "space-between",
                    }}
                  >
                    <span>Full timeline ({data.timeline.length} events)</span>
                    <span>{showTimeline ? "▲ hide" : "▼ show"}</span>
                  </button>
                  {showTimeline && (
                    <div style={{
                      marginTop: 6, padding: "10px 14px", borderRadius: 10,
                      background: T.surface, border: `1px solid ${T.cardBorder}`,
                    }}>
                      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        {data.timeline.map((ev, i) => (
                          <div key={i} style={{
                            display: "flex", gap: 10, alignItems: "flex-start",
                            paddingBottom: i < data.timeline.length - 1 ? 8 : 0,
                            borderBottom: i < data.timeline.length - 1
                              ? `1px solid ${T.cardBorder}` : "none",
                          }}>
                            <span style={{
                              fontSize: 9, fontWeight: 700, color: T.detection,
                              fontFamily: "'DM Mono', monospace", minWidth: 52, flexShrink: 0,
                            }}>
                              {(ev.date || "").slice(0, 7)}
                            </span>
                            <div style={{ flex: 1 }}>
                              <div style={{ fontSize: 10, color: T.textSecondary, lineHeight: 1.5 }}>
                                {ev.event}
                              </div>
                              <div style={{ fontSize: 9, color: T.textFaint, marginTop: 1 }}>
                                {ev.source}
                                {ev.url && (
                                  <a
                                    href={ev.url}
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{ color: T.detection, marginLeft: 6, textDecoration: "none" }}
                                  >
                                    ↗
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ── Sources (collapsible) ── */}
              {data.sources && data.sources.length > 0 && (
                <div>
                  <button
                    onClick={() => setShowSources(v => !v)}
                    style={{
                      background: "none", border: `1px solid ${T.cardBorder}`,
                      borderRadius: 8, padding: "6px 12px", cursor: "pointer",
                      fontSize: 10, color: T.textMuted, width: "100%", textAlign: "left",
                      display: "flex", justifyContent: "space-between",
                    }}
                  >
                    <span>Sources ({data.sources.length})</span>
                    <span>{showSources ? "▲ hide" : "▼ show"}</span>
                  </button>
                  {showSources && (
                    <div style={{
                      marginTop: 6, display: "flex", flexDirection: "column", gap: 6,
                    }}>
                      {data.sources.map((src, i) => (
                        <div key={i} style={{
                          padding: "8px 12px", borderRadius: 8,
                          background: T.surface, border: `1px solid ${T.cardBorder}`,
                          display: "flex", alignItems: "flex-start", gap: 8,
                        }}>
                          <span style={{ fontSize: 14, flexShrink: 0 }}>
                            {sourceIcon(src.type)}
                          </span>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 2 }}>
                              <CredDot level={src.credibility} />
                              {src.source_url
                                ? (
                                  <a
                                    href={src.source_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{
                                      fontSize: 10, fontWeight: 700,
                                      color: T.detection, textDecoration: "none",
                                    }}
                                  >
                                    {src.source_name}
                                  </a>
                                )
                                : (
                                  <span style={{ fontSize: 10, fontWeight: 700, color: T.textSecondary }}>
                                    {src.source_name}
                                  </span>
                                )
                              }
                            </div>
                            <div style={{ fontSize: 9, color: T.textFaint, lineHeight: 1.4 }}>
                              {src.first_date_str || (src.first_date ? `First record: ${src.first_date}` : "")}
                              {src.note && <span style={{ marginLeft: 6, fontStyle: "italic" }}>{src.note}</span>}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* ── Cached notice ── */}
              {data.cached && (
                <div style={{ fontSize: 9, color: T.textFaint, textAlign: "right" }}>
                  Cached result · {data.researched_at ? new Date(data.researched_at).toLocaleDateString() : ""}
                </div>
              )}
              {data.from_known_database && (
                <div style={{ fontSize: 9, color: T.textFaint, textAlign: "right" }}>
                  ✓ Manually verified research database
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
