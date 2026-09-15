"""
divergence.py — the SEALED Positioning-vs-Price residual (internal: `perp_divergence`).

HELD-OUT COMPUTATION MODULE — declared in `heldout_registry.HELD_OUT_ARRIVAL_INPUTS`.
Feeds NO score, NO ledger, NO served value. Built under the sealed pre-registration
`audits/board/DIVERGENCE_PREREG_2026-09-14.md`; PARAM_VERSION below is that file's
SHA-256 and is stamped into every output. Any edit to a sealed section of the prereg
mints a NEW param_version — quiet retuning is the forbidden path.

WHAT IT MEASURES (prereg §1): the residual of leveraged-positioning QUANTITY after
price momentum is removed — leverage positioning, never money inflow (perps are
zero-sum; OI is coin-denominated contract count). Client-facing forbidden words
(§1) apply to any rendering of this signal; this module renders nothing.

THE STATISTIC (prereg §2, sealed — implemented exactly):
  q_t = Δln(quantity)  over a `dln_window`-observation window (7 for daily crypto OI)
  p_t = Δln(price)     over the same window
  zq, zp = robust z: (x − median) / (1.4826 · MAD), trailing `z_window` (90)
           observations, FORWARD-ONLY — each day uses only data ≤ that day.
           MAD == 0 (≤ tiny epsilon) → z is None for that day: HONEST ABSENCE,
           never a fabricated z.
  Theil–Sen fit  zq ~ α + β·zp  on the trailing `fit_window` (90) observations,
           refit every `refit_every` (7) observations, forward-only.
  D_t = zq_t − (α̂ + β̂·zp_t) — one continuous SIGNED residual. No phase labels.

FLAGGING (prereg §3): the ONLY flag logic here marks rows with D ≥ θ = +1.5 as
{"flag": true}, BTC and ETH only — θ set BY CONSTRUCTION, never re-tuned under this
param_version. The flag is INTERNAL/SHADOW research state: it resolves nothing,
publishes nothing, and enters no ledger.

§8 ANALYSIS-CODE CONTRACT (sealed — binding on this module):
  NO FORWARD-LOOKING JOINS. This module does not import or query any ledger or
  outcome table (accuracy_ledger*, market_accuracy_ledger, crypto_accuracy_ledger,
  flow_ledger, shadow_ledger — none), and no function accepts a future-return,
  subsequent-return, or outcome argument. It computes D_t and series statistics
  only. Joining D_t to any subsequent-return or ledger-outcome column is the
  research runner's job and is FORBIDDEN until the §5 gates are met (≥90 post-seal
  daily observations per scored coin; instrument audits passed). Pre-seal
  `coinapi_derivs` rows are SPEC-DEVELOPMENT DATA (§5/K16): training/context only,
  permanently excluded from any scored window.

Sanctioned read-only consumer (K4): tools/divergence_research.py. The engine's
GET /diag/divergence is a thin held-out STATUS route only.

Fixture: test_divergence.py (seal binding, residual recovery, Theil–Sen robustness,
forward-only invariance, MAD==0 honest absence, suspect-row exclusion, D2 hardening
guards: fit-staleness bound + calendar-gap guard + clean-series byte-identity).
"""
from __future__ import annotations

import datetime
import math
import random
from typing import Dict, List, Optional, Sequence

#: SHA-256 of audits/board/DIVERGENCE_PREREG_2026-09-14.md — the seal. Stamped into
#: every output; test_divergence.py rehashes the prereg file and fails the build if
#: the sealed spec is edited without minting a new param_version.
PARAM_VERSION = "bd6e36498ef6b1fb80056873cca6998c03e1fbb8268aff28b61a0864c022877b"

#: Prereg §3 — set BY CONSTRUCTION, not fitted; never re-tuned under this
#: param_version. Applies to the internal/shadow flag only.
THETA = 1.5

#: Prereg §3 scope: only BTC and ETH are independently scorable (one venue ≈ one
#: factor; Operator's reflexivity fence — no flag on thin-book coins).
FLAG_COINS = ("BTC", "ETH")

_MAD_EPS = 1e-12

