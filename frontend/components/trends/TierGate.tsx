import React from 'react';
import { View, Text } from 'react-native';
import { Lock } from 'lucide-react-native';
import { useRouter } from 'expo-router';
import { Button } from '../ui/Button';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TIER_ORDER, canAccess, TierID } from '../../constants/tiers';

type BooleanFeature =
  | 'canSearch'
  | 'canQueryNew'
  | 'canAccessGradientScore'
  | 'canSetAlerts'
  | 'canEditSources'
  | 'canDirectSearch';

interface TierGateProps {
  children: React.ReactNode;
  requiredTier: TierID;
  feature: BooleanFeature;
  message?: string;
}

export function TierGate({ children, requiredTier, feature, message }: TierGateProps) {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;

  const hasAccess = TIER_ORDER[tier] >= TIER_ORDER[requiredTier] && canAccess(tier, feature);
  if (hasAccess) return <>{children}</>;

  const cfg = TIERS[requiredTier];

  return (
    <View className="relative overflow-hidden rounded-xl">
      <View className="opacity-30" pointerEvents="none">
        {children}
      </View>
      <View className="absolute inset-0 items-center justify-center rounded-xl p-6" style={{ backgroundColor: 'rgba(244,245,247,0.88)' }}>
        <View className="w-12 h-12 rounded-full items-center justify-center mb-4" style={{ backgroundColor: `${cfg.colour}20` }}>
          <Lock size={22} color={cfg.colour} />
        </View>
        <Text className="text-textPrimary font-bold text-base text-center mb-1">
          {cfg.name} plan required
        </Text>
        <Text className="text-textMuted text-sm text-center mb-5">
          {message ?? `Upgrade to ${cfg.name} to access this content`}
        </Text>
        <Button
          variant={requiredTier}
          size="sm"
          fullWidth={false}
          onPress={() => router.push('/membership')}
        >
          {`Upgrade — $${cfg.price.toLocaleString()}/mo`}
        </Button>
      </View>
    </View>
  );
}
