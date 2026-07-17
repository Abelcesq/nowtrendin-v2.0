import { Text } from 'react-native';

/** Standard not-financial-advice disclaimer. Shown at the top and bottom of analysis
 *  surfaces (trend/market detail, dashboard, accuracy ledger, history, alerts).
 *  Founder-approved legal copy (2026-07-07) — verbatim; do not edit without founder sign-off. */
export function Disclaimer({ className = '' }: { className?: string }) {
  return (
    <Text className={`text-textSecondary text-[12px] text-center mt-6 mb-2 px-4 leading-4 ${className}`}>
      *All information contained herein may not be accurate including any and all figures
      indicated in this section and or site and may be an approximation and should not be
      construed as financial, investment, or legal advice.
    </Text>
  );
}
