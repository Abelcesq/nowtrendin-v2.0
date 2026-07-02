# Expo HAS CHANGED

Read the exact versioned docs at https://docs.expo.dev/versions/v56.0.0/ before writing any code.

# Design System — MANDATORY

This app has an enforced visual design ("Aurora"). **Any code you add or merge — new cards,
analysis sections, screens, fields — MUST follow it automatically, with no exceptions.** Read it
before touching the frontend, and apply it as part of every change/merge so the UI/UX stays intact.

@DESIGN_SYSTEM.md

Quick rules: approved color tokens only (no raw hex, no neon green/orange, gold only on the Home
hero score); Plus Jakarta Sans (auto-applied); Title Case for trend/topic names (use `TopicTitle`
or `titleCaseTopic`); **borderless** cards (use `<Card>` / `bg-card`, never a border outline);
build screens with `<Screen>` and analysis sections with `<Collapsible>` to inherit the motion;
touch-only (no hover). See DESIGN_SYSTEM.md for the full contract and the reusable primitives in
`components/ui`.
