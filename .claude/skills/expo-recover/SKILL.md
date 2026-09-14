---
name: expo-recover
description: NowTrendIn Expo recovery runbook — when the Expo app is timing out on the user's phone or won't connect (common after a Windows crash, reboot, or sleep). Walks through the proven diagnostic order: same-WiFi check FIRST, then port 8081 conflicts, then Metro restart, then the inbound firewall rule. Use when the user says "app keeps timing out", "Expo isn't loading", "phone can't connect to Metro", "my computer crashed and now Expo broken", "reload Expo", or shows an ERR_NGROK or connection-refused error.
---

# /expo-recover — Post-crash Expo Metro recovery runbook

You diagnose and fix Expo Metro connection problems for NowTrendIn 2.0 in **strict diagnostic order**. Do NOT skip steps or jump ahead — each step has been load-bearing in past incidents, and skipping the early ones wastes the user's time on wrong-direction debugging.

**Project frontend**: `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\frontend`
**Canonical phone URL**: `exp://192.168.68.52:8081` (LAN IP may shift if router DHCP changes — re-verify via `ipconfig`)

## The ORDER (do NOT reorder)

### Step 1 — Same-WiFi check (ALWAYS FIRST)

Before any technical debugging, get the PC's current WiFi name:

```powershell
Get-NetConnectionProfile | Select-Object Name, InterfaceAlias
```

Then **ASK the user**: "Your PC is on WiFi `<network_name>`. Is your phone connected to that **same** network right now?"

- If user says NO or "let me check" — STOP. Network mismatch is the #1 cause of timeouts. Wait for them to confirm same-network before proceeding.
- If user confirms same network — proceed to Step 2.

This step looks trivial but the user has explicitly flagged it as the one check that catches more issues than any other. **Skipping it is a saved-memory violation** (see `feedback-expo-same-network-first` in MEMORY.md).

### Step 2 — Verify LAN IP hasn't changed

```powershell
ipconfig | Select-String -Pattern "IPv4 Address.*: (192\.|10\.)"
```

If the IPv4 address is no longer `192.168.68.52`, the phone URL must change to match. Tell the user the new URL.

### Step 3 — Check what's on port 8081

```powershell
Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue | Select-Object LocalPort, State, OwningProcess
```

Three outcomes:
- **Empty (nothing on 8081)** → no Metro running, proceed to Step 4 to start it
- **One PID in Listen state** → Metro is up; skip to Step 5 (firewall) since the problem is reachability not Metro
- **Multiple holders or stuck CLOSE_WAIT** → kill the stale process, then start Metro:
  ```powershell
  Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
  ```

NEVER accept the "Use port 8082 instead?" fallback. Port must be **8081** per saved-memory rule (`feedback-expo-port-8081`).

### Step 4 — Start Metro in LAN mode

Tell the user to run this in their own terminal (not via tools — interactive Metro needs a real TTY for the QR display):

```
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\frontend"
npx expo start --lan
```

Confirm with them they see:
- `Metro waiting on exp://192.168.68.52:8081`
- A QR code rendered in the terminal

### Step 5 — Verify the inbound firewall rule

Without elevation, try:

```powershell
Get-NetFirewallRule -DisplayName "Expo Metro 8081" -ErrorAction SilentlyContinue | Select-Object DisplayName, Enabled, Profile
```

- If rule shows `Enabled: True` → firewall is fine
- If empty or `Enabled: False` → the rule was dropped (this happens after Windows crashes — confirmed pattern). Tell the user to run the recovery script at their Desktop:
  ```
  Desktop\fix-expo-firewall.ps1   (right-click → Run with PowerShell, approve UAC)
  ```
  If that file doesn't exist, regenerate it (see "Firewall script" section below).

### Step 6 — Phone-side test

Have the user open `http://192.168.68.52:8081` in their **phone's browser** (not Expo Go). 
- If it loads a page or JSON → reachability is good, the problem is in Expo Go itself (have them force-quit and reopen Expo Go, then re-enter `exp://192.168.68.52:8081`)
- If it times out → router AP-isolation is the most likely remaining cause. Ask if they're on a guest WiFi network; have them switch to the main network.

### ❌ Things NOT to suggest

- **Do not** recommend changing Windows network profile from Public to Private. The user has confirmed this is not necessary — the app worked in the past on Public. (Saved-memory rule.)
- **Do not** suggest tunneling via ngrok (`npx expo start --tunnel`) as a fix. It worked once but introduced new failure modes (`ERR_NGROK_3200` subdomain churn). LAN mode is the canonical path.
- **Do not** skip Step 1 even if the user "obviously" knows their network. The check is fast and catches the common case.

## Firewall script (if missing from Desktop)

Recreate `C:\Users\acinv\OneDrive\Desktop\fix-expo-firewall.ps1` with:

```powershell
Get-NetFirewallRule -DisplayName "Expo Metro 8081" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName "Expo Metro 8081" -Direction Inbound -LocalPort 8081 -Protocol TCP -Action Allow -Profile Any | Out-Null
Write-Host "Done. Phone should now connect to exp://192.168.68.52:8081" -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```

## Reporting back

Once recovered, give a one-line summary like:
> **Fixed** — root cause was [phone on wrong WiFi / stale process on 8081 / firewall rule dropped]. Metro is up on `exp://192.168.68.52:8081`, phone connecting.

If you escalated to the phone-browser test and that succeeded but Expo Go still won't connect, escalate further (Expo Go version mismatch, Hermes/JSC, etc.) rather than blindly retrying.
