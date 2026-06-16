import { View, Text, TouchableOpacity, Linking } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, ChevronRight, FileText, ShieldCheck, AlertTriangle } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';

// Canonical legal documents — hosted on the marketing site so there is ONE
// source of truth across web, desktop, and mobile.
const LEGAL = [
  {
    key: 'terms',
    title: 'Terms & Conditions',
    subtitle: 'View our terms of service',
    url: 'https://nowtrendin.com/terms/',
    Icon: FileText,
  },
  {
    key: 'privacy',
    title: 'Privacy Policy',
    subtitle: 'How we handle your data',
    url: 'https://nowtrendin.com/privacy/',
    Icon: ShieldCheck,
  },
  {
    key: 'disclaimer',
    title: 'Disclaimer',
    subtitle: 'Important information and limitations',
    url: 'https://nowtrendin.com/disclaimer/',
    Icon: AlertTriangle,
  },
] as const;

export default function ProfileLegal() {
  const router = useRouter();

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>

      <View className="pb-4">
        <Text className="text-textPrimary text-3xl font-bold mb-1">Legal</Text>
        <Text className="text-textMuted text-base">View our legal documents</Text>
      </View>

      {LEGAL.map(({ key, title, subtitle, url, Icon }) => (
        <TouchableOpacity
          key={key}
          onPress={() => Linking.openURL(url)}
          activeOpacity={0.7}
          className="bg-surface rounded-2xl border border-border p-4 mb-3 flex-row items-center"
        >
          <View className="w-12 h-12 rounded-xl items-center justify-center mr-3.5" style={{ backgroundColor: '#00C8961A' }}>
            <Icon size={22} color="#00C896" />
          </View>
          <View className="flex-1">
            <Text className="text-textPrimary text-lg font-bold">{title}</Text>
            <Text className="text-textMuted text-sm mt-0.5">{subtitle}</Text>
          </View>
          <ChevronRight size={20} color="#94A3B8" />
        </TouchableOpacity>
      ))}
    </Screen>
  );
}
