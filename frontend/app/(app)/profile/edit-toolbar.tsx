import { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, Home, User, Lock, Check } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { useAuthStore } from '../../../store/auth.store';
import { usePrefsStore } from '../../../store/prefs.store';
import { canAccess, TierID } from '../../../constants/tiers';
import { TOOLBAR_CANDIDATES, TOOLBAR_SLOTS, ToolbarItem } from '../../../constants/toolbar';

// Edit Toolbar Icons — pick which features fill the 3 middle bottom-tab slots.
// Home and Profile are fixed ends and can't be changed. Tap to add (in order);
// tap a selected one to remove. Exactly 3 must be chosen to save.
export default function EditToolbar() {
  const router = useRouter();
  const tier = (useAuthStore((s) => s.user?.tier) ?? 'consumer') as TierID;
  const toolbar = usePrefsStore((s) => s.toolbar);
  const setToolbar = usePrefsStore((s) => s.setToolbar);

  const allowed = (c: ToolbarItem) => !c.feature || canAccess(tier, c.feature);
  // seed with current selection, dropping anything not entitled
  const [sel, setSel] = useState<string[]>(
    toolbar.filter((k) => { const c = TOOLBAR_CANDIDATES.find((x) => x.key === k); return c && allowed(c); })
  );

  const toggle = (c: ToolbarItem) => {
    if (!allowed(c)) return;
    setSel((cur) =>
      cur.includes(c.key) ? cur.filter((k) => k !== c.key)
        : cur.length >= TOOLBAR_SLOTS ? cur
          : [...cur, c.key]
    );
  };

  const canSave = sel.length === TOOLBAR_SLOTS;
  const save = () => { if (!canSave) return; setToolbar(sel); router.back(); };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="pt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#3C4663" /><Text className="text-textSecondary text-base">Back</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-2xl font-bold mb-1">Edit Toolbar Icons</Text>
      <Text className="text-textMuted text-sm mb-4">
        Choose the {TOOLBAR_SLOTS} features for your bottom toolbar. Home and Profile stay fixed at the ends.
      </Text>

      {/* Fixed ends preview */}
      <View className="flex-row items-center gap-2 mb-5">
        <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full bg-bg">
          <Home size={14} color="#8A8F9C" /><Text className="text-textMuted text-xs font-semibold">Home</Text>
          <Lock size={11} color="#8A8F9C" />
        </View>
        <Text className="text-textMuted text-xs">· {sel.length}/{TOOLBAR_SLOTS} chosen ·</Text>
        <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full bg-bg">
          <User size={14} color="#8A8F9C" /><Text className="text-textMuted text-xs font-semibold">Profile</Text>
          <Lock size={11} color="#8A8F9C" />
        </View>
      </View>

      {TOOLBAR_CANDIDATES.map((c) => {
        const Icon = c.icon;
        const idx = sel.indexOf(c.key);
        const on = idx >= 0;
        const gated = !allowed(c);
        const full = !on && sel.length >= TOOLBAR_SLOTS;
        return (
          <TouchableOpacity
            key={c.key}
            onPress={() => toggle(c)}
            disabled={gated}
            className="flex-row items-center justify-between bg-card rounded-xl p-3.5 mb-2.5"
            style={{ borderColor: on ? '#2E7D5B' : '#ECECEC', opacity: gated || full ? 0.45 : 1 }}
          >
            <View className="flex-row items-center gap-3">
              <Icon size={20} color={on ? '#2E7D5B' : '#8A8F9C'} />
              <Text className="text-textPrimary text-base">{c.label}</Text>
              {gated && <View className="flex-row items-center gap-1"><Lock size={12} color="#8A8F9C" /><Text className="text-textMuted text-[11px]">Upgrade</Text></View>}
            </View>
            {on ? (
              <View className="w-6 h-6 rounded-full items-center justify-center" style={{ backgroundColor: '#2E7D5B' }}>
                <Text className="text-white text-xs font-bold">{idx + 1}</Text>
              </View>
            ) : (
              <View className="w-6 h-6 rounded-full" />
            )}
          </TouchableOpacity>
        );
      })}

      <TouchableOpacity
        onPress={save}
        disabled={!canSave}
        className="flex-row items-center justify-center gap-2 rounded-xl py-3.5 mt-3"
        style={{ backgroundColor: canSave ? '#2E7D5B' : '#D8DCE3' }}
      >
        <Check size={18} color="#FFFFFF" />
        <Text className="text-white font-semibold">{canSave ? 'Save toolbar' : `Pick ${TOOLBAR_SLOTS - sel.length} more`}</Text>
      </TouchableOpacity>
    </Screen>
  );
}
