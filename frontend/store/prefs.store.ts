import { create } from 'zustand';
import * as Storage from '../lib/storage';
import { DEFAULT_TOOLBAR } from '../constants/toolbar';

// Local-only UI preferences (not server-synced). Currently: the customizable
// bottom-toolbar layout (which 3 features occupy the middle slots, in order).
const KEY = 'toolbar_pref';

interface PrefsState {
  toolbar: string[];
  loaded: boolean;
  load: () => void;
  setToolbar: (keys: string[]) => void;
}

export const usePrefsStore = create<PrefsState>((set) => ({
  toolbar: DEFAULT_TOOLBAR,
  loaded: false,
  load: () => {
    Storage.getItem(KEY)
      .then((raw) => {
        let next = DEFAULT_TOOLBAR;
        if (raw) {
          try {
            const p = JSON.parse(raw);
            if (Array.isArray(p) && p.length) next = p.filter((k) => typeof k === 'string');
          } catch { /* keep default */ }
        }
        set({ toolbar: next, loaded: true });
      })
      .catch(() => set({ loaded: true }));
  },
  setToolbar: (keys) => {
    Storage.setItem(KEY, JSON.stringify(keys)).catch(() => {});
    set({ toolbar: keys });
  },
}));
