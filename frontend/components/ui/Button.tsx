import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator } from 'react-native';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'consumer' | 'business' | 'enterprise';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: React.ReactNode;
  variant?: Variant;
  size?: Size;
  onPress?: () => void;
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
}

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary',
  secondary: 'bg-transparent border-primary',
  ghost: 'bg-transparent',
  danger: 'bg-error',
  consumer: 'bg-transparent border-consumer',
  business: 'bg-primary',
  enterprise: 'bg-transparent border-enterprise',
};

const TEXT_VARIANTS: Record<Variant, string> = {
  primary: 'text-white font-bold',
  secondary: 'text-primary font-semibold',
  ghost: 'text-textSecondary font-medium',
  danger: 'text-white font-bold',
  consumer: 'text-consumer font-semibold',
  business: 'text-white font-bold',
  enterprise: 'text-enterprise font-semibold',
};

const SIZES: Record<Size, string> = {
  sm: 'px-3 py-2 rounded-lg',
  md: 'px-4 py-3 rounded-xl',
  lg: 'px-5 py-4 rounded-xl',
};

const TEXT_SIZES: Record<Size, string> = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  onPress,
  loading = false,
  disabled = false,
  icon,
  className = '',
  fullWidth = true,
}: ButtonProps) {
  const isDisabled = disabled || loading;
  const spinnerColor =
    variant === 'primary' || variant === 'business' || variant === 'danger' ? '#FFFFFF' : '#2E7D5B';

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.85}
      className={`${VARIANTS[variant]} ${SIZES[size]} ${fullWidth ? 'w-full' : ''} ${
        isDisabled ? 'opacity-50' : ''
      } items-center justify-center flex-row gap-2 ${className}`}
    >
      {loading ? (
        <ActivityIndicator size="small" color={spinnerColor} />
      ) : (
        <>
          {icon}
          <Text className={`${TEXT_VARIANTS[variant]} ${TEXT_SIZES[size]}`}>{children}</Text>
        </>
      )}
    </TouchableOpacity>
  );
}
