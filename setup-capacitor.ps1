# One-time setup + rebuild for the Capacitor shell (desktop via Electron, plus
# optional Android/iOS WebView wraps) around the Expo web build.
#
# Usage — from any PowerShell window (no cd needed):
#   powershell -ExecutionPolicy Bypass -File "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\setup-capacitor.ps1"
#
# Prerequisite: Node.js LTS installed (https://nodejs.org) in a FRESH terminal.
# Safe to re-run: platform adds are skipped when already present; the web bundle
# and sync refresh every run (so re-run this after any frontend change).

$root = $PSScriptRoot

Write-Host "[0/6] Preflight: Node..." -ForegroundColor Cyan
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Error "Node.js not found. Install the LTS from https://nodejs.org, open a NEW PowerShell window, and re-run."
    exit 1
}
Write-Host ("      node " + (node -v))

Write-Host "[1/6] Building web bundle (npx expo export)..." -ForegroundColor Cyan
Push-Location "$root\frontend"
npx expo export --platform web
if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "Expo export failed."; exit 1 }
Pop-Location

Write-Host "[2/6] Copying frontend\dist -> capacitor\www..." -ForegroundColor Cyan
if (Test-Path "$root\capacitor\www") { Remove-Item -Recurse -Force "$root\capacitor\www" }
Copy-Item -Recurse "$root\frontend\dist" "$root\capacitor\www"

Push-Location "$root\capacitor"

Write-Host "[3/6] Installing Capacitor packages..." -ForegroundColor Cyan
npm install @capacitor/core@latest @capacitor/cli@latest @capacitor/android@latest @capacitor/ios@latest
if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "npm install of Capacitor failed."; exit 1 }
npm install @capacitor-community/electron@latest
if ($LASTEXITCODE -ne 0) { Write-Warning "Electron platform package failed to install — desktop step will be skipped. (Fallback: plain Electron wrapper; ask Claude.)" }

Write-Host "[4/6] Adding platforms (skipped when already present)..." -ForegroundColor Cyan
if (-not (Test-Path "$root\capacitor\electron")) {
    npx cap add @capacitor-community/electron
    if ($LASTEXITCODE -ne 0) { Write-Warning "cap add electron failed — see output above." }
}
if (-not (Test-Path "$root\capacitor\android")) {
    npx cap add android
    if ($LASTEXITCODE -ne 0) { Write-Warning "cap add android failed (building also needs Android Studio)." }
}
if (-not (Test-Path "$root\capacitor\ios")) {
    npx cap add ios
    if ($LASTEXITCODE -ne 0) { Write-Warning "cap add ios failed — expected on Windows; iOS builds need a Mac anyway." }
}

Write-Host "[5/6] Syncing web bundle into platforms..." -ForegroundColor Cyan
npx cap sync
if ($LASTEXITCODE -ne 0) { Write-Warning "cap sync reported errors (iOS sync errors on Windows are normal)." }

Pop-Location

Write-Host "[6/6] Done. Next steps:" -ForegroundColor Green
Write-Host "  Desktop (run):     cd capacitor\electron ; npm install ; npm run electron:start"
Write-Host "  Desktop (package): cd capacitor\electron ; npm run electron:make"
Write-Host "  Android:           cd capacitor ; npx cap open android   (needs Android Studio)"
Write-Host "  iOS:               needs a Mac with Xcode (capacitor\ios)"
Write-Host "  See docs\PLATFORMS.md for the full platform map."
