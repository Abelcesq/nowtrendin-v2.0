import React from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { BookOpen } from 'lucide-react-native';
import { useExplainer } from '../../hooks/useSignals';

// "Research" section for the Signal Intel detail — the AI (Perplexity) plain-
// English explanation of what the trend means. Evergreen + cached, so it's
// shown to every tier at ~zero cost.
export function TopicResearch({ topicKey, topicName }: { topicKey: string; topicName?: string }) {
  const { explainer, isLoading } = useExplainer(topicKey, topicName);

  if (!isLoading && !explainer?.full && !explainer?.short) return null;

  const body = explainer?.full || explainer?.short || '';
  // Light markdown → RN: split into blocks, strip ** and leading #, render bold-free.
  const blocks = body
    .split(/\n{2,}/)
    .map((b) => b.replace(/\*\*/g, '').replace(/^#+\s*/gm, '').trim())
    .filter(Boolean);

  return (
    <View className="mb-5">
      <View className="flex-row items-center gap-2 mb-2">
        <BookOpen size={15} color="#2A5B9E" />
        <Text className="text-textSecondary text-xs uppercase tracking-wider">Research — what this means</Text>
      </View>
      <View className="bg-card rounded-2xl p-4">
        {isLoading && !blocks.length ? (
          <View className="flex-row items-center gap-2">
            <ActivityIndicator size="small" color="#2A5B9E" />
            <Text className="text-textMuted text-xs">Researching what this trend means…</Text>
          </View>
        ) : (
          <>
            {blocks.map((b, i) => {
              const isHeading = b.length < 60 && !b.endsWith('.') && !/^\d/.test(b);
              return (
                <Text
                  key={i}
                  className={isHeading
                    ? 'text-textPrimary text-sm font-bold mt-2 mb-1'
                    : 'text-textSecondary text-[14px] leading-5 mb-2'}
                >
                  {b}
                </Text>
              );
            })}
            <Text className="text-textMuted text-[12px] mt-1">AI-generated overview · qualitative context, not investment advice. Any figures are approximate; the measured score and velocity are the engine's.</Text>
          </>
        )}
      </View>
    </View>
  );
}
