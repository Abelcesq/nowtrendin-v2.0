import React from 'react';
import { View, ViewStyle, StyleProp } from 'react-native';

// Aurora design-system CARD. Borderless, soft light-gray fill, rounded — the ONLY
// way to render a card/box/container in this app. New cards or analysis sections
// merged from the backend should use this so they inherit the look automatically.
// NEVER add a border outline; NEVER use a hard-coded white box with a border.
export function Card({
  children,
  className = '',
  style,
  padded = true,
}: {
  children: React.ReactNode;
  className?: string;
  style?: StyleProp<ViewStyle>;
  padded?: boolean;
}) {
  return (
    <View className={`bg-card rounded-3xl ${padded ? 'px-5 py-5' : ''} ${className}`} style={style}>
      {children}
    </View>
  );
}
