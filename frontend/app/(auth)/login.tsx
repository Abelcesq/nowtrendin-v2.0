import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, KeyRound, ChevronLeft } from 'lucide-react-native';
import { Logo } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/auth.store';
import { login as apiLogin } from '../../lib/auth';
import { useGoogleAuth } from '../../lib/useGoogleAuth';

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const { promptGoogle, googleBusy, googleError, ready: googleReady } = useGoogleAuth();
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      const { user, token } = await apiLogin(data.email, data.password);
      setUser(user, token);
      router.replace(user.tier ? '/(app)' : '/membership');
    } catch (err: any) {
      const msg = err?.data?.detail ?? 'Incorrect email or password';
      setError('root', { message: msg });
    }
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-6 self-start">
        <ChevronLeft size={24} color="#8A8F9C" />
      </TouchableOpacity>

      <View className="mb-6">
        <Logo size={56} />
      </View>

      <Text className="text-textPrimary text-3xl font-bold mb-1">Welcome back</Text>
      <Text className="text-textMuted text-base mb-8">Sign in to Now TrendIn</Text>

      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, value } }) => (
          <Input
            placeholder="Email address"
            value={value}
            onChangeText={onChange}
            error={errors.email?.message}
            icon={<Mail size={18} color="#8A8F9C" />}
            keyboardType="email-address"
          />
        )}
      />
      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, value } }) => (
          <Input
            placeholder="Password"
            value={value}
            onChangeText={onChange}
            error={errors.password?.message}
            icon={<KeyRound size={18} color="#8A8F9C" />}
            secureText
          />
        )}
      />

      <TouchableOpacity onPress={() => router.push('/forgot-password')} className="self-end mb-6 -mt-1">
        <Text className="text-primary text-sm font-medium">Forgot password?</Text>
      </TouchableOpacity>

      {errors.root && <Text className="text-error text-sm text-center mb-4">{errors.root.message}</Text>}

      <Button onPress={handleSubmit(onSubmit)} loading={isSubmitting} size="lg">
        Sign In
      </Button>

      <View className="flex-row items-center my-6">
        <View className="flex-1 h-px bg-border" />
        <Text className="text-textMuted text-sm mx-4">or</Text>
        <View className="flex-1 h-px bg-border" />
      </View>

      {googleError && <Text className="text-error text-sm text-center mb-3">{googleError}</Text>}

      <Button
        variant="secondary"
        size="lg"
        onPress={promptGoogle}
        loading={googleBusy}
        disabled={!googleReady || googleBusy}
      >
        Continue with Google
      </Button>

      <View className="flex-row justify-center mt-8">
        <Text className="text-textMuted text-sm">Don't have an account? </Text>
        <TouchableOpacity onPress={() => router.push('/signup')}>
          <Text className="text-primary text-sm font-semibold">Sign up</Text>
        </TouchableOpacity>
      </View>
    </Screen>
  );
}
