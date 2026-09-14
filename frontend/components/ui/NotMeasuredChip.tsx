import React from 'react';
import { View, Text } from 'react-native';

// C1 honest-absence chip (web parity: Crypto.tsx AbsentTierChip). Absence is not
// a tier: hollow/outlined — transparent background, DASHED hairline, muted ink —
// never a filled tier chip in a measured color, never red. The dashed outline is
// the semantic absence device, not a card border (Aurora §3 governs cards; this
// is a chip-scale state marker).
export function NotMeasuredChip({ label = 'NOT MEASURED' }: { label?: string }) {
  return (
    <View
      style={{
        borderWidth: 1,
        borderStyle: 'dashed',
        borderColor: '#9A9AA2',
        backgroundColor: 'transparent',
        borderRadius: 6,
        paddingHorizontal: 7,
        paddingVertical: 2,
        alignSelf: 'flex-start',
      }}
    >
      <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 0.5 }}>{label}</Text>
    </View>
  );
}

// C1: absence-class-aware label — the structural/transient split the engine
// serves. NEVER "yet"/"soon"/roadmap phrasing.
export function absentTierLabel(absenceClass?: string): string {
  return absenceClass === 'structural' ? 'NOT MEASURED · source limit'
    : absenceClass === 'transient' ? 'NOT MEASURED · none this cycle'
    : 'NOT MEASURED';
}
