import { useState } from 'react';
import { View, Text, TouchableOpacity, Switch } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { useAuthStore } from '../../../store/auth.store';
import { updateNotifyPrefs } from '../../../lib/auth';

function PrefRow({ label, desc, value, onChange }: { label: string; desc: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <View className="flex-row items-center justify-between bg-surface rounded-xl border border-border p-4 mb-3">
      <View className="flex-1 pr-3">
        <Text className="text-textPrimary text-base font-semibold">{label}</Text>
        <Text className="text-textMuted text-xs mt-0.5">{desc}</Text>
      </View>
      <Switch value={value} onValueChange={onChange} trackColor={{ true: '#00C896', false: '#E4E7EC' }} thumbColor="#FFFFFF" />
    </View>
  );
}

export default function Notifications() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);

  const [email, setEmail] = useState(user?.notifyEmail ?? true);
  const [push, setPush] = useState(user?.notifyPush ?? true);
  const [saved, setSaved] = useState(false);

  const persist = async (next: { notifyEmail?: boolean; notifyPush?: boolean }) => {
    setSaved(false);
    try {
      const updated = await updateNotifyPrefs(next);
      updateUser(updated);
      setSaved(true);
    } catch {
      /* keep optimistic UI */
    }
  };

  const onEmail = (v: boolean) => { setEmail(v); persist({ notifyEmail: v }); };
  const onPush = (v: boolean) => { setPush(v); persist({ notifyPush: v }); };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-3xl font-bold mb-6">Notifications</Text>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Delivery channels</Text>
      <PrefRow label="Email" desc="Trend alerts and account updates by email." value={email} onChange={onEmail} />
      <PrefRow label="Push notifications" desc="Real-time alerts on this device." value={push} onChange={onPush} />

      {saved && (
        <View className="flex-row items-center gap-2 mt-1">
          <CheckCircle size={14} color="#00C896" />
          <Text className="text-sm" style={{ color: '#009970' }}>Preferences saved.</Text>
        </View>
      )}

      <Text className="text-textMuted text-[11px] mt-4">
        These control how trend alerts you create are delivered. Manage individual alerts on the Alerts tab.
      </Text>
    </Screen>
  );
}
