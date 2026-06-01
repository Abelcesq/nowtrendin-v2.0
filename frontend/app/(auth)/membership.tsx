import { useState } from 'react';
import { View, Text, TouchableOpacity, Linking } from 'react-native';
import { useRouter } from 'expo-router';
import { Zap, Briefcase, Building2, Check, X } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';
import { TIERS, TierID } from '../../constants/tiers';
import { useAuthStore } from '../../store/auth.store';
import { tierDefaults } from '../../lib/auth';

const TIER_ICONS: Record<TierID, any> = {
  consumer: Zap,
  business: Briefcase,
  enterprise: Building2,
};

function TierCard({
  tierId,
  selected,
  onSelect,
  onAction,
}: {
  tierId: TierID;
  selected: boolean;
  onSelect: () => void;
  onAction: () => void;
}) {
  const tier = TIERS[tierId];
  const Icon = TIER_ICONS[tierId];
  const isPopular = tierId === 'business';
  const isEnterprise = tierId === 'enterprise';

  return (
    <TouchableOpacity
      onPress={onSelect}
      activeOpacity={0.9}
      className="rounded-2xl p-5 mb-4 border-2 bg-surface"
      style={{ borderColor: selected ? tier.colour : '#1E2D3D' }}
    >
      {isPopular && (
        <View className="self-start px-3 py-1 rounded-full mb-3" style={{ backgroundColor: `${tier.colour}30` }}>
          <Text style={{ color: tier.colour }} className="text-xs font-bold">
            ✦ Most Popular
          </Text>
        </View>
      )}

      <View className="flex-row items-center justify-between mb-4">
        <View className="flex-row items-center gap-3">
          <View className="w-10 h-10 rounded-xl items-center justify-center" style={{ backgroundColor: `${tier.colour}20` }}>
            <Icon size={20} color={tier.colour} />
          </View>
          <View>
            <Text className="text-textPrimary font-bold text-lg">{tier.name}</Text>
            <Text style={{ color: tier.colour }} className="text-sm font-medium">
              {isEnterprise ? 'Contact for pricing' : `$${tier.price.toLocaleString()}/month`}
            </Text>
          </View>
        </View>
        {selected && (
          <View className="w-6 h-6 rounded-full items-center justify-center" style={{ backgroundColor: tier.colour }}>
            <Check size={14} color="#07080C" />
          </View>
        )}
      </View>

      <View className="gap-2 mb-4">
        {tier.features.map((f) => (
          <View key={f} className="flex-row items-start gap-2">
            <Check size={14} color="#00C896" />
            <Text className="text-textSecondary text-sm flex-1">{f}</Text>
          </View>
        ))}
        {tier.restrictions.map((r) => (
          <View key={r} className="flex-row items-start gap-2">
            <X size={14} color="#475569" />
            <Text className="text-textMuted text-sm flex-1">{r}</Text>
          </View>
        ))}
      </View>

      <Button variant={tierId} size="md" onPress={onAction}>
        {isEnterprise ? 'Contact Sales' : `Start ${tier.name} Plan`}
      </Button>
    </TouchableOpacity>
  );
}

export default function Membership() {
  const router = useRouter();
  const updateTier = useAuthStore((s) => s.updateTier);
  const decrementTokens = useAuthStore((s) => s.decrementTokens);
  const [selected, setSelected] = useState<TierID>('business');

  const choose = (tierId: TierID) => {
    if (tierId === 'enterprise') {
      Linking.openURL('mailto:enterprise@nowtrendin.com?subject=Enterprise%20Access');
      return;
    }
    // Phase 1: skip Stripe — just set the tier and enter the app.
    updateTier(tierId);
    router.replace('/(app)');
  };

  return (
    <Screen scroll>
      <View className="pt-10 pb-4">
        <Text className="text-textPrimary text-3xl font-bold mb-2">Choose your plan</Text>
        <Text className="text-textMuted text-base">Start measuring attention intelligence today.</Text>
      </View>

      {(['consumer', 'business', 'enterprise'] as TierID[]).map((tierId) => (
        <TierCard
          key={tierId}
          tierId={tierId}
          selected={selected === tierId}
          onSelect={() => setSelected(tierId)}
          onAction={() => choose(tierId)}
        />
      ))}

      <View className="pb-8 pt-2">
        <Text className="text-textMuted text-xs text-center mb-3">
          All plans include push + email alerts · Cancel anytime
        </Text>
        <Button
          variant="ghost"
          size="sm"
          fullWidth={false}
          className="self-center"
          onPress={() => {
            updateTier('consumer');
            router.replace('/(app)');
          }}
        >
          Continue with free trial
        </Button>
      </View>
    </Screen>
  );
}
