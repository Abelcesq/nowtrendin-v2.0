import { Tabs } from 'expo-router';
import { useEffect } from 'react';
import { Home, User } from 'lucide-react-native';
import { useAuthStore } from '../../store/auth.store';
import { usePrefsStore } from '../../store/prefs.store';
import { canAccess, TierID } from '../../constants/tiers';
import { TOOLBAR_CANDIDATES, ToolbarItem } from '../../constants/toolbar';

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const toolbar = usePrefsStore((s) => s.toolbar);
  const load = usePrefsStore((s) => s.load);
  useEffect(() => { load(); }, []);

  // Home and Profile are fixed; the 3 middle slots are user-customizable
  // (Edit Toolbar Icons). Resolve the chosen items in the user's order, skipping
  // any the tier isn't entitled to; the rest of the pool is registered but hidden.
  const allowed = (c: ToolbarItem) => !c.feature || canAccess(tier, c.feature);
  const selected = toolbar
    .map((k) => TOOLBAR_CANDIDATES.find((c) => c.key === k))
    .filter((c): c is ToolbarItem => !!c && allowed(c));
  const selectedKeys = new Set(selected.map((c) => c.key));
  const hidden = TOOLBAR_CANDIDATES.filter((c) => !selectedKeys.has(c.key));

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

      {/* User-chosen middle tabs, in order */}
      {selected.map((c) => {
        const Icon = c.icon;
        return (
          <Tabs.Screen
            key={c.route}
            name={c.route}
            options={{ title: c.label, tabBarIcon: ({ color }) => <Icon size={20} color={color} /> }}
          />
        );
      })}

      {/* Unselected pool members — registered but hidden from the bar */}
      {hidden.map((c) => (
        <Tabs.Screen key={c.route} name={c.route} options={{ href: null }} />
      ))}

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
