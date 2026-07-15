import React from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { GradientScoreRing } from '../../../components/ui/GradientScoreRing';
import { SignalAnalysisPanel } from '../../../components/trends/SignalAnalysisPanel';
import { useCrypto } from '../../../hooks/useSignals';
import { MARKET_TIER_COLOR } from '../../../lib/marketCategories';

// Aurora detail-screen conventions (same as the market detail risk/[key]):
// Money Movement = sapphire, Market Confirmation = emerald.
const MM_COLOR = '#2A5B9E';
const MC_COLOR = '#2E7D5B';

const FLOW_META: Record<string, { label: string; color: string }> = {
  inflow: { label: '▲ INFLOW', color: '#2E7D5B' },
  outflow: { label: '▼ OUTFLOW', color: '#B11226' },
  divergent: { label: '◆ DIVERGENT', color: '#6B4FA0' },
  neutral: { label: '• NEUTRAL', color: '#9A9AA2' },
};

// Full crypto detail — WEB PARITY: the same sections and data points as the
// web terminal's Crypto rail (header · price-as-of · disclaimer · dual rings ·
// gap state + interpretation · Signal Analysis · Market Factors · Price & Dark
// Matter facts · what-it-measures explainer · disclaimer), in Aurora form.
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

  const tierColor = MARKET_TIER_COLOR[c.tier] ?? '#9A9AA2';
  const flow = c.flow ? (FLOW_META[c.flow] ?? { label: `• ${c.flow.toUpperCase()}`, color: '#9A9AA2' }) : null;
  const comps = Object.entries(c.components ?? {});
  const gapAbs = Math.abs(Math.round(c.lead * 10) / 10);
  const gapHead = c.calibrating ? 'CALIBRATING' : (c.gapState || '').replace(/_/g, ' ');

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
      <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1, marginTop: 6 }}>
        CRYPTO · <Text style={{ color: tierColor }}>{c.tier}</Text>
        {flow ? <Text> · <Text style={{ color: flow.color }}>{flow.label}</Text></Text> : null}
        {c.calibrating ? ' · CALIBRATING' : ''}
      </Text>
      {c.priceClose != null && (
        <Text style={{ color: '#3C4663', fontSize: 14, fontWeight: '600', marginTop: 6 }}>
          ${Number(c.priceClose).toLocaleString()}{c.priceAsOf ? <Text style={{ color: '#9A9AA2', fontWeight: '500' }}> · price as of {c.priceAsOf}</Text> : null}
        </Text>
      )}

      <Disclaimer className="mt-4 mb-2 px-0 text-left" />

      {/* Dual rings — Money Movement (D) / Market Confirmation (M) */}
      <View className="bg-card rounded-3xl p-5 mt-2">
        <View className="flex-row justify-around">
          <View className="items-center">
            <GradientScoreRing score={Math.round(c.moneyMovement)} color={MM_COLOR} size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">MONEY MOVEMENT</Text>
            <Text className="text-textMuted text-xs mt-0.5">informed money · D</Text>
          </View>
          <View className="items-center">
            <GradientScoreRing score={Math.round(c.marketConfirmation)} color={MC_COLOR} size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">MARKET CONFIRMATION</Text>
            <Text className="text-textMuted text-xs mt-0.5">coin price · M</Text>
          </View>
        </View>
      </View>

      {/* Gap state + interpretation */}
      {(gapHead || c.interpretation) && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          {!!gapHead && (
            <Text style={{ color: tierColor, fontSize: 12, fontWeight: '800', letterSpacing: 1 }}>
              {gapHead}{!c.calibrating ? ` · ${gapAbs}-pt gap` : ''}
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
          <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase mb-3">Market Factors</Text>
          {comps.map(([label, comp]) => {
            const na = comp.notApplicable || comp.score == null;
            const col = na ? '#9A9AA2' : comp.feeds === 'money_movement' ? MM_COLOR : MC_COLOR;
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
            <Text style={{ color: MM_COLOR }}>●</Text> money movement · <Text style={{ color: MC_COLOR }}>●</Text> market confirmation · ✓ = scored vs own history
          </Text>
        </View>
      )}

      {/* Price & Dark Matter facts — only what contributed (§17) */}
      {(c.change7dPct != null || c.darkMatter) && (
        <View className="bg-card rounded-3xl p-5 mt-4">
          <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase mb-3">Price & Dark Matter</Text>
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
              <Text style={{ color: '#3C4663', fontSize: 12, fontWeight: '600' }}>Dark Matter (proxies)</Text>
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                {c.darkMatter.flow ?? '—'} · {c.darkMatter.intensity ?? '—'} · {c.darkMatter.coverage ?? '—'}
              </Text>
            </View>
          )}
          <Text className="text-textMuted text-xs mt-1">
            Price via FMP (coin) · Dark Matter via crypto-exposure proxy 13F / insider. Measurement only.
          </Text>
        </View>
      )}

      {/* What the Crypto signal measures — same explainer as the web rail */}
      <Text className="text-textMuted text-xs mt-5" style={{ lineHeight: 17 }}>
        <Text className="font-bold">What the Crypto signal measures:</Text> The Crypto section tracks
        whether money is moving into or out of a coin. Money Movement "D" = informed / early money via
        crypto-exposure proxies (spot-ETF 13F + MSTR / COIN insider). Market Confirmation "M" = the
        coin's own price / volume confirmation. The flow (IN/OUT) is a measurement; whether an early
        read led realized price is recorded, after the fact, in the crypto accuracy ledger. Be advised
        that this summary may be inaccurate and is not intended to be financial, legal or investment advice.
      </Text>

      <Disclaimer className="mt-5 mb-8" />
    </Screen>
  );
}
