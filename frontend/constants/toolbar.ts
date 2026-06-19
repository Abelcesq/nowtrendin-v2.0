import { Search, Clock, Bell, Star, Heart, type LucideIcon } from 'lucide-react-native';

// The customizable bottom toolbar. Home (index) and Profile are FIXED ends and
// are NOT part of this pool — only the 3 middle slots are user-editable.
// Each candidate must map to a real route file under app/(app)/.
export interface ToolbarItem {
  key: string;
  route: string;        // (app)-level route name
  label: string;
  icon: LucideIcon;
  feature?: 'canSearch'; // tier feature gate (constants/tiers canAccess) — hides if not entitled
}

export const TOOLBAR_CANDIDATES: ToolbarItem[] = [
  { key: 'search', route: 'search', label: 'Search', icon: Search, feature: 'canSearch' },
  { key: 'history', route: 'history', label: 'History', icon: Clock },
  { key: 'alerts', route: 'alerts', label: 'Alerts', icon: Bell },
  { key: 'watchlists', route: 'watchlists', label: 'Watchlist', icon: Star },
  { key: 'favorites', route: 'favorites', label: 'Favorites', icon: Heart },
];

export const DEFAULT_TOOLBAR = ['search', 'history', 'alerts'];
export const TOOLBAR_SLOTS = 3;
