import { titleCaseTopic } from "../../lib/signals";
import { useMemo, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Switch, ActivityIndicator, ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Bell, Trash2, Plus, Minus, ChevronLeft, Search, X, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Disclaimer } from '../../components/ui/Disclaimer';
import { Button } from '../../components/ui/Button';
import { alertsApi } from '../../lib/api';
import { useSignals, useRiskScores } from '../../hooks/useSignals';
import { ageLabel } from '../../lib/signals';

const SCORE_TYPES = ['detection', 'confidence', 'overall'] as const;
type Picked = { key: string; display: string; kind: 'topic' | 'market' };

export default function Alerts() {
  const params = useLocalSearchParams<{ topic?: string; key?: string; kind?: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const { data: alerts = [], isLoading } = useQuery({ queryKey: ['alerts'], queryFn: () => alertsApi.list() });
  const { signals } = useSignals();
  const { risks } = useRiskScores();

  // Verified-only selection: an alert can ONLY target a topic OR market signal
  // that exists in our live data (same universe as the watchlist). Free text is
  // never accepted (it would link to nothing).
  const [query, setQuery] = useState('');
  const [picked, setPicked] = useState<Picked | null>(
    params.key ? { key: String(params.key), display: String(params.topic ?? params.key), kind: (params.kind === 'market' ? 'market' : 'topic') } : null
  );
  const [scoreType, setScoreType] = useState<string>('detection');
  // falls-below alerts (2026-07-19): 'above' = original rises-past behavior;
  // 'below' = watch a held topic losing signal.
  const [direction, setDirection] = useState<'above' | 'below'>('above');
  const [threshold, setThreshold] = useState(75);
  const [push, setPush] = useState(true);
  const [email, setEmail] = useState(true);
  const [sms, setSms] = useState(false);
  const [creating, setCreating] = useState(false);

  const reload = () => qc.invalidateQueries({ queryKey: ['alerts'] });
  const bump = (d: number) => setThreshold((t) => Math.max(0, Math.min(100, t + d)));

  // Unified universe: trends + market signals (same as the watchlist).
  const entities = useMemo<Picked[]>(() => [
    ...risks.map((r: any) => ({ key: String(r.key), display: r.display || String(r.key), kind: 'market' as const })),
    ...signals.map((s: any) => ({ key: String(s.id), display: s.topic || String(s.id), kind: 'topic' as const })),
  ], [signals, risks]);

  const q = query.trim().toLowerCase();
  const matches = q.length >= 2
    ? entities.filter((e) => e.display.toLowerCase().includes(q) || e.key.toLowerCase().includes(q)).slice(0, 8)
    : [];

  const create = async () => {
    if (!picked) return;  // hard gate — must be a verified entity
    setCreating(true);
    try {
      await alertsApi.create({
        topic_key: picked.key,
        topic_display: picked.display,
        kind: picked.kind,
        score_type: scoreType,
        direction,
        threshold,
        notify_push: push,
        notify_email: email,
        notify_sms: sms,
      });
      setPicked(null); setQuery('');
      reload();
    } finally {
      setCreating(false);
    }
  };

  const toggle = async (a: any) => { await alertsApi.update(a.id, { active: !a.active }); reload(); };
  const remove = async (a: any) => { await alertsApi.remove(a.id); reload(); };
  const openDetail = (a: any) => {
    if (a.kind === 'market') {
      router.push({ pathname: '/risk/[key]', params: { key: a.topic_key, from: '/alerts' } } as any);
    } else {
      router.push({ pathname: '/signal/[id]', params: { id: a.topic_key, from: '/alerts' } } as any);
    }
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.push('/profile')} className="pt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#3C4663" /><Text className="text-textSecondary text-base">Profile</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-2xl font-bold mb-4">Alerts</Text>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Active alerts</Text>
      {isLoading ? (
        <ActivityIndicator color="#2E7D5B" style={{ marginVertical: 16 }} />
      ) : alerts.length === 0 ? (
        <Text className="text-textMuted text-sm mb-4">No alerts yet. Create one below.</Text>
      ) : (
        alerts.map((a: any) => (
          <View key={a.id} className="bg-card rounded-xl p-4 mb-3 flex-row items-center">
            <View className="w-9 h-9 rounded-full items-center justify-center mr-3" style={{ backgroundColor: '#2E7D5B20' }}>
              <Bell size={16} color="#2E7D5B" />
            </View>
            <TouchableOpacity className="flex-1 pr-2" onPress={() => openDetail(a)} activeOpacity={0.6}>
              <Text className="text-textPrimary font-semibold">{a.topic_display || a.topic_key}</Text>
              <Text className="text-textMuted text-xs mt-0.5">
                {a.kind === 'market' ? 'Market' : 'Trend'} · when {a.score_type} {a.direction === 'below' ? '≤' : '≥'} {a.threshold} · {[a.notify_push && 'Push', a.notify_email && 'Email', a.notify_sms && 'Text'].filter(Boolean).join(' + ') || 'No channel'}
              </Text>
              {a.last_triggered_at && (
                <Text className="text-[12px] font-bold mt-1" style={{ color: '#246B4A' }}>
                  🔔 Triggered {ageLabel(Date.parse(a.last_triggered_at))}
                </Text>
              )}
            </TouchableOpacity>
            <Switch value={a.active} onValueChange={() => toggle(a)} trackColor={{ true: '#2E7D5B', false: '#ECECEC' }} thumbColor="#FFFFFF" />
            <TouchableOpacity onPress={() => remove(a)} className="ml-2 p-1">
              <Trash2 size={18} color="#B11226" />
            </TouchableOpacity>
          </View>
        ))
      )}

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2 mt-5">Create new alert</Text>
      <View className="bg-card rounded-2xl p-4">
        <Text className="text-textMuted text-[12px] mb-1">Topic — search and select a verified topic or market signal</Text>
        {picked ? (
          <TouchableOpacity onPress={() => setPicked(null)} className="flex-row items-center justify-between bg-bg rounded-lg px-3 py-2.5 mb-3" style={{ borderColor: '#2E7D5B' }}>
            <View className="flex-row items-center gap-2 flex-1">
              <CheckCircle size={16} color="#2E7D5B" />
              <Text className="text-textPrimary text-base flex-1">{titleCaseTopic(picked.display)} <Text className="text-textMuted text-xs">· {picked.kind === 'market' ? 'Market' : 'Trend'}</Text></Text>
            </View>
            <X size={16} color="#8A8F9C" />
          </TouchableOpacity>
        ) : (
          <>
            <View className="flex-row items-center bg-bg rounded-lg px-3 mb-2">
              <Search size={16} color="#9A9AA2" />
              <TextInput value={query} onChangeText={setQuery} placeholder="Search a topic or market signal…" placeholderTextColor="#9A9AA2" className="flex-1 py-2.5 ml-2" style={{ color: '#16264A' }} />
            </View>
            {q.length >= 2 && matches.length === 0 ? (
              <Text className="text-textMuted text-xs mb-3">Not in our database — only existing topics/market signals can be alerted on.</Text>
            ) : matches.length > 0 ? (
              <View className="mb-3">
                {matches.map((e) => (
                  <TouchableOpacity key={`${e.kind}:${e.key}`} onPress={() => { setPicked(e); setQuery(''); }} className="flex-row items-center justify-between py-2 border-b border-border">
                    <Text className="text-textPrimary text-[16px]">{titleCaseTopic(e.display)}</Text>
                    <Text className="text-textMuted text-[12px]">{e.kind === 'market' ? 'Market' : 'Trend'}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : null}
          </>
        )}

        <Text className="text-textMuted text-[12px] mb-1">Score type</Text>
        <View className="flex-row gap-2 mb-3">
          {SCORE_TYPES.map((st) => {
            const active = scoreType === st;
            return (
              <TouchableOpacity key={st} onPress={() => setScoreType(st)} className="px-3 py-1.5 rounded-full" style={{ backgroundColor: active ? '#2E7D5B' : '#FFFFFF', borderColor: active ? '#2E7D5B' : '#ECECEC' }}>
                <Text className="text-xs font-semibold capitalize" style={{ color: active ? '#FFFFFF' : '#3C4663' }}>{st}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text className="text-textMuted text-[12px] mb-1">Direction</Text>
        <View className="flex-row gap-2 mb-3">
          {(['above', 'below'] as const).map((d) => {
            const active = direction === d;
            return (
              <TouchableOpacity key={d} onPress={() => setDirection(d)} className="px-3 py-1.5 rounded-full" style={{ backgroundColor: active ? '#2E7D5B' : '#FFFFFF', borderColor: active ? '#2E7D5B' : '#ECECEC' }}>
                <Text className="text-xs font-semibold" style={{ color: active ? '#FFFFFF' : '#3C4663' }}>
                  {d === 'above' ? 'Rises above' : 'Falls below'}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text className="text-textMuted text-[12px] mb-1">{direction === 'below' ? 'Alert when score falls to' : 'Alert when score reaches'}</Text>
        <View className="flex-row items-center gap-4 mb-3">
          <TouchableOpacity onPress={() => bump(-5)} className="w-9 h-9 rounded-full items-center justify-center">
            <Minus size={16} color="#3C4663" />
          </TouchableOpacity>
          <Text className="text-textPrimary text-2xl font-black w-12 text-center">{threshold}</Text>
          <TouchableOpacity onPress={() => bump(5)} className="w-9 h-9 rounded-full items-center justify-center">
            <Plus size={16} color="#3C4663" />
          </TouchableOpacity>
        </View>

        <View className="flex-row items-center justify-between py-1">
          <Text className="text-textSecondary text-sm">Push notification</Text>
          <Switch value={push} onValueChange={setPush} trackColor={{ true: '#2E7D5B', false: '#ECECEC' }} thumbColor="#FFFFFF" />
        </View>
        <View className="flex-row items-center justify-between py-1">
          <Text className="text-textSecondary text-sm">Email</Text>
          <Switch value={email} onValueChange={setEmail} trackColor={{ true: '#2E7D5B', false: '#ECECEC' }} thumbColor="#FFFFFF" />
        </View>
        <View className="flex-row items-center justify-between py-1 mb-3">
          <View className="flex-1 pr-2">
            <Text className="text-textSecondary text-sm">Text (SMS)</Text>
            <Text className="text-textMuted text-[12px]">Needs a verified phone (Profile → Notifications)</Text>
          </View>
          <Switch value={sms} onValueChange={setSms} trackColor={{ true: '#2E7D5B', false: '#ECECEC' }} thumbColor="#FFFFFF" />
        </View>

        <Button onPress={create} loading={creating} disabled={!picked} size="lg">
          {picked ? 'Create Alert' : 'Select a topic first'}
        </Button>
      </View>

      <Disclaimer />
    </Screen>
  );
}
