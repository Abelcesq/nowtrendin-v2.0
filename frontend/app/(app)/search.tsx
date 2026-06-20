import { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Search as SearchIcon, TrendingUp, Activity, Globe, X } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { TrendCard } from '../../components/trends/TrendCard';
import { RiskCard } from '../../components/trends/RiskCard';
import { useTierFeed, useRiskScores } from '../../hooks/useSignals';
import { useAuthStore } from '../../store/auth.store';
import { TierID, isDataAccessible } from '../../constants/tiers';
import { queryApi } from '../../lib/api';

type Tab = 'trends' | 'market' | 'graded';

const STAGE_COLOR: Record<string, string> = {
  BREAKOUT: '#00C896', STRONG: '#2D7EEF', EMERGING: '#D4A017', MARGINAL: '#E85A1E', WATCHING: '#E85A1E', MONITORING: '#94A3B8',
};

function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${Math.max(1, mins)}m ago`;
  const h = Math.floor(mins / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return d < 30 ? `${d}d ago` : new Date(iso).toLocaleDateString();
}

// Search A Topic — one place to search across all three data sections (Trends,
// Market, Graded). FREE, no tokens; tier time-restrictions still apply to the
// underlying data windows.
export default function Search() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const [tab, setTab] = useState<Tab>('trends');

  return (
    <Screen scroll>
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-1">Search A Topic</Text>
      <Text className="text-textMuted text-xs mb-4 leading-4">
        Find a trend, market topic, or graded item in our database — free, no tokens used but subject to tier time restrictions.
      </Text>

      {/* Three section tabs */}
      <View className="flex-row gap-2 mb-4">
        <TabBtn icon={<TrendingUp size={15} color={tab === 'trends' ? '#FFFFFF' : '#5B6472'} />} label="Trends" color="#00C896" active={tab === 'trends'} onPress={() => setTab('trends')} />
        <TabBtn icon={<Activity size={15} color={tab === 'market' ? '#FFFFFF' : '#5B6472'} />} label="Market" color="#CF2A1B" active={tab === 'market'} onPress={() => setTab('market')} />
        <TabBtn icon={<Globe size={15} color={tab === 'graded' ? '#FFFFFF' : '#5B6472'} />} label="Graded" color="#D4A017" active={tab === 'graded'} onPress={() => setTab('graded')} />
      </View>

      {tab === 'trends' && <TrendsSearch tier={tier} />}
      {tab === 'market' && <MarketSearch tier={tier} />}
      {tab === 'graded' && <GradedSearch />}
    </Screen>
  );
}

function TabBtn({ icon, label, color, active, onPress }: { icon: React.ReactNode; label: string; color: string; active: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity onPress={onPress} className="flex-1 flex-row items-center justify-center gap-1.5 rounded-xl py-2.5 border"
      style={{ backgroundColor: active ? color : '#FFFFFF', borderColor: active ? color : '#E4E7EC' }}>
      {icon}
      <Text className="text-[12px] font-bold" style={{ color: active ? '#FFFFFF' : '#5B6472' }}>{label}</Text>
    </TouchableOpacity>
  );
}

function SearchBar({ value, onChange, placeholder, onClear }: { value: string; onChange: (s: string) => void; placeholder: string; onClear?: () => void }) {
  return (
    <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
      <SearchIcon size={18} color="#9AA3B0" />
      <TextInput value={value} onChangeText={onChange} placeholder={placeholder} placeholderTextColor="#9AA3B0"
        className="flex-1 ml-3 text-base" style={{ color: '#1A1A2E' }} />
      {value && onClear ? <TouchableOpacity onPress={onClear} className="ml-2"><X size={16} color="#9AA3B0" /></TouchableOpacity> : null}
    </View>
  );
}

function TrendsSearch({ tier }: { tier: TierID }) {
  const { accessible, isLoading } = useTierFeed(tier);
  const [q, setQ] = useState('');
  const ql = q.trim().toLowerCase();
  const results = ql ? accessible.filter((s) => s.topic.toLowerCase().includes(ql) || s.category.toLowerCase().includes(ql)) : accessible;
  return (
    <>
      <SearchBar value={q} onChange={setQ} placeholder="Search trends…" onClear={() => setQ('')} />
      <Text className="text-textMuted text-[11px] mb-2">{results.length} trend{results.length === 1 ? '' : 's'} in your data window</Text>
      {isLoading ? <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 32 }} />
        : results.length === 0 ? <Empty text={`No trends match "${q}".`} />
        : results.map((s) => <TrendCard key={s.id} signal={s} />)}
    </>
  );
}

function MarketSearch({ tier }: { tier: TierID }) {
  const { risks, isLoading } = useRiskScores();
  const [q, setQ] = useState('');
  const accessible = risks.filter((r) => isDataAccessible(tier, Date.now() - r.firstSeenAt));
  const ql = q.trim().toLowerCase();
  const results = ql ? accessible.filter((r) => r.display.toLowerCase().includes(ql)) : accessible;
  return (
    <>
      <SearchBar value={q} onChange={setQ} placeholder="Search market topics…" onClear={() => setQ('')} />
      <Text className="text-textMuted text-[11px] mb-2">{results.length} market item{results.length === 1 ? '' : 's'} in your data window</Text>
      {isLoading ? <ActivityIndicator size="large" color="#CF2A1B" style={{ marginTop: 32 }} />
        : results.length === 0 ? <Empty text={`No market topics match "${q}".`} />
        : results.map((r) => <RiskCard key={r.key} risk={r} />)}
    </>
  );
}

function GradedSearch() {
  const [q, setQ] = useState('');
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async (query: string) => {
    setLoading(true);
    try { const d: any = await queryApi.gradedAll(query); setRows(Array.isArray(d?.grades) ? d.grades : []); }
    catch { setRows([]); } finally { setLoading(false); }
  }, []);
  useEffect(() => { load(''); }, [load]);
  useEffect(() => { const t = setTimeout(() => load(q.trim()), 350); return () => clearTimeout(t); }, [q, load]);
  return (
    <>
      <SearchBar value={q} onChange={setQ} placeholder="Search graded topics…" onClear={() => setQ('')} />
      <Text className="text-textMuted text-[11px] mb-2">Topics graded by members across all plans — free to view.</Text>
      {loading ? <ActivityIndicator size="small" color="#D4A017" style={{ marginTop: 28 }} />
        : rows.length === 0 ? <Empty text={q ? `No graded topics match "${q}".` : 'No topics have been graded yet.'} />
        : rows.map((g) => {
            const col = STAGE_COLOR[g.stage] ?? '#94A3B8';
            return (
              <View key={g.id} className="bg-surface rounded-xl border border-border p-3 mb-2">
                <View className="flex-row items-center justify-between">
                  <Text className="text-textPrimary text-sm font-bold flex-1 pr-2" numberOfLines={1}>{g.topic}</Text>
                  {!!g.stage && <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${col}1A` }}><Text className="text-[9px] font-bold" style={{ color: col }}>{g.stage}</Text></View>}
                </View>
                <View className="flex-row items-center gap-3 mt-1">
                  <Text className="text-[11px]" style={{ color: '#2D7EEF' }}>DET {Math.round(g.detection)}</Text>
                  <Text className="text-[11px]" style={{ color: '#00C896' }}>CONF {Math.round(g.confidence)}</Text>
                  <Text className="text-textMuted text-[11px] ml-auto">{timeAgo(g.createdAt)}</Text>
                </View>
              </View>
            );
          })}
    </>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <View className="items-center mt-12">
      <SearchIcon size={44} color="#C7CDD6" />
      <Text className="text-textMuted text-sm mt-4 text-center px-6">{text}</Text>
    </View>
  );
}
