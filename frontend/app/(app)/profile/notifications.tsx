import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Switch } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { useAuthStore } from '../../../store/auth.store';
import { updateNotifyPrefs, sendPhoneCode, verifyPhoneCode } from '../../../lib/auth';

function PrefRow({ label, desc, value, onChange, disabled }: { label: string; desc: string; value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <View className="flex-row items-center justify-between bg-card rounded-xl p-4 mb-3" style={disabled ? { opacity: 0.55 } : undefined}>
      <View className="flex-1 pr-3">
        <Text className="text-textPrimary text-base font-semibold">{label}</Text>
        <Text className="text-textMuted text-xs mt-0.5">{desc}</Text>
      </View>
      <Switch value={value} onValueChange={onChange} disabled={disabled} trackColor={{ true: '#2E7D5B', false: '#ECECEC' }} thumbColor="#FFFFFF" />
    </View>
  );
}

export default function Notifications() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);

  const [email, setEmail] = useState(user?.notifyEmail ?? true);
  const [push, setPush] = useState(user?.notifyPush ?? true);
  const [sms, setSms] = useState(user?.notifySms ?? false);
  const [saved, setSaved] = useState(false);

  // phone capture / verification
  const [phone, setPhone] = useState(user?.phone ?? '');
  const [verified, setVerified] = useState(user?.phoneVerified ?? false);
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const persist = async (next: { notifyEmail?: boolean; notifyPush?: boolean; notifySms?: boolean }) => {
    setSaved(false);
    try { const updated = await updateNotifyPrefs(next); updateUser(updated); setSaved(true); } catch { /* keep optimistic */ }
  };
  const onEmail = (v: boolean) => { setEmail(v); persist({ notifyEmail: v }); };
  const onPush = (v: boolean) => { setPush(v); persist({ notifyPush: v }); };
  const onSms = (v: boolean) => {
    if (v && !verified) { setMsg({ ok: false, text: 'Verify a phone number below to enable text alerts.' }); return; }
    setSms(v); persist({ notifySms: v });
  };

  const sendCode = async () => {
    setMsg(null);
    if (phone.trim().length < 7) { setMsg({ ok: false, text: 'Enter a valid phone number with country code.' }); return; }
    try { const r = await sendPhoneCode(phone.trim()); setCodeSent(true); setMsg({ ok: true, text: r?.detail || 'Verification code sent.' }); }
    catch (e: any) { setMsg({ ok: false, text: e?.data?.detail ?? 'Could not send the code. SMS may not be configured yet.' }); }
  };
  const confirmCode = async () => {
    setMsg(null);
    try { const u = await verifyPhoneCode(code.trim()); updateUser(u); setVerified(true); setCodeSent(false); setCode(''); setMsg({ ok: true, text: 'Phone verified. You can now enable text alerts.' }); }
    catch (e: any) { setMsg({ ok: false, text: e?.data?.detail ?? 'Incorrect or expired code.' }); }
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#3C4663" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-3xl font-bold mb-6">Notifications</Text>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Delivery channels</Text>
      <PrefRow label="Email" desc="Trend alerts and account updates by email." value={email} onChange={onEmail} />
      <PrefRow label="Push notifications" desc="Real-time alerts on this device." value={push} onChange={onPush} />
      <PrefRow label="Text (SMS)" desc="Alerts to your verified phone. Standard rates may apply." value={sms} onChange={onSms} disabled={!verified} />

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2 mt-4">Cell phone for text alerts</Text>
      {verified ? (
        <View className="flex-row items-center bg-card rounded-xl p-4 mb-2">
          <Text className="text-textPrimary text-base font-semibold flex-1">{phone}</Text>
          <View className="flex-row items-center gap-1.5 px-2 py-1 rounded-full" style={{ backgroundColor: '#2E7D5B20' }}>
            <CheckCircle size={13} color="#2E7D5B" /><Text className="text-xs font-bold" style={{ color: '#246B4A' }}>VERIFIED</Text>
          </View>
          <TouchableOpacity onPress={() => { setVerified(false); setCodeSent(false); }} className="ml-3"><Text className="text-primary text-sm font-semibold">Change</Text></TouchableOpacity>
        </View>
      ) : (
        <View className="bg-card rounded-xl p-4 mb-2">
          <TextInput value={phone} onChangeText={setPhone} placeholder="+1 555 123 4567" placeholderTextColor="#9A9AA2" keyboardType="phone-pad" className="bg-bg rounded-lg px-3 py-2.5 mb-3" style={{ color: '#16264A' }} />
          {!codeSent ? (
            <TouchableOpacity onPress={sendCode} className="rounded-lg py-3 items-center" style={{ backgroundColor: '#2E7D5B' }}>
              <Text className="text-white font-semibold">Send verification code</Text>
            </TouchableOpacity>
          ) : (
            <View className="flex-row gap-2">
              <TextInput value={code} onChangeText={setCode} placeholder="6-digit code" placeholderTextColor="#9A9AA2" keyboardType="number-pad" className="flex-1 bg-bg rounded-lg px-3 py-2.5" style={{ color: '#16264A' }} />
              <TouchableOpacity onPress={confirmCode} className="rounded-lg py-3 px-5 items-center justify-center" style={{ backgroundColor: '#2E7D5B' }}><Text className="text-white font-semibold">Verify</Text></TouchableOpacity>
            </View>
          )}
        </View>
      )}

      {msg && (
        <View className="flex-row items-center gap-2 mt-1">
          <Text className="text-sm" style={{ color: msg.ok ? '#246B4A' : '#B11226' }}>{msg.ok ? '✓ ' : '• '}{msg.text}</Text>
        </View>
      )}
      {saved && !msg && (
        <View className="flex-row items-center gap-2 mt-1">
          <CheckCircle size={14} color="#2E7D5B" />
          <Text className="text-sm" style={{ color: '#246B4A' }}>Preferences saved.</Text>
        </View>
      )}

      <Text className="text-textMuted text-[11px] mt-4">
        These control how trend alerts you create are delivered. Manage individual alerts on the Alerts tab.
      </Text>
    </Screen>
  );
}
