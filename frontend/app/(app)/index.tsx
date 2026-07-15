import { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useNavigation } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Bell, Zap, Briefcase, Building2, Search, Crown, ArrowRight } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Rise } from '../../components/ui/Rise';
import { TrendCard } from '../../components/trends/TrendCard';
import { RiskCard } from '../../components/trends/RiskCard';
import { CryptoCard } from '../../components/trends/CryptoCard';
import { MacroLeverageCard } from '../../components/trends/MacroLeverageCard';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { PullTrendsButton } from '../../components/trends/PullTrendsButton';
import { PullMarketButton } from '../../components/trends/PullMarketButton';
import { GradeTool } from '../../components/trends/GradeTool';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID, isDataAccessible } from '../../constants/tiers';
import { dataWindowLabel, actionLine, ageLabel, titleCaseTopic, CATEGORY_DEFS, CONTENT_CATEGORIES, contentCategoryMeta, feedOrder } from '../../lib/signals';
import { MARKET_LANES, MARKET_TIER_FILTERS, MARKET_DIRECTION_FILTERS, laneOf } from '../../lib/marketCategories';
import { useTierFeed, useRiskScores, useCrypto } from '../../hooks/useSignals';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };
const PAGE = 6; // how many rows reveal per batch (mobile perf + gentle discovery)

