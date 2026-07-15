import React, { useState } from 'react';
import { View, Text, TouchableOpacity, LayoutAnimation, Platform, UIManager } from 'react-native';
import { ChevronDown } from 'lucide-react-native';
import { Rise } from '../ui/Rise';
import { CryptoCoin } from '../../lib/gradientApi';
import { MARKET_TIER_COLOR } from '../../lib/marketCategories';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Factual flow direction — a measurement (informed proxies vs the coin's own
// price), never a buy/sell call. Colors are Aurora tokens (no gold outside the
// Home hero, no neon green).
const FLOW_META: Record<string, { label: string; color: string }> = {
  inflow: { label: '▲ INFLOW', color: '#2E7D5B' },
  outflow: { label: '▼ OUTFLOW', color: '#B11226' },
  divergent: { label: '◆ DIVERGENT', color: '#6B4FA0' },
  neutral: { label: '• NEUTRAL', color: '#9A9AA2' },
};

// Calm, tap-to-expand crypto row — mirrors RiskCard (WEB PARITY: the web
// Crypto table's columns). Collapsed: name·ticker, tier + flow, Money
// Movement. Expanded: Market Confirmation, Lead, price, interpretation.
export function CryptoCard({ coin }: { coin: CryptoCoin }) {
  const [open, setOpen] = useState(false);
  const tierColor = MARKET_TIER_COLOR[coin.tier] ?? '#9A9AA2';
  const flow = coin.flow ? (FLOW_META[coin.flow] ?? { label: `• ${coin.flow.toUpperCase()}`, color: '#9A9AA2' }) : null;
  const lead = Math.round(coin.lead * 10) / 10;

  const toggle = () => {
    LayoutAnimation.configureNext({
      duration: 440,
      create: { type: 'easeInEaseOut', property: 'opacity' },
      update: { type: 'easeInEaseOut' },
      delete: { type: 'easeInEaseOut', property: 'opacity' },
    });
    setOpen((o) => !o);
  };

  return (
    <View style={{ borderBottomWidth: 1, borderBottomColor: '#ECECEC' }}>
      <TouchableOpacity activeOpacity={0.7} onPress={toggle} className="py-4">
        <View className="flex-row items-center" style={{ gap: 14 }}>
          <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: tierColor }} />
          <View style={{ flex: 1 }}>
            <Text numberOfLines={1} style={{ color: '#16264A', fontSize: 16, fontWeight: '700', letterSpacing: -0.2 }}>
              {coin.name} <Text style={{ color: '#9A9AA2', fontWeight: '600' }}>· {coin.coin}</Text>
            </Text>
            <Text numberOfLines={1} style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1, marginTop: 4 }}>
              <Text style={{ color: tierColor }}>{coin.tier}</Text>
              {flow ? <Text> · <Text style={{ color: flow.color }}>{flow.label}</Text></Text> : null}
              {coin.calibrating ? ' · CALIBRATING' : ''}
            </Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ color: '#16264A', fontSize: 22, fontWeight: '800', letterSpacing: -0.6, lineHeight: 24 }}>{coin.moneyMovement}</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>MM</Text>
          </View>
          <ChevronDown size={18} color="#C7C7CE" style={{ transform: [{ rotate: open ? '180deg' : '0deg' }] }} />
        </View>

        {open && (
          <Rise duration={420} distance={10} style={{ paddingTop: 16 }}>
            <View className="flex-row" style={{ gap: 24, marginBottom: 12 }}>
              <View>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>MARKET CONFIRMATION</Text>
                <Text style={{ color: '#16264A', fontSize: 18, fontWeight: '800', marginTop: 3 }}>{coin.marketConfirmation}</Text>
              </View>
              <View>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>LEAD</Text>
                <Text style={{ color: '#16264A', fontSize: 18, fontWeight: '800', marginTop: 3 }}>{lead > 0 ? `+${lead}` : lead}</Text>
              </View>
              {coin.priceClose != null && (
                <View>
                  <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>PRICE · 7D</Text>
                  <Text style={{ color: '#16264A', fontSize: 18, fontWeight: '800', marginTop: 3 }}>
                    ${Number(coin.priceClose).toLocaleString()}
                    {coin.change7dPct != null ? (
                      <Text style={{ color: coin.change7dPct >= 0 ? '#2E7D5B' : '#B11226', fontSize: 12, fontWeight: '700' }}> {coin.change7dPct >= 0 ? '+' : ''}{coin.change7dPct}%</Text>
                    ) : null}
                  </Text>
                </View>
              )}
            </View>

            {!!coin.interpretation && (
              <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, fontWeight: '500', marginBottom: 4 }}>
                {coin.interpretation}
              </Text>
            )}
          </Rise>
        )}
      </TouchableOpacity>
    </View>
  );
}
