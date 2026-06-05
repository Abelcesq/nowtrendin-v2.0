import { Stack } from 'expo-router';

export default function ProfileLayout() {
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#F4F5F7' } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="membership" />
      <Stack.Screen name="edit" />
      <Stack.Screen name="notifications" />
      <Stack.Screen name="accuracy" />
    </Stack>
  );
}
