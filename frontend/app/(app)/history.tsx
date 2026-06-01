import { View, Text } from 'react-native';
import { Clock } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';

export default function History() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const window = tier === 'enterprise' ? 'Live + all history' : tier === 'business' ? '1h+ data' : '12h+ data';

  return (
    <Screen scroll>
      <View className="flex-row items-center justify-between pt-4 mb-4">
        <Text className="text-textPrimary text-2xl font-bold">History</Text>
        <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ backgroundColor: `${cfg.colour}20` }}>
          <Clock size={12} color={cfg.colour} />
          <Text style={{ color: cfg.colour }} className="text-xs font-bold">{window}</Text>
        </View>
      </View>

      {['14h ago', '13h ago', '12h ago', '36h ago'].map((age, i) => (
        <View key={i} className="bg-surface rounded-xl p-4 mb-3 border border-border">
          <View className="flex-row items-center justify-between">
            <Text className="text-textPrimary font-semibold">{['agentic coding', 'mcp servers', 'rag pipelines', 'vector dbs'][i]}</Text>
            <Text className="text-primary font-black text-xl">{[87, 72, 65, 58][i]}</Text>
          </View>
          <Text className="text-textMuted text-xs mt-1">{age}</Text>
        </View>
      ))}
    </Screen>
  );
}
