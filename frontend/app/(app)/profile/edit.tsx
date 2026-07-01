import { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, User as UserIcon, Mail, Phone, KeyRound, ShieldCheck, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { CountryCodePicker } from '../../../components/ui/CountryCodePicker';
import { splitPhone } from '../../../constants/countries';
import { useAuthStore } from '../../../store/auth.store';
import { updateProfile, changePassword, sendPhoneCode, verifyPhoneCode } from '../../../lib/auth';

export default function EditProfile() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);

  const initialPhone = splitPhone(user?.phone);
  const [name, setName] = useState(user?.name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [countryDial, setCountryDial] = useState(initialPhone.dial);
  const [localPhone, setLocalPhone] = useState(initialPhone.local);
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ ok: boolean; text: string } | null>(null);

  // Full E.164 number (country code + digits), or null if no number entered.
  const fullPhone = () => {
    const digits = localPhone.replace(/[^0-9]/g, '');
    return digits ? `${countryDial}${digits}` : null;
  };

  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [sending2fa, setSending2fa] = useState(false);
  const [verifying2fa, setVerifying2fa] = useState(false);
  const [twoFAMsg, setTwoFAMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [savingPw, setSavingPw] = useState(false);
  const [pwMsg, setPwMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const saveProfile = async () => {
    setProfileMsg(null);
    setSavingProfile(true);
    try {
      const updated = await updateProfile({ name: name.trim(), email: email.trim(), phone: fullPhone() });
      updateUser(updated);
      setProfileMsg({ ok: true, text: 'Profile updated.' });
    } catch (err: any) {
      const msg = err?.data?.email?.[0] ?? err?.data?.detail ?? 'Could not update profile.';
      setProfileMsg({ ok: false, text: msg });
    } finally {
      setSavingProfile(false);
    }
  };

  const requestCode = async () => {
    setTwoFAMsg(null);
    const full = fullPhone();
    if (!full) return setTwoFAMsg({ ok: false, text: 'Enter a phone number first.' });
    setSending2fa(true);
    try {
      await sendPhoneCode(full);
      setCodeSent(true);
      setTwoFAMsg({ ok: true, text: 'Code sent — check your phone.' });
    } catch (err: any) {
      setTwoFAMsg({ ok: false, text: err?.data?.detail ?? 'Could not send code.' });
    } finally {
      setSending2fa(false);
    }
  };

  const verifyCode = async () => {
    setTwoFAMsg(null);
    setVerifying2fa(true);
    try {
      const updated = await verifyPhoneCode(code.trim());
      updateUser(updated);
      setCodeSent(false);
      setCode('');
      setTwoFAMsg({ ok: true, text: 'Phone verified ✓' });
    } catch (err: any) {
      setTwoFAMsg({ ok: false, text: err?.data?.detail ?? 'Could not verify code.' });
    } finally {
      setVerifying2fa(false);
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
        <ChevronLeft size={22} color="#3C4663" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-3xl font-bold mb-6">Edit Profile</Text>

      {/* Account details */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Account details</Text>
      <Input placeholder="Full name" value={name} onChangeText={setName} icon={<UserIcon size={18} color="#8A8F9C" />} autoCapitalize="words" />
      <Input placeholder="Email address" value={email} onChangeText={setEmail} icon={<Mail size={18} color="#8A8F9C" />} keyboardType="email-address" />

      {/* Phone / 2FA */}
      <View className="flex-row items-center gap-2 mb-1 mt-1">
        <ShieldCheck size={14} color="#2E7D5B" />
        <Text className="text-textSecondary text-xs font-semibold">Phone (extra security)</Text>
        {user?.phone ? (
          <Text className="text-[12px] font-bold" style={{ color: user?.phoneVerified ? '#246B4A' : '#A8456A' }}>
            {user?.phoneVerified ? 'VERIFIED' : 'UNVERIFIED'}
          </Text>
        ) : null}
      </View>
      <View className="flex-row gap-2 mb-1">
        <CountryCodePicker dial={countryDial} onSelect={setCountryDial} />
        <View className="flex-1 flex-row items-center bg-card rounded-xl px-4" style={{ height: 50 }}>
          <Phone size={18} color="#8A8F9C" />
          <TextInput
            value={localPhone}
            onChangeText={setLocalPhone}
            placeholder="555 123 4567"
            placeholderTextColor="#9A9AA2"
            keyboardType="phone-pad"
            className="flex-1 ml-3 text-base"
            style={{ color: '#16264A' }}
          />
        </View>
      </View>
      <Text className="text-textMuted text-[12px] mb-3 mt-1">
        Pick your country code and enter your number, then verify it below for two-factor security.
      </Text>

      {profileMsg && (
        <View className="flex-row items-center gap-2 mb-3">
          {profileMsg.ok && <CheckCircle size={14} color="#2E7D5B" />}
          <Text className="text-sm" style={{ color: profileMsg.ok ? '#246B4A' : '#B11226' }}>{profileMsg.text}</Text>
        </View>
      )}

      <Button onPress={saveProfile} loading={savingProfile} size="lg">Save Changes</Button>

      {/* Two-factor authentication */}
      <View className="mt-6">
        <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Two-factor authentication</Text>
        {user?.phoneVerified ? (
          <View className="flex-row items-center gap-2">
            <CheckCircle size={16} color="#2E7D5B" />
            <Text className="text-textSecondary text-sm">Your phone is verified for two-factor security.</Text>
          </View>
        ) : (
          <>
            <Text className="text-textMuted text-[12px] mb-2">
              Verify your number to protect your account with SMS codes at sign-in.
            </Text>
            <Button variant="secondary" size="md" onPress={requestCode} loading={sending2fa}>
              {codeSent ? 'Resend code' : 'Send verification code'}
            </Button>
            {codeSent && (
              <View className="mt-3">
                <Input
                  placeholder="6-digit code"
                  value={code}
                  onChangeText={setCode}
                  keyboardType="numeric"
                  icon={<KeyRound size={18} color="#8A8F9C" />}
                />
                <Button size="md" onPress={verifyCode} loading={verifying2fa}>Verify code</Button>
              </View>
            )}
          </>
        )}
        {twoFAMsg && (
          <View className="flex-row items-center gap-2 mt-3">
            {twoFAMsg.ok && <CheckCircle size={14} color="#2E7D5B" />}
            <Text className="text-sm" style={{ color: twoFAMsg.ok ? '#246B4A' : '#B11226' }}>{twoFAMsg.text}</Text>
          </View>
        )}
      </View>

      <View className="h-px bg-border my-7" />

      {/* Change password */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Change password</Text>
      <Input placeholder="Current password" value={current} onChangeText={setCurrent} icon={<KeyRound size={18} color="#8A8F9C" />} secureText />
      <Input placeholder="New password" value={next} onChangeText={setNext} icon={<KeyRound size={18} color="#8A8F9C" />} secureText />
      <Input placeholder="Confirm new password" value={confirm} onChangeText={setConfirm} icon={<KeyRound size={18} color="#8A8F9C" />} secureText />

      {pwMsg && (
        <View className="flex-row items-center gap-2 mb-3">
          {pwMsg.ok && <CheckCircle size={14} color="#2E7D5B" />}
          <Text className="text-sm" style={{ color: pwMsg.ok ? '#246B4A' : '#B11226' }}>{pwMsg.text}</Text>
        </View>
      )}

      <Button onPress={savePassword} loading={savingPw} variant="secondary" size="lg">Update Password</Button>
      <View className="h-6" />
    </Screen>
  );
}
