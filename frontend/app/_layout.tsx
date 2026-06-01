import '../global.css';
import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function RootLayout() {
  useEffect(() => {}, []);
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#F4F5F7' } }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(app)" />
          <Stack.Screen name="signal/[id]" options={{ animation: 'slide_from_right' }} />
        </Stack>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
