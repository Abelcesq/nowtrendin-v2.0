import React from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft } from 'lucide-react-native';
import Svg, { Circle } from 'react-native-svg';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { GradientScoreRing } from '../../../components/ui/GradientScoreRing';
import { NotMeasuredChip, absentTierLabel } from '../../../components/ui/NotMeasuredChip';
import { SignalAnalysisPanel } from '../../../components/trends/SignalAnalysisPanel';
import { useCrypto } from '../../../hooks/useSignals';
import { MARKET_TIER_COLOR, isAbsentTier } from '../../../lib/marketCategories';

// Aurora detail-screen conventions (same as the market detail risk/[key]):
// Positioning = sapphire, Market Confirmation = emerald.
// Chairman 2026-09-14: "Money Movement" retired from ALL visible crypto copy —
// the client-facing name is "Positioning" (engine field names unchanged).
const POS_COLOR = '#2A5B9E';
const MC_COLOR = '#2E7D5B';
const POS_LABEL = 'POSITIONING';
const MC_LABEL = 'MARKET CONFIRMATION';

// D6 (board 2026-09-15): the gap_state ENUM values are payload contract and never change;
// the DISPLAY retires "money" vocabulary (web parity: Crypto.tsx GAP_STATE_DISPLAY). Known
// states map here; anything unknown falls back to the plain underscore-replace.
const GAP_STATE_DISPLAY: Record<string, string> = {
  money_absent: 'positioning absent',
  confirmation_absent: 'confirmation absent',
  CALIBRATING: 'CALIBRATING',
  LIMITED_DATA: 'LIMITED DATA',
  EARLY_MOVEMENT: 'EARLY MOVEMENT',
  CONFIRMED_MOVEMENT: 'CONFIRMED MOVEMENT',
  BROAD_ONLY: 'BROAD ONLY',
  MIXED: 'MIXED',
};
const gapStateLabel = (s?: string | null) =>
  s ? (GAP_STATE_DISPLAY[s] ?? s.replace(/_/g, ' ')) : '';

const FLOW_META: Record<string, { label: string; color: string }> = {
  inflow: { label: '▲ INFLOW', color: '#2E7D5B' },
  outflow: { label: '▼ OUTFLOW', color: '#B11226' },
  divergent: { label: '◆ DIVERGENT', color: '#6B4FA0' },
  neutral: { label: '• NEUTRAL', color: '#9A9AA2' },
};

// C1 (board 2026-09-14): an absent read gets an EMPTY SLOT, never an arc — an
// arc at 0 draws a measured zero. Dashed empty track + centered em-dash, muted,
// never red (web parity: Crypto.tsx absentSlot).
function AbsentGauge() {
  return (
    <View style={{ width: 120, height: 120, alignItems: 'center', justifyContent: 'center' }}>
      <Svg width={120} height={120}>
        <Circle cx={60} cy={60} r={54} stroke="#ECECEC" strokeWidth={2} strokeDasharray="3 6" fill="none" />
      </Svg>
      <Text style={{ position: 'absolute', color: '#9A9AA2', fontSize: 30, fontWeight: '900' }}>—</Text>
    </View>
  );
}

// Section headline in the Aurora card style.
function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase mb-3">{children}</Text>
  );
}