export default function Dashboard() {
  const router = useRouter();
  const navigation = useNavigation();
  const scrollRef = useRef<ScrollView>(null);
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];
  const TierBadgeIcon = tier === 'enterprise' ? Crown : Icon;
  const canPull = cfg.canQueryNew;

  const { accessible, lockedCount, isLoading, isSample } = useTierFeed(tier);
  const { risks, isLoading: riskLoading } = useRiskScores();
  const { coins, warming: cryptoWarming, isLoading: cryptoLoading } = useCrypto();
  const [mode, setMode] = useState<'attention' | 'risk' | 'crypto' | 'grade'>('attention');
  const [query, setQuery] = useState('');
  const [contentCat, setContentCat] = useState('all');
  // Default view = Now TrendIn (ranked by N) — the web terminal's default.
  const [signalFilter, setSignalFilter] = useState('nowtrendin');
  const [marketQuery, setMarketQuery] = useState('');
  // Market filter axes — WEB PARITY: lane / tier / direction, all defaulting to
  // 'all' exactly like the web terminal's Market Signal page.
  const [marketLane, setMarketLane] = useState('all');
  const [marketTier, setMarketTier] = useState('all');
  const [marketDir, setMarketDir] = useState('all');
  // Crypto DIRECTION filter — the web Crypto page's single chip axis.
  const [cryptoDir, setCryptoDir] = useState('all');
  const [visible, setVisible] = useState(PAGE);

  // ── Attention feed ──
  // TRENDS (signal-stage) filter — same row as the web terminal, driven by
  // CATEGORY_DEFS (the SSOT for the stage bands). Combines with the content-
  // category chips exactly like the web: stage AND category AND search.
  const signalDef = CATEGORY_DEFS.find((d) => d.key === signalFilter);
  const filtered = accessible.filter((s) =>
    (!query || s.topic.toLowerCase().includes(query.toLowerCase())) &&
    (contentCat === 'all' || contentCategoryMeta(s.category).key === contentCat) &&
    (!signalDef || signalDef.filter(s))
  );
  // WEB PARITY ranking: each view ranks by its def's sort (Now TrendIn → N,
  // everything else → Detection). The displayed number follows the ranking
  // metric, exactly like the web's ranked column.
  const ranked = [...filtered].sort(signalDef?.sort ?? ((a, b) => (b.detection - a.detection) || feedOrder(a, b)));
  const isNRanked = signalFilter === 'nowtrendin';
  const metricOf = (s: (typeof ranked)[number]) => (isNRanked ? (s.nowTrending ?? 0) : s.score);
  const metricLabel = isNRanked ? 'N' : 'SCORE';
  const topPick = ranked[0];
  const rest = ranked.slice(1);
  const lastUpdated = accessible.length ? ageLabel(accessible[0].createdAt) : '—';

  const counts = Object.fromEntries(
    CATEGORY_DEFS.map((c) => [c.key, accessible.filter(c.filter).length])
  ) as Record<string, number>;
  const contentCounts = Object.fromEntries(
    CONTENT_CATEGORIES.map((c) => [c.key, accessible.filter((s) => contentCategoryMeta(s.category).key === c.key).length])
  ) as Record<string, number>;

  // ── Market feed ──
  const accessibleRisks = risks.filter((r) => isDataAccessible(tier, Date.now() - r.firstSeenAt));
  const lockedRiskCount = risks.length - accessibleRisks.length;
  const mq = marketQuery.trim().toLowerCase();
  // The three axes COMBINE (lane AND tier AND direction AND search) — web parity.
  const laneDef = MARKET_LANES.find((l) => l.key === marketLane);
  const tierDef = MARKET_TIER_FILTERS.find((t) => t.key === marketTier);
  const dirDef = MARKET_DIRECTION_FILTERS.find((d) => d.key === marketDir);
  // WEB PARITY ranking: Money Movement (the Money Gradient's leading read)
  // descending — the web table's default sort column.
  const mmOf = (r: (typeof accessibleRisks)[number]) => r.marketGradient?.detection ?? r.detection ?? 0;
  const marketFiltered = accessibleRisks
    .filter((r) =>
      (!mq || r.display.toLowerCase().includes(mq)) &&
      (!laneDef?.lane || laneOf(r) === laneDef.lane) &&
      (!tierDef?.test || tierDef.test(r)) &&
      (!dirDef || dirDef.test(r)))
    .sort((a, b) => mmOf(b) - mmOf(a));
  // Lane counts (over the full accessible set, before the other filters) for the
  // chip labels — same as the web ("Covered 15 · Halted / micro-cap 283 …").
  const laneCounts = Object.fromEntries(
    MARKET_LANES.filter((l) => l.lane).map((l) => [l.key, accessibleRisks.filter((r) => laneOf(r) === l.lane).length])
  ) as Record<string, number>;
  // #1 market signal — the top Money Movement read (web parity: the web table's
  // top row), NOT the positioning-anomaly score (that's the expanded-detail read).
  const topRisk = [...accessibleRisks].sort((a, b) => mmOf(b) - mmOf(a))[0];

  // ── Crypto feed — WEB PARITY: engine roster order (never re-sorted), one
  // DIRECTION chip axis. Neutral covers anything without a clear in/out read.
  const CRYPTO_DIRS = [
    { key: 'all', label: 'All' },
    { key: 'inflow', label: 'Inflow' },
    { key: 'outflow', label: 'Outflow' },
    { key: 'neutral', label: 'Neutral' },
  ];
  const shownCoins = coins.filter((c) =>
    cryptoDir === 'all' ? true
      : cryptoDir === 'inflow' ? c.flow === 'inflow'
      : cryptoDir === 'outflow' ? c.flow === 'outflow'
      : c.flow !== 'inflow' && c.flow !== 'outflow');

  const firstName = (user?.name ?? 'there').split(' ')[0];
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? 'Good morning'          // 12:00am – 11:59am
      : hour < 18 ? 'Good afternoon'    // 12:00pm – 5:59pm
      : 'Good evening';                 // 6:00pm – 11:59pm

  // Reset the visible window whenever the feed/filter/mode changes.
  useEffect(() => { setVisible(PAGE); }, [mode, contentCat, signalFilter, query, marketQuery, marketLane, marketTier, marketDir, cryptoDir]);

  // Tapping the Home tab resets the screen to its just-opened state: Trends
  // selected (not Market/Grade), filters cleared, scrolled to the top.
  useEffect(() => {
    const unsub = (navigation as any).addListener('tabPress', () => {
      setMode('attention');
      setContentCat('all');
      setSignalFilter('nowtrendin');
      setQuery('');
      setMarketQuery('');
      setMarketLane('all');
      setMarketTier('all');
      setMarketDir('all');
      setCryptoDir('all');
      setVisible(PAGE);
      scrollRef.current?.scrollTo({ y: 0, animated: true });
    });
    return unsub;
  }, [navigation]);

  const activeLen = mode === 'attention' ? rest.length : mode === 'risk' ? marketFiltered.length : mode === 'crypto' ? shownCoins.length : 0;
  // Seamless reveal: as the user nears the bottom, load the next batch.
  const onScroll = (e: any) => {
    const { layoutMeasurement, contentOffset, contentSize } = e.nativeEvent;
    if (contentOffset.y + layoutMeasurement.height >= contentSize.height - 480) {
      setVisible((v) => (v < activeLen ? Math.min(v + PAGE, activeLen) : v));
    }
  };

  // Tab order mirrors the web sidebar: Trends → Market Signal → Crypto → Grade.
  const MODES = [
    { k: 'attention', label: 'Trends' },
    { k: 'risk', label: 'Market' },
    { k: 'crypto', label: 'Crypto' },
    { k: 'grade', label: 'Grade' },
  ] as const;

  // Pull bar exists for Trends + Market only (the web has no crypto pull).
  const showPull = canPull && (mode === 'attention' || mode === 'risk');

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#FFFFFF' }} edges={['top', 'left', 'right']}>
      <ScrollView
        ref={scrollRef}
        onScroll={onScroll}
        scrollEventThrottle={16}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: showPull ? 132 : 36 }}
      >
        {/* Brand header */}
        <View className="flex-row items-center justify-between pt-3">
          <View className="flex-row items-center gap-2">
            <Logo size={34} />
            <View>
              <Wordmark size="text-xl" />
              <Text className="text-textMuted text-[12px] tracking-widest uppercase">Attention Intelligence</Text>
            </View>
          </View>
          <View className="flex-row items-center gap-4">
            <TouchableOpacity activeOpacity={0.6} onPress={() => router.push('/search' as any)}><Search size={20} color="#16264A" /></TouchableOpacity>
            <TouchableOpacity activeOpacity={0.6} onPress={() => router.push('/alerts' as any)}><Bell size={20} color="#16264A" /></TouchableOpacity>
          </View>
        </View>

        {/* Greeting + tier status */}
        <Rise>
          <View className="mt-7">
            <Text className="text-textPrimary text-[12px] font-extrabold tracking-[2.5px] uppercase">{greeting}, {firstName}</Text>
            {/* Headline follows the active tab: Trends count on Trends, market-item
                count on Market (founder 2026-07-15 — the number must describe what
                the user is looking at). */}
            {mode === 'risk' ? (
              <Text className="text-textPrimary text-[32px] font-extrabold mt-2.5" style={{ letterSpacing: -1.1, lineHeight: 36 }}>
                {marketFiltered.length.toLocaleString()} Market {marketFiltered.length === 1 ? 'Signal Is' : 'Signals Are'} <Text style={{ color: '#B11226' }}>Moving!</Text>
              </Text>
            ) : mode === 'crypto' ? (
              <Text className="text-textPrimary text-[32px] font-extrabold mt-2.5" style={{ letterSpacing: -1.1, lineHeight: 36 }}>
                {shownCoins.length.toLocaleString()} {shownCoins.length === 1 ? 'Coin Is' : 'Coins Are'} <Text style={{ color: '#B11226' }}>Moving!</Text>
              </Text>
            ) : (
              <Text className="text-textPrimary text-[32px] font-extrabold mt-2.5" style={{ letterSpacing: -1.1, lineHeight: 36 }}>
                {ranked.length.toLocaleString()} {ranked.length === 1 ? 'Trend Is' : 'Trends Are'} <Text style={{ color: '#B11226' }}>Heating Up!</Text>
              </Text>
            )}
            <View className="flex-row items-center gap-2.5 mt-3.5">
              <View className="flex-row items-center gap-1.5">
                <TierBadgeIcon size={13} color={cfg.colour} />
                <Text className="text-textPrimary text-[12px] font-extrabold tracking-[1.6px] uppercase">{cfg.name}</Text>
              </View>
              <Text className="text-[12px] font-bold" style={{ color: '#D6D6DC' }}>·</Text>
              <Text className="text-textMuted text-[12px] font-bold tracking-[1.4px] uppercase">Updated {lastUpdated}</Text>
            </View>
          </View>
        </Rise>

        {/* Tabs */}
        <View className="flex-row gap-6 mt-6 mb-1" style={{ borderBottomWidth: 1.5, borderBottomColor: '#ECECEC' }}>
          {MODES.map((t) => {
            const on = mode === t.k;
            return (
              <TouchableOpacity key={t.k} onPress={() => setMode(t.k as typeof mode)} activeOpacity={0.7}
                style={{ paddingBottom: 11, marginBottom: -1.5, borderBottomWidth: on ? 2.5 : 0, borderBottomColor: '#B11226' }}>
                <Text className="text-xs uppercase" style={{ letterSpacing: 1.8, fontWeight: on ? '800' : '700', color: on ? '#16264A' : '#B6B6BD' }}>{t.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {mode === 'attention' && (
          <>
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 18 }}>
              What's gaining attention across every platform right now — ranked by our Gradient Score, surfaced before it hits the mainstream.
            </Text>
            {topPick && (
              <Rise delay={90}>
                <TouchableOpacity activeOpacity={0.93} onPress={() => router.push(`/signal/${topPick.id}`)} className="rounded-3xl overflow-hidden mt-5"
                  style={{ shadowColor: '#0C1B3A', shadowOpacity: 0.4, shadowRadius: 24, shadowOffset: { width: 0, height: 16 }, elevation: 9 }}>
                  <LinearGradient colors={['#1B3066', '#0C1B3A', '#1A1442']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={{ padding: 24 }}>
                    <View style={{ position: 'absolute', right: -34, top: -30, width: 150, height: 150, borderRadius: 75, backgroundColor: 'rgba(201,162,75,0.13)' }} />
                    <View style={{ position: 'absolute', left: -44, bottom: -54, width: 130, height: 130, borderRadius: 65, backgroundColor: 'rgba(177,18,38,0.16)' }} />
                    <Text style={{ color: '#F0758A', fontSize: 12, fontWeight: '800', letterSpacing: 2.2 }}>TODAY'S #1 · NOWTRENDIN PICK</Text>
                    <Text numberOfLines={2} style={{ color: '#FBF4E4', fontSize: 28, fontWeight: '800', letterSpacing: -0.5, marginTop: 11, lineHeight: 33 }}>{titleCaseTopic(topPick.topic)}</Text>
                    <View className="flex-row items-end justify-between" style={{ marginTop: 16 }}>
                      <Text style={{ color: '#B9C4E0', fontSize: 12, fontWeight: '500', maxWidth: 175, lineHeight: 18 }}>{actionLine(topPick.stage)}</Text>
                      <View style={{ alignItems: 'flex-end' }}>
                        <Text style={{ color: '#E2C275', fontSize: 44, fontWeight: '800', lineHeight: 46, letterSpacing: -1.5 }}>{metricOf(topPick)}</Text>
                        <Text style={{ color: '#C9A24B', fontSize: 12, fontWeight: '700', letterSpacing: 2, marginTop: 3 }}>{metricLabel}</Text>
                      </View>
                    </View>
                    <View className="flex-row items-center self-start" style={{ backgroundColor: '#B11226', borderRadius: 980, paddingVertical: 12, paddingHorizontal: 22, marginTop: 20 }}>
                      <Text style={{ color: '#FFFFFF', fontSize: 12, fontWeight: '800', letterSpacing: 1 }}>VIEW TREND</Text>
                      <ArrowRight size={15} color="#FFFFFF" style={{ marginLeft: 6 }} />
                    </View>
                  </LinearGradient>
                </TouchableOpacity>
              </Rise>
            )}

            {/* TWO filter rows, matching the web terminal (frontend-consistency B8):
                TRENDS (signal stage, from CATEGORY_DEFS — the SSOT) above CATEGORY
                (content). They COMBINE exactly like the web: stage AND category.
                (Founder-requested 2026-07-06 — restores the row Aurora dropped.) */}
            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mt-7 mb-2.5">Trends</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {CATEGORY_DEFS.map((d) => {
                  const on = signalFilter === d.key;
                  return (
                    <TouchableOpacity key={d.key} onPress={() => setSignalFilter(d.key)} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? d.color : '#F1F1F4' }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{d.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mt-4 mb-2.5">Filter by Category</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {[{ key: 'all', label: 'All', color: '#16264A' }, ...CONTENT_CATEGORIES].map((c) => {
                  const on = contentCat === c.key;
                  const count = c.key === 'all' ? accessible.length : (contentCounts[c.key] ?? 0);
                  const empty = c.key !== 'all' && count === 0;
                  return (
                    <TouchableOpacity key={c.key} onPress={() => setContentCat(c.key)} disabled={empty} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? c.color : '#F1F1F4', borderColor: on ? c.color : '#ECECEC', opacity: empty ? 0.4 : 1 }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{c.label}</Text>
                      {count > 0 && <Text style={{ color: on ? '#FFFFFF' : '#9A9AA2', fontSize: 12, fontWeight: '800', marginLeft: 7 }}>{count}</Text>}
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <View className="flex-row items-center bg-card rounded-xl px-4 py-3 mt-5 mb-4">
              <Search size={18} color="#9A9AA2" />
              <TextInput value={query} onChangeText={setQuery} placeholder="Search trends" placeholderTextColor="#9A9AA2" className="flex-1 ml-3 text-base" style={{ color: '#16264A' }} />
            </View>

            <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase">More Trending</Text>
            <Text className="text-textMuted text-[12px] font-semibold mt-1">Ranked by score, after #1</Text>
            <Text className="text-textMuted text-[12px] mt-2 mb-3">Tap any trend to open its full breakdown.</Text>

            {isSample && (
              <View className="rounded-lg px-3 py-2 mb-4 bg-card">
                <Text className="text-textMuted text-[12px]">Showing sample data — live engine unreachable.</Text>
              </View>
            )}

            {isLoading ? (
              <ActivityIndicator size="large" color="#1B3066" style={{ marginTop: 40 }} />
            ) : (
              <>
                {rest.slice(0, visible).map((s, i) => (
                  <TrendCard key={s.id} signal={s} rank={i + 2} metric={isNRanked ? { value: s.nowTrending ?? 0, label: 'N' } : undefined} />
                ))}
                {ranked.length === 0 && <Text className="text-textMuted text-center mt-8 mb-4">No trends match your search.</Text>}
                {visible < rest.length && (
                  <Text className="text-textMuted text-center mt-4" style={{ fontSize: 12, letterSpacing: 0.5 }}>
                    Showing {visible + 1} of {ranked.length} · scroll for more
                  </Text>
                )}
                <View className="mt-3"><LockedSignalsBanner tier={tier} lockedCount={lockedCount} /></View>
              </>
            )}
          </>
        )}

        {mode === 'crypto' && (
          <>
            {/* Minimalist intro — the web Crypto page's header line. */}
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 18 }}>
              The Crypto Money Gradient — Money Movement (informed money via crypto-exposure proxies) vs Market Confirmation (the coin's own price). Measurement, not advice.
            </Text>

            {/* DIRECTION chips — same single axis as the web Crypto page. */}
            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mt-6 mb-2.5">Direction</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {CRYPTO_DIRS.map((d) => {
                  const on = cryptoDir === d.key;
                  return (
                    <TouchableOpacity key={d.key} onPress={() => setCryptoDir(d.key)} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? '#16264A' : '#F1F1F4' }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{d.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase mt-6">Coins</Text>
            <Text className="text-textMuted text-[12px] font-semibold mt-1 mb-3">Ranked as served · tap any to expand</Text>

            {cryptoLoading || (cryptoWarming && coins.length === 0) ? (
              <>
                <ActivityIndicator size="large" color="#1B3066" style={{ marginTop: 40 }} />
                {cryptoWarming && (
                  <Text className="text-textMuted text-center mt-4" style={{ fontSize: 12 }}>
                    Crypto feed is warming — the roster arrives shortly.
                  </Text>
                )}
              </>
            ) : shownCoins.length === 0 ? (
              <Text className="text-textMuted text-center mt-8">No coins match this direction.</Text>
            ) : (
              shownCoins.slice(0, visible).map((c) => <CryptoCard key={c.coin} coin={c} />)
            )}
          </>
        )}

        {mode === 'grade' && <View className="mt-6"><GradeTool /></View>}

        {mode === 'risk' && (
          <>
            {/* Minimalist intro — what the Market tab is */}
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 21, fontWeight: '500', marginTop: 18 }}>
              The Gradient Score applied to markets — how early informed money is positioning, measured against each item's own baseline.
            </Text>

            {/* ── #1 MARKET HERO — the top market signal, mirrors the Trends pick ── */}
            {topRisk && (
              <Rise delay={90}>
                <TouchableOpacity activeOpacity={0.93} onPress={() => router.push(`/risk/${topRisk.key}`)} className="rounded-3xl overflow-hidden mt-5"
                  style={{ shadowColor: '#0C1B3A', shadowOpacity: 0.4, shadowRadius: 24, shadowOffset: { width: 0, height: 16 }, elevation: 9 }}>
                  <LinearGradient colors={['#1B3066', '#0C1B3A', '#1A1442']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={{ padding: 24 }}>
                    <View style={{ position: 'absolute', right: -34, top: -30, width: 150, height: 150, borderRadius: 75, backgroundColor: 'rgba(201,162,75,0.13)' }} />
                    <View style={{ position: 'absolute', left: -44, bottom: -54, width: 130, height: 130, borderRadius: 65, backgroundColor: 'rgba(177,18,38,0.16)' }} />
                    <Text style={{ color: '#F0758A', fontSize: 12, fontWeight: '800', letterSpacing: 2.2 }}>TODAY'S #1 · MARKET SIGNAL</Text>
                    <Text numberOfLines={2} style={{ color: '#FBF4E4', fontSize: 28, fontWeight: '800', letterSpacing: -0.5, marginTop: 11, lineHeight: 33 }}>{titleCaseTopic(topRisk.display)}</Text>
                    <View className="flex-row items-end justify-between" style={{ marginTop: 16 }}>
                      <Text numberOfLines={2} style={{ color: '#B9C4E0', fontSize: 12, fontWeight: '500', maxWidth: 175, lineHeight: 18 }}>
                        {topRisk.narrative || topRisk.interpretation || `${topRisk.classification ?? 'Unusual'} positioning vs its baseline.`}
                      </Text>
                      <View style={{ alignItems: 'flex-end' }}>
                        <Text style={{ color: '#E2C275', fontSize: 44, fontWeight: '800', lineHeight: 46, letterSpacing: -1.5 }}>{Math.round(mmOf(topRisk))}</Text>
                        <Text style={{ color: '#C9A24B', fontSize: 12, fontWeight: '700', letterSpacing: 2, marginTop: 3 }}>MONEY MOVEMENT</Text>
                      </View>
                    </View>
                    <View className="flex-row items-center self-start" style={{ backgroundColor: '#B11226', borderRadius: 980, paddingVertical: 12, paddingHorizontal: 22, marginTop: 20 }}>
                      <Text style={{ color: '#FFFFFF', fontSize: 12, fontWeight: '800', letterSpacing: 1 }}>VIEW SIGNAL</Text>
                      <ArrowRight size={15} color="#FFFFFF" style={{ marginLeft: 6 }} />
                    </View>
                  </LinearGradient>
                </TouchableOpacity>
              </Rise>
            )}

            <View className="flex-row items-center bg-card rounded-xl px-4 py-3 mt-7 mb-4">
              <Search size={18} color="#9A9AA2" />
              <TextInput value={marketQuery} onChangeText={setMarketQuery} placeholder="Search market signals" placeholderTextColor="#9A9AA2" className="flex-1 ml-3 text-base" style={{ color: '#16264A' }} />
            </View>

            {/* THREE filter rows — WEB PARITY (frontend-consistency): LANE / TIER /
                DIRECTION, defaults 'all' on every axis, filtering IN PLACE exactly
                like the web terminal's Market Signal page. They combine:
                lane AND tier AND direction AND search. */}
            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mb-2.5">Lane</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {MARKET_LANES.map((l) => {
                  const on = marketLane === l.key;
                  const count = l.lane ? (laneCounts[l.key] ?? 0) : 0;
                  return (
                    <TouchableOpacity key={l.key} onPress={() => setMarketLane(l.key)} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? '#16264A' : '#F1F1F4' }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{l.label}</Text>
                      {count > 0 && <Text style={{ color: on ? '#FFFFFF' : '#9A9AA2', fontSize: 12, fontWeight: '800', marginLeft: 7 }}>{count}</Text>}
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mt-4 mb-2.5">Tier</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {MARKET_TIER_FILTERS.map((t) => {
                  const on = marketTier === t.key;
                  return (
                    <TouchableOpacity key={t.key} onPress={() => setMarketTier(t.key)} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? '#16264A' : '#F1F1F4' }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{t.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mt-4 mb-2.5">Direction</Text>
            <View style={{ marginHorizontal: -20 }}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
                {MARKET_DIRECTION_FILTERS.map((d) => {
                  const on = marketDir === d.key;
                  return (
                    <TouchableOpacity key={d.key} onPress={() => setMarketDir(d.key)} activeOpacity={0.8} className="flex-row items-center rounded-full"
                      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? '#16264A' : '#F1F1F4' }}>
                      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700' }}>{d.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>

            <View className="mt-4"><MacroLeverageCard /></View>

            <Text className="text-textPrimary text-sm font-extrabold tracking-[1.8px] uppercase mt-6">Market Signals</Text>
            <Text className="text-textMuted text-[12px] font-semibold mt-1 mb-3">{dataWindowLabel(tier)} · tap any to expand</Text>

            {riskLoading ? (
              <ActivityIndicator size="large" color="#1B3066" style={{ marginTop: 40 }} />
            ) : marketFiltered.length === 0 ? (
              <Text className="text-textMuted text-center mt-8">
                {mq ? `No market items match "${marketQuery}".`
                  : (marketLane !== 'all' || marketTier !== 'all' || marketDir !== 'all') ? 'No market items match these filters.'
                  : lockedRiskCount > 0 ? 'Newer market signals are still aging into your tier.' : 'No market signals yet.'}
              </Text>
            ) : (
              <>
                {marketFiltered.slice(0, visible).map((r) => <RiskCard key={r.key} risk={r} />)}
                {visible < marketFiltered.length && (
                  <Text className="text-textMuted text-center mt-4" style={{ fontSize: 12, letterSpacing: 0.5 }}>
                    Showing {visible} of {marketFiltered.length} · scroll for more
                  </Text>
                )}
              </>
            )}
            {lockedRiskCount > 0 && marketFiltered.length > 0 && (
              <View className="mt-3"><LockedSignalsBanner tier={tier} lockedCount={lockedRiskCount} /></View>
            )}
          </>
        )}

        <Text className="text-textMuted text-[12px] text-center mt-8 mb-2 px-4 leading-4">
          Now TrendIn provides signal analysis for informational purposes only — not financial,
          investment, or legal advice. All decisions are your own.
        </Text>
      </ScrollView>

      {/* Persistent action bar — always visible, never buried in the list. A soft
          white fade sits behind it so it reads cleanly over scrolling content
          without a hard edge (kept short so it doesn't eat the screen). */}
      {showPull && (
        <>
          <LinearGradient
            colors={['rgba(255,255,255,0)', 'rgba(255,255,255,0.92)', '#FFFFFF']}
            locations={[0, 0.55, 1]}
            pointerEvents="none"
            style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 120 }}
          />
          <View style={{ position: 'absolute', left: 18, right: 18, bottom: 14 }}>
            {mode === 'attention' ? <PullTrendsButton /> : <PullMarketButton />}
          </View>
        </>
      )}
    </SafeAreaView>
  );
}
