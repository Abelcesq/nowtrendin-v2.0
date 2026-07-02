import React, { useState } from 'react';
import { View, Text, TouchableOpacity, LayoutAnimation, Platform, UIManager } from 'react-native';
import { ChevronDown } from 'lucide-react-native';
import { Rise } from './Rise';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Aurora design-system COLLAPSIBLE — the canonical "analysis section" / progressive-
// disclosure row: a tappable title that reveals its content with a soft, relaxed
// (non-bouncy) animation. New analysis sections merged from the backend should be
// wrapped in this so the calm, minimalist behavior + motion apply automatically.
export function Collapsible({
  title,
  hint,
  defaultOpen = false,
  children,
}: {
  title: string;
  hint?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const toggle = () => {
    // Soft, relaxed easeInEaseOut — no spring/bounce (Apple feel).
    LayoutAnimation.configureNext({
      duration: 440,
      create: { type: 'easeInEaseOut', property: 'opacity' },
      update: { type: 'easeInEaseOut' },
      delete: { type: 'easeInEaseOut', property: 'opacity' },
    });
    setOpen((o) => !o);
  };
  return (
    <View style={{ borderBottomWidth: 1, borderBottomColor: '#ECECEC' }}>
      <TouchableOpacity onPress={toggle} activeOpacity={0.7} className="flex-row items-center py-4">
        <View className="flex-1">
          <Text style={{ color: '#16264A', fontSize: 14, fontWeight: '800', letterSpacing: 0.4 }}>{title}</Text>
          {!!hint && <Text style={{ color: '#9A9AA2', fontSize: 12, marginTop: 3 }}>{hint}</Text>}
        </View>
        <ChevronDown size={18} color="#C7C7CE" style={{ transform: [{ rotate: open ? '180deg' : '0deg' }] }} />
      </TouchableOpacity>
      {open && <Rise duration={420} distance={10}><View className="pb-5">{children}</View></Rise>}
    </View>
  );
}