// Full crypto detail — WEB PARITY: the same sections and data points as the
// web terminal's Crypto rail (header · price-as-of · disclaimer · dual rings ·
// gap state + interpretation · Signal Analysis · Market Factors · Price & Insider
// Tracking facts · Positioning vs Price Register · the two explainers ·
// what-it-measures · disclaimer), in Aurora form.
export default function CryptoDetail() {
  const router = useRouter();
  const { coin: ticker } = useLocalSearchParams<{ coin: string }>();
  const { coins, isLoading } = useCrypto();
  const c = coins.find((x) => x.coin === (ticker || '').toUpperCase());

  if (isLoading && !c) {
    return (
      <Screen scroll>
        <ActivityIndicator size="large" color="#1B3066" style={{ marginTop: 80 }} />
      </Screen>
    );
  }
  if (!c) {
    return (
      <Screen scroll>
        <TouchableOpacity onPress={() => router.back()} className="flex-row items-center py-4">
          <ChevronLeft size={20} color="#3C4663" />
          <Text className="text-textSecondary text-sm font-semibold">Back</Text>
        </TouchableOpacity>
        <Text className="text-textMuted text-center mt-12">Coin not found in the current roster.</Text>
      </Screen>
    );
  }

  // C1/K1: an engine-served ABSENT (or missing) tier is ABSENCE — hollow
  // NOT MEASURED chip, never a filled tier chip in a measured color.
  const tierAbsent = isAbsentTier(c.tier);
  const tierColor = !tierAbsent ? (MARKET_TIER_COLOR[c.tier!] ?? '#9A9AA2') : '#9A9AA2';
  const flow = c.flow ? (FLOW_META[c.flow] ?? { label: `• ${c.flow.toUpperCase()}`, color: '#9A9AA2' }) : null;
  const comps = Object.entries(c.components ?? {});
  // K17: the lead/gap is SIGNED — positive = Positioning ahead, negative = price
  // confirmation ahead. Print the sign explicitly; never Math.abs in display.
  const lead = c.lead == null ? null : Math.round(c.lead * 10) / 10;
  const leadLabel = lead == null ? null : lead > 0 ? `+${lead}` : `${lead}`;
  const gapHead = c.moneyDataAbsent ? 'MARKET-CONFIRMATION ONLY'
    : c.calibrating ? 'CALIBRATING' : gapStateLabel(c.gapState);

  return (
    <Screen scroll>
      {/* Back */}
      <TouchableOpacity onPress={() => router.back()} className="flex-row items-center pt-2 pb-3 self-start">
        <ChevronLeft size={20} color="#3C4663" />
        <Text className="text-textSecondary text-sm font-semibold">Back</Text>
      </TouchableOpacity>

      {/* Header — name · ticker, Crypto · tier · flow, price as-of */}
      <Text className="text-textPrimary text-3xl font-extrabold" style={{ letterSpacing: -0.8 }}>
        {c.name} <Text style={{ color: '#9A9AA2', fontWeight: '600' }}>· {c.coin}</Text>
      </Text>
      <View className="flex-row items-center flex-wrap mt-1.5" style={{ gap: 6 }}>
        <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>CRYPTO ·</Text>
        {tierAbsent ? (
          <NotMeasuredChip label={absentTierLabel(c.absenceClass)} />
        ) : (
          <Text style={{ color: tierColor, fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>{c.tier}</Text>
        )}
        {flow ? (
          <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>
            · <Text style={{ color: flow.color }}>{flow.label}</Text>
          </Text>
        ) : null}
        {c.calibrating ? (
          <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>· CALIBRATING</Text>
        ) : null}
      </View>
      {c.priceClose != null && (
        <Text style={{ color: '#3C4663', fontSize: 14, fontWeight: '600', marginTop: 6 }}>
          ${Number(c.priceClose).toLocaleString()}{c.priceAsOf ? <Text style={{ color: '#9A9AA2', fontWeight: '500' }}> · price as of {c.priceAsOf}</Text> : null}
        </Text>
      )}

      <Disclaimer className="mt-4 mb-2 px-0 text-left" />

      {/* Dual rings — Positioning (D) / Market Confirmation (M). An absent
          Positioning read renders the C1 empty slot — never a numeric 0 arc. */}
      <View className="bg-card rounded-3xl p-5 mt-2">
        <View className="flex-row justify-around">
          <View className="items-center">
            {c.moneyDataAbsent || c.moneyMovement == null ? (
              <AbsentGauge />
            ) : (
              <GradientScoreRing score={Math.round(c.moneyMovement)} color={POS_COLOR} size="lg" caption="/100" />
            )}
            <Text className="text-textPrimary text-xs font-bold mt-2">{POS_LABEL}</Text>
            <Text className="text-textMuted text-xs mt-0.5">
              {c.moneyDataAbsent || c.moneyMovement == null
                ? absentTierLabel(c.absenceClass).toLowerCase()
                : 'informed proxies · D'}
            </Text>
          </View>
          <View className="items-center">
            <GradientScoreRing score={Math.round(c.marketConfirmation)} color={MC_COLOR} size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">{MC_LABEL}</Text>
            <Text className="text-textMuted text-xs mt-0.5">coin price · M</Text>
          </View>
        </View>
      </View>

      {/* Gap state + interpretation — K17: signed gap, sign printed */}
      {(gapHead || c.interpretation) && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          {!!gapHead && (
            <Text style={{ color: tierAbsent ? '#3C4663' : tierColor, fontSize: 12, fontWeight: '800', letterSpacing: 1 }}>
              {gapHead}{!c.calibrating && !c.moneyDataAbsent && leadLabel != null ? ` · ${leadLabel}-pt gap` : ''}
            </Text>
          )}
          {!!c.interpretation && (
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 8 }}>
              {c.interpretation}
            </Text>
          )}
          {!!c.interpretation && (
            <Text className="text-textMuted text-xs mt-3" style={{ lineHeight: 16 }}>
              AI-generated overview · qualitative context are computer generated. All information
              contained herein may not be accurate including any and all figures indicated in this
              section and or site and may be an approximation and should not be construed as
              financial, investment, or legal advice.
            </Text>
          )}
        </View>
      )}

      {/* Signal Analysis — enterprise per-item narrative (held-out, measurement-only) */}
      <SignalAnalysisPanel
        kind="crypto"
        item={{
          item_name: c.name,
          detection: c.moneyMovement,
          confidence: c.marketConfirmation,
          flow: c.flow,
          tier: c.tier,
          dark_matter: c.darkMatter ?? undefined,
        }}
      />

      {/* Market Factors — §17: real value or n/a, never NaN */}
      {comps.length > 0 && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          <SectionTitle>Market Factors</SectionTitle>
          {comps.map(([label, comp]) => {
            const na = comp.notApplicable || comp.score == null;
            const col = na ? '#9A9AA2' : comp.feeds === 'money_movement' ? POS_COLOR : MC_COLOR;
            const short = label.replace(/\s*\(.*\)$/, '');
            const width = na ? 0 : Math.max(4, Math.min(100, comp.score ?? 0));
            return (
              <View key={label} className="flex-row items-center mb-2.5" style={{ gap: 10, opacity: na ? 0.5 : 1 }}>
                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: col }} />
                <Text numberOfLines={1} style={{ color: '#3C4663', fontSize: 12, fontWeight: '600', flex: 1 }}>
                  {short}{!na && comp.baselineRelative ? ' ✓' : ''}
                </Text>
                <View style={{ width: 84, height: 5, borderRadius: 3, backgroundColor: '#ECECEC', overflow: 'hidden' }}>
                  <View style={{ width: `${width}%`, height: 5, backgroundColor: col }} />
                </View>
                <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '800', minWidth: 28, textAlign: 'right' }}>
                  {na ? 'n/a' : Math.round(comp.score ?? 0)}
                </Text>
              </View>
            );
          })}
          <Text className="text-textMuted text-xs mt-2">
            <Text style={{ color: POS_COLOR }}>●</Text> positioning · <Text style={{ color: MC_COLOR }}>●</Text> market confirmation · ✓ = scored vs own history
          </Text>
        </View>
      )}

      {/* Price & Insider Tracking facts — only what contributed (§17) */}
      {(c.change7dPct != null || c.darkMatter) && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          <SectionTitle>Price & Insider Tracking</SectionTitle>
          {c.change7dPct != null && (
            <View className="flex-row justify-between mb-2">
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Price trend</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                7d {c.change7dPct}% · 30d {c.change30dPct ?? '—'}%
              </Text>
            </View>
          )}
          {!!c.darkMatter && (
            <View className="flex-row justify-between mb-2">
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Insider Tracking (proxies)</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                {c.darkMatter.flow ?? '—'} · {c.darkMatter.intensity ?? '—'} · {c.darkMatter.coverage ?? '—'}
              </Text>
            </View>
          )}
          <Text className="text-textMuted text-xs mt-1">
            Price via FMP (coin) · Insider tracking via crypto-exposure proxy 13F / insider. Measurement only.
          </Text>
        </View>
      )}

      {/* Network Value & Supply — display-only reference facts (C1+C2, web parity).
          §17: the engine omits the block entirely when live data is absent, so
          this renders only when real. */}
      {c.supply?.networkValueUsd != null && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          <SectionTitle>Network Value & Supply</SectionTitle>
          <View className="flex-row justify-between mb-2">
            <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Network value (circulating)</Text>
            <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
              ${(c.supply.networkValueUsd / 1e9).toFixed(1)}B{c.supply.sizeBand ? ` · ${c.supply.sizeBand.toUpperCase()}` : ''}
            </Text>
          </View>
          {c.supply.circulatingSupply != null && (
            <View className="flex-row justify-between mb-2">
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Circulating supply</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                {c.supply.circulatingSupply.toLocaleString()}
              </Text>
            </View>
          )}
          {c.supply.maxSupply ? (
            <>
              <View className="flex-row justify-between mb-2">
                <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Max supply · % outstanding</Text>
                <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                  {c.supply.maxSupply.toLocaleString()}{c.supply.pctOfMaxOutstanding != null ? ` · ${c.supply.pctOfMaxOutstanding}%` : ''}
                </Text>
              </View>
              {c.supply.fdvUsd != null && (
                <View className="flex-row justify-between mb-2">
                  <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Fully diluted value</Text>
                  <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                    ${(c.supply.fdvUsd / 1e9).toFixed(1)}B
                  </Text>
                </View>
              )}
            </>
          ) : (
            <View className="flex-row justify-between mb-2">
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Max supply / FDV</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                no max supply{c.supply.supplySchedule ? ` (${c.supply.supplySchedule.replace(/_/g, ' ')})` : ''}
              </Text>
            </View>
          )}
          {!!c.supply.supplySchedule && (
            <View className="flex-row justify-between mb-2">
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Issuance model</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                {c.supply.supplySchedule.replace(/_/g, ' ')}{c.supply.supplyAsOf ? ` · as of ${c.supply.supplyAsOf}` : ''}
              </Text>
            </View>
          )}
          <Text className="text-textMuted text-xs mt-1" style={{ lineHeight: 16 }}>
            {c.supply.bandBasis ? `${c.supply.bandBasis}` : ''}{c.supply.caveat ? ` ${c.supply.caveat}.` : ''} Reference facts, not a valuation or advice.
          </Text>
        </View>
      )}

      {/* POSITIONING VS PRICE — web parity (Chairman order 2026-09-14). The
          engine serves no divergence block yet, so the value slot renders the
          honest hollow NOT MEASURED state — never a 0. */}
      <View className="bg-card rounded-3xl p-5 mt-4">
        <SectionTitle>Positioning vs Price</SectionTitle>
        <View className="flex-row items-center justify-between">
          <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Signed 7-day reading</Text>
          <NotMeasuredChip />
        </View>
        <Text className="text-textMuted text-xs mt-2" style={{ lineHeight: 16 }}>
          Positioning vs Price requires cleared source rights and instrument audits — accruing since
          2026-08-10. Until then no number is shown.
        </Text>
      </View>

      {/* POSITIONING VS PRICE REGISTER — its OWN fenced register; honest-empty
          state (web parity: "unresolved is never a pending win"). */}
      <View className="bg-card rounded-3xl p-5 mt-4">
        <SectionTitle>Positioning vs Price Register</SectionTitle>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500' }}>
          No track record exists. Flags are sealed internally under pre-registration{' '}
          <Text style={{ fontWeight: '700' }}>bd6e3649…</Text>;{' '}
          <Text style={{ fontWeight: '700' }}>{c.divergenceRegister?.resolved ?? 0} resolved</Text>
          {c.divergenceRegister ? (
            <>
              {' · '}
              <Text style={{ fontWeight: '700' }}>{c.divergenceRegister.open} open</Text>
            </>
          ) : null}{' '}
          (unresolved is never a pending win). At observed episode rates an honest calibration claim
          takes <Text style={{ fontWeight: '700' }}>8–15 years</Text>.
        </Text>
      </View>

      {/* Explainer — what Positioning vs Price is and how the three readings differ */}
      <View className="bg-card rounded-3xl p-5 mt-4">
        <SectionTitle>About Positioning vs Price</SectionTitle>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500' }}>
          <Text style={{ fontWeight: '700' }}>Positioning vs Price</Text> is a signed reading built
          from exchange open-interest counts: how much leveraged futures positioning changed over 7
          days beyond what the coin's own price move explains. Positive = positions building faster
          than price explains; negative = positions closing faster than price explains. It is always
          stated as arithmetic (e.g. "open interest +4% while price −2% over 7 days").
        </Text>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 8 }}>
          <Text style={{ fontWeight: '700' }}>How the three readings differ:</Text> the{' '}
          <Text style={{ fontWeight: '700' }}>Positioning</Text> gauge (D) reads who holds exposure —
          holdings via crypto-exposure proxies (spot-ETF 13F + insider filings).{' '}
          <Text style={{ fontWeight: '700' }}>Positioning vs Price</Text> reads how fast leverage is
          being added or removed relative to price.{' '}
          <Text style={{ fontWeight: '700' }}>Market Confirmation</Text> (M) is the coin's own price /
          volume behavior against its baseline. Three different questions; none is a forecast or advice.
        </Text>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 8 }}>
          <Text style={{ fontWeight: '700' }}>Why it reads NOT MEASURED:</Text> the value displays
          only after its source rights are cleared, its instrument audits pass, and enough post-seal
          daily history accrues per coin (~6 months; accruing since 2026-08-10). Until then no number
          is shown — an unmeasured reading is never rendered as a zero.
        </Text>
      </View>

      {/* Explainer — what Tier means (web parity; MARKET_LEVELS bands) */}
      <View className="bg-card rounded-3xl p-5 mt-4">
        <SectionTitle>About Tier</SectionTitle>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500' }}>
          <Text style={{ fontWeight: '700' }}>Tier</Text> is a neutral intensity label — the average
          of the two gauges (Positioning D and Market Confirmation M, each 0–100) mapped to a band:{' '}
          <Text style={{ fontWeight: '700' }}>ELEVATED</Text> ≥80 ·{' '}
          <Text style={{ fontWeight: '700' }}>ACTIVE</Text> ≥60 ·{' '}
          <Text style={{ fontWeight: '700' }}>MODERATE</Text> ≥40 ·{' '}
          <Text style={{ fontWeight: '700' }}>ROUTINE</Text> ≥25 ·{' '}
          <Text style={{ fontWeight: '700' }}>DORMANT</Text> &lt;25. It describes how much is
          happening versus the coin's own baseline — it is not a rating, a ranking, or advice.
        </Text>
        <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 8 }}>
          <Text style={{ fontWeight: '700' }}>NOT MEASURED is not a tier.</Text> When either input is
          absent (the panel states which case applies), no tier is computed — the chip shows the
          absence honestly instead of a number. Coins with limited history read "calibrating" until
          their baseline accumulates.
        </Text>
      </View>

      {/* What the Crypto signal measures — same explainer as the web rail */}
      <Text className="text-textMuted text-xs mt-5" style={{ lineHeight: 17 }}>
        <Text className="font-bold">What the Crypto signal measures:</Text> The Crypto section tracks
        the direction of informed positioning in a coin. Positioning "D" = holdings via
        crypto-exposure proxies (spot-ETF 13F + MSTR / COIN insider filings). Market Confirmation "M"
        = the coin's own price / volume confirmation. The flow (IN/OUT) is a measurement; whether an
        early read led realized price is recorded, after the fact, in the crypto accuracy ledger. Be
        advised that this summary may be inaccurate and is not intended to be financial, legal or
        investment advice.
      </Text>

      <Disclaimer className="mt-5 mb-8" />
    </Screen>
  );
}
