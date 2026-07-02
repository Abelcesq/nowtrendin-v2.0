import { Text } from 'react-native';

/** Standard not-financial-advice disclaimer. Shown at the bottom of analysis
 *  surfaces (dashboard, accuracy ledger, history, alerts). */
export function Disclaimer({ className = '' }: { className?: string }) {
  return (
    <Text className={`text-textMuted text-[12px] text-center mt-6 mb-2 px-4 leading-4 ${className}`}>
      All information contained herein may not be accurate including any figures are approximate
      and the measured score and velocity and should not be construed as financial, investment,
      or legal advice.
    </Text>
  );
}
