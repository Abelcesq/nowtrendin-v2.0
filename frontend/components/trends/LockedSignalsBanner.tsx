import React from 'react';
import { View, Text } from 'react-native';
import { Lock } from 'lucide-react-native';
import { useRouter } from 'expo-router';
import { Button } from '../ui/Button';
import { TIERS, TierID } from '../../constants/tiers';
import { nextTier } from '../../lib/signals';

// Shows how many fresher signals are gated for this tier + an upgrade CTA.
export function LockedSignalsBanner({ tier, lockedCount }: { tier: TierID; lockedCount: number }) {
  const router = useRouter();
  if (lockedCount <= 0) return null;

  const next = nextTier(tier);
  if (!next) return null;

  const cfg = TIERS[next];
  const window = next === 'enterprise' ? 'real-time live' : '1h+';

  return (
    <View
      className="rounded-xl p-5 mb-3 border items-center"
      style={{ borderColor: cfg.colour, backgroundColor: `${cfg.colour}10` }}
    >
      <View className="w-11 h-11 rounded-full items-center justify-center mb-3" style={{ backgroundColor: `${cfg.colour}20` }}>
        <Lock size={20} color={cfg.colour} />
      </View>
      <Text className="text-textPrimary font-bold text-base text-center">
        {lockedCount} newer signal{lockedCount > 1 ? 's' : ''} hidden
      </Text>
      <Text className="text-textMuted text-sm text-center mt-1 mb-4">
        Upgrade to {cfg.name} to access {window} data
      </Text>
      <Button variant={next} size="sm" fullWidth={false} onPress={() => router.push('/membership')}>
        {`Upgrade — $${cfg.price.toLocaleString()}/mo`}
      </Button>
    </View>
  );
}
