/**
 * ================================================================
 * NOW TRENDIN — AI VARIATION MAP COMPONENT  (light theme)
 * ================================================================
 *
 * Answers the core user question:
 *   "Why does 'AI' score 26 when AI is the hottest thing right now?"
 *
 * Shows ALL variations of the searched AI term ranked by current
 * velocity tier — so 'AI' at 26 immediately surfaces the Tier 1
 * sub-topics ('agentic coding', 'agent memory', etc.) at 97–100.
 *
 * Components exported:
 *   AIVariationMap       — full variation list for TopicDetailCard
 *   AIResearchSection    — tier-context + what to do/watch
 *   AITierBadge          — small badge for TopicCard list view
 *   AIScoreWithContext   — score pair + tier headline
 * ================================================================
 */

import { useState } from "react";

// ── Light theme tokens (matches GradientScoreDashboard T object) ──
const C = {
  bg:          "#F1F5F9",
  surface:     "#FFFFFF",
  border:      "#E2E8F0",
  text:        "#0F172A",
  secondary:   "#374151",
  muted:       "#6B7280",
  faint:       "#9CA3AF",
  // Tier colours
  green:       "#047857",   // VIRAL
  greenLight:  "#D1FAE5",
  greenBorder: "#6EE7B7",
  blue:        "#1D4ED8",   // STRONG
  blueLight:   "#DBEAFE",
  blueBorder:  "#93C5FD",
  gold:        "#D97706",   // RESURGENT
  goldLight:   "#FEF3C7",
  goldBorder:  "#FDE68A",
  gray:        "#64748B",   // ESTABLISHED
  grayLight:   "#F8FAFC",
  grayBorder:  "#CBD5E1",
  dim:         "#94A3B8",   // MAINSTREAM
  dimLight:    "#F1F5F9",
  dimBorder:   "#E2E8F0",
  orange:      "#9A3412",
  orangeLight: "#FFEDD5",
};

const TIER_CONFIG = {
  tier_1: {
    emoji:      "🟢",
    label:      "VIRAL",
    colour:     C.green,
    bg:         C.greenLight,
    border:     C.greenBorder,
    action:     "ACT NOW",
    actionCol:  C.green,
    desc:       "Maximum lead time — still in expert communities",
  },
  tier_2: {
    emoji:      "🔵",
    label:      "STRONG",
    colour:     C.blue,
    bg:         C.blueLight,
    border:     C.blueBorder,
    action:     "PLAN",
    actionCol:  C.blue,
    desc:       "Window open — begin positioning",
  },
  tier_3: {
    emoji:      "⚪",
    label:      "ESTABLISHED",
    colour:     C.gray,
    bg:         C.grayLight,
    border:     C.grayBorder,
    action:     "MONITOR",
    actionCol:  C.gray,
    desc:       "Established expert vocabulary — not currently emerging",
  },
  tier_3_resurgent: {
    emoji:      "🟡",
    label:      "RESURGENT",
    colour:     C.gold,
    bg:         C.goldLight,
    border:     C.goldBorder,
    action:     "ACT NOW",
    actionCol:  C.gold,
    desc:       "Established topic showing renewed acceleration",
  },
  tier_4: {
    emoji:      "⚫",
    label:      "MAINSTREAM",
    colour:     C.dim,
    bg:         C.dimLight,
    border:     C.dimBorder,
    action:     "PAST",
    actionCol:  C.dim,
    desc:       "Already arrived — low gradient is correct",
  },
};

// ── Mini score bar ────────────────────────────────────────────────
function ScoreBar({ score, col, label }) {
  return (
    <div style={{ minWidth: 80 }}>
      <div style={{
        display: "flex", justifyContent: "space-between",
        alignItems: "center", marginBottom: 2,
      }}>
        <span style={{ fontSize: 9, color: C.muted }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 700, color: col }}>
          {Math.round(score)}
        </span>
      </div>
      <div style={{
        height: 4, borderRadius: 2, background: C.border, overflow: "hidden",
      }}>
        <div style={{
          height: "100%",
          width: `${Math.min(100, score)}%`,
          background: col,
          borderRadius: 2,
          transition: "width 0.5s ease",
        }} />
      </div>
    </div>
  );
}


