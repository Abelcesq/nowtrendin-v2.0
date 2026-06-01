import { useEffect } from 'react';
import { View, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { Flame } from 'lucide-react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withDelay,
} from 'react-native-reanimated';
import * as SecureStore from 'expo-secure-store';

export default function Splash() {
  const router = useRouter();

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
        router.replace('/(app)');
        return;
      }
      const seen = await SecureStore.getItemAsync('onboarding_seen');
      router.replace(seen ? '/login' : '/onboarding');
    };
    go();
  }, []);

  return (
    <View className="flex-1 bg-bg items-center justify-center">
      <Animated.View style={logoStyle} className="items-center">
        <View className="w-24 h-24 rounded-3xl bg-surface items-center justify-center border border-border">
          <Flame size={48} color="#00C896" />
        </View>
      </Animated.View>

      <Animated.View style={textStyle} className="mt-6 items-center">
        <Text className="text-textPrimary text-3xl font-black">
          Now <Text className="text-primary">TrendIn</Text>
        </Text>
      </Animated.View>

      <Animated.View style={tagStyle} className="mt-2">
        <Text className="text-textMuted text-xs tracking-widest uppercase">
          Attention Intelligence
        </Text>
      </Animated.View>
    </View>
  );
}
