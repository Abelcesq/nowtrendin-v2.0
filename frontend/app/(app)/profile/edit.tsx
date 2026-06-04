import { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, User as UserIcon, Mail, Phone, KeyRound, ShieldCheck, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useAuthStore } from '../../../store/auth.store';
import { updateProfile, changePassword } from '../../../lib/auth';

export default function EditProfile() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);

  const [name, setName] = useState(user?.name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [phone, setPhone] = useState(user?.phone ?? '');
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [savingPw, setSavingPw] = useState(false);
  const [pwMsg, setPwMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const saveProfile = async () => {
    setProfileMsg(null);
    setSavingProfile(true);
    try {
      const updated = await updateProfile({ name: name.trim(), email: email.trim(), phone: phone.trim() || null });
      updateUser(updated);
      setProfileMsg({ ok: true, text: 'Profile updated.' });
    } catch (err: any) {
      const msg = err?.data?.email?.[0] ?? err?.data?.detail ?? 'Could not update profile.';
      setProfileMsg({ ok: false, text: msg });
    } finally {
      setSavingProfile(false);
    }
  };

  const savePassword = async () => {
    setPwMsg(null);
    if (next.length < 8) return setPwMsg({ ok: false, text: 'New password must be at least 8 characters.' });
    if (next !== confirm) return setPwMsg({ ok: false, text: "Passwords don't match." });
    setSavingPw(true);
    try {
      await changePassword(current, next);
      setCurrent(''); setNext(''); setConfirm('');
      setPwMsg({ ok: true, text: 'Password updated.' });
    } catch (err: any) {
      setPwMsg({ ok: false, text: err?.data?.detail ?? 'Could not change password.' });
    } finally {
      setSavingPw(false);
    }
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-3xl font-bold mb-6">Edit Profile</Text>

      {/* Account details */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Account details</Text>
      <Input placeholder="Full name" value={name} onChangeText={setName} icon={<UserIcon size={18} color="#94A3B8" />} autoCapitalize="words" />
      <Input placeholder="Email address" value={email} onChangeText={setEmail} icon={<Mail size={18} color="#94A3B8" />} keyboardType="email-address" />

      {/* Phone / 2FA */}
      <View className="flex-row items-center gap-2 mb-1 mt-1">
        <ShieldCheck size={14} color="#00C896" />
        <Text className="text-textSecondary text-xs font-semibold">Phone (extra security)</Text>
        {user?.phone ? (
          <Text className="text-[10px] font-bold" style={{ color: user?.phoneVerified ? '#009970' : '#D4A017' }}>
            {user?.phoneVerified ? 'VERIFIED' : 'UNVERIFIED'}
          </Text>
        ) : null}
      </View>
      <Input placeholder="Phone number (e.g. +1 555 123 4567)" value={phone ?? ''} onChangeText={setPhone} icon={<Phone size={18} color="#94A3B8" />} keyboardType="default" />
      <Text className="text-textMuted text-[11px] -mt-2 mb-3">
        Used for two-factor authentication. SMS verification is coming soon — until then your number is stored for account recovery.
      </Text>

      {profileMsg && (
        <View className="flex-row items-center gap-2 mb-3">
          {profileMsg.ok && <CheckCircle size={14} color="#00C896" />}
          <Text className="text-sm" style={{ color: profileMsg.ok ? '#009970' : '#DC2626' }}>{profileMsg.text}</Text>
        </View>
      )}

      <Button onPress={saveProfile} loading={savingProfile} size="lg">Save Changes</Button>

      <View className="h-px bg-border my-7" />

      {/* Change password */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Change password</Text>
      <Input placeholder="Current password" value={current} onChangeText={setCurrent} icon={<KeyRound size={18} color="#94A3B8" />} secureText />
      <Input placeholder="New password" value={next} onChangeText={setNext} icon={<KeyRound size={18} color="#94A3B8" />} secureText />
      <Input placeholder="Confirm new password" value={confirm} onChangeText={setConfirm} icon={<KeyRound size={18} color="#94A3B8" />} secureText />

      {pwMsg && (
        <View className="flex-row items-center gap-2 mb-3">
          {pwMsg.ok && <CheckCircle size={14} color="#00C896" />}
          <Text className="text-sm" style={{ color: pwMsg.ok ? '#009970' : '#DC2626' }}>{pwMsg.text}</Text>
        </View>
      )}

      <Button onPress={savePassword} loading={savingPw} variant="secondary" size="lg">Update Password</Button>
      <View className="h-6" />
    </Screen>
  );
}
