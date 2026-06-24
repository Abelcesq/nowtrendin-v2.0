#Requires -Version 5.1
<#
.SYNOPSIS
    Now TrendIn scoring-engine data-integrity monitor.
    Runs 9 invariant checks against the live Heroku engine and prints
    a PASS / FAIL / WARN / INFO report with a summary.

.NOTES
    PowerShell 5.1 compatible - no && / || / ternary / null-coalescing.
    Exit code 1 if any check is FAIL; 0 otherwise.
    Run: .\monitoring\integrity-check.ps1
#>

# v2 engine — the ONLY active engine (corrected 2026-06-24; was the frozen 1.0
# nowtrendin-e62dcb9ecb69, which would QA the wrong/stale engine). Override with -Base.
$BASE = "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com"
$VALID_STAGES = @("BREAKOUT","STRONG","EMERGING","WATCHING","MONITORING","VIRAL","DECAY","WATCH")
# Legacy anchor set the continuous formula should now exceed (at 4+ platforms):
$LEGACY_ANCHORS = @(0,20,35,50,65,80,90,95,100)

# ── Result tracking ────────────────────────────────────────────────────────────
$Results   = [System.Collections.Generic.List[PSCustomObject]]::new()
$FailCount = 0
$WarnCount = 0
$PassCount = 0

function Add-Result {
    param(
        [string]$Status,   # PASS | FAIL | WARN | INFO
        [string]$Check,
        [string]$Detail
    )
    $script:Results.Add([PSCustomObject]@{ Status = $Status; Check = $Check; Detail = $Detail })
    switch ($Status) {
        "PASS" { $script:PassCount++ }
        "FAIL" { $script:FailCount++ }
        "WARN" { $script:WarnCount++ }
    }
}

function Invoke-API {
    param([string]$Path, [hashtable]$Headers = @{})
    $url = "$BASE$Path"
    try {
        $resp = Invoke-RestMethod -Uri $url -Method GET -Headers $Headers -ErrorAction Stop
        return $resp
    } catch {
        return $null
    }
}

# ── Helper: safe property access on PSObject / hashtable ─────────────────────
function Get-Prop {
    param($Obj, [string]$Key)
    if ($null -eq $Obj) { return $null }
    if ($Obj -is [hashtable] -or $Obj -is [System.Collections.Specialized.OrderedDictionary]) {
        if ($Obj.ContainsKey($Key)) { return $Obj[$Key] }
        return $null
    }
    $prop = $Obj.PSObject.Properties[$Key]
    if ($null -ne $prop) { return $prop.Value }
    return $null
}

function Has-Prop {
    param($Obj, [string]$Key)
    if ($null -eq $Obj) { return $false }
    if ($Obj -is [hashtable] -or $Obj -is [System.Collections.Specialized.OrderedDictionary]) {
        return $Obj.ContainsKey($Key)
    }
    return ($null -ne $Obj.PSObject.Properties[$Key])
}

