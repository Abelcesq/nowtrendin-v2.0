import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Switch, ActivityIndicator, ScrollView } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Bell, Trash2, Plus, Minus } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Disclaimer } from '../../components/ui/Disclaimer';
import { Button } from '../../components/ui/Button';
import { alertsApi } from '../../lib/api';
import { useSignals } from '../../hooks/useSignals';
import { ageLabel } from '../../lib/signals';

const SCORE_TYPES = ['detection', 'confidence', 'overall'] as const;

export default function Alerts() {
  const params = useLocalSearchParams<{ topic?: string; key?: string }>();
  const qc = useQueryClient();
  const { data: alerts = [], isLoading } = useQuery({ queryKey: ['alerts'], queryFn: () => alertsApi.list() });
  const { signals } = useSignals();

  const [topicDisplay, setTopicDisplay] = useState(params.topic ?? '');
  const [topicKey, setTopicKey] = useState(params.key ?? '');
  const [scoreType, setScoreType] = useState<string>('detection');
  const [threshold, setThreshold] = useState(75);
  const [push, setPush] = useState(true);
  const [email, setEmail] = useState(true);
  const [creating, setCreating] = useState(false);

  const reload = () => qc.invalidateQueries({ queryKey: ['alerts'] });
  const bump = (d: number) => setThreshold((t) => Math.max(0, Math.min(100, t + d)));

  const create = async () => {
    if (!topicDisplay.trim()) return;
    setCreating(true);
    try {
      await alertsApi.create({
        topic_key: topicKey || topicDisplay.trim().toLowerCase().replace(/\s+/g, '_'),
        topic_display: topicDisplay.trim(),
        score_type: scoreType,
        threshold,
        notify_push: push,
        notify_email: email,
      });
      setTopicDisplay('');
      setTopicKey('');
      reload();
    } finally {
      setCreating(false);
    }
  };

  const toggle = async (a: any) => { await alertsApi.update(a.id, { active: !a.active }); reload(); };
  const remove = async (a: any) => { await alertsApi.remove(a.id); reload(); };

  const suggestions = signals.slice(0, 8);

  return (
    <Screen scroll>
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-4">Alerts</Text>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Active alerts</Text>
      {isLoading ? (
        <ActivityIndicator color="#00C896" style={{ marginVertical: 16 }} />
      ) : alerts.length === 0 ? (
        <Text className="text-textMuted text-sm mb-4">No alerts yet. Create one below.</Text>
      ) : (
        alerts.map((a: any) => (
          <View key={a.id} className="bg-surface rounded-xl border border-border p-4 mb-3 flex-row items-center">
            <View className="w-9 h-9 rounded-full items-center justify-center mr-3" style={{ backgroundColor: '#00C89620' }}>
              <Bell size={16} color="#00C896" />
            </View>
            <View className="flex-1 pr-2">
              <Text className="text-textPrimary font-semibold">{a.topic_display || a.topic_key}</Text>
              <Text className="text-textMuted text-xs mt-0.5">
                When {a.score_type} ≥ {a.threshold} · {[a.notify_push && 'Push', a.notify_email && 'Email'].filter(Boolean).join(' + ') || 'No channel'}
              </Text>
              {a.last_triggered_at && (
                <Text className="text-[11px] font-bold mt-1" style={{ color: '#009970' }}>
                  🔔 Triggered {ageLabel(Date.parse(a.last_triggered_at))}
                </Text>
              )}
            </View>
            <Switch value={a.active} onValueChange={() => toggle(a)} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
            <TouchableOpacity onPress={() => remove(a)} className="ml-2 p-1">
              <Trash2 size={18} color="#DC2626" />
            </TouchableOpacity>
          </View>
        ))
      )}

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2 mt-5">Create new alert</Text>
      <View className="bg-surface rounded-2xl border border-border p-4">
        <Text className="text-textMuted text-[11px] mb-1">Topic</Text>
        <TextInput
          value={topicDisplay}
          onChangeText={(t) => { setTopicDisplay(t); setTopicKey(''); }}
          placeholder="Type or pick a topic"
          placeholderTextColor="#9AA3B0"
          className="bg-bg rounded-lg px-3 py-2.5 border border-border mb-2"
          style={{ color: '#1A1A2E' }}
        />
        {!!suggestions.length && (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6 }} className="mb-3">
            {suggestions.map((s) => (
              <TouchableOpacity key={s.id} onPress={() => { setTopicDisplay(s.topic); setTopicKey(s.id); }} className="px-3 py-1.5 rounded-full border border-border bg-bg">
                <Text className="text-textSecondary text-xs">{s.topic}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}

        <Text className="text-textMuted text-[11px] mb-1">Score type</Text>
        <View className="flex-row gap-2 mb-3">
          {SCORE_TYPES.map((st) => {
            const active = scoreType === st;
            return (
              <TouchableOpacity key={st} onPress={() => setScoreType(st)} className="px-3 py-1.5 rounded-full border" style={{ backgroundColor: active ? '#00C896' : '#FFFFFF', borderColor: active ? '#00C896' : '#E4E7EC' }}>
                <Text className="text-xs font-semibold capitalize" style={{ color: active ? '#FFFFFF' : '#5B6472' }}>{st}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text className="text-textMuted text-[11px] mb-1">Alert when score reaches</Text>
        <View className="flex-row items-center gap-4 mb-3">
          <TouchableOpacity onPress={() => bump(-5)} className="w-9 h-9 rounded-full border border-border items-center justify-center">
            <Minus size={16} color="#5B6472" />
          </TouchableOpacity>
          <Text className="text-textPrimary text-2xl font-black w-12 text-center">{threshold}</Text>
          <TouchableOpacity onPress={() => bump(5)} className="w-9 h-9 rounded-full border border-border items-center justify-center">
            <Plus size={16} color="#5B6472" />
          </TouchableOpacity>
        </View>

        <View className="flex-row items-center justify-between py-1">
          <Text className="text-textSecondary text-sm">Push notification</Text>
          <Switch value={push} onValueChange={setPush} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
        </View>
        <View className="flex-row items-center justify-between py-1 mb-3">
          <Text className="text-textSecondary text-sm">Email</Text>
          <Switch value={email} onValueChange={setEmail} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
        </View>

        <Button onPress={create} loading={creating} disabled={!topicDisplay.trim()} size="lg">
          Create Alert
        </Button>
      </View>

      <Disclaimer />
    </Screen>
  );
}
