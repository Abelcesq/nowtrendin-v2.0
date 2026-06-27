import { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Activity } from 'lucide-react-native';
import { fetchSignalAnalysis, type SignalAnalysisData } from '../../lib/gradientApi';

/**
 * SignalAnalysisPanel — the per-item Signal Analysis section (mobile parity with the web
 * terminal). POSTs the item the detail screen already rendered to /analysis/{kind}; the engine
 * attaches the matching accuracy-ledger report and returns a held-out, reproducible,
 * formula-confidential narrative (measurement, not advice). Render-only. §17-safe: if the engine
 * returns no sections, the panel renders nothing rather than an empty shell.
 */

// Render **bold** spans inline (the descriptor bolds each metric name).
function Body({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <Text className="text-textPrimary text-[12px] leading-5">
      {parts.map((p, i) =>
        p.startsWith('**') && p.endsWith('**')
          ? <Text key={i} className="font-bold">{p.slice(2, -2)}</Text>
          : <Text key={i}>{p}</Text>,
      )}
    </Text>
  );
}

export function SignalAnalysisPanel({ kind, item }: { kind: 'trend' | 'market' | 'crypto'; item: any }) {
  const [a, setA] = useState<SignalAnalysisData | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'empty'>('loading');
  const sig = JSON.stringify(item || {});
  useEffect(() => {
    let alive = true;
    setState('loading');
    fetchSignalAnalysis(kind, item).then((r) => {
      if (!alive) return;
      if (r && Array.isArray(r.sections) && r.sections.length) { setA(r); setState('ready'); }
      else setState('empty');
    });
    return () => { alive = false; };
  }, [kind, sig]);

  if (state === 'empty') return null;
  return (
    <View className="mb-5 rounded-2xl border border-border bg-surface px-4 py-3.5">
      <View className="flex-row items-center gap-2 mb-2">
        <Activity size={16} color="#00C896" />
        <Text className="text-textPrimary font-semibold">Signal Analysis</Text>
        {a?.headline ? <Text className="text-textMuted text-[11px] flex-1" numberOfLines={1}> · {a.headline}</Text> : null}
      </View>

      {state === 'loading' ? (
        <View className="flex-row items-center gap-2 py-2">
          <ActivityIndicator size="small" color="#9AA3B0" />
          <Text className="text-textSecondary text-xs">Composing analysis…</Text>
        </View>
      ) : (
        <>
          {a?.facts && a.facts.length > 0 ? (
            <View className="flex-row flex-wrap gap-1.5 mb-3">
              {a.facts.map((f, i) => (
                <View key={i} className="rounded-md border border-border bg-bg px-2 py-1">
                  <Text className="text-[10px] text-textSecondary">
                    <Text className="font-bold text-textPrimary">{f.label}</Text> {f.value}
                  </Text>
                </View>
              ))}
            </View>
          ) : null}

          {(a?.sections || []).map((s, i) => (
            <View key={i} className="mb-2.5">
              <Text className="text-[10px] font-bold text-textSecondary mb-0.5">{s.heading.toUpperCase()}</Text>
              <Body text={s.body} />
            </View>
          ))}

          {a?.disclaimer ? (
            <Text className="text-textMuted text-[10px] leading-4 mt-1 italic">{a.disclaimer}</Text>
          ) : null}
        </>
      )}
    </View>
  );
}
