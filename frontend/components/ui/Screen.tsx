import React from 'react';
import { ScrollView, View, StatusBar, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle } from 'react-native-reanimated';
import { Rise } from './Rise';

interface ScreenProps {
  children: React.ReactNode;
  scroll?: boolean;
  className?: string;
  padded?: boolean;
}

const isAndroid = Platform.OS === 'android';
const isWeb = Platform.OS === 'web';

// On web, constrain content to a readable column and center it so the app
// doesn't stretch edge-to-edge on desktop monitors. No-op on native.
const WEB_MAX_WIDTH = 760;
const webContentStyle = isWeb
  ? ({ width: '100%', maxWidth: WEB_MAX_WIDTH, alignSelf: 'center' } as const)
  : undefined;

export function Screen({ children, scroll = false, className = '', padded = true }: ScreenProps) {
  const padding = padded ? 'px-5' : '';
  const webWrap = (node: React.ReactNode) =>
    isWeb ? <View style={webContentStyle} className="flex-1">{node}</View> : node;

  // Pinch-to-zoom. iOS uses the ScrollView's native zoom; Android has none,
  // so we drive a transform scale via a pinch gesture.
  const scale = useSharedValue(1);
  const start = useSharedValue(1);
  const pinch = Gesture.Pinch()
    .onStart(() => {
      start.value = scale.value;
    })
    .onUpdate((e) => {
      scale.value = Math.min(3, Math.max(1, start.value * e.scale));
    });
  const zoomStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  // Every screen fades + settles in on navigation — a subtle, consistent
  // transition between screens (touch app, so motion is light and purposeful).
  const frame = (inner: React.ReactNode) => (
    <SafeAreaView className="flex-1 bg-bg" edges={['top', 'left', 'right']}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <Rise style={{ flex: 1 }} axis="x" distance={28} duration={420}>{inner}</Rise>
    </SafeAreaView>
  );

  if (!scroll) {
    return frame(<View className={`flex-1 ${padding} ${className}`}>{webWrap(children)}</View>);
  }

  const sv = (
    <ScrollView
      className={`flex-1 ${padding} ${className}`}
      contentContainerStyle={{ flexGrow: 1, paddingBottom: 32, ...(isWeb ? { alignItems: 'center' } : null) }}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
      {...(isAndroid
        ? {}
        : { minimumZoomScale: 1, maximumZoomScale: 3, bouncesZoom: true, pinchGestureEnabled: true })}
    >
      {isAndroid ? (
        <Animated.View style={zoomStyle}>{children}</Animated.View>
      ) : isWeb ? (
        <View style={webContentStyle}>{children}</View>
      ) : (
        children
      )}
    </ScrollView>
  );

  return frame(isAndroid ? <GestureDetector gesture={pinch}>{sv}</GestureDetector> : sv);
}