#: D2 HARDENING (board 2026-09-15, `audits/board/BOARD_24h-review_2026-09-15.md`,
#: Challenger R1 conditions — no seat objected). The sealed prereg is SILENT on fit
#: staleness and calendar continuity, so these two guards are UNSEALED implementation
#: hardening, not a §2 edit: they only convert would-be-measured rows to honest
#: absence (measured:false / D:None) and NEVER change any computed numeric on a row
#: that remains measured (test_divergence.py h3 proves byte-identity on clean series).
#: Guard (i) — FIT-STALENESS BOUND: α̂/β̂ from the last successful Theil–Sen refit
#: expire once the fit is older than this multiple of `refit_every` observations
#: (repeated refit failures would otherwise reuse arbitrarily old coefficients while
#: stamping measured:true). Stale rows disclose `fit_age_obs`.
_FIT_STALE_MULT = 2

#: Guard (ii) — CALENDAR-GAP tolerance for the Δln leg: the dln window is defined in
#: OBSERVATIONS; if its calendar-day span exceeds `max_dln_span_days` (default
#: dln_window + this slack, for daily cadence) the row's Δln is silently a different
#: statistic → measured:false / D:None with `window_gap: true`. The z window is
#: deliberately NOT span-guarded (robust median/MAD tolerates gaps — per the memo).
_DLN_SPAN_SLACK_DAYS = 2


def _v(row, key, idx):
    """Dict-style access on db_compat PG rows, positional on raw sqlite tuples."""
    return row[key] if hasattr(row, "keys") else row[idx]
_MAX_TS_PAIRS = 2000
_TS_SEED = 20260914  # deterministic pair sampling — depends only on window size


def _span_days(later: str, earlier: str) -> Optional[int]:
    """Calendar-day span between two canonical `YYYY-MM-DD`(-prefixed) date labels.
    Returns None when either label does not parse as a real calendar date — the
    calendar-gap guard then CANNOT bind and is skipped (the core otherwise treats
    dates as opaque sort keys; production dates are §14-canonical ISO, so in
    production the guard always binds)."""
    try:
        a = datetime.date.fromisoformat(str(later)[:10])
        b = datetime.date.fromisoformat(str(earlier)[:10])
    except (TypeError, ValueError):
        return None
    return (a - b).days


# ── Robust primitives ───────────────────────────────────────────────────────────────────

def _median(xs: Sequence[float]) -> float:
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else 0.5 * (s[mid - 1] + s[mid])


def robust_z(window: Sequence[float], x: float) -> Optional[float]:
    """(x − median) / (1.4826 · MAD) over `window`. MAD at/under the epsilon floor
    returns None — honest absence, never a fabricated z (prereg §2)."""
    if not window:
        return None
    med = _median(window)
    mad = _median([abs(v - med) for v in window])
    if mad <= _MAD_EPS:
        return None
    return (x - med) / (1.4826 * mad)


def theil_sen(xs: Sequence[float], ys: Sequence[float]):
    """Theil–Sen robust fit y ~ alpha + beta*x: beta = median of pairwise slopes,
    alpha = median(y − beta·x). Pairs capped at ~2000, sampled DETERMINISTICALLY
    (fixed seed, a function of n only — so a refit over a same-length window is
    reproducible and append-invariant). Returns (alpha, beta) or (None, None) when
    no informative pair exists (all x identical)."""
    n = len(xs)
    if n < 2 or n != len(ys):
        return (None, None)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if xs[j] != xs[i]]
    if not pairs:
        return (None, None)
    if len(pairs) > _MAX_TS_PAIRS:
        rng = random.Random(_TS_SEED + n)
        pairs = rng.sample(pairs, _MAX_TS_PAIRS)
    slopes = [(ys[j] - ys[i]) / (xs[j] - xs[i]) for i, j in pairs]
    beta = _median(slopes)
    alpha = _median([ys[k] - beta * xs[k] for k in range(n)])
    return (alpha, beta)


# ── The asset-agnostic core (prereg §2; §7 instantiates it with scaled windows) ─────────

