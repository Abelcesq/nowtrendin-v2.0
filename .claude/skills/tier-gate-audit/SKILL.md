---
name: tier-gate-audit
description: NowTrendIn access-control audit — confirms every restricted feature in the frontend uses canAccess()/TierGate and flags any HARDCODED tier checks outside constants/tiers.ts. Protects against access-control drift as features are added. Use when the user says "audit tiers", "check access control", "tier audit", or asks if Consumer/Business/Enterprise gating is correct anywhere.
---

# /tier-gate-audit — Frontend access-control integrity check

You audit the frontend codebase for tier-gating violations.

**Frontend root**: `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\frontend`
**Source of truth**: `constants/tiers.ts` — defines `canAccess(tier, feature)`, `isDataAccessible(tier, dataAgeMs)`, `gradeTokens`, etc.
**Gating component**: `components/trends/TierGate.tsx`

## Steps

1. **Read `constants/tiers.ts`** first to know which features are defined and which functions exist.

2. **Find all tier-decision points in the codebase** with Grep:
   - `Grep "membership|tier" type:tsx` — every screen that reads the user's tier
   - `Grep "consumer|business|enterprise" type:tsx` — every hardcoded tier reference
   - `Grep "canAccess|TierGate|isDataAccessible" type:tsx` — every legitimate gate call

3. **Classify each hit**:
   - **OK**: uses `canAccess(tier, feature)`, `isDataAccessible(...)`, wrapped in `<TierGate>`, OR is in `constants/tiers.ts` itself
   - **VIOLATION (high)**: hardcoded `if (tier === 'consumer')` / `tier !== 'enterprise'` style check OUTSIDE tiers.ts — these will silently drift when tiers change
   - **VIOLATION (low)**: tier name in a display string (label), no logic — note it but don't flag
   - **ORPHAN**: a feature is `canAccess`-able but doesn't appear in `constants/tiers.ts`'s feature list — feature doesn't exist in source of truth

4. **Check restricted screens** are wrapped:
   - Search tab (Business + Enterprise only)
   - Pull Trends button (Enterprise only)
   - Direct query / Search Current Trends (Business + Enterprise)
   - Alerts (depends on plan)
   - Grade tool (all three tiers but with `gradeTokens` quota)
   
   Each MUST either be inside `<TierGate>` or have an early-return guard using `canAccess()`. Flag any that don't.

5. **Verify data-aging waterfall**:
   - Grep for `dataFreshness` / `first_scored_at` usage — should ONLY be gated via `isDataAccessible(tier, age)`, never hardcoded.

6. **Report** as three sections:
   - ✅ Compliant gates (count)
   - ⚠ Violations to fix (file:line, brief diagnosis)
   - ❓ Orphan features (in code but not in tiers.ts feature list)

## Safety

- Do NOT modify any file — this is an audit, output-only.
- Frontend AGENTS.md says "Read the exact versioned docs at https://docs.expo.dev/versions/v56.0.0/ before writing any code" — but this skill writes nothing, only reads.
