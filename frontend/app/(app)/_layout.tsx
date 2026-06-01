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
          backgroundColor: '#111827',
          borderTopColor: '#1E2D3D',
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 6,
        },
        tabBarActiveTintColor: '#00C896',
        tabBarInactiveTintColor: '#475569',
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
    </Tabs>
  );
}
