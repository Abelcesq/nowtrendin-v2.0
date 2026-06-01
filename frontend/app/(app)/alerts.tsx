import { View, Text } from 'react-native';
import { Bell, Plus } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';

export default function Alerts() {
  return (
    <Screen scroll>
      <View className="flex-row items-center justify-between pt-4 mb-4">
        <Text className="text-textPrimary text-2xl font-bold">Alerts</Text>
        <Button variant="secondary" size="sm" fullWidth={false} icon={<Plus size={16} color="#00C896" />}>
          New
        </Button>
      </View>

      {[
        { topic: 'agentic coding', threshold: 85, on: true, channels: 'Email + Push' },
        { topic: 'mcp', threshold: 70, on: false, channels: 'Email only' },
      ].map((a, i) => (
        <View key={i} className="bg-surface rounded-xl p-4 mb-3 border border-border flex-row items-center justify-between">
          <View className="flex-row items-center gap-3 flex-1">
            <Bell size={18} color="#00C896" />
            <View className="flex-1">
              <Text className="text-textPrimary font-semibold">{a.topic}</Text>
              <Text className="text-textMuted text-xs mt-0.5">Score ≥ {a.threshold} · {a.channels}</Text>
            </View>
          </View>
          <Text className={`text-xs font-bold ${a.on ? 'text-primary' : 'text-textMuted'}`}>
            {a.on ? 'ON' : 'OFF'}
          </Text>
        </View>
      ))}
    </Screen>
  );
}