Write-Host ""
Write-Host "============================================================"
Write-Host " Now TrendIn - Engine Integrity Check"
Write-Host " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"
Write-Host " Target: $BASE"
Write-Host "============================================================"
Write-Host ""

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1 - /health status
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[1/9] Health endpoint ..."
$health = Invoke-API "/health"
if ($null -eq $health) {
    Add-Result "FAIL" "Health endpoint" "/health unreachable or returned non-200"
} else {
    $hs = Get-Prop $health "status"
    if ($hs -eq "operational") {
        Add-Result "PASS" "Health endpoint" "status = '$hs'"
    } else {
        Add-Result "FAIL" "Health endpoint" "status = '$hs' (expected 'operational')"
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2 - /scores?limit=50 score-range validation
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[2/9] Score list range validation ..."
$scoreList = Invoke-API "/scores?limit=50"
$listRows  = $null

if ($null -eq $scoreList) {
    Add-Result "FAIL" "Score list" "/scores?limit=50 unreachable"
} else {
    $listRows = Get-Prop $scoreList "results"
    if ($null -eq $listRows) {
        Add-Result "FAIL" "Score list" "Response has no 'results' key"
    } else {
        $rangeErrors   = [System.Collections.Generic.List[string]]::new()
        $missingKeyErr = [System.Collections.Generic.List[string]]::new()
        $rowIdx = 0

        foreach ($row in $listRows) {
            $rowIdx++
            $tk = Get-Prop $row "topic_key"
            if ([string]::IsNullOrEmpty($tk)) {
                $missingKeyErr.Add("row $rowIdx missing topic_key")
            }

            foreach ($field in @("detection_score","confidence_score","overall_score")) {
                $val = Get-Prop $row $field
                if ($null -eq $val) {
                    $rangeErrors.Add("row $rowIdx ($tk): $field is null")
                } else {
                    $fval = [double]$val
                    if ($fval -lt 0 -or $fval -gt 100) {
                        $rangeErrors.Add("row $rowIdx ($tk): $field = $fval out of [0,100]")
                    }
                }
            }

            # nowtrendin_score (optional field - only if present)
            if (Has-Prop $row "nowtrendin_score") {
                $ns = Get-Prop $row "nowtrendin_score"
                if ($null -ne $ns) {
                    $nsv = [double]$ns
                    if ($nsv -lt 0 -or $nsv -gt 100) {
                        $rangeErrors.Add("row $rowIdx ($tk): nowtrendin_score = $nsv out of [0,100]")
                    }
                }
            }
        }

        $totalErrors = $missingKeyErr.Count + $rangeErrors.Count
        if ($totalErrors -eq 0) {
            Add-Result "PASS" "Score list ranges" "$($listRows.Count) rows - all keys present, all scores in [0,100]"
        } else {
            $allErrs = ($missingKeyErr + $rangeErrors) -join "; "
            Add-Result "FAIL" "Score list ranges" "$totalErrors error(s): $allErrs"
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3 - Trade-secret hygiene on /scores/{topic_key}
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[3/9] Trade-secret hygiene ..."
$firstKey = $null
$detail   = $null

if ($null -ne $listRows -and $listRows.Count -gt 0) {
    $firstKey = Get-Prop $listRows[0] "topic_key"
}

if ([string]::IsNullOrEmpty($firstKey)) {
    Add-Result "FAIL" "Trade-secret hygiene" "Cannot test - no topic_key available from /scores"
} else {
    $detail = Invoke-API "/scores/$firstKey"
    if ($null -eq $detail) {
        Add-Result "FAIL" "Trade-secret hygiene" "/scores/$firstKey unreachable"
    } else {
        $leaks = [System.Collections.Generic.List[string]]::new()

        # Check each component for weight_* keys
        $components = Get-Prop $detail "components"
        if ($null -ne $components) {
            $compNames = @()
            if ($components -is [hashtable] -or $components -is [System.Collections.Specialized.OrderedDictionary]) {
                $compNames = $components.Keys
            } else {
                $compNames = $components.PSObject.Properties.Name
            }

            foreach ($cname in $compNames) {
                $comp = Get-Prop $components $cname
                foreach ($wk in @("weight_overall","weight_detect","weight_conf")) {
                    if (Has-Prop $comp $wk) {
                        $leaks.Add("components.$cname.$wk exposed")
                    }
                }
            }
        }

        # Check heisenberg for false-positive keys
        $heis = Get-Prop $detail "heisenberg"
        if ($null -ne $heis) {
            foreach ($fk in @("false_positive_detect","false_positive_confirm")) {
                if (Has-Prop $heis $fk) {
                    $leaks.Add("heisenberg.$fk exposed")
                }
            }
        }

        if ($leaks.Count -eq 0) {
            Add-Result "PASS" "Trade-secret hygiene" "No weight_* or false_positive_* keys found in /scores/$firstKey"
        } else {
            Add-Result "FAIL" "Trade-secret hygiene" "$($leaks.Count) leak(s): $($leaks -join '; ')"
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 4 - What-if fields presence on detail + WARN on list rows
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[4/9] What-if fields (nowtrending_gradient_*) ..."

if ($null -eq $detail) {
    Add-Result "WARN" "What-if fields" "Cannot test - detail response unavailable"
} else {
    $vs = Get-Prop $detail "velocity_scores"
    if ($null -eq $vs) {
        Add-Result "WARN" "What-if fields" "velocity_scores block absent in detail response"
    } else {
        # Determine if N score > 0
        $nScore = 0
        $nComp  = Get-Prop (Get-Prop $detail "components") "N_nowtrendin"
        if ($null -ne $nComp) {
            $nv = Get-Prop $nComp "score"
            if ($null -ne $nv) { $nScore = [double]$nv }
        }

        $hasGD  = Has-Prop $vs "nowtrending_gradient_detection"
        $hasGC  = Has-Prop $vs "nowtrending_gradient_confidence"
        $hasGDD = Has-Prop $vs "nowtrending_gradient_demand_driven"

        if ($nScore -gt 0) {
            if ($hasGD -and $hasGC -and $hasGDD) {
                $gdVal  = Get-Prop $vs "nowtrending_gradient_detection"
                $gcVal  = Get-Prop $vs "nowtrending_gradient_confidence"
                $gddVal = Get-Prop $vs "nowtrending_gradient_demand_driven"
                Add-Result "PASS" "What-if fields" "N>0 on '$firstKey': detection=$gdVal, confidence=$gcVal, demand_driven=$gddVal"
            } else {
                $missing = @()
                if (-not $hasGD)  { $missing += "nowtrending_gradient_detection" }
                if (-not $hasGC)  { $missing += "nowtrending_gradient_confidence" }
                if (-not $hasGDD) { $missing += "nowtrending_gradient_demand_driven" }
                Add-Result "FAIL" "What-if fields" "N=$nScore but missing: $($missing -join ', ') on /scores/$firstKey"
            }
        } else {
            # N=0: fields may legitimately be absent
            if ($hasGD -and $hasGC) {
                Add-Result "PASS" "What-if fields" "N=0 but what-if fields present (fine) on '$firstKey'"
            } else {
                Add-Result "WARN" "What-if fields" "N=0 on '$firstKey' - what-if fields not present (expected when N=0)"
            }
        }

        # WARN (not FAIL) if list rows lack the what-if fields - may be pre-deploy cache
        $listMissing = 0
        if ($null -ne $listRows) {
            foreach ($row in $listRows) {
                if (-not (Has-Prop $row "nowtrending_gradient_detection")) {
                    $listMissing++
                }
            }
        }
        if ($listMissing -gt 0) {
            Add-Result "WARN" "What-if fields (list)" "$listMissing/$($listRows.Count) list rows missing nowtrending_gradient_detection (may be pre-deploy cached payloads - re-score will fix)"
        } else {
            Add-Result "PASS" "What-if fields (list)" "All $($listRows.Count) list rows contain nowtrending_gradient_detection"
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 5 - Demand-driven logic: total_mentions guard
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[5/9] Demand-driven logic (total_mentions guard) ..."

if ($null -eq $listRows) {
    Add-Result "WARN" "Demand-driven logic" "Cannot test - list rows unavailable"
} else {
    $ddRows        = [System.Collections.Generic.List[PSCustomObject]]::new()
    $ddViolations  = [System.Collections.Generic.List[string]]::new()

    foreach ($row in $listRows) {
        $ddFlag = Get-Prop $row "nowtrending_gradient_demand_driven"
        if ($ddFlag -eq $true -or $ddFlag -eq "true") {
            $ddRows.Add($row)
            $tm = Get-Prop $row "total_mentions"
            if ($null -ne $tm -and [double]$tm -ge 15) {
                $tk2 = Get-Prop $row "topic_key"
                $ddViolations.Add("$tk2 demand_driven=true but total_mentions=$tm (>= 15)")
            }
        }
    }

    if ($ddRows.Count -eq 0) {
        Add-Result "PASS" "Demand-driven logic" "No demand_driven=true rows in list (flag not triggered or N=0 everywhere)"
    } elseif ($ddViolations.Count -eq 0) {
        Add-Result "PASS" "Demand-driven logic" "$($ddRows.Count) demand_driven=true row(s) - all have total_mentions < 15"
    } else {
        Add-Result "FAIL" "Demand-driven logic" "$($ddViolations.Count) violation(s): $($ddViolations -join '; ')"
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 6 - Frozen-score detector (top-5 topics by detection_score)
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[6/9] Frozen-score detector ..."

$top5 = [System.Collections.Generic.List[string]]::new()
if ($null -ne $listRows) {
    # Sort by detection_score descending, take first 5
    $sorted = $listRows | Sort-Object { [double](Get-Prop $_ "detection_score") } -Descending
    $cnt = 0
    foreach ($row in $sorted) {
        if ($cnt -ge 5) { break }
        $tk3 = Get-Prop $row "topic_key"
        if (-not [string]::IsNullOrEmpty($tk3)) {
            $top5.Add($tk3)
            $cnt++
        }
    }
}

if ($top5.Count -eq 0) {
    Add-Result "WARN" "Frozen-score detector" "No topics available for history check"
} else {
    $frozenTopics = [System.Collections.Generic.List[string]]::new()

    foreach ($tk4 in $top5) {
        $hist = Invoke-API "/scores/$tk4/score-history"
        if ($null -eq $hist) {
            Add-Result "WARN" "Frozen-score detector" "/scores/$tk4/score-history unreachable - skipped"
            continue
        }
        $histRows = Get-Prop $hist "rows"
        if ($null -eq $histRows -or $histRows.Count -lt 2) {
            # Not enough history to assess
            continue
        }

        # Take the 8 most recent (already ordered newest-first from API)
        $recentN = [Math]::Min(8, $histRows.Count)
        $recent  = @()
        $ridx = 0
        foreach ($hr in $histRows) {
            if ($ridx -ge $recentN) { break }
            $recent += $hr
            $ridx++
        }

        if ($recent.Count -lt 2) { continue }

        # Check if ALL detection values are identical
        $detVals = @()
        foreach ($hr2 in $recent) {
            $dv = Get-Prop $hr2 "detection"
            if ($null -ne $dv) { $detVals += [double]$dv }
        }

        if ($detVals.Count -lt 2) { continue }

        $allSame = $true
        $first   = $detVals[0]
        foreach ($dv2 in $detVals) {
            if ($dv2 -ne $first) { $allSame = $false; break }
        }

        if ($allSame) {
            $frozenTopics.Add("$tk4 (det=$first across $($detVals.Count) cycles)")
        }
    }

    if ($frozenTopics.Count -eq 0) {
        Add-Result "PASS" "Frozen-score detector" "None of the top-$($top5.Count) topics show frozen detection across last 8 cycles"
    } else {
        Add-Result "WARN" "Frozen-score detector" "$($frozenTopics.Count) topic(s) still showing frozen detection: $($frozenTopics -join '; ')"
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 7 - Platform-diversity spread (informational)
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[7/9] Platform-diversity spread ..."

if ($null -eq $listRows -or $listRows.Count -eq 0) {
    Add-Result "WARN" "Platform-diversity spread" "No list rows to analyze"
} else {
    $pdValues   = [System.Collections.Generic.List[double]]::new()
    $nonLegacy  = [System.Collections.Generic.List[double]]::new()

    foreach ($row in $listRows) {
        $pd = Get-Prop $row "platform_diversity"
        if ($null -ne $pd) {
            $pdv = [double]$pd
            $pdValues.Add($pdv)
            # Check if NOT in legacy anchor set (within 0.01 tolerance for float comparison)
            $isLegacy = $false
            foreach ($anchor in $LEGACY_ANCHORS) {
                if ([Math]::Abs($pdv - $anchor) -lt 0.01) {
                    $isLegacy = $true
                    break
                }
            }
            if (-not $isLegacy) {
                $nonLegacy.Add($pdv)
            }
        }
    }

    $distinctVals = $pdValues | Sort-Object -Unique
    $minPD = if ($pdValues.Count -gt 0) { ($pdValues | Measure-Object -Minimum).Minimum } else { $null }
    $maxPD = if ($pdValues.Count -gt 0) { ($pdValues | Measure-Object -Maximum).Maximum } else { $null }

    $distinctStr = ($distinctVals | ForEach-Object { [Math]::Round($_, 2) }) -join ", "
    $continuousProven = $nonLegacy.Count -gt 0

    $detail7 = "$($pdValues.Count) rows with platform_diversity; distinct values: [$distinctStr]; range [$minPD, $maxPD]"
    if ($continuousProven) {
        $nlSample = (($nonLegacy | Select-Object -Unique | Sort-Object | Select-Object -First 5) | ForEach-Object { [Math]::Round($_, 2) }) -join ", "
        $detail7 += " | CONTINUOUS formula confirmed: $($nonLegacy.Count) non-legacy value(s) e.g. $nlSample"
    } else {
        $detail7 += " | All values still in legacy anchor set - continuous formula not yet reflected in served data (re-score needed)"
    }
    Add-Result "INFO" "Platform-diversity spread" $detail7
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 8 - signal_stage values
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[8/9] Signal stage values ..."

if ($null -eq $listRows -or $listRows.Count -eq 0) {
    Add-Result "WARN" "Signal stage values" "No list rows to check"
} else {
    $badStages = [System.Collections.Generic.List[string]]::new()

    foreach ($row in $listRows) {
        $stage = Get-Prop $row "signal_stage"
        if ([string]::IsNullOrEmpty($stage)) {
            $tk5 = Get-Prop $row "topic_key"
            $badStages.Add("${tk5}: null/empty stage")
        } elseif ($stage -notin $VALID_STAGES) {
            $tk5 = Get-Prop $row "topic_key"
            $badStages.Add("${tk5}: '$stage'")
        }
    }

    if ($badStages.Count -eq 0) {
        $stageCounts = $listRows | Group-Object { Get-Prop $_ "signal_stage" } | Sort-Object Count -Descending
        $stageStr = ($stageCounts | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ", "
        Add-Result "PASS" "Signal stage values" "All $($listRows.Count) rows have valid stages: $stageStr"
    } else {
        Add-Result "FAIL" "Signal stage values" "$($badStages.Count) invalid stage(s): $($badStages -join '; ')"
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 9 - /accuracy reachable + /health/collectors trust gate
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "[9/9] Accuracy endpoint + collector trust ..."

# 9a - /accuracy
try {
    $accResp = Invoke-RestMethod -Uri "$BASE/accuracy" -Method GET -ErrorAction Stop
    Add-Result "PASS" "Accuracy endpoint" "/accuracy returned 200 with $($accResp.count) prediction(s)"
} catch {
    Add-Result "FAIL" "Accuracy endpoint" "/accuracy unreachable: $_"
}

# 9b - /health/collectors
$hc = Invoke-API "/health/collectors"
if ($null -eq $hc) {
    Add-Result "WARN" "Collector health" "/health/collectors unreachable"
} else {
    $trust = Get-Prop $hc "trust"
    $reason = Get-Prop $hc "trust_reason"
    if ($null -eq $trust) { $trust = Get-Prop $hc "reason" }
    if ($trust -eq $true -or $trust -eq "True") {
        Add-Result "PASS" "Collector health" "trust=true (scores are reliable)"
    } else {
        Add-Result "WARN" "Collector health" "trust=false - reason: '$reason'"
    }
}

# ── Optional X budget telemetry (informational, uses internal key) ─────────────
Write-Host ""
Write-Host "[INFO] Fetching X post-budget telemetry ..."
try {
    $xHeaders = @{ "X-Internal-Key" = "nt-internal-7f3a9c2e5b81" }
    $xBudget  = Invoke-RestMethod -Uri "$BASE/x/budget" -Method GET -Headers $xHeaders -ErrorAction Stop
    $used   = Get-Prop $xBudget "posts_used"
    $budget = Get-Prop $xBudget "monthly_budget"
    $pct    = if ($null -ne $used -and $null -ne $budget -and [double]$budget -gt 0) {
        [Math]::Round([double]$used / [double]$budget * 100, 1)
    } else { $null }
    $budgetStr = if ($null -ne $pct) { "Used $used / $budget posts ($pct%)" } else { ($xBudget | ConvertTo-Json -Depth 2 -Compress) }
    Add-Result "INFO" "X post budget" $budgetStr
} catch {
    Add-Result "INFO" "X post budget" "Budget endpoint not reachable or key not accepted (non-critical): $_"
}

# ══════════════════════════════════════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "============================================================"
Write-Host " RESULTS"
Write-Host "============================================================"

$padStatus = 6
$padCheck  = 36

foreach ($r in $Results) {
    $statusPad = $r.Status.PadRight($padStatus)
    $checkPad  = $r.Check.PadRight($padCheck)
    $color = switch ($r.Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host ("  [{0}]  {1}  {2}" -f $statusPad.TrimEnd(), $checkPad, $r.Detail) -ForegroundColor $color
}

Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host (" SUMMARY: {0} PASS   {1} FAIL   {2} WARN   (INFO rows not counted)" -f $PassCount, $FailCount, $WarnCount)
Write-Host "------------------------------------------------------------"

if ($FailCount -gt 0) {
    Write-Host " EXIT 1 - at least one FAIL detected." -ForegroundColor Red
    exit 1
} else {
    Write-Host " EXIT 0 - no FAILs." -ForegroundColor Green
    exit 0
}
