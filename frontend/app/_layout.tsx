import '../global.css';
import { Stack } from 'expo-router';
import { View, Text as RNText, TextInput as RNTextInput } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useFonts,
  PlusJakartaSans_400Regular,
  PlusJakartaSans_500Medium,
  PlusJakartaSans_600SemiBold,
  PlusJakartaSans_700Bold,
  PlusJakartaSans_800ExtraBold,
} from '@expo-google-fonts/plus-jakarta-sans';

const queryClient = new QueryClient();

// Plus Jakarta Sans is the design's type family. Apply it as the DEFAULT font for
// every Text / TextInput in the app. Any component that sets its own fontFamily
// still wins, because props.style overrides defaultProps.style — so this is a safe,
// non-destructive global default. Weight (font-bold etc.) renders via fontWeight.
const FONT = 'PlusJakartaSans_400Regular';
function applyDefaultFont(Comp: any) {
  Comp.defaultProps = Comp.defaultProps || {};
  Comp.defaultProps.style = [{ fontFamily: FONT }, Comp.defaultProps.style];
}
applyDefaultFont(RNText);
applyDefaultFont(RNTextInput);

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    PlusJakartaSans_400Regular,
    PlusJakartaSans_500Medium,
    PlusJakartaSans_600SemiBold,
    PlusJakartaSans_700Bold,
    PlusJakartaSans_800ExtraBold,
  });

  // Briefly hold render until the font is ready (loads from the bundled package,
  // no network). If it ever errors, fall through and render with the system font.
  if (!fontsLoaded && !fontError) return null;

  const stack = (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#FFFFFF' } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="(auth)" />
      <Stack.Screen name="(app)" />
    </Stack>
  );

  return (
    <GestureHandlerRootView style={{ flex: 1, backgroundColor: '#FFFFFF' }}>
      <QueryClientProvider client={queryClient}>
        <SafeAreaProvider>
          {/* Full-bleed, edge-to-edge content on every device/orientation (phone
              portrait/landscape + iPad). Content still respects the safe-area
              insets (notch/home indicator) via each screen's SafeAreaView. */}
          <View style={{ flex: 1, backgroundColor: '#FFFFFF' }}>
            {stack}
          </View>
        </SafeAreaProvider>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
