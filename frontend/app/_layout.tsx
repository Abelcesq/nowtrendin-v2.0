import '../global.css';
import { Stack } from 'expo-router';
import { Platform, View } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

export default function RootLayout() {
  const stack = (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#F4F5F7' } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="(auth)" />
      <Stack.Screen name="(app)" />
    </Stack>
  );

  return (
    <GestureHandlerRootView style={{ flex: 1, backgroundColor: Platform.OS === 'web' ? '#D6D9DE' : '#F4F5F7' }}>
      <QueryClientProvider client={queryClient}>
        <SafeAreaProvider>
          {Platform.OS === 'web' ? (
            // On desktop web, render the app in a centered phone-width column
            // so the mobile layout isn't stretched across a wide browser.
            <View style={{ flex: 1, alignItems: 'center', backgroundColor: '#D6D9DE' }}>
              <View style={{ flex: 1, width: '100%', maxWidth: 480, backgroundColor: '#F4F5F7',
                shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 16, elevation: 4 }}>
                {stack}
              </View>
            </View>
          ) : stack}
        </SafeAreaProvider>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
