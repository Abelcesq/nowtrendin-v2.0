import React, { useState } from 'react';
import { View, TextInput, Text, TouchableOpacity } from 'react-native';
import { Eye, EyeOff } from 'lucide-react-native';

interface InputProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChangeText?: (text: string) => void;
  error?: string;
  secureText?: boolean;
  icon?: React.ReactNode;
  keyboardType?: 'default' | 'email-address' | 'numeric';
  autoCapitalize?: 'none' | 'sentences' | 'words';
  className?: string;
}

export function Input({
  label,
  placeholder,
  value,
  onChangeText,
  error,
  secureText = false,
  icon,
  keyboardType = 'default',
  autoCapitalize = 'none',
  className = '',
}: InputProps) {
  const [showPw, setShowPw] = useState(false);

  return (
    <View className={`mb-4 ${className}`}>
      {label && <Text className="text-textSecondary text-sm font-medium mb-2">{label}</Text>}
      <View
        className={`flex-row items-center bg-surface rounded-xl px-4 py-3.5 border ${
          error ? 'border-error' : 'border-border'
        }`}
        style={{ shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 3, shadowOffset: { width: 0, height: 1 }, elevation: 1 }}
      >
        {icon && <View className="mr-3 opacity-60">{icon}</View>}
        <TextInput
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#9AA3B0"
          secureTextEntry={secureText && !showPw}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          className="flex-1 text-base"
          style={{ color: '#1A1A2E' }}
        />
        {secureText && (
          <TouchableOpacity onPress={() => setShowPw(!showPw)} className="ml-2">
            {showPw ? <EyeOff size={18} color="#475569" /> : <Eye size={18} color="#475569" />}
          </TouchableOpacity>
        )}
      </View>
      {error && <Text className="text-error text-xs mt-1 ml-1">{error}</Text>}
    </View>
  );
}