def divergence_series(dates: Sequence[str],
                      q_raw: Sequence[float],
                      p_raw: Sequence[float],
                      *,
                      dln_window: int = 7,
                      z_window: int = 90,
                      fit_window: int = 90,
                      refit_every: int = 7,
                      flag_theta: Optional[float] = None,
                      max_dln_span_days: Optional[int] = None) -> List[dict]:
    """Compute the sealed §2 residual over ALIGNED raw level series (ascending by
    date; q_raw = quantity level, p_raw = price level).

    FORWARD-ONLY BY CONSTRUCTION: every value at index t is computed from data at
    indices ≤ t only, left-to-right; appending future observations can never change
    an already-computed row (test_divergence.py t-d proves byte-identity).

    Warm-up is HONEST ABSENCE: until the full Δln lag, the full trailing z window,
    and the full trailing Theil–Sen window are available (a resolved prereg
    ambiguity — "trailing 90 observations" is read STRICTLY as requiring the full
    window; a shorter window would be a different, unsealed statistic), rows carry
    measured=False and D=None — never a partial-window value wearing the sealed
    badge.

    Returns one dict per date: {date, q_chg, p_chg, zq, zp, D, measured}. When
    `flag_theta` is set (BTC/ETH crypto only, θ=+1.5 §3), rows with D ≥ θ
    additionally carry {"flag": True} — internal/shadow only.

    D2 HARDENING GUARDS (unsealed — 2026-09-15 board, Challenger R1; see the
    module-level constants): (i) a row whose last successful fit is older than
    `_FIT_STALE_MULT × refit_every` observations renders measured:false / D:None
    (rows with any missed refit disclose `fit_age_obs`); (ii) a row whose dln
    window spans more than `max_dln_span_days` calendar days (default
    dln_window + 2, daily cadence — pass a cadence-appropriate bound for slower
    series) renders measured:false / D:None with `window_gap: true`. Both guards
    ONLY convert would-be-measured rows to honest absence; on a gap-free,
    refit-healthy series output is byte-identical to the pre-guard behavior.
    """
    n = len(dates)
    if max_dln_span_days is None:
        max_dln_span_days = dln_window + _DLN_SPAN_SLACK_DAYS
    if not (n == len(q_raw) == len(p_raw)):
        raise ValueError("dates, q_raw, p_raw must be aligned")

    def _dln(series, i):
        j = i - dln_window
        if j < 0:
            return None
        a, b = series[i], series[j]
        try:
            if a is None or b is None or a <= 0 or b <= 0:
                return None
            return math.log(a / b)
        except (TypeError, ValueError):
            return None

    q_chg = [_dln(q_raw, i) for i in range(n)]
    p_chg = [_dln(p_raw, i) for i in range(n)]

    def _z(series, i):
        lo = i - z_window + 1
        if lo < 0:
            return None
        win = series[lo:i + 1]
        if any(v is None for v in win):
            return None
        return robust_z(win, series[i])

    zq = [_z(q_chg, i) for i in range(n)]
    zp = [_z(p_chg, i) for i in range(n)]

    out: List[dict] = []
    alpha: Optional[float] = None
    beta: Optional[float] = None
    last_fit_i: Optional[int] = None
    for i in range(n):
        # Refit on schedule (first opportunity, then every `refit_every` obs) using
        # ONLY the trailing fit_window pairs ending at i — data ≤ i, forward-only.
        due = last_fit_i is None or (i - last_fit_i) >= refit_every
        if due:
            lo = i - fit_window + 1
            if lo >= 0:
                wx = zp[lo:i + 1]
                wy = zq[lo:i + 1]
                if all(v is not None for v in wx) and all(v is not None for v in wy):
                    a, b = theil_sen(wx, wy)
                    if a is not None:
                        alpha, beta = a, b
                        last_fit_i = i
        d = None
        measured = False
        if zq[i] is not None and zp[i] is not None and alpha is not None:
            d = zq[i] - (alpha + beta * zp[i])
            measured = True
        # D2 guard (i) — FIT-STALENESS BOUND: a due refit that keeps failing must
        # not let weeks-old α̂/β̂ mint measured:true rows forever.
        fit_age = (i - last_fit_i) if last_fit_i is not None else None
        if measured and fit_age is not None and fit_age > _FIT_STALE_MULT * refit_every:
            d, measured = None, False
        # D2 guard (ii) — CALENDAR-GAP GUARD on the dln leg: an observation-index
        # window that straddles a calendar gap is a different statistic.
        gap = False
        if i >= dln_window:
            span = _span_days(dates[i], dates[i - dln_window])
            if span is not None and span > max_dln_span_days:
                gap = True
                d, measured = None, False
        row = {"date": dates[i], "q_chg": q_chg[i], "p_chg": p_chg[i],
               "zq": zq[i], "zp": zp[i], "D": d, "measured": measured}
        if fit_age is not None and fit_age >= refit_every:
            row["fit_age_obs"] = fit_age  # disclosed: at least one refit missed
        if gap:
            row["window_gap"] = True
        if flag_theta is not None and d is not None and d >= flag_theta:
            row["flag"] = True  # internal/shadow only (prereg §3)
        out.append(row)
    return out


