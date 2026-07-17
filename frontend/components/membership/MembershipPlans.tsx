import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Linking } from 'react-native';
import { Zap, Briefcase, Building2, Check, X } from 'lucide-react-native';
import { Button } from '../ui/Button';
import { TIERS, TierID } from '../../constants/tiers';

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

  return (
    <TouchableOpacity
      onPress={onSelect}
      activeOpacity={0.9}
      className="rounded-2xl p-5 mb-4 border-2 bg-card"
      style={{ borderColor: selected ? tier.colour : '#ECECEC' }}
    >
      {isPopular && (
        <View className="self-start px-3 py-1 rounded-full mb-3" style={{ backgroundColor: `${tier.colour}30` }}>
          <Text style={{ color: tier.colour }} className="text-xs font-bold">✦ Most Popular</Text>
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
              {`$${tier.price.toLocaleString()}/month`}
            </Text>
          </View>
        </View>
        {selected && (
          <View className="w-6 h-6 rounded-full items-center justify-center" style={{ backgroundColor: tier.colour }}>
            <Check size={14} color="#FFFFFF" />
          </View>
        )}
      </View>

      <View className="gap-2 mb-4">
        {tier.features.map((f) => (
          <View key={f} className="flex-row items-start gap-2">
            <Check size={14} color="#2E7D5B" />
            <Text className="text-textSecondary text-sm flex-1">{f}</Text>
          </View>
        ))}
        {tier.restrictions.map((r) => (
          <View key={r} className="flex-row items-start gap-2">
            <X size={14} color="#9A9AA2" />
            <Text className="text-textMuted text-sm flex-1">{r}</Text>
          </View>
        ))}
      </View>

      {tierId === 'enterprise' ? (
        // Board ruling 2026-07-17: the $250k tier is NEVER self-serve on mobile —
        // provisioned by the team after a sales conversation.
        <Button variant={tierId} size="md"
          onPress={() => Linking.openURL('mailto:sales@nowtrendin.com?subject=NowTrendIn%20Enterprise%20access')}>
          Contact Sales
        </Button>
      ) : (
        <Button variant={tierId} size="md" onPress={onAction}>
          {`Start ${tier.name} Plan`}
        </Button>
      )}
    </TouchableOpacity>
  );
}

// Shared plan picker used by the post-signup screen and the in-app upgrade screen.
export function MembershipPlans({ onChoose }: { onChoose: (tier: TierID) => void }) {
  const [selected, setSelected] = useState<TierID>('business');

  const choose = (tierId: TierID) => {
    onChoose(tierId);
  };

  return (
    <View>
      {(['consumer', 'business', 'enterprise'] as TierID[]).map((tierId) => (
        <TierCard
          key={tierId}
          tierId={tierId}
          selected={selected === tierId}
          onSelect={() => setSelected(tierId)}
          onAction={() => choose(tierId)}
        />
      ))}

      <View className="pb-4 pt-1">
        <Text className="text-textMuted text-xs text-center mb-3">
          All plans include push + email alerts · Cancel anytime
        </Text>
        <Button variant="ghost" size="sm" fullWidth={false} className="self-center" onPress={() => onChoose('consumer')}>
          Continue with free trial
        </Button>
      </View>
    </View>
  );
}
