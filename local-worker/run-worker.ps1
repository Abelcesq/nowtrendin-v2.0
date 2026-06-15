# ── NowTrendIn v2.0 — LOCAL primary scorer ───────────────────────────────
# Runs the heavy scoring (score_all_topics) against the SHARED cloud Postgres,
# freeing the Heroku dyno from the ~400MB scoring spike. Heroku stays on
# collect-every-6h + failover scoring (it scores only if this worker goes quiet
# for > SCORE_STALE_MIN). One database, one source of truth.
#
# Usage:  cd local-worker ; .\run-worker.ps1
# Leave this window running. Close it (or sleep the PC) and Heroku failover
# resumes scoring automatically within ~20 min.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) { Write-Error "Missing $envFile (secrets). Regenerate from Heroku config."; exit 1 }

# Load .env into the process environment
Get-Content $envFile | Where-Object { $_ -and ($_ -notmatch '^\s*#') } | ForEach-Object {
    $i = $_.IndexOf('=')
    if ($i -gt 0) {
        $k = $_.Substring(0, $i).Trim()
        $v = $_.Substring($i + 1).Trim()
        [Environment]::SetEnvironmentVariable($k, $v, 'Process')
    }
}

$py = Join-Path $root "venv\Scripts\python.exe"
$engine = Join-Path $root "..\transfer"
Write-Host "Local scorer starting — WORKER_COLLECT=$($env:WORKER_COLLECT) WORKER_SCORE=$($env:WORKER_SCORE) SCORE_INTERVAL_MIN=$($env:SCORE_INTERVAL_MIN)" -ForegroundColor Cyan
Write-Host "DB: shared v2 Postgres | Heroku handles collection + failover. Keep this window open." -ForegroundColor DarkGray
Set-Location $engine
& $py gravitational_anomaly_detector.py --mode=worker
