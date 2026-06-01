import { useRef, useState } from 'react';
import { View, Text, useWindowDimensions, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { TrendingUp, Activity, Building2 } from 'lucide-react-native';
import * as SecureStore from 'expo-secure-store';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';

const SLIDES = [
  {
    icon: TrendingUp,
    colour: '#00C896',
    title: "The world has data.\nIt doesn't have foresight.",
    titleColour: 'text-textPrimary',
    body: 'By the time Google Trends fires, the opportunity is already captured.',
  },
  {
    icon: Activity,
    colour: '#00C896',
    title: 'Introducing the\nGradient Score.',
    titleColour: 'text-primary',
    body: 'The only instrument that measures where human attention is moving before it arrives.',
  },
  {
    icon: Building2,
    colour: '#D4A017',
    title: 'Built for every\ndecision-maker.',
    titleColour: 'text-textPrimary',
    body: 'Consumer · Business · Enterprise. Three tiers. One engine. Your competitive edge.',
  },
];

export default function Onboarding() {
  const router = useRouter();
  const { width } = useWindowDimensions();
  const scrollRef = useRef<ScrollView>(null);
  const [index, setIndex] = useState(0);

  const finish = async () => {
    await SecureStore.setItemAsync('onboarding_seen', '1');
    router.replace('/login');
  };

  const next = () => {
    if (index < SLIDES.length - 1) {
      const ni = index + 1;
      scrollRef.current?.scrollTo({ x: ni * width, animated: true });
      setIndex(ni);
    } else {
      finish();
    }
  };

  return (
    <Screen padded={false}>
      <View className="flex-row justify-end px-5 pt-4">
        {index < SLIDES.length - 1 ? (
          <TouchableOpacity onPress={finish}>
            <Text className="text-textMuted text-sm">Skip</Text>
          </TouchableOpacity>
        ) : (
          <View className="h-5" />
        )}
      </View>

      <ScrollView
        ref={scrollRef}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(e) => setIndex(Math.round(e.nativeEvent.contentOffset.x / width))}
        className="flex-1"
      >
        {SLIDES.map((s, i) => {
          const Icon = s.icon;
          return (
            <View key={i} style={{ width }} className="flex-1 items-center justify-center px-8">
              <View className="w-20 h-20 rounded-3xl bg-surface items-center justify-center border border-border mb-8">
                <Icon size={40} color={s.colour} />
              </View>
              <Text className={`text-2xl font-bold text-center mb-4 ${s.titleColour}`}>{s.title}</Text>
              <Text className="text-base text-textSecondary text-center leading-6">{s.body}</Text>
            </View>
          );
        })}
      </ScrollView>

      <View className="px-8 pb-10">
        <View className="flex-row justify-center gap-2 mb-8">
          {SLIDES.map((_, i) => (
            <View
              key={i}
              className={`h-2 rounded-full ${i === index ? 'w-6 bg-primary' : 'w-2 bg-border'}`}
            />
          ))}
        </View>
        <Button size="lg" onPress={next}>
          {index === SLIDES.length - 1 ? 'Get Started' : 'Continue'}
        </Button>
        {index === SLIDES.length - 1 && (
          <Button variant="ghost" size="md" onPress={finish} className="mt-2">
            Sign in
          </Button>
        )}
      </View>
    </Screen>
  );
}
