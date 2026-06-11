import { Tabs } from 'expo-router';
import { Home, Clock, Search, Bell, User } from 'lucide-react-native';
import { useAuthStore } from '../../store/auth.store';
import { canAccess, TierID } from '../../constants/tiers';

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const showSearch = canAccess(tier, 'canSearch'); // business + enterprise only

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E4E7EC',
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 6,
        },
        tabBarActiveTintColor: '#00C896',
        tabBarInactiveTintColor: '#9AA3B0',
        tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home', tabBarIcon: ({ color }) => <Home size={20} color={color} /> }} />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          href: showSearch ? '/search' : null,
          tabBarIcon: ({ color }) => <Search size={20} color={color} />,
        }}
      />
      <Tabs.Screen name="history" options={{ title: 'History', tabBarIcon: ({ color }) => <Clock size={20} color={color} /> }} />
      <Tabs.Screen name="alerts" options={{ title: 'Alerts', tabBarIcon: ({ color }) => <Bell size={20} color={color} /> }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarIcon: ({ color }) => <User size={20} color={color} /> }} />

      {/* Detail / focused routes live under (app) so they inherit the tab bar,
          but they must NOT appear AS tabs — href: null hides them from the bar. */}
      <Tabs.Screen name="category/[stage]" options={{ href: null }} />
      <Tabs.Screen name="market-category/[key]" options={{ href: null }} />
      <Tabs.Screen name="risk/[key]" options={{ href: null }} />
      <Tabs.Screen name="signal/[id]" options={{ href: null }} />
    </Tabs>
  );
}
