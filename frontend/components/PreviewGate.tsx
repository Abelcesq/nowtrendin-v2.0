import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Lock, LogOut } from 'lucide-react-native';
import { useAuthStore } from '../store/auth.store';
import { logout } from '../lib/auth';
import { Logo } from './ui/Logo';

// Shared lock screen for the live enterprise-only WEB preview build
// (constants/preview.ts · EXPO_PUBLIC_ENTERPRISE_ONLY). Rendered wherever a
// non-Enterprise account would otherwise reach app content — the app tab layout
// and the membership self-select. The only way past it is signing into an account
// that is ALREADY provisioned Enterprise (tier set server-side), so a fresh signup
// cannot grant itself access. Never shown on the mobile build (flag unset).
export function EnterprisePreviewGate() {
  const router = useRouter();
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const signOut = async () => { await logout(); clearAuth(); router.replace('/login'); };
  return (
    <View className="flex-1 bg-bg items-center justify-center px-8">
      <Logo size={72} />
      <View className="w-11 h-11 rounded-full items-center justify-center mt-6 mb-4" style={{ backgroundColor: '#B1122614' }}>
        <Lock size={22} color="#B11226" />
      </View>
      <Text className="text-textPrimary text-2xl font-bold text-center">Enterprise preview</Text>
      <Text className="text-textSecondary text-base leading-6 text-center mt-2">
        This is a private testing build of Now TrendIn. Access is limited to current
        Enterprise accounts. Sign in with an Enterprise account to continue.
      </Text>
      <TouchableOpacity onPress={signOut} activeOpacity={0.8}
        className="flex-row items-center gap-2 mt-8 px-5 py-3 rounded-full" style={{ backgroundColor: '#16264A' }}>
        <LogOut size={16} color="#FFFFFF" />
        <Text className="text-white text-sm font-bold">Sign in with another account</Text>
      </TouchableOpacity>
    </View>
  );
}
