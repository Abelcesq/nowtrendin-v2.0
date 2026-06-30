import { Stack } from 'expo-router';

export default function ProfileLayout() {
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#FFFFFF' } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="membership" />
      <Stack.Screen name="edit" />
      <Stack.Screen name="notifications" />
      <Stack.Screen name="accuracy" />
      <Stack.Screen name="watchlists" />
      <Stack.Screen name="favorites" />
      <Stack.Screen name="methodology" />
      <Stack.Screen name="billing" />
      <Stack.Screen name="edit-toolbar" />
      <Stack.Screen name="legal" />
    </Stack>
  );
}
