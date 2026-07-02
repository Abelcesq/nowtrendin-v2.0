import { Tabs } from 'expo-router';
import { useEffect } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Home, User } from 'lucide-react-native';
import { useAuthStore } from '../../store/auth.store';
import { usePrefsStore } from '../../store/prefs.store';
import { canAccess, TierID } from '../../constants/tiers';
import { TOOLBAR_CANDIDATES, ToolbarItem } from '../../constants/toolbar';
import { ENTERPRISE_ONLY } from '../../constants/preview';
import { EnterprisePreviewGate } from '../../components/PreviewGate';

// Fully custom tab bar — we own the layout so labels can never be clipped by the
// navigator's internal sizing. Icons + labels are stacked in a flex row with
// explicit safe-area bottom padding.
function NowTabBar({ state, descriptors, navigation }: any) {
  const insets = useSafeAreaInsets();
  const bottomPad = insets.bottom > 0 ? insets.bottom : 12;

  return (
    <View
      style={{
        flexDirection: 'row',
        backgroundColor: '#FFFFFF',
        borderTopWidth: 1,
        borderTopColor: '#ECECEC',
        paddingTop: 9,
        paddingBottom: bottomPad,
      }}
    >
      {state.routes.map((route: any, index: number) => {
        const { options } = descriptors[route.key];
        // Only real tabs are given a tabBarIcon; the hidden routes (focused
        // detail pages + the unselected toolbar pool) have none, so skip them.
        if (!options.tabBarIcon) return null;

        const label = options.title ?? route.name;
        const focused = state.index === index;
        const color = focused ? '#B11226' : '#9A9AA2';

        const onPress = () => {
          const event = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true });
          if (!focused && !event.defaultPrevented) navigation.navigate(route.name);
        };

        return (
          <TouchableOpacity
            key={route.key}
            accessibilityRole="button"
            accessibilityState={focused ? { selected: true } : {}}
            onPress={onPress}
            activeOpacity={0.7}
            style={{ flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 2 }}
          >
            {options.tabBarIcon ? options.tabBarIcon({ focused, color, size: 22 }) : null}
            <Text style={{ fontSize: 12, fontWeight: '700', color, marginTop: 4 }}>{label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const toolbar = usePrefsStore((s) => s.toolbar);
  const load = usePrefsStore((s) => s.load);
  useEffect(() => { load(); }, []);

  // Hard gate for the enterprise-only preview build — no app screen mounts for a
  // non-Enterprise account (defense in depth: the backend already tier-gates data).
  if (ENTERPRISE_ONLY && user && tier !== 'enterprise') {
    return <EnterprisePreviewGate />;
  }

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
      tabBar={(props) => <NowTabBar {...props} />}
      screenOptions={{ headerShown: false }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home', tabBarIcon: ({ color }) => <Home size={22} color={color} /> }} />

      {/* User-chosen middle tabs, in order */}
      {selected.map((c) => {
        const Icon = c.icon;
        return (
          <Tabs.Screen
            key={c.route}
            name={c.route}
            options={{ title: c.label, tabBarIcon: ({ color }: any) => <Icon size={22} color={color} /> }}
          />
        );
      })}

      {/* Unselected pool members — registered but hidden from the bar */}
      {hidden.map((c) => (
        <Tabs.Screen key={c.route} name={c.route} options={{ href: null }} />
      ))}

      <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarIcon: ({ color }) => <User size={22} color={color} /> }} />

      {/* Detail / focused routes live under (app) so they inherit the tab bar,
          but they must NOT appear AS tabs — href: null hides them from the bar. */}
      <Tabs.Screen name="category/[stage]" options={{ href: null }} />
      <Tabs.Screen name="market-category/[key]" options={{ href: null }} />
      <Tabs.Screen name="risk/[key]" options={{ href: null }} />
      <Tabs.Screen name="signal/[id]" options={{ href: null }} />
    </Tabs>
  );
}
