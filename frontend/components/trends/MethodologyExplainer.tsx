import { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { ChevronDown, ChevronUp, Atom } from 'lucide-react-native';

/**
 * "How the Gradient Score works" — ported from the web dashboard's
 * "How It Works" tab. Static, collapsible institutional-trust explainer:
 * the three laws + the Duality dual-score principle.
 */
const LAWS = [
  {
    tag: 'Law 1',
    title: 'Attention follows energy gradients',
    color: '#2E7D5B',
    body: 'Attention moves from high-concentration communities (niche, expert, passionate) to low-concentration ones (mainstream, passive). Gradient Strength measures that density difference — a steep gradient means maximum potential energy is still to be released.',
  },
  {
    tag: 'Law 2',
    title: 'Attention has inertia',
    color: '#2A5B9E',
    body: 'A trend accelerating for 72 hours is more likely to continue than one that spiked in the last 6. Inertia + Persistence measure self-reinforcing momentum across consecutive windows — separating genuine trends from viral spikes.',
  },
  {
    tag: 'Law 3',
    title: 'Attention requires a medium',
    color: '#6B4FA0',
    body: 'Different platforms carry attention differently. GitHub → Hacker News → Reddit is a technology-commercialization path; niche → general → mainstream is a cultural one. The sequence a signal travels reveals its trajectory and velocity.',
  },
];

export function MethodologyExplainer() {
  const [open, setOpen] = useState(false);
  return (
    <View className="mb-5 rounded-2xl bg-card overflow-hidden">
      <TouchableOpacity
        onPress={() => setOpen(!open)}
        className="flex-row items-center justify-between px-4 py-3.5"
        activeOpacity={0.8}
      >
        <View className="flex-row items-center gap-2">
          <Atom size={16} color="#3C4663" />
          <Text className="text-textPrimary font-semibold">How the Gradient Score works</Text>
        </View>
        {open ? <ChevronUp size={18} color="#9A9AA2" /> : <ChevronDown size={18} color="#9A9AA2" />}
      </TouchableOpacity>

      {open && (
        <View className="px-4 pb-4">
          <Text className="text-textSecondary text-xs leading-5 mb-3">
            The Gradient Score treats human attention like a physical system — discovering the laws that
            govern how attention moves through information networks, the same way physics uncovers laws of matter.
          </Text>

          {LAWS.map((l) => (
            <View
              key={l.tag}
              className="rounded-xl px-3 py-3 mb-2"
              style={{ borderColor: `${l.color}33`, backgroundColor: `${l.color}0A` }}
            >
              <View className="flex-row items-center gap-2 mb-1">
                <Text className="text-[12px] font-bold px-1.5 py-0.5 rounded" style={{ color: l.color, backgroundColor: `${l.color}1A` }}>
                  {l.tag}
                </Text>
                <Text className="text-textPrimary text-sm font-bold flex-1">{l.title}</Text>
              </View>
              <Text className="text-textMuted text-[12px] leading-5">{l.body}</Text>
            </View>
          ))}

          <View className="rounded-xl px-3 py-3 mt-1" style={{ borderColor: '#A8456A33', backgroundColor: '#A8456A0D' }}>
            <Text className="text-[12px] font-bold mb-1" style={{ color: '#A8456A' }}>THE DUALITY PRINCIPLE</Text>
            <Text className="text-textMuted text-[12px] leading-5">
              Earlier detection comes with lower certainty; higher certainty needs more data, which means later
              detection. That's why every topic shows two scores — Detection (optimized for earliness) and
              Confidence (optimized for precision). You choose based on your risk tolerance.
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}
