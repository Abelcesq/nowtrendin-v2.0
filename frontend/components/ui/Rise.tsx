import React, { useEffect, useRef } from 'react';
import { Animated, Easing, ViewStyle } from 'react-native';

// Subtle, purposeful entrance motion (fade + small slide) — the Apple "content
// settles into place" feel: smooth, decelerating, never bouncy. Touch-only app,
// so motion reads as polish without getting in the way. `axis` slides vertically
// ('y', default) or horizontally ('x', for screen-to-screen transitions).
export function Rise({
  children,
  delay = 0,
  distance = 14,
  duration = 480,
  axis = 'y',
  style,
}: {
  children: React.ReactNode;
  delay?: number;
  distance?: number;
  duration?: number;
  axis?: 'x' | 'y';
  style?: ViewStyle | ViewStyle[];
}) {
  const progress = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(progress, {
      toValue: 1,
      duration,
      delay,
      // Gentle deceleration — relaxed, no overshoot/bounce.
      easing: Easing.bezier(0.22, 1, 0.36, 1),
      useNativeDriver: true,
    }).start();
  }, []);

  const offset = progress.interpolate({ inputRange: [0, 1], outputRange: [distance, 0] });
  const transform = axis === 'x' ? [{ translateX: offset }] : [{ translateY: offset }];

  return (
    <Animated.View style={[{ opacity: progress, transform }, style as any]}>
      {children}
    </Animated.View>
  );
}
