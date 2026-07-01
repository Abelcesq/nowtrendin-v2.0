import { View, Text } from 'react-native';
import { Gauge, Activity } from 'lucide-react-native';
import { useMacroLeverage } from '../../hooks/useSignals';

function fmtUsd(n?: number | null) {
  if (n == null) return '—';
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
  return `$${Math.round(n).toLocaleString()}`;
}

const STRESS_COLOR: Record<string, string> = {
  'Calm funding markets': '#2E7D5B',
  'Mild funding stress': '#A8456A',
  'Elevated funding stress': '#B11226',
};

/** Systemic-leverage + funding-stress card (OFR Short-Term Funding Monitor). */
export function MacroLeverageCard() {
  const { macro } = useMacroLeverage();
  if (!macro) return null;
  const stressColor = STRESS_COLOR[macro.stressLabel || ''] || '#3C4663';
  const chg = macro.repoVolumeChangePct;

  return (
    <View className="bg-card rounded-2xl p-4 mb-4">
      <View className="flex-row items-center gap-2 mb-2">
        <Gauge size={18} color="#2A5B9E" />
        <Text className="text-textPrimary text-sm font-bold flex-1">Systemic Leverage</Text>
        {!!macro.asOf && <Text className="text-textMuted text-[12px]">as of {macro.asOf}</Text>}
      </View>

      <View className="flex-row gap-3">
        <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: '#2A5B9E12' }}>
          <Text className="text-textMuted text-[12px] font-bold">REPO LEVERAGE</Text>
          <Text className="text-textPrimary text-sm font-black mt-0.5">{macro.leverageLabel}</Text>
          <Text className="text-textSecondary text-[12px] mt-1">
            Repo volume {fmtUsd(macro.repoVolumeUsd)}
            {chg != null ? `  ·  ${chg >= 0 ? '+' : ''}${chg}%` : ''}
          </Text>
        </View>
        <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: `${stressColor}12` }}>
          <View className="flex-row items-center gap-1">
            <Activity size={12} color={stressColor} />
            <Text className="text-textMuted text-[12px] font-bold">FUNDING STRESS</Text>
          </View>
          <Text className="text-sm font-black mt-0.5" style={{ color: stressColor }}>{macro.stressLabel}</Text>
          {macro.repoSpreadBps != null && (
            <Text className="text-textSecondary text-[12px] mt-1">Rate spread {macro.repoSpreadBps} bps</Text>
          )}
        </View>
      </View>

      <Text className="text-textMuted text-[12px] mt-2 leading-3">
        Source: U.S. Office of Financial Research — Short-Term Funding Monitor. Descriptive macro
        analysis only, not investment advice.
      </Text>
    </View>
  );
}