# ── Crypto adapter (coin-denominated OI from coinapi_derivs) ────────────────────────────

def _read_oi_rows(db_path: str) -> Dict[str, List[tuple]]:
    """{coin: [(signal_date, open_interest), ...] ascending} — suspect=1 rows
    EXCLUDED (K14: a >10× OI step breaks the series rather than silently converting
    the leg). The `suspect` column may be missing on an old SQLite file — handled
    by falling back to a suspect-less SELECT (treated as suspect=0)."""
    import db_compat
    conn = db_compat.connect(db_path)
    try:
        try:
            rows = conn.execute(
                "SELECT coin, signal_date, open_interest, suspect FROM coinapi_derivs "
                "WHERE open_interest IS NOT NULL ORDER BY coin, signal_date").fetchall()
            picked = [(_v(r, "coin", 0), _v(r, "signal_date", 1),
                       _v(r, "open_interest", 2), _v(r, "suspect", 3)) for r in rows]
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            rows = conn.execute(
                "SELECT coin, signal_date, open_interest FROM coinapi_derivs "
                "WHERE open_interest IS NOT NULL ORDER BY coin, signal_date").fetchall()
            picked = [(_v(r, "coin", 0), _v(r, "signal_date", 1),
                       _v(r, "open_interest", 2), 0) for r in rows]
    finally:
        conn.close()
    out: Dict[str, List[tuple]] = {}
    for coin, day, oi, suspect in picked:
        if suspect:
            continue
        out.setdefault(coin, []).append((day, float(oi)))
    return out


def crypto_divergence(db_path: str,
                      prices_by_coin: Dict[str, Dict[str, float]],
                      *, theta: float = THETA) -> dict:
    """Crypto instantiation of the §2 residual over coin-denominated open interest.

    q = OI in BASE-COIN units read from `coinapi_derivs` (suspect=1 rows excluded;
    USD-notional OI×price is disqualified by construction, §2). p = coin close
    prices INJECTED by the caller as {coin: {YYYY-MM-DD: close}} — no stored
    independent coin-price table exists in-engine (FMP prices feed the M composite
    and are therefore not independent of it), so the research runner supplies
    RESEARCH-ONLY prices. GRADUATION to any scored/served use additionally requires
    a §16-onboarded independent price snapshot table (plus the §5 instrument gates
    and the §6 board note + Chairman sign-off).

    Residual series are computed for ALL roster coins present; the internal/shadow
    θ-flag applies to BTC/ETH ONLY (§3). Nothing here resolves, enrolls, or joins
    to any outcome (§8).
    """
    oi = _read_oi_rows(db_path)
    coins_out = {}
    for coin in sorted(oi):
        prices = (prices_by_coin or {}).get(coin) or {}
        aligned = [(day, q, prices[day]) for day, q in oi[coin] if day in prices]
        dates = [a[0] for a in aligned]
        qs = [a[1] for a in aligned]
        ps = [a[2] for a in aligned]
        series = divergence_series(
            dates, qs, ps,
            flag_theta=(theta if coin in FLAG_COINS else None))
        coins_out[coin] = {
            "days": len(series),
            "oi_days": len(oi[coin]),
            "series": series,
            "latest": series[-1] if series else None,
        }
    return {
        "param_version": PARAM_VERSION,
        "basis": "perp_divergence",
        "flag_note": ("internal/shadow only — D>=+1.5 marks BTC/ETH rows; "
                      "resolves nothing, publishes nothing, enters no ledger"),
        "coins": coins_out,
    }


# ── Equity adapter (FINRA short interest, bi-monthly cadence — prereg §7) ───────────────

