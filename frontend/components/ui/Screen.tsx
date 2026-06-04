import React from 'react';
import { ScrollView, View, StatusBar } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface ScreenProps {
  children: React.ReactNode;
  scroll?: boolean;
  className?: string;
  padded?: boolean;
}

export function Screen({ children, scroll = false, className = '', padded = true }: ScreenProps) {
  const padding = padded ? 'px-5' : '';
  return (
    <SafeAreaView className="flex-1 bg-bg" edges={['top', 'left', 'right']}>
      <StatusBar barStyle="dark-content" backgroundColor="#F4F5F7" />
      {scroll ? (
        <ScrollView
          className={`flex-1 ${padding} ${className}`}
          contentContainerStyle={{ flexGrow: 1, paddingBottom: 32 }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          minimumZoomScale={1}
          maximumZoomScale={3}
          bouncesZoom
          pinchGestureEnabled
        >
          {children}
        </ScrollView>
      ) : (
        <View className={`flex-1 ${padding} ${className}`}>{children}</View>
      )}
    </SafeAreaView>
  );
}
