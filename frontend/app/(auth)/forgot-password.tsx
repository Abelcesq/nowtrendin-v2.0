import { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Linking } from 'react-native';
import { useRouter } from 'expo-router';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, ChevronLeft, CheckCircle } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

const schema = z.object({ email: z.string().email('Enter a valid email address') });
type FormData = z.infer<typeof schema>;

export default function ForgotPassword() {
  const router = useRouter();
  const [sent, setSent] = useState(false);
  const [sentEmail, setSentEmail] = useState('');
  const [cooldown, setCooldown] = useState(0);

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const onSubmit = async (data: FormData) => {
    await new Promise((r) => setTimeout(r, 600)); // mock send
    setSentEmail(data.email);
    setSent(true);
    setCooldown(45);
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
        <ChevronLeft size={24} color="#94A3B8" />
      </TouchableOpacity>

      {!sent ? (
        <View>
          <View className="w-14 h-14 rounded-2xl bg-surface items-center justify-center border border-border mb-6">
            <Mail size={26} color="#00C896" />
          </View>
          <Text className="text-textPrimary text-2xl font-bold mb-2">Forgot your password?</Text>
          <Text className="text-textMuted text-sm mb-8 leading-5">
            No problem. Enter your email and we'll send you a reset link.
          </Text>

          <Controller
            control={control}
            name="email"
            render={({ field: { onChange, value } }) => (
              <Input placeholder="Email address" value={value} onChangeText={onChange} error={errors.email?.message} icon={<Mail size={18} color="#94A3B8" />} keyboardType="email-address" />
            )}
          />

          <Button onPress={handleSubmit(onSubmit)} loading={isSubmitting} size="lg" className="mt-2">
            Send Reset Link
          </Button>

          <View className="flex-row justify-center mt-8">
            <Text className="text-textMuted text-sm">Back to </Text>
            <TouchableOpacity onPress={() => router.replace('/login')}>
              <Text className="text-primary text-sm font-semibold">Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View>
          <View className="w-14 h-14 rounded-2xl bg-surface items-center justify-center border border-border mb-6">
            <CheckCircle size={26} color="#00C896" />
          </View>
          <Text className="text-primary text-2xl font-bold mb-2">Email sent!</Text>
          <Text className="text-textMuted text-sm mb-8 leading-5">
            We sent a reset link to {sentEmail}. Check your inbox.
          </Text>

          <Button size="lg" onPress={() => Linking.openURL('mailto:')}>
            Open Email App
          </Button>

          <Button
            variant="secondary"
            size="lg"
            className="mt-3"
            disabled={cooldown > 0}
            onPress={() => setCooldown(45)}
          >
            {cooldown > 0 ? `Resend (in 0:${cooldown.toString().padStart(2, '0')})` : 'Resend link'}
          </Button>

          <View className="flex-row justify-center mt-8">
            <Text className="text-textMuted text-sm">Back to </Text>
            <TouchableOpacity onPress={() => router.replace('/login')}>
              <Text className="text-primary text-sm font-semibold">Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </Screen>
  );
}
