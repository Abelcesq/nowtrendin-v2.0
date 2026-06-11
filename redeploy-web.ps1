# Rebuild the Expo web bundle and redeploy it to the public Heroku web app (nowtrendin-web).
# PowerShell version of redeploy-web.sh (bash &&/|| don't work in PowerShell 5.1).
#
# Usage — from a PowerShell window:
#   cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
#   .\redeploy-web.ps1
#
# The Heroku push will pop up Git Credential Manager for git.heroku.com:
#   Username = your Heroku email,  Password = your Heroku API KEY (not your login password).

$root = $PSScriptRoot

Write-Host "[1/4] Building web bundle (npx expo export)..." -ForegroundColor Cyan
Push-Location "$root\frontend"
npx expo export --platform web
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Error "Expo export failed. Check Node is installed ('node -v') and deps are present ('npm install' in frontend)."
    exit 1
}
Pop-Location

Write-Host "[2/4] Refreshing web-deploy\dist..." -ForegroundColor Cyan
if (Test-Path "$root\web-deploy\dist") { Remove-Item -Recurse -Force "$root\web-deploy\dist" }
Copy-Item -Recurse "$root\frontend\dist" "$root\web-deploy\dist"

Write-Host "[3/4] Committing the new bundle..." -ForegroundColor Cyan
Push-Location "$root\web-deploy"
git add -A
git commit -m "web rebuild $(Get-Date -Format yyyy-MM-dd)"   # harmless if nothing changed

Write-Host "[4/4] Deploying to Heroku (nowtrendin-web)..." -ForegroundColor Cyan
git push heroku HEAD:main
$pushCode = $LASTEXITCODE
Pop-Location

if ($pushCode -ne 0) {
    Write-Error "Heroku push failed. If it was an auth popup: Username = Heroku email, Password = Heroku API key."
    exit 1
}
Write-Host "Done -> https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/" -ForegroundColor Green
