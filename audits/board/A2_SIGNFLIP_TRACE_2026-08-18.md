# A2 ETF-FLOW RECONCILE — SIGN-FLIP ROOT-CAUSE TRACE (2026-08-18)

Chairman-released read-only investigation (verify-before-fix, CLAUDE.md §10a). No code
changed, no fix deployed. Verdict below is reproduced from real data end-to-end.

## 0. VERDICT (one paragraph)

**Root cause FOUND and reproduced: the A2.1 `t_of` settled-through mapping
(`transfer/etf_flow_reconcile.py:386-398`) derives each strike's trade date from OUR
capture instant under a fixed one-day publication model. The issuer pages do not obey
that model: (a) iShares' share count is SETTLED-basis (as-of D reflects trades through
D−1) and its page rollover latency VARIES day-to-day (as-of-D value became visible
T+1 ~16:30 ET on 08-11..08-15, but T+0 ~22:49 ET on 08-17); (b) 21Shares' count is
TRADE-DATE-basis (as-of D already includes D's trades). Net effect: every scored
IBIT interval 08-10..08-13 was labeled one trading day AFTER the flow it actually
contained, and every ARKB interval one trading day BEFORE. The derived dollar values
themselves are correct to 4-5 significant figures against the issuers' own published
flows — only the day labels are wrong, so the harness compared each day's true flow
against the neighboring day's published number. BTC flows began alternating sign
daily on 08-10 (+86.7 → −53.6 → +50.2 → −14.3), which is the only regime where a
±1-day label shift produces direction FAILs — that, not any 08-10 deploy, is why the
failures burst then.** Not a parser regression, not the catch-up-at-boot change, not
comparator date semantics (all three disproven below, §5).

## 1. Method

1. Read `transfer/etf_flow.py`, `transfer/etf_flow_reconcile.py` (reconcile_a2 /
   t_of / _strikes_with_capture), `transfer/etf_issuer_pages.py`, the A2 spec
   (`audits/board/CRYPTO_FLOW_SPEC_A2_AMENDMENT_2026-08-05.md` + annex N1).
2. Pulled live `etf_reconcile_log2` rows and `etf_share_snapshots` strike rows
   (IBIT/ARKB/ETHA/BITB, 08-04..08-18) from the engine Postgres (read-only SELECTs).
3. Fetched the comparator ground truth (farside.co.uk/btc/, declared UA) for per-day
   published flows.
4. Recomputed every issuer-src interval by hand (dedupe → t_of → Δshares×NAV) and
   matched derived values against SHIFTED published days.
5. Live-fetched the IBIT + ARKB issuer pages (2026-08-18) to confirm as-of-stamp
   semantics against the DB's newest strikes.

## 2. Ground truth (Farside, fetched 2026-08-18)

Published daily flows ($M; parentheses = outflow):

| trade day | IBIT | ARKB | BITB | FBTC |
|---|---|---|---|---|
| Thu 08-06 | +128.3 | 0.0 | +1.7 | +11.2 |
| Fri 08-07 | +86.7 | +1.9 | +2.1 | +41.0 |
| Mon 08-10 | −53.6 | 0.0 | −28.4 | −40.3 |
| Tue 08-11 | +50.2 | −11.5 | 0.0 | −4.1 |
| Wed 08-12 | −14.3 | 0.0 | 0.0 | −46.8 |
| Thu 08-13 | −5.7 | −58.8 | −9.3 | −55.1 |
| Fri 08-14 | −55.5 | 0.0 | +6.1 | −6.8 |

## 3. Reproduction — the labels are exactly one trading day off, values exact

IBIT strike rows (etf_share_snapshots, src=issuer_ishares): 08-09/10 collapsed
1,318,000,000 @ capt 08-09T20:39Z; 08-11 1,320,359,900 @ 08-11T21:29Z; 08-12
1,318,880,000 @ 08-12T20:32Z; 08-13 1,320,280,100 @ 08-13T21:09Z; 08-14
1,319,879,900 @ 08-14T21:35Z; 08-15..17 1,319,719,900; 08-18 1,318,160,000 @
08-18T02:49Z.

**IBIT (label = t_of interval; content = the published day the derived value matches):**

| interval label (T_a,T_b] | derived $ | published(label) | verdict | TRUE content day | pub(content) |
|---|---|---|---|---|---|
| (08-06,08-10] {07,10} | +85,405,890 | +33.1M | FAIL | Fri 08-07 | **+86.7M** |
| (08-10,08-11] {11} | −53,061,044 | +50.2M | FAIL (sign flip) | Mon 08-10 | **−53.6M** |
| (08-11,08-12] {12} | +50,199,120 | −14.3M | EMPTY_INTERVAL | Tue 08-11 | **+50.2M** (exact) |
| (08-12,08-13] {13} | −14,355,781 | −5.7M | IMMATERIAL | Wed 08-12 | **−14.3M** (exact) |
| (08-13,08-14] | −56,806,788 | pending | PENDING_FINAL | Fri 08-14 | **−55.5M** (aligned — see §4b) |

Content = label − 1 trading day on all four scored rows. The "coincidence" flagged in
the symptom (derived 08-12 = published 08-11 = $50.2M) is row 3: it is the SAME flow,
mislabeled. Residuals (85.4 vs 86.7 etc.) are NAV-vintage noise: derived multiplies
Δshares by the newer strike's NAV, which under the mislabel is also one day off.

**ARKB (src=issuer_21shares):**

| interval label | derived $ | published(label) | verdict | TRUE content day(s) | pub(content) |
|---|---|---|---|---|---|
| (08-06,08-07] {07} | 0 | +1.9M | IMMATERIAL | Mon 08-10 | **0.0** |
| (08-07,08-10] {10} | −11,550,000 | 0.0 | EMPTY_INTERVAL | Tue 08-11 | **−11.5M** (exact) |
| (08-10,08-12] {11,12} | −58,828,000 | −11.5M | FAIL | Wed+Thu 08-12/13 | **0.0 + −58.8M** (exact) |
| (08-12,08-13] {13} | 0 | −58.8M | FAIL | Fri 08-14 | **0.0** (exact) |

Content = label + 1 trading day on all rows — the OPPOSITE direction from IBIT.
All 6 open live-source bad rows (3 IBIT + 3 ARKB) are this one defect.

## 4. Mechanism — exact code + page semantics

**Code:** `transfer/etf_flow_reconcile.py:386-398` (`t_of`): T(strike) =
`_prev_bday(_last_bday(effective_ET_date(captured_at)))` — one fixed trading-day
subtraction from OUR capture instant, per A2.1's model ("a count captured evening-ET
on day D reflects creations/redemptions TRADED through D−1"). `captured_at` is the
FIRST time our 4h loop saw the new (shares, nav) value, i.e. the page's rollover
time, not anything the issuer stamps. `transfer/etf_issuer_pages.py:19-23` explicitly
declines to use the page's own as-of stamp for the join ("DATE RULE ... We do NOT
interpret their stamps").

**(a) iShares (IBIT/ETHA) — settled basis + variable rollover latency.**
Live page 2026-08-18: shares 1,318,160,000 "as of Aug 17, 2026" — identical to the DB
strike first seen 08-18T02:49Z (Mon 22:49 ET): the as-of-Mon value was visible Mon
evening (T+0). But the 08-11..08-15 strikes were first seen 16:32–18:14 ET NEXT day
(T+1 afternoon rollover). Basis: Δ(as-of Mon − as-of Fri) = −1,559,900 sh ×36.42 =
−$56.8M ≈ Farside Fri (−55.5M) → as-of D counts shares SETTLED through D = traded
through D−1 (T+1 settlement). So a T+1-afternoon capture gives t_of eff-date D+1 →
label D, while content is trades through D−1: label late by one. When the rollover
happens T+0 evening (08-17), the same t_of lands correctly — the offset is not even
a per-fund constant; it flips with the page's posting hour. ETHA's page rolled T+0
overnight all week (first-sights 00:32–01:28 ET), which is why ETHA's issuer rows
genuinely PASSED — same family, same code, different posting hour.

**(b) 21Shares (ARKB/TSOL) — trade-date basis.** ARKB strikes are first seen pre-dawn
ET (00:31–02:13). Δ(as-of D − as-of D−1) matches Farside's flow FOR day D itself
(−11.55 vs −11.5 on 08-11; −58.83 vs 0.0+−58.8 over 08-12/13): the count already
includes same-day creations (trade-date basis). t_of maps a pre-dawn D+1 capture →
effective D → label D−1, one day BEHIND the content.

**(c) Bitwise (BITB/BSOL)** — currently lands aligned (BITB (08-07,08-10] −28.44
derived vs −28.4 published on 08-10, PASS), so its 2 passes are genuine — but by the
same argument as (a), alignment depends on a posting-hour that is not under our
control or observation.

## 5. Hypotheses tested and DISPROVEN

- **H2 — the 08-10 catch-up-at-boot fix (`8efadda`):** touched only
  `gravitational_anomaly_detector.py` (loop scheduling), `heldout_registry.py`,
  `SESSION_LOG.md` — zero join/parse logic. It changes when boot-time runs fire; the
  strike `captured_at` values that matter are governed by the PAGES' rollover times
  (first sight lands ≤4h after rollover on any grid phase, and every observed
  rollover sits ≥4h from the 06:00-ET t_of boundary). The 08-10..08-12 timing is
  explained by (i) the issuer era's first scoreable intervals only ripening then
  (takeover was 08-08/09; edge intervals are held PENDING_FINAL), and (ii) BTC flow
  signs starting to alternate daily on 08-10 — the 08-04..08-07 streak
  (+170/+197/+128/+87) would have PASSED even mislabeled. The 08-09 "0/5 open_bad"
  was vacuously clean: no issuer interval had finished scoring yet.
- **H3 — issuer-page parse regression (iShares/ARK):** disproven. Parsed share levels
  are internally consistent and Δshares×NAV reproduces the issuers' own published
  flows to 4-5 significant figures (50,199,120 vs 50.2M; −14,355,781 vs −14.3M;
  −11.55M vs −11.5M; −58.828M vs −58.8M). The parser reads the right numbers.
- **H4 — comparator (Farside) date semantics:** disproven. Farside dates are trade
  dates; the genuinely-aligned funds (ETHA, BITB) match them exactly on the same
  fetch. The 18 FMP-src FAILs in the same report are the already-ruled FMP
  disqualification (A2.3), out of scope here.
- **H1 — day-offset/alignment:** CONFIRMED, as the ±1-trading-day label shift above
  (not a uniform shift — opposite signs per family, and variable within iShares).

## 6. Recommended fix (for Chairman approval — NOT implemented)

The capture-instant mapping is unfixable by a constant (iShares' own offset flipped
between 08-15 and 08-17). The mechanism-true key is the page's OWN as-of stamp,
which every adapter already parses, canonicalizes (`asof_iso`, §14 `to_iso_date`)
and trusts for the staleness guard — but does not persist or use for the join.

1. **Spec sub-version A2.2** (mandatory per annex N1.2 — this changes labeling
   semantics): for issuer-src strikes, T(strike) = f(page as-of, family basis),
   pre-declared per family from mechanism:
   - iShares (settled basis): **T = prev_bday(asof)** (as-of D = trades through D−1);
   - 21Shares (trade basis): **T = asof**;
   - Bitwise: determine basis from its `asOfDate` field during the §16 re-test
     (current evidence is consistent with its stamps already landing aligned).
   Fallback when the stamp is unparseable: current `t_of` (declared + flagged on the
   row), mirroring the staleness-guard's fail-open posture.
2. **Persist the stamp:** additive `page_asof` column on `etf_share_snapshots` +
   `etf_share_observations`, written by `snapshot_issuer` (value already in
   `fetch_one`'s output). Forward-only; never backfill/guess historical as-ofs (§14).
3. **Amend the DATE RULE** in `etf_issuer_pages.py:19-23` (the "never interpret their
   stamps" declaration) — requires the Chairman's sign-off since it reverses a
   pre-declared spec decision; the reversal is now evidence-based, not fitted (four
   exact-match reproductions per family).
4. **Re-verdict as rule_version 'A2.2'** in `etf_reconcile_log2`; A2 rows preserved
   verbatim (N1.2). Under corrected labels every one of the 6 open live-source bad
   rows recomputes to PASS or IMMATERIAL against §2's table — a strong internal
   consistency check for the fix, and honest evidence the pipeline itself is sound.
5. **Re-arm:** clocks restart on A2.2 per A2.4 (recommended even though the ETHA/BITB
   passes were genuinely aligned — they were scored under a defective join). Since
   `page_asof` only exists forward, the A2.2 series starts at deploy; realistic
   re-arm at ≥5 material in-band issuer comparisons thereafter. Nothing served was
   ever wrong: `CRYPTO_ETF_FLOW=0`, harness is held-out, `latest_delta`/shadow votes
   do no published-day join and are unaffected.

## 7. Secondary findings (flagged, separate approval)

- **21Shares AUM parse returns None** (live-verified 2026-08-18: `nav-aum` regex no
  longer matches). Consequences: the shares×NAV≈AUM identity check
  (`etf_issuer_pages.py:288-296`, `if aum:`) is silently INERT for the whole
  21shares family; the NO_DERIVED materiality floor for ARKB collapses to the flat
  $10M (FLOOR_AUM_FRAC×0); shadow votes read "AUM $0 below $50M voting floor" for
  ARKB/TSOL/TOXR. Fix the selector or take AUM from another page element.
- **NAV vintage under A2.2:** keep derived $ = Δshares × NAV(b); after re-keying on
  as-of, NAV(b) is the correct-day NAV automatically (the 85.4-vs-86.7 class of
  residual shrinks).

*Evidence: engine Postgres reads 2026-08-18; farside.co.uk/btc fetch 2026-08-18;
live issuer-page fetches 2026-08-18; git 8efadda / d8c23d9 / 953c31c / b3eaf00.*
