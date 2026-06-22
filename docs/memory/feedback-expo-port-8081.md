---
name: feedback-expo-port-8081
description: User wants Expo Metro to always run on port 8081 — kill stale processes rather than fall back to 8082
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

Always start Expo Metro on **port 8081** for NowTrendIn 2.0 — never accept the "Use port 8082 instead?" fallback.

**Why:** 8081 is the React Native convention and the app's defaults assume it. Switching to 8082 means re-teaching the phone (different URL each time), inconsistent firewall coverage, and confusion across restarts. The user explicitly said "let's keep this as a rule."

**How to apply:**
- Before running `npx expo start --lan`, kill anything holding 8081:
  ```powershell
  Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
  ```
- If `npx expo start` ever prompts "Use port 8082 instead?", the answer is NO. Kill the offending process and retry on 8081.
- Phone URL is always `exp://192.168.68.52:8081` (the user's LAN IP, [[project-nowtrendin-2]]).
- If I ever start Metro in a background task, document the PID so it can be killed cleanly later — do NOT leave orphan Metro processes.

Related: [[feedback-expo-firewall-rule]] — the inbound TCP 8081 firewall rule must exist for the phone to reach Metro.
