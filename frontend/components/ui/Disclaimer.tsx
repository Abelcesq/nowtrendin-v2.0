import { Text } from 'react-native';

/** Standard not-financial-advice disclaimer. Shown at the bottom of analysis
 *  surfaces (dashboard, accuracy ledger, history, alerts). */
export function Disclaimer({ className = '' }: { className?: string }) {
  return (
    <Text className={`text-textMuted text-[10px] text-center mt-6 mb-2 px-4 leading-4 ${className}`}>
      Now TrendIn provides signal analysis for informational purposes only — not financial,
      investment, or legal advice. All decisions are your own.
    </Text>
  );
}
