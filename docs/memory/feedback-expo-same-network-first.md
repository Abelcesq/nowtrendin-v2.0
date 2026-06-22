---
name: feedback-expo-same-network-first
description: "When the NowTrendIn Expo app times out on the user's phone, ALWAYS confirm phone + PC are on the same WiFi BEFORE any other troubleshooting"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

When the user reports "the app keeps timing out" / "Expo Go won't connect", the **FIRST** check is always: is the phone on the **same WiFi network** as the PC?

**Why:** Confirmed during a real session — after a crash, the user's app timed out and the diagnosis path included firewall, port, and network-profile checks. The user clarified that they don't want to change Public→Private network profile (since the app worked in the past on Public), and that the truly load-bearing check across every timeout debug is same-network. Asking this up front avoids minutes of wrong-direction debugging.

**How to apply:**
- Before ANY firewall / port / process / Node.js debugging, ask (or have the user confirm): "Is your phone connected to the same WiFi as the PC right now?"
- The PC's WiFi shows up via `Get-NetConnectionProfile | Select-Object Name` — tell the user that network name and ask if their phone matches it.
- ONLY after same-network is confirmed should I proceed to: (a) Metro running on 8081, (b) firewall rule for 8081, (c) process holding the port, etc.
- Do NOT recommend changing the Windows network profile (Public → Private) as a fix. The user explicitly said this is not necessary because the app worked in the past with the current settings. Leave network profile alone.

Related: [[feedback-expo-firewall-rule]], [[feedback-expo-port-8081]], [[project-nowtrendin-2]]
