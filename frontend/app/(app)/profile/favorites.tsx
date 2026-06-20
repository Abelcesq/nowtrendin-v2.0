import { useEffect, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Plus, X, ChevronRight, ChevronLeft, Search } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { dashboardApi, type Favorite } from '../../../lib/api';
import { fetchScores, fetchRiskScores } from '../../../lib/gradientApi';

// Favorites — saved filtered-view shortcuts, synced via /api/dashboard/ (matches the
// web). "Track topic" is DB-validated: you can only pin a topic or market instrument
// that actually exists in our data, and clicking opens its real detail.
const SECTIONS = [['trends', 'Trends'], ['market', 'Market'], ['history', 'Track topic']] as const;
const OPTIONS: Record<string, { k: string; label: string }[]> = {
  trends: [{ k: 'nowtrendin', label: 'Now TrendIn' }, { k: 'all', label: 'All' }, { k: 'breakout', label: 'Breakout' }, { k: 'strong', label: 'Strong' }, { k: 'emerging', label: 'Emerging' }, { k: 'marginal', label: 'Marginal' }, { k: 'anomalies', label: 'Anomalies' }],
  market: [{ k: 'all', label: 'All' }, { k: 'elevated', label: 'Elevated' }, { k: 'active', label: 'Active' }, { k: 'building', label: 'Building' }, { k: 'routine', label: 'Routine' }, { k: 'dormant', label: 'Dormant' }, { k: 'leverage', label: 'Leverage ≥60' }],
};
const COLORS = ['#00C896', '#8B5CF6', '#DC2626', '#2D7EEF', '#D4A017', '#E85A1E'];

type Entity = { key: string; display: string; kind: 'topic' | 'market' };

