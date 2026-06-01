import React from 'react';
import { Text, Image } from 'react-native';

// Flame mark only (cropped from the brand logo) — for headers, login, etc.
export function Logo({ size = 48 }: { size?: number }) {
  return (
    <Image
      source={require('../../assets/logo-mark.png')}
      style={{ width: size, height: size }}
      resizeMode="contain"
    />
  );
}

// Full brand lockup (flame + "NowTrendIn" wordmark) — for the splash screen.
export function FullLogo({ width = 240 }: { width?: number }) {
  return (
    <Image
      source={require('../../assets/logo.png')}
      style={{ width, height: width * 1.25 }}
      resizeMode="contain"
    />
  );
}

// Text wordmark — "Now" dark maroon, "TrendIn" orange-red (matches logo PNG).
// Use next to the flame <Logo> in the home header.
export function Wordmark({ size = 'text-3xl' }: { size?: string }) {
  return (
    <Text className={`${size} font-black`}>
      <Text className="text-brandMaroon">Now</Text>
      <Text className="text-brandOrange">TrendIn</Text>
    </Text>
  );
}