def equity_divergence(ticker: str,
                      si_series: Dict[str, float],
                      price_series: Dict[str, float]) -> dict:
    """Equity-first instantiation (prereg §7, Chairman-ruled GO): the SAME §2
    residual with windows scaled to the bi-monthly FINRA short-interest cadence —
    Δln over 1 observation, robust z over trailing 24 observations, Theil–Sen on
    the same trailing 24, refit every observation (the weekly-in-daily-terms
    cadence collapses to per-observation at ~24 obs/year). `si_series` and
    `price_series` are {date: level} on the SAME settlement dates; only dates
    present in both are used. Research-only under this seal until its own board
    note; §1 forbidden-words rule applies to any rendering. No flag logic (§3
    scopes the θ-flag to BTC/ETH)."""
    dates = sorted(set(si_series) & set(price_series))
    series = divergence_series(
        dates,
        [float(si_series[d]) for d in dates],
        [float(price_series[d]) for d in dates],
        dln_window=1, z_window=24, fit_window=24, refit_every=1,
        flag_theta=None,
        # D2 calendar-gap guard, cadence-scaled (windows above UNCHANGED): one
        # bi-monthly FINRA settlement step spans ≤ ~16 calendar days (mid-month ↔
        # EOM); the daily default (dln_window+2 = 3) would mark every healthy
        # bi-monthly row a gap. 19 keeps holiday-shifted settlements measured
        # while a skipped settlement (≈28+ days) honestly renders window_gap.
        max_dln_span_days=19)
    return {
        "param_version": PARAM_VERSION,
        "basis": "equity_si_divergence",
        "ticker": ticker,
        "days": len(series),
        "series": series,
        "latest": series[-1] if series else None,
    }


# ── Thin status report for GET /diag/divergence (held-out, internal-gated) ──────────────

def diag_report(db_path: str) -> dict:
    """OI-side series status per coin (usable days, suspect-excluded count, latest
    date). The real computation runs in the research runner; the engine holds NO
    price source independent of M, so D is computed here ONLY if a
    research-supplied `divergence_price_cache` table (coin, signal_date, close)
    exists — otherwise prices are declared research-runner-only. Read-only."""
    import db_compat
    out = {"param_version": PARAM_VERSION, "basis": "perp_divergence", "coins": {}}
    conn = db_compat.connect(db_path)
    try:
        try:
            rows = conn.execute(
                "SELECT coin, "
                "SUM(CASE WHEN open_interest IS NOT NULL AND COALESCE(suspect,0)=0 "
                "THEN 1 ELSE 0 END) AS usable, "
                "SUM(CASE WHEN COALESCE(suspect,0)=1 THEN 1 ELSE 0 END) AS suspect_n, "
                "MAX(signal_date) AS latest FROM coinapi_derivs GROUP BY coin "
                "ORDER BY coin").fetchall()
            for r in rows:
                out["coins"][_v(r, "coin", 0)] = {
                    "usable_days": _v(r, "usable", 1),
                    "suspect_excluded": _v(r, "suspect_n", 2),
                    "latest": _v(r, "latest", 3)}
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            try:  # old schema without `suspect` — report without the exclusion count
                rows = conn.execute(
                    "SELECT coin, "
                    "SUM(CASE WHEN open_interest IS NOT NULL THEN 1 ELSE 0 END) "
                    "AS usable, MAX(signal_date) AS latest FROM coinapi_derivs "
                    "GROUP BY coin ORDER BY coin").fetchall()
                for r in rows:
                    out["coins"][_v(r, "coin", 0)] = {
                        "usable_days": _v(r, "usable", 1),
                        "suspect_excluded": None,
                        "latest": _v(r, "latest", 2)}
            except Exception as e:
                try:
                    conn.rollback()
                except Exception:
                    pass
                out["coins_error"] = str(e)[:120]

        # Research-supplied price cache (optional; absent in production by design).
        prices: Dict[str, Dict[str, float]] = {}
        try:
            for r in conn.execute("SELECT coin, signal_date, close "
                                  "FROM divergence_price_cache").fetchall():
                prices.setdefault(_v(r, "coin", 0), {})[_v(r, "signal_date", 1)] = \
                    float(_v(r, "close", 2))
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            prices = {}
    finally:
        conn.close()

    if prices:
        res = crypto_divergence(db_path, prices)
        out["last_D"] = {c: {"date": (v["latest"] or {}).get("date"),
                             "D": (v["latest"] or {}).get("D"),
                             "measured": (v["latest"] or {}).get("measured")}
                         for c, v in res["coins"].items()}
    else:
        out["prices"] = "research-runner only"
    return out