// ================================================================
// 1. AI VARIATION MAP — Full ranked list for the detail panel
// ================================================================

export function AIVariationMap({ signal }) {
  const [expanded,      setExpanded]      = useState(null);
  const [showVariations, setShowVariations] = useState(false);

  if (!signal) return null;

  const {
    variations       = [],
    ai_tier,
    ai_tier_label,
    ai_classification,
    detection_score  = 0,
    confidence_score = 0,
    research         = {},
    topic_display,
  } = signal;

  // Only show when AI taxonomy data is present
  if (!ai_tier && (!variations || variations.length === 0)) return null;

  const currentTier  = TIER_CONFIG[ai_tier] || TIER_CONFIG.tier_4;
  const isMainstream = ai_tier === "tier_4";
  const isViral      = ai_tier === "tier_1";
  const tier1Related = (variations || []).filter(
    v => v.tier === "tier_1" && !v.is_queried
  );

  return (
    <div style={{ marginBottom: 20 }}>
      {/* Section header */}
      <div style={{
        fontSize: 10, letterSpacing: 1.2, color: C.faint,
        fontWeight: 700, textTransform: "uppercase", marginBottom: 10,
      }}>
        AI Topic Intelligence
      </div>

      {/* ── Tier context card ── */}
      <div style={{
        padding: "12px 14px", borderRadius: 10, marginBottom: 10,
        background: currentTier.bg, border: `1px solid ${currentTier.border}`,
        borderLeft: `4px solid ${currentTier.colour}`,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
          <span style={{ fontSize: 16, flexShrink: 0 }}>{currentTier.emoji}</span>
          <div>
            <span style={{
              fontSize: 11, fontWeight: 800, color: currentTier.colour,
              letterSpacing: "0.05em",
            }}>
              {currentTier.label}
            </span>
            <span style={{ fontSize: 10, color: C.muted, marginLeft: 8 }}>
              {currentTier.desc}
            </span>
          </div>
        </div>

        {/* Mainstream redirect */}
        {isMainstream && (
          <div style={{
            padding: "8px 10px", borderRadius: 6, marginTop: 6,
            background: C.orangeLight, border: `1px solid #FDBA74`,
          }}>
            <div style={{ fontSize: 11, color: C.text, lineHeight: 1.6 }}>
              <span style={{ fontWeight: 700, color: C.orange }}>
                "{ai_classification || topic_display}" has already arrived —{" "}
              </span>
              the generic term scores low ({Math.round(detection_score)}) because
              mentions are distributed across all audience types, not concentrated
              in expert communities. The leading edge is in the Tier 1 sub-topics below.
            </div>
          </div>
        )}

        {/* Viral confirmation */}
        {isViral && (
          <div style={{ fontSize: 11, color: C.secondary, lineHeight: 1.5, marginTop: 4 }}>
            This is genuinely new vocabulary in the developer community.
            Mainstream awareness has not yet arrived — this is the early-actor window.
          </div>
        )}

        {/* Tier 1 callout for non-viral parent topics */}
        {!isViral && !isMainstream && tier1Related.length > 0 && (
          <div style={{
            marginTop: 6, padding: "6px 10px", borderRadius: 6,
            background: C.greenLight, border: `1px solid ${C.greenBorder}`,
          }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: C.green }}>
              🟢 Tier 1 sub-signals active:{" "}
            </span>
            <span style={{ fontSize: 10, color: C.secondary }}>
              {tier1Related.slice(0, 3).map(r => r.display).join(", ")}
            </span>
          </div>
        )}
      </div>

      {/* ── Research section (what to do / what to watch) ── */}
      {research?.what_to_do && (
        <div style={{
          padding: "10px 12px", borderRadius: 8, marginBottom: 10,
          background: C.surface, border: `1px solid ${C.border}`,
        }}>
          <div style={{
            fontSize: 9, letterSpacing: 1, fontWeight: 700,
            color: C.faint, marginBottom: 5, textTransform: "uppercase",
          }}>
            What to do — AI tier context
          </div>
          <div style={{ fontSize: 11, color: C.secondary, lineHeight: 1.6 }}>
            {research.what_to_do}
          </div>
        </div>
      )}

      {research?.what_to_watch && (
        <div style={{
          padding: "10px 12px", borderRadius: 8, marginBottom: 10,
          background: C.bg, border: `1px solid ${C.border}`,
        }}>
          <div style={{
            fontSize: 9, letterSpacing: 1, fontWeight: 700,
            color: C.faint, marginBottom: 5, textTransform: "uppercase",
          }}>
            What to watch
          </div>
          <div style={{ fontSize: 11, color: C.secondary, lineHeight: 1.6 }}>
            {research.what_to_watch}
          </div>
        </div>
      )}

      {/* ── Variation map — collapsible ── */}
      {variations && variations.length > 1 && (
        <div>
          <button
            onClick={() => setShowVariations(v => !v)}
            style={{
              width: "100%", textAlign: "left", cursor: "pointer",
              background: "none", border: `1px solid ${C.border}`,
              borderRadius: 8, padding: "8px 12px",
              display: "flex", justifyContent: "space-between",
              alignItems: "center", marginBottom: showVariations ? 8 : 0,
            }}
          >
            <span style={{ fontSize: 10, color: C.muted, fontWeight: 600 }}>
              All variations — ranked by velocity ({variations.length})
            </span>
            <span style={{ fontSize: 10, color: C.faint }}>
              {showVariations ? "▲ hide" : "▼ show"}
            </span>
          </button>

          {showVariations && (
            <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              {variations.map((v, i) => {
                const tier   = TIER_CONFIG[v.tier] || TIER_CONFIG.tier_4;
                const isOpen = expanded === i;
                const isThis = v.is_queried;

                return (
                  <div key={i}>
                    <div
                      onClick={() => setExpanded(isOpen ? null : i)}
                      style={{
                        display: "flex", alignItems: "center", gap: 8,
                        padding: "8px 12px", borderRadius: 8, cursor: "pointer",
                        background: isThis ? tier.bg : C.surface,
                        border: `1px solid ${isThis ? tier.border : C.border}`,
                        borderLeft: `3px solid ${tier.colour}`,
                      }}
                    >
                      {/* Tier emoji */}
                      <span style={{ fontSize: 12, flexShrink: 0 }}>
                        {tier.emoji}
                      </span>

                      {/* Name */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{
                          display: "flex", alignItems: "center",
                          gap: 6, marginBottom: 1,
                        }}>
                          <span style={{
                            fontSize: 11, fontWeight: isThis ? 700 : 500,
                            color: C.text,
                          }}>
                            {v.display}
                          </span>
                          {isThis && (
                            <span style={{
                              fontSize: 8, padding: "1px 5px",
                              background: tier.colour, color: "#fff",
                              borderRadius: 8, fontWeight: 700,
                            }}>
                              THIS SIGNAL
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: 9, color: C.muted }}>
                          {tier.label}
                          {v.velocity && v.velocity !== "UNKNOWN"
                            ? ` · ${v.velocity}` : ""}
                        </div>
                      </div>

                      {/* Score bars */}
                      <div style={{
                        display: "flex", flexDirection: "column", gap: 3,
                        width: 82, flexShrink: 0,
                      }}>
                        <ScoreBar score={v.typical_detection}  col={tier.colour} label="DET" />
                        <ScoreBar score={v.typical_confidence} col={tier.colour} label="CONF" />
                      </div>

                      {/* Action badge */}
                      <div style={{
                        padding: "3px 7px", borderRadius: 5, flexShrink: 0,
                        background: tier.bg,
                        border: `1px solid ${tier.border}`,
                        fontSize: 8, fontWeight: 700, color: tier.actionCol,
                        width: 58, textAlign: "center",
                      }}>
                        {tier.action}
                      </div>

                      <span style={{ fontSize: 9, color: C.faint, flexShrink: 0 }}>
                        {isOpen ? "▲" : "▼"}
                      </span>
                    </div>

                    {/* Expanded detail */}
                    {isOpen && v.why_different && (
                      <div style={{
                        padding: "8px 12px",
                        background: C.bg,
                        border: `1px solid ${C.border}`,
                        borderTop: "none",
                        borderRadius: "0 0 8px 8px",
                        fontSize: 10, color: C.secondary, lineHeight: 1.6,
                      }}>
                        {v.why_different}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Accuracy footnote */}
      {research?.accuracy_note && (
        <div style={{
          marginTop: 10, padding: "6px 10px",
          background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6,
          fontSize: 9, color: C.faint, lineHeight: 1.5, fontStyle: "italic",
        }}>
          {research.accuracy_note}
        </div>
      )}

      {/* Lead time warning */}
      {research?.lead_time_warning && (
        <div style={{
          marginTop: 8, padding: "6px 10px",
          background: C.blueLight, border: `1px solid ${C.blueBorder}`,
          borderRadius: 6, fontSize: 10, color: C.blue,
        }}>
          {research.lead_time_warning}
        </div>
      )}
    </div>
  );
}


// ================================================================
// 2. AI RESEARCH SECTION — compact version for use alongside existing panels
// ================================================================

export function AIResearchSection({ signal }) {
  const [showContext, setShowContext] = useState(false);
  if (!signal?.research?.tier_context && !signal?.ai_tier) return null;

  const { research = {}, ai_tier } = signal;
  const tier = TIER_CONFIG[ai_tier] || TIER_CONFIG.tier_4;

  return (
    <div style={{ marginBottom: 12 }}>
      {research.topic_age && (
        <div style={{
          padding: "8px 10px", borderRadius: 7,
          background: `${tier.colour}10`,
          border: `1px solid ${tier.border || C.border}`,
          marginBottom: 8,
        }}>
          <div style={{
            fontSize: 9, fontWeight: 700, color: C.faint,
            letterSpacing: 0.8, marginBottom: 4,
          }}>
            TOPIC AGE
          </div>
          <div style={{ fontSize: 10, color: C.secondary, lineHeight: 1.5 }}>
            {research.topic_age}
          </div>
        </div>
      )}

      {research.tier_context && (
        <div>
          <button
            onClick={() => setShowContext(v => !v)}
            style={{
              background: "none", border: "none", cursor: "pointer",
              fontSize: 10, color: C.muted, padding: 0, marginBottom: 4,
            }}
          >
            {showContext ? "▲ hide tier context" : "▼ why this score?"}
          </button>
          {showContext && (
            <div style={{
              padding: "8px 12px", borderRadius: 7,
              background: C.surface, border: `1px solid ${C.border}`,
              fontSize: 10, color: C.secondary, lineHeight: 1.6,
            }}>
              {research.tier_context}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


// ================================================================
// 3. AI TIER BADGE — compact for TopicCard list view
// ================================================================

export function AITierBadge({ signal }) {
  if (!signal?.ai_tier) return null;

  const { ai_tier, ai_velocity_signal } = signal;
  const tier = TIER_CONFIG[ai_tier];
  if (!tier) return null;

  return (
    <div style={{
      display: "inline-flex", alignItems: "center",
      gap: 5, marginTop: 3,
    }}>
      <span style={{ fontSize: 10 }}>{tier.emoji}</span>
      <span style={{
        fontSize: 8, fontWeight: 700, color: tier.colour,
        letterSpacing: "0.04em",
      }}>
        {tier.label}
      </span>
      {(ai_tier === "tier_4") && (
        <span style={{ fontSize: 8, color: C.faint, fontStyle: "italic" }}>
          — see sub-topics
        </span>
      )}
      {(ai_tier === "tier_1" || ai_tier === "tier_3_resurgent") && ai_velocity_signal && (
        <span style={{
          fontSize: 7, padding: "1px 4px",
          background: `${tier.colour}18`,
          border: `1px solid ${tier.colour}50`,
          borderRadius: 6, color: tier.colour, fontWeight: 700,
        }}>
          {ai_velocity_signal}
        </span>
      )}
    </div>
  );
}


// ================================================================
// 4. AI SCORE WITH CONTEXT — tier headline above the score pair
// ================================================================

export function AIScoreWithContext({ signal }) {
  if (!signal?.ai_tier) return null;

  const {
    detection_score  = 0,
    confidence_score = 0,
    ai_tier,
    ai_classification,
  } = signal;

  const tier = TIER_CONFIG[ai_tier] || TIER_CONFIG.tier_4;
  const gap  = Math.abs((detection_score || 0) - (confidence_score || 0));

  const MESSAGES = {
    tier_1:           { headline: "Viral AI Topic — Maximum Lead Time",
                        sub: "Expert community only. Mainstream awareness has not arrived." },
    tier_2:           { headline: "Strong Active Signal — Window Open",
                        sub: "Building momentum. Still early enough to position." },
    tier_3:           { headline: "Established Expert Vocabulary",
                        sub: "High gradient is permanent home, not emergence. Monitor sub-topics." },
    tier_3_resurgent: { headline: "Resurgence — Established Topic Accelerating",
                        sub: "Above its historical baseline — genuine renewed momentum." },
    tier_4:           { headline: "Mainstream — Already Arrived",
                        sub: "Low score is correct. See Tier 1 variations below for the leading edge." },
  };

  const msg = MESSAGES[ai_tier] || MESSAGES.tier_4;

  return (
    <div style={{
      padding: "12px 14px", borderRadius: 10, marginBottom: 12,
      background: tier.bg, border: `1px solid ${tier.border}`,
      borderLeft: `4px solid ${tier.colour}`,
    }}>
      {/* Tier headline */}
      <div style={{
        fontSize: 12, fontWeight: 700, color: tier.colour, marginBottom: 3,
      }}>
        {tier.emoji} {msg.headline}
      </div>
      <div style={{
        fontSize: 10, color: C.muted, marginBottom: 12, lineHeight: 1.4,
      }}>
        {msg.sub}
      </div>

      {/* Score pair */}
      <div style={{ display: "flex", gap: 12 }}>
        <div style={{
          flex: 1, textAlign: "center", padding: "8px 0",
          borderRadius: 8, background: C.blueLight,
          border: `1px solid ${C.blueBorder}`,
        }}>
          <div style={{
            fontSize: 26, fontWeight: 800, color: C.blue, lineHeight: 1,
          }}>
            {Math.round(detection_score || 0)}
          </div>
          <div style={{ fontSize: 8, color: C.muted, marginTop: 3, letterSpacing: 0.5 }}>
            DETECTION
          </div>
          <div style={{ fontSize: 8, color: C.faint }}>~22% false positive</div>
        </div>

        <div style={{
          flex: 1, textAlign: "center", padding: "8px 0",
          borderRadius: 8, background: C.greenLight,
          border: `1px solid ${C.greenBorder}`,
        }}>
          <div style={{
            fontSize: 26, fontWeight: 800, color: C.green, lineHeight: 1,
          }}>
            {Math.round(confidence_score || 0)}
          </div>
          <div style={{ fontSize: 8, color: C.muted, marginTop: 3, letterSpacing: 0.5 }}>
            CONFIDENCE
          </div>
          <div style={{ fontSize: 8, color: C.faint }}>&lt;9% false positive</div>
        </div>
      </div>

      {/* Gap */}
      {gap > 0 && (
        <div style={{
          marginTop: 8, fontSize: 9, color: C.muted, textAlign: "center",
        }}>
          {Math.round(gap)}-point gap ·{" "}
          {gap <= 15 ? "Both scores agree — high conviction"
           : gap <= 35 ? "Confirmation building — early stage"
           : gap <= 60 ? "Very early — maximum lead time"
           : "Speculative — dark matter signal"}
        </div>
      )}

      {/* Classification name */}
      {ai_classification && ai_classification !== signal.topic_display && (
        <div style={{
          marginTop: 8, fontSize: 9, color: C.faint, textAlign: "center",
          fontStyle: "italic",
        }}>
          Classified as: {ai_classification}
        </div>
      )}
    </div>
  );
}
