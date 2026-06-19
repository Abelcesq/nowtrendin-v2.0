import { useEffect, useMemo, useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, ActivityIndicator, Switch, Alert as RNAlert } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, Plus, X, Star } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { watchlistApi } from '../../../lib/api';
import { useAuthStore } from '../../../store/auth.store';
import { TierID } from '../../../constants/tiers';
import { useTierFeed, useRiskScores } from '../../../hooks/useSignals';

interface WItem { id: number; key: string; display: string; kind: 'topic' | 'market' }
interface WList { id: number; name: string; items: WItem[]; notify_email?: boolean; notify_sms?: boolean; notify_threshold?: number }

const DET = '#2D7EEF', CONF = '#00C896';

export default function ProfileWatchlists() {
  const router = useRouter();
  const tier = (useAuthStore((s) => s.user)?.tier ?? 'consumer') as TierID;
  const { accessible } = useTierFeed(tier);
  const { risks } = useRiskScores();

  const [lists, setLists] = useState<WList[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [adding, setAdding] = useState('');
  const [busy, setBusy] = useState(false);

  // live score lookup keyed by `${kind}:${key}`
  const live = useMemo(() => {
    const m: Record<string, { det: number; conf: number; label: string }> = {};
    for (const s of accessible as any[]) {
      m[`topic:${String(s.id).toLowerCase()}`] = { det: s.detection, conf: s.confidence, label: s.topic };
    }
    for (const r of (risks as any[])) {
      const g = r.marketGradient || {};
      m[`market:${String(r.key).toLowerCase()}`] = { det: Math.round(g.detection ?? r.detection ?? 0), conf: Math.round(g.confidence ?? 0), label: r.display };
    }
    return m;
  }, [accessible, risks]);

  const load = async () => {
    setErr(null);
    try {
      const data = await watchlistApi.list();
      setLists(data);
      setActiveId((cur) => cur ?? (data[0]?.id ?? null));
    } catch (e: any) {
      setErr(e?.data?.detail || 'Could not load watchlists.');
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const current = lists.find((l) => l.id === activeId) || null;

  const newList = async () => {
    setBusy(true);
    try { const wl = await watchlistApi.create('New list'); setLists((ls) => [...ls, wl]); setActiveId(wl.id); }
    catch { setErr('Could not create list.'); } finally { setBusy(false); }
  };
  const deleteList = (id: number) => {
    RNAlert.alert('Delete watchlist?', 'This removes the list and its items.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Delete', style: 'destructive', onPress: async () => {
        await watchlistApi.remove(id).catch(() => {});
        setLists((ls) => ls.filter((l) => l.id !== id));
        setActiveId((a) => (a === id ? null : a));
      } },
    ]);
  };
  const addItem = async () => {
    const raw = adding.trim(); if (!raw || !current) return;
    const q = raw.toLowerCase();
    const found = Object.entries(live).find(([, v]) => v.label.toLowerCase() === q) ||
      Object.entries(live).find(([k]) => k.endsWith(`:${q}`));
    const [kind, key] = found ? [found[0].split(':')[0], found[0].split(':').slice(1).join(':')] : ['topic', raw];
    const display = found ? found[1].label : raw;
    setBusy(true);
    try {
      const item = await watchlistApi.addItem(current.id, { key, display, kind: kind as 'topic' | 'market' });
      setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: [...l.items.filter((i) => i.key !== item.key), item] } : l));
      setAdding('');
    } catch { setErr('Could not add item.'); } finally { setBusy(false); }
  };
  const removeItem = async (itemId: number) => {
    if (!current) return;
    setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, items: l.items.filter((i) => i.id !== itemId) } : l));
    await watchlistApi.removeItem(current.id, itemId).catch(() => load());
  };
  // Per-list movement notifications (email / text). Optimistic; reverts on error.
  const setNotify = async (fields: { notify_email?: boolean; notify_sms?: boolean; notify_threshold?: number }) => {
    if (!current) return;
    setLists((ls) => ls.map((l) => l.id === current.id ? { ...l, ...fields } : l));
    await watchlistApi.update(current.id, fields).catch(() => load());
  };
  const phoneVerified = useAuthStore.getState().user?.phoneVerified ?? false;

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <View className="pb-3">
        <Text className="text-textPrimary text-3xl font-bold mb-1">Watchlists</Text>
        <Text className="text-textMuted text-base">Track the gap on the names you care about — synced across your devices.</Text>
      </View>

      {/* list selector */}
      <View className="flex-row flex-wrap gap-2 mb-3">
        {lists.map((l) => {
          const on = l.id === activeId;
          return (
            <TouchableOpacity key={l.id} onPress={() => setActiveId(l.id)} onLongPress={() => deleteList(l.id)}
              className="px-3 py-2 rounded-full flex-row items-center gap-1.5"
              style={{ backgroundColor: on ? '#1A1A2E' : '#FFFFFF', borderWidth: 1, borderColor: on ? '#1A1A2E' : '#E4E7EC' }}>
              <Text className="text-xs font-semibold" style={{ color: on ? '#FFFFFF' : '#5B6472' }}>{l.name}</Text>
              <Text className="text-[10px] font-bold" style={{ color: on ? '#9AA3B0' : '#9AA3B0' }}>{l.items.length}</Text>
            </TouchableOpacity>
          );
        })}
        <TouchableOpacity onPress={newList} disabled={busy} className="px-3 py-2 rounded-full flex-row items-center gap-1 border border-border bg-surface">
          <Plus size={13} color="#2D7EEF" /><Text className="text-xs font-bold" style={{ color: '#2D7EEF' }}>New</Text>
        </TouchableOpacity>
      </View>
      {current && <Text className="text-textMuted text-[11px] mb-3">Long-press a list to delete it.</Text>}

      {/* add row */}
      {current && (
        <View className="flex-row gap-2 mb-4">
          <TextInput value={adding} onChangeText={setAdding} onSubmitEditing={addItem} placeholder="Add a topic or instrument…"
            placeholderTextColor="#9AA3B0"
            className="flex-1 h-11 px-3 rounded-xl border border-border bg-surface text-textPrimary" />
          <TouchableOpacity onPress={addItem} disabled={busy} className="h-11 px-4 rounded-xl items-center justify-center" style={{ backgroundColor: '#1A1A2E' }}>
            <Text className="text-white font-bold text-sm">Add</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Per-list movement notifications */}
      {current && (
        <View className="bg-surface rounded-2xl border border-border p-4 mb-4">
          <Text className="text-textSecondary text-xs font-semibold mb-1">Notify me when any item crosses Detection</Text>
          <View className="flex-row flex-wrap gap-1.5 mb-2">
            {[60, 70, 75, 80, 85, 90].map((v) => {
              const on = (current.notify_threshold ?? 75) === v;
              return (
                <TouchableOpacity key={v} onPress={() => setNotify({ notify_threshold: v })} className="px-3 py-1.5 rounded-full border" style={{ backgroundColor: on ? '#00C896' : '#FFFFFF', borderColor: on ? '#00C896' : '#E4E7EC' }}>
                  <Text className="text-xs font-semibold" style={{ color: on ? '#FFFFFF' : '#5B6472' }}>{v}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
          <View className="flex-row items-center justify-between py-1">
            <Text className="text-textSecondary text-sm">Email</Text>
            <Switch value={!!current.notify_email} onValueChange={(v) => setNotify({ notify_email: v })} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
          </View>
          <View className="flex-row items-center justify-between py-1">
            <View className="flex-1 pr-2">
              <Text className="text-textSecondary text-sm">Text (SMS)</Text>
              {!phoneVerified && <Text className="text-textMuted text-[10px]">Needs a verified phone (Profile → Notifications)</Text>}
            </View>
            <Switch value={!!current.notify_sms} disabled={!phoneVerified} onValueChange={(v) => setNotify({ notify_sms: v })} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
          </View>
        </View>
      )}

      {loading ? (
        <View className="py-16 items-center"><ActivityIndicator color="#00C896" /></View>
      ) : err ? (
        <Text className="text-textMuted text-center py-10">{err}</Text>
      ) : !current ? (
        <Text className="text-textMuted text-center py-10">Create a list to start tracking.</Text>
      ) : current.items.length === 0 ? (
        <View className="items-center py-12">
          <Star size={28} color="#9AA3B0" />
          <Text className="text-textSecondary font-semibold mt-2">Nothing tracked yet</Text>
          <Text className="text-textMuted text-sm text-center mt-1">Add a topic or instrument above to watch its gap.</Text>
        </View>
      ) : (
        current.items.map((it) => {
          const lv = live[`${it.kind}:${it.key.toLowerCase()}`];
          const det = lv?.det ?? 0, conf = lv?.conf ?? 0, gap = det - conf;
          return (
            <View key={it.id} className="bg-surface rounded-2xl border border-border p-4 mb-2.5 flex-row items-center">
              <View className="flex-1">
                <Text className="text-textPrimary text-base font-bold">{it.display || it.key}</Text>
                <Text className="text-textMuted text-[11px] mt-0.5">{it.kind === 'market' ? 'Market Signal' : 'Trend'}</Text>
              </View>
              {lv ? (
                <View className="flex-row items-center gap-3 mr-1">
                  <View className="items-center"><Text className="text-textMuted text-[9px] font-bold">DET</Text><Text style={{ color: DET }} className="text-lg font-black">{det}</Text></View>
                  <View className="items-center"><Text className="text-textMuted text-[9px] font-bold">CONF</Text><Text style={{ color: CONF }} className="text-lg font-black">{conf}</Text></View>
                  <View className="items-center"><Text className="text-textMuted text-[9px] font-bold">GAP</Text><Text className="text-lg font-black" style={{ color: Math.abs(gap) >= 20 ? '#EE6A2A' : '#5B6472' }}>{gap > 0 ? '+' : ''}{gap}</Text></View>
                </View>
              ) : (
                <Text className="text-textMuted text-[11px] mr-2 flex-1 text-right">Not yet scored</Text>
              )}
              <TouchableOpacity onPress={() => removeItem(it.id)} className="p-1.5"><X size={16} color="#9AA3B0" /></TouchableOpacity>
            </View>
          );
        })
      )}
    </Screen>
  );
}
