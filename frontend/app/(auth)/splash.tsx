import { useEffect } from 'react';
import { View, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { FullLogo } from '../../components/ui/Logo';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withDelay,
} from 'react-native-reanimated';
import * as SecureStore from '../../lib/storage';
import { fetchMe, logout } from '../../lib/auth';
import { useAuthStore } from '../../store/auth.store';

export default function Splash() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);

  const logoScale = useSharedValue(0.7);
  const logoOpacity = useSharedValue(0);
  const textOpacity = useSharedValue(0);
  const tagOpacity = useSharedValue(0);

  const logoStyle = useAnimatedStyle(() => ({
    transform: [{ scale: logoScale.value }],
    opacity: logoOpacity.value,
  }));
  const textStyle = useAnimatedStyle(() => ({ opacity: textOpacity.value }));
  const tagStyle = useAnimatedStyle(() => ({ opacity: tagOpacity.value }));

  useEffect(() => {
    logoScale.value = withTiming(1, { duration: 600 });
    logoOpacity.value = withTiming(1, { duration: 600 });
    textOpacity.value = withDelay(300, withTiming(1, { duration: 400 }));
    tagOpacity.value = withDelay(600, withTiming(1, { duration: 400 }));

    const go = async () => {
      await new Promise((r) => setTimeout(r, 2000));
      const token = await SecureStore.getItemAsync('access_token');
      if (token) {
        // Validate the token against the backend and hydrate the user.
        const user = await fetchMe();
        if (user) {
          setUser(user, token);
          router.replace(user.tier ? '/(app)' : '/membership');
          return;
        }
        await logout(); // token expired/invalid
      }
      const seen = await SecureStore.getItemAsync('onboarding_seen');
      router.replace(seen ? '/login' : '/onboarding');
    };
    go();
  }, []);

  return (
    <View className="flex-1 bg-bg items-center justify-center">
      <Animated.View style={logoStyle} className="items-center">
        <FullLogo width={260} />
      </Animated.View>

      <Animated.View style={tagStyle} className="mt-1">
        <Text className="text-textMuted text-xs tracking-widest uppercase">
          Attention Intelligence
        </Text>
      </Animated.View>
    </View>
  );
}
