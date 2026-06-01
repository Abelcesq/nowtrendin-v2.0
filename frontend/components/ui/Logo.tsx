import React from 'react';
import { Text } from 'react-native';
import Svg, { Path, Defs, LinearGradient, Stop } from 'react-native-svg';

// "Now TrendIn" wordmark — matches logo PNG: "Now" dark maroon, "TrendIn" orange-red.
export function Wordmark({ size = 'text-3xl' }: { size?: string }) {
  return (
    <Text className={`${size} font-black`}>
      <Text className="text-brandMaroon">Now</Text>
      <Text className="text-brandOrange">TrendIn</Text>
    </Text>
  );
}

// Flame + rising-arrow mark approximating the Now TrendIn v1.0 logo.
// Stand-in until the original logo.png is dropped into assets/ (then swap for <Image>).
export function Logo({ size = 48 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 100 100">
      <Defs>
        <LinearGradient id="ntFlame" x1="0" y1="0" x2="0.2" y2="1">
          <Stop offset="0" stopColor="#F7A41C" />
          <Stop offset="0.4" stopColor="#F26522" />
          <Stop offset="0.75" stopColor="#CF2A1B" />
          <Stop offset="1" stopColor="#6E1410" />
        </LinearGradient>
      </Defs>

      {/* Flame body */}
      <Path
        d="M55 5 c 5 17 23 23 19 43 c -2 12 9 15 3 28 c -6 12 -30 14 -41 4 c -10 -9 -9 -22 -2 -30 c 6 -7 2 -15 5 -22 c 3 -10 11 -11 11 -25 Z"
        fill="url(#ntFlame)"
      />

      {/* Rising chart arrow (light, sits over the flame) */}
      <Path
        d="M28 68 L45 53 L41 49 L60 33"
        stroke="#EFEFEF"
        strokeWidth={7}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <Path d="M50 30 L67 30 L65 47 Z" fill="#EFEFEF" />
    </Svg>
  );
}
