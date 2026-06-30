import React from 'react';
import { View, Text } from 'react-native';
import Svg, { Circle } from 'react-native-svg';

type Size = 'sm' | 'md' | 'lg' | 'xl';

const DIM: Record<Size, number> = { sm: 60, md: 90, lg: 120, xl: 168 };
const STROKE: Record<Size, number> = { sm: 6, md: 8, lg: 10, xl: 13 };
const FONT: Record<Size, number> = { sm: 16, md: 26, lg: 36, xl: 50 };

interface Props {
  score: number;
  color: string;
  size?: Size;
  label?: string;
  caption?: string;
}

// Arc-style Gradient Score ring — the hero visual of the product.
export function GradientScoreRing({ score, color, size = 'md', label, caption }: Props) {
  const dim = DIM[size];
  const stroke = STROKE[size];
  const r = (dim - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;

  return (
    <View style={{ width: dim, height: dim }} className="items-center justify-center">
      <Svg width={dim} height={dim}>
        <Circle cx={dim / 2} cy={dim / 2} r={r} stroke="#ECECEC" strokeWidth={stroke} fill="none" />
        <Circle
          cx={dim / 2}
          cy={dim / 2}
          r={r}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={`${circ * pct} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${dim / 2} ${dim / 2})`}
        />
      </Svg>
      <View style={{ position: 'absolute' }} className="items-center">
        <Text style={{ fontSize: FONT[size], color: '#16264A', lineHeight: FONT[size] * 1.05 }} className="font-black">
          {score}
        </Text>
        {label && (
          <Text style={{ color }} className="text-[10px] font-bold tracking-wide">
            {label}
          </Text>
        )}
        {caption && <Text className="text-textMuted text-[9px] mt-0.5">{caption}</Text>}
      </View>
    </View>
  );
}
