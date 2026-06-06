import { View, Text } from 'react-native';
import { Layers } from 'lucide-react-native';
import { TopicVariation, tierColourHex } from '../../lib/signals';

/**
 * The AI Variation Map — shows that "AI" the umbrella term scores very
 * differently from a specific live variation like "agentic coding".
 * Renders only when the engine returns taxonomy variations for the topic.
 */
export function TopicVariationMap({
  variations,
  intro,
}: {
  variations?: TopicVariation[];
  intro?: string;
}) {
  if (!variations || variations.length === 0) return null;

  return (
    <View className="mb-5">
      <View className="flex-row items-center gap-2 mb-2">
        <Layers size={16} color="#5B6472" />
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          AI Variation Map
        </Text>
      </View>
      {!!intro && <Text className="text-textMuted text-xs mb-3 leading-5">{intro}</Text>}

      <View className="bg-surface rounded-2xl border border-border overflow-hidden">
        {variations.map((v, i) => {
          const c = tierColourHex(v.tierColour);
          return (
            <View
              key={v.topicKey || String(i)}
              className="px-4 py-3 border-b border-border"
              style={[
                i === variations.length - 1 ? { borderBottomWidth: 0 } : null,
                v.isQueried ? { backgroundColor: `${c}0F` } : null,
              ]}
            >
              <View className="flex-row items-center justify-between">
                <View className="flex-row items-center gap-2 flex-1 pr-2">
                  <View className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: c }} />
                  <Text
                    className={`text-sm ${v.isQueried ? 'font-bold text-textPrimary' : 'text-textSecondary'}`}
                    numberOfLines={1}
                  >
                    {v.display}
                    {v.isQueried ? '  ·  this topic' : ''}
                  </Text>
                </View>
                <Text className="text-sm font-bold" style={{ color: c }}>
                  {v.typicalDetection}
                  <Text className="text-textMuted font-normal"> / {v.typicalConfidence}</Text>
                </Text>
              </View>
              {!!v.tierLabel && (
                <Text className="text-[10px] mt-1 ml-3.5" style={{ color: c }}>
                  {v.tierLabel}
                  {v.velocity ? ` · ${v.velocity}` : ''}
                </Text>
              )}
              {!!v.whyDifferent && !v.isQueried && (
                <Text className="text-textMuted text-[11px] mt-1 ml-3.5 leading-4">
                  {v.whyDifferent}
                </Text>
              )}
            </View>
          );
        })}
      </View>
      <Text className="text-textMuted text-[10px] mt-2">Detection / Confidence — typical range for each variation.</Text>
    </View>
  );
}
