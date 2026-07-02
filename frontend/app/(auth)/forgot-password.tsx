import { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Mail, ChevronLeft, CheckCircle, KeyRound } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { requestPasswordReset, resetPassword } from '../../lib/auth';

export default function ForgotPassword() {
  const router = useRouter();
  const [step, setStep] = useState<'email' | 'reset' | 'done'>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const sendCode = async () => {
    setMsg(null);
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) return setMsg('Enter a valid email address.');
    setBusy(true);
    try {
      await requestPasswordReset(email.trim());
      setStep('reset');
      setCooldown(45);
    } catch {
      setMsg('Could not send the code. Try again.');
    } finally {
      setBusy(false);
    }
  };

  const submitReset = async () => {
    setMsg(null);
    if (password.length < 8) return setMsg('Password must be at least 8 characters.');
    if (password !== confirm) return setMsg("Passwords don't match.");
    setBusy(true);
    try {
      await resetPassword(email.trim(), code.trim(), password);
      setStep('done');
    } catch (err: any) {
      setMsg(err?.data?.detail ?? 'Could not reset password.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
        <ChevronLeft size={24} color="#8A8F9C" />
      </TouchableOpacity>

      {step === 'email' && (
        <View>
          <View className="w-14 h-14 rounded-2xl bg-card items-center justify-center mb-6">
            <Mail size={26} color="#2E7D5B" />
          </View>
          <Text className="text-textPrimary text-2xl font-bold mb-2">Forgot your password?</Text>
          <Text className="text-textMuted text-sm mb-8 leading-5">
            Enter your email and we'll send you a 6-digit reset code.
          </Text>
          <Input placeholder="Email address" value={email} onChangeText={setEmail} icon={<Mail size={18} color="#8A8F9C" />} keyboardType="email-address" />
          {msg && <Text className="text-error text-sm mb-3">{msg}</Text>}
          <Button onPress={sendCode} loading={busy} size="lg" className="mt-2">Send Reset Code</Button>
        </View>
      )}

      {step === 'reset' && (
        <View>
          <View className="w-14 h-14 rounded-2xl bg-card items-center justify-center mb-6">
            <KeyRound size={26} color="#2E7D5B" />
          </View>
          <Text className="text-textPrimary text-2xl font-bold mb-2">Enter your code</Text>
          <Text className="text-textMuted text-sm mb-6 leading-5">
            We sent a 6-digit code to {email}. Enter it with your new password.
          </Text>
          <Input placeholder="6-digit code" value={code} onChangeText={setCode} keyboardType="numeric" icon={<KeyRound size={18} color="#8A8F9C" />} />
          <Input placeholder="New password" value={password} onChangeText={setPassword} secureText icon={<KeyRound size={18} color="#8A8F9C" />} />
          <Input placeholder="Confirm new password" value={confirm} onChangeText={setConfirm} secureText icon={<KeyRound size={18} color="#8A8F9C" />} />
          {msg && <Text className="text-error text-sm mb-3">{msg}</Text>}
          <Button onPress={submitReset} loading={busy} size="lg">Reset Password</Button>
          <Button variant="secondary" size="lg" className="mt-3" disabled={cooldown > 0} onPress={sendCode}>
            {cooldown > 0 ? `Resend code (0:${cooldown.toString().padStart(2, '0')})` : 'Resend code'}
          </Button>
        </View>
      )}

      {step === 'done' && (
        <View>
          <View className="w-14 h-14 rounded-2xl bg-card items-center justify-center mb-6">
            <CheckCircle size={26} color="#2E7D5B" />
          </View>
          <Text className="text-primary text-2xl font-bold mb-2">Password updated</Text>
          <Text className="text-textMuted text-sm mb-8 leading-5">You can now sign in with your new password.</Text>
          <Button size="lg" onPress={() => router.replace('/login')}>Back to Sign In</Button>
        </View>
      )}

      <View className="flex-row justify-center mt-8">
        <Text className="text-textMuted text-sm">Back to </Text>
        <TouchableOpacity onPress={() => router.replace('/login')}>
          <Text className="text-primary text-sm font-semibold">Sign In</Text>
        </TouchableOpacity>
      </View>
    </Screen>
  );
}