export default function Favorites() {
  const router = useRouter();
  const [favs, setFavs] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [section, setSection] = useState<'trends' | 'market' | 'history'>('trends');
  const [filter, setFilter] = useState('breakout');
  // Track-topic search (DB-validated)
  const [entities, setEntities] = useState<Entity[] | null>(null);
  const [query, setQuery] = useState('');
  const [picked, setPicked] = useState<Entity | null>(null);

  useEffect(() => {
    dashboardApi.get().then((d) => setFavs(d.favorites || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  // Lazy-load the searchable universe (topics + market instruments) when the user
  // first opens "Track topic".
  useEffect(() => {
    if (section !== 'history' || entities !== null) return;
    setEntities([]);
    Promise.all([fetchScores().catch(() => []), fetchRiskScores().catch(() => [])]).then(([sigs, risks]) => {
      const ts: Entity[] = (sigs || []).map((s: any) => ({ key: String(s.id), display: s.topic || String(s.id), kind: 'topic' }));
      const ms: Entity[] = (risks || []).map((r: any) => ({ key: String(r.key), display: r.display || String(r.key), kind: 'market' }));
      setEntities([...ms, ...ts]);
    });
  }, [section]);

  const persist = (next: Favorite[]) => { setFavs(next); dashboardApi.saveFavorites(next).catch(() => {}); };
  const remove = (id: string) => persist(favs.filter((f) => f.id !== id));
  const resetForm = () => { setAdding(false); setQuery(''); setPicked(null); };
  const add = () => {
    let fav: Favorite;
    const color = COLORS[favs.length % COLORS.length];
    if (section === 'history') {
      if (!picked) return;   // must be a real DB entity
      fav = { id: `fav_${Date.now()}`, label: picked.display, section: 'history', filter: picked.key, kind: picked.kind, color };
    } else {
      const opt = OPTIONS[section].find((o) => o.k === filter) || OPTIONS[section][0];
      fav = { id: `fav_${Date.now()}`, label: opt.label, section, filter, color };
    }
    persist([...favs, fav]); resetForm();
  };
  const open = (f: Favorite) => {
    if (f.section === 'history' && f.filter) {
      if (f.kind === 'market') {
        router.push({ pathname: '/risk/[key]', params: { key: f.filter, from: '/profile/favorites' } } as any);
      } else {
        router.push({ pathname: '/signal/[id]', params: { id: f.filter, from: '/profile/favorites' } } as any);
      }
    } else if (f.section === 'watchlist') {
      router.push('/profile/watchlists' as any);
    } else {
      router.push('/' as any);
    }
  };

  const matches = (entities || []).filter((e) => query.trim().length >= 2 && e.display.toLowerCase().includes(query.trim().toLowerCase())).slice(0, 8);
  const chip = (on: boolean, label: string, fn: () => void) => (
    <TouchableOpacity key={label} onPress={fn} className="px-3 py-1.5 rounded-full border mr-1.5 mb-1.5" style={{ backgroundColor: on ? '#00C896' : '#FFFFFF', borderColor: on ? '#00C896' : '#E4E7EC' }}>
      <Text className="text-xs font-semibold" style={{ color: on ? '#FFFFFF' : '#5B6472' }}>{label}</Text>
    </TouchableOpacity>
  );

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="pt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" /><Text className="text-textSecondary text-base">Back</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-2xl font-bold mb-1">Favorites</Text>
      <Text className="text-textMuted text-sm mb-4">Saved shortcuts to your filtered views.</Text>

      {loading ? <ActivityIndicator color="#00C896" style={{ marginVertical: 20 }} /> : favs.length === 0 ? (
        <Text className="text-textMuted text-sm mb-3">No favorites yet. Add one below.</Text>
      ) : favs.map((f) => (
        <View key={f.id} className="bg-surface rounded-xl border border-border p-3.5 mb-2.5 flex-row items-center">
          <View className="w-2 h-2 rounded-sm mr-3" style={{ backgroundColor: f.color || '#2D7EEF' }} />
          <TouchableOpacity className="flex-1 flex-row items-center justify-between" onPress={() => open(f)}>
            <Text className="text-textPrimary text-base">{f.label}</Text>
            <ChevronRight size={18} color="#475569" />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => remove(f.id)} className="ml-3 p-1"><X size={18} color="#DC2626" /></TouchableOpacity>
        </View>
      ))}

      {!adding ? (
        <TouchableOpacity onPress={() => setAdding(true)} className="flex-row items-center gap-2 py-3 mt-1">
          <Plus size={18} color="#00C896" /><Text className="text-primary text-base font-semibold">Add favorite</Text>
        </TouchableOpacity>
      ) : (
        <View className="bg-surface rounded-2xl border border-border p-4 mt-2">
          <Text className="text-textMuted text-[11px] mb-1.5">Section</Text>
          <View className="flex-row flex-wrap mb-3">{SECTIONS.map(([s, label]) => chip(section === s, label, () => { setSection(s); setPicked(null); setQuery(''); if (s !== 'history') setFilter(OPTIONS[s][0].k); }))}</View>

          {section === 'history' ? (
            <>
              <Text className="text-textMuted text-[11px] mb-1.5">Search a topic or company</Text>
              {picked ? (
                <TouchableOpacity onPress={() => setPicked(null)} className="flex-row items-center justify-between bg-bg rounded-lg px-3 py-2.5 border mb-3" style={{ borderColor: '#00C896' }}>
                  <Text className="text-textPrimary text-base">{picked.display} <Text className="text-textMuted text-xs">· {picked.kind === 'market' ? 'Market' : 'Trend'}</Text></Text>
                  <X size={16} color="#94A3B8" />
                </TouchableOpacity>
              ) : (
                <>
                  <View className="flex-row items-center bg-bg rounded-lg px-3 border border-border mb-2">
                    <Search size={16} color="#9AA3B0" />
                    <TextInput value={query} onChangeText={setQuery} placeholder="Type a topic or ticker…" placeholderTextColor="#9AA3B0" className="flex-1 py-2.5 ml-2" style={{ color: '#1A1A2E' }} />
                  </View>
                  {entities === null || (entities.length === 0 && query.length >= 2) ? (
                    <Text className="text-textMuted text-xs mb-3">Loading the topic universe…</Text>
                  ) : query.trim().length >= 2 && matches.length === 0 ? (
                    <Text className="text-textMuted text-xs mb-3">Not in our database — only existing topics/instruments can be tracked.</Text>
                  ) : (
                    <View className="mb-3">
                      {matches.map((e) => (
                        <TouchableOpacity key={`${e.kind}:${e.key}`} onPress={() => { setPicked(e); setQuery(''); }} className="flex-row items-center justify-between py-2 border-b border-border">
                          <Text className="text-textPrimary text-[15px]">{e.display}</Text>
                          <Text className="text-textMuted text-[11px]">{e.kind === 'market' ? 'Market' : 'Trend'}</Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  )}
                </>
              )}
            </>
          ) : (
            <><Text className="text-textMuted text-[11px] mb-1.5">Filter</Text>
              <View className="flex-row flex-wrap mb-3">{OPTIONS[section].map((o) => chip(filter === o.k, o.label, () => setFilter(o.k)))}</View></>
          )}

          <View className="flex-row gap-2">
            <TouchableOpacity onPress={add} disabled={section === 'history' && !picked} className="flex-1 rounded-lg py-3 items-center" style={{ backgroundColor: section === 'history' && !picked ? '#9DDDC9' : '#00C896' }}>
              <Text className="text-white font-semibold">Add</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={resetForm} className="flex-1 border border-border rounded-lg py-3 items-center"><Text className="text-textSecondary font-semibold">Cancel</Text></TouchableOpacity>
          </View>
        </View>
      )}
    </Screen>
  );
}
