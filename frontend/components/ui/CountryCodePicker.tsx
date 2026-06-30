import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, TextInput, FlatList } from 'react-native';
import { ChevronDown, Search, X } from 'lucide-react-native';
import { COUNTRIES, Country } from '../../constants/countries';

export function CountryCodePicker({ dial, onSelect }: { dial: string; onSelect: (dial: string) => void }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');

  const current = COUNTRIES.find((c) => c.dial === dial) ?? COUNTRIES[0];
  const filtered = q
    ? COUNTRIES.filter(
        (c) => c.name.toLowerCase().includes(q.toLowerCase()) || c.dial.includes(q) || c.iso.toLowerCase().includes(q.toLowerCase()),
      )
    : COUNTRIES;

  const pick = (c: Country) => { onSelect(c.dial); setOpen(false); setQ(''); };

  return (
    <>
      <TouchableOpacity
        onPress={() => setOpen(true)}
        className="flex-row items-center bg-card rounded-xl px-3"
        style={{ height: 50 }}
      >
        <Text className="text-base mr-1">{current.flag}</Text>
        <Text className="text-textPrimary text-base font-semibold mr-1">{current.dial}</Text>
        <ChevronDown size={16} color="#9A9AA2" />
      </TouchableOpacity>

      <Modal visible={open} animationType="slide" transparent onRequestClose={() => setOpen(false)}>
        <View className="flex-1 justify-end bg-black/40">
          <View className="bg-elevated rounded-t-2xl pt-4" style={{ maxHeight: '75%' }}>
            <View className="flex-row items-center justify-between px-5 mb-3">
              <Text className="text-textPrimary text-lg font-bold">Select country</Text>
              <TouchableOpacity onPress={() => setOpen(false)}><X size={22} color="#3C4663" /></TouchableOpacity>
            </View>
            <View className="flex-row items-center bg-card rounded-xl px-4 py-2.5 mx-5 mb-3">
              <Search size={16} color="#9A9AA2" />
              <TextInput
                value={q}
                onChangeText={setQ}
                placeholder="Search country or code"
                placeholderTextColor="#9A9AA2"
                className="flex-1 ml-2"
                style={{ color: '#16264A' }}
              />
            </View>
            <FlatList
              data={filtered}
              keyExtractor={(c) => c.iso}
              keyboardShouldPersistTaps="handled"
              renderItem={({ item }) => (
                <TouchableOpacity onPress={() => pick(item)} className="flex-row items-center px-5 py-3 border-b border-border">
                  <Text className="text-lg mr-3">{item.flag}</Text>
                  <Text className="text-textPrimary text-base flex-1">{item.name}</Text>
                  <Text className="text-textMuted text-base">{item.dial}</Text>
                </TouchableOpacity>
              )}
            />
          </View>
        </View>
      </Modal>
    </>
  );
}
