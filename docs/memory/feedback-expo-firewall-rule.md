---
name: feedback-expo-firewall-rule
description: NowTrendIn Expo Metro requires an inbound Windows Firewall rule for TCP 8081 — without it phone connections time out
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

The user's phone reaching Expo Metro on `exp://192.168.68.52:8081` requires a **Windows Firewall inbound rule for TCP 8081**. Without it the phone times out connecting even when Metro is up.

**Why:** Confirmed twice now — once during initial Expo setup and once after the computer crashed. The fix both times was the firewall rule. The user explicitly confirmed "SUCCESS!! It was the firewall!" the first time. Windows can drop or disable the rule after major OS events (crash, restart, Windows Update).

**How to apply:**
- **FIRST**, before checking the firewall, confirm the phone is on the same WiFi as the PC — see [[feedback-expo-same-network-first]]. Network mismatch is the most common cause and a faster check.
- Then verify the firewall rule exists:
  ```powershell
  Get-NetFirewallRule -DisplayName "Expo Metro 8081" -ErrorAction SilentlyContinue
  ```
- If missing OR disabled, recreate (requires admin elevation):
  ```powershell
  Start-Process powershell -Verb RunAs -ArgumentList '-Command "New-NetFirewallRule -DisplayName \"Expo Metro 8081\" -Direction Inbound -LocalPort 8081 -Protocol TCP -Action Allow"'
  ```
- If the rule exists but is `Enabled: False`, enable it:
  ```powershell
  Set-NetFirewallRule -DisplayName "Expo Metro 8081" -Enabled True
  ```
- Phone URL is `exp://192.168.68.52:8081`.
- Do NOT recommend changing Windows network profile from Public to Private. The user has confirmed this is not necessary — the app has worked in the past with the current Public profile, so that path is a red herring.

Related: [[feedback-expo-same-network-first]] (check first), [[feedback-expo-port-8081]] — port must be 8081, never 8082.
