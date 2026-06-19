import { useEffect, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Plus, X, ChevronRight, ChevronLeft } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { dashboardApi, type Favorite } from '../../../lib/api';

// Favorites — saved filtered-view shortcuts, identical flow to the web terminal and
// synced via the SAME /api/dashboard/ backend, so they match across every platform.
const SECTIONS = [['trends', 'Trends'], ['market', 'Market'], ['history', 'Track topic'], ['watchlist', 'Watchlist']] as const;
const OPTIONS: Record<string, { k: string; label: string }[]> = {
  trends: [{ k: 'nowtrendin', label: 'Now TrendIn' }, { k: 'all', label: 'All' }, { k: 'breakout', label: 'Breakout' }, { k: 'strong', label: 'Strong' }, { k: 'emerging', label: 'Emerging' }, { k: 'marginal', label: 'Marginal' }, { k: 'anomalies', label: 'Anomalies' }],
  market: [{ k: 'all', label: 'All' }, { k: 'elevated', label: 'Elevated' }, { k: 'active', label: 'Active' }, { k: 'building', label: 'Building' }, { k: 'routine', label: 'Routine' }, { k: 'dormant', label: 'Dormant' }, { k: 'leverage', label: 'Leverage ≥60' }],
};
const COLORS = ['#00C896', '#8B5CF6', '#DC2626', '#2D7EEF', '#D4A017', '#E85A1E'];

export default function Favorites() {
  const router = useRouter();
  const [favs, setFavs] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [section, setSection] = useState<'trends' | 'market' | 'history' | 'watchlist'>('trends');
  const [filter, setFilter] = useState('breakout');
  const [topic, setTopic] = useState('');
  const [name, setName] = useState('');

  useEffect(() => {
    dashboardApi.get().then((d) => setFavs(d.favorites || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);
  const persist = (next: Favorite[]) => { setFavs(next); dashboardApi.saveFavorites(next).catch(() => {}); };
  const remove = (id: string) => persist(favs.filter((f) => f.id !== id));
  const add = () => {
    let fav: Favorite;
    const color = COLORS[favs.length % COLORS.length];
    if (section === 'history') {
      if (!topic.trim()) return;
      fav = { id: `fav_${Date.now()}`, label: name.trim() || topic.trim(), section: 'history', filter: topic.trim().toLowerCase().replace(/\s+/g, '_'), color };
    } else if (section === 'watchlist') {
      fav = { id: `fav_${Date.now()}`, label: name.trim() || 'My watchlists', section: 'watchlist', color };
    } else {
      const opt = OPTIONS[section].find((o) => o.k === filter) || OPTIONS[section][0];
      fav = { id: `fav_${Date.now()}`, label: name.trim() || opt.label, section, filter, color };
    }
    persist([...favs, fav]); setAdding(false); setName(''); setTopic('');
  };
  const open = (f: Favorite) => {
    if (f.section === 'history' && f.filter) router.push(`/signal/${encodeURIComponent(f.filter)}` as any);
    else if (f.section === 'history') router.push('/history' as any);
    else if (f.section === 'watchlist') router.push('/profile/watchlists' as any);
    else router.push('/' as any);
  };
  const chip = (on: boolean, label: string, fn: () => void) => (
    <TouchableOpacity onPress={fn} className="px-3 py-1.5 rounded-full border mr-1.5 mb-1.5" style={{ backgroundColor: on ? '#00C896' : '#FFFFFF', borderColor: on ? '#00C896' : '#E4E7EC' }}>
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
          <View className="flex-row flex-wrap mb-3">{SECTIONS.map(([s, label]) => chip(section === s, label, () => { setSection(s); if (s !== 'history' && s !== 'watchlist') setFilter(OPTIONS[s][0].k); }))}</View>
          {section === 'history' ? (
            <><Text className="text-textMuted text-[11px] mb-1.5">Topic</Text>
              <TextInput value={topic} onChangeText={setTopic} placeholder="Type a topic to track…" placeholderTextColor="#9AA3B0" className="bg-bg rounded-lg px-3 py-2.5 border border-border mb-3" style={{ color: '#1A1A2E' }} /></>
          ) : section !== 'watchlist' ? (
            <><Text className="text-textMuted text-[11px] mb-1.5">Filter</Text>
              <View className="flex-row flex-wrap mb-3">{OPTIONS[section].map((o) => chip(filter === o.k, o.label, () => setFilter(o.k)))}</View></>
          ) : null}
          <TextInput value={name} onChangeText={setName} placeholder="Name (optional)" placeholderTextColor="#9AA3B0" className="bg-bg rounded-lg px-3 py-2.5 border border-border mb-3" style={{ color: '#1A1A2E' }} />
          <View className="flex-row gap-2">
            <TouchableOpacity onPress={add} className="flex-1 bg-primary rounded-lg py-3 items-center"><Text className="text-white font-semibold">Add</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setAdding(false)} className="flex-1 border border-border rounded-lg py-3 items-center"><Text className="text-textSecondary font-semibold">Cancel</Text></TouchableOpacity>
          </View>
        </View>
      )}
    </Screen>
  );
}
