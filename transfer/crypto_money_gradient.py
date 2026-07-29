"""
crypto_money_gradient.py — Crypto Money Gradient scoring (flag-gated CRYPTO_SIGNAL; held-out until live).

Mirrors market_signal_engine (the equity Money Gradient) for crypto — a baseline-relative DUAL score:
  MONEY MOVEMENT (D)      — informed / early money into the coin via crypto-EXPOSURE proxies
                            (spot-ETF 13F + MSTR/COIN insider[Finviz primary]+13F; P2+: congress + CME futures).
  MARKET CONFIRMATION (M) — the coin's OWN price / volume momentum (the broad crypto market confirming).

Every component is z-scored vs the COIN's OWN history — reusing market_signal_engine's baseline store under
item_key 'crypto:BTC' — so a coin doesn't auto-score high (same integrity principle as the equity side).
FLOW (inflow / outflow) = consensus of D + M. MEASUREMENT, NOT ADVICE — no buy/sell, no price prediction;
the crypto Accuracy Ledger (P3) judges, after the fact, whether a movement led realized price.

Held-out until CRYPTO_SIGNAL=1 (default OFF). Uses crypto_signals (held-out) + market_signal_engine primitives.
"""
from __future__ import annotations
import os
from typing import Optional

import crypto_signals as cs
import market_signal_engine as mse

CRYPTO_SIGNAL = os.getenv("CRYPTO_SIGNAL", "0") == "1"
DEFAULT_COINS = [c.strip().upper() for c in os.getenv(
    "CRYPTO_COINS", "BTC,ETH,SOL,XRP,BNB,DOGE,ADA,AVAX,LINK,DOT,LTC,BCH").split(",") if c.strip()]

# Crypto Money Gradient components (0-1), z-scored vs the coin's own baseline.
CRYPTO_MM_WEIGHTS = {            # D — informed money via crypto-exposure proxies
    "proxy_positioning": 0.75,   # spot-ETF 13F + MSTR/COIN insider accumulation (Finviz) + 13F
    "signal_freshness":  0.25,
}
CRYPTO_MC_WEIGHTS = {            # M — broad crypto market confirmation
    "price_momentum":    0.75,   # the coin's own price / volume trend
    "venue_diffusion":   0.25,   # how many proxy venues are active / covered
}
CRYPTO_LABELS = {
    "proxy_positioning": "Proxy Positioning (crypto-exposure 13F / insider accumulation)",
    "price_momentum":    "Price Momentum (coin price / volume trend)",
    "venue_diffusion":   "Venue Diffusion (proxy venues active)",
    "signal_freshness":  "Signal Freshness (recency)",
}

_DISCLAIMER = ("The Crypto Measurement section tracks significant money movement relative to this coin's own "
               "baseline. Whether an early movement led realized price is recorded, after the fact, in the "
               "crypto Accuracy Ledger. Be advised that this summary may be inaccurate and is not intended to "
               "be financial, legal or investment advice.")


def assemble_crypto_components(coin: str, sig: Optional[dict] = None) -> dict:
    """Build the 0-1 components from crypto_signals.signal_for output (proxy Dark Matter + price)."""
    sig = sig or cs.signal_for(coin, with_dark_matter=True)
    dm = sig.get("_dark_matter") or {}
    pm = sig.get("_price") or {}
    proxy_pos = (dm.get("intensity") or 0.0) / 100.0          # Dark-Matter intensity → 0-1
    covered, total = dm.get("proxies_covered") or 0, dm.get("proxies_total") or 1
    venue = covered / total if total else 0.0
    price_avail = bool(pm.get("available"))
    return {
        "proxy_positioning": round(mse._norm(proxy_pos), 3),
        # §17: Price Momentum is n/a (None) when the price leg is unavailable — NEVER a misleading 0.
        "price_momentum":    (round(mse._norm((pm.get("confirmation") or 0.0) / 100.0), 3) if price_avail else None),
        "venue_diffusion":   round(mse._norm(venue), 3),
        "signal_freshness":  round(0.8 if price_avail else 0.3, 3),
    }


def _crypto_analysis(d, c, gap, flow) -> str:
    """A factual, REPRODUCIBLE walk of the crypto Money-Gradient read — Money Movement, Market
    Confirmation, and the flow — parallel to the equity `_market_analysis` (image-1 style), but
    crypto-worded (proxies, coin price). MEASUREMENT, not advice; deterministic (no LLM)."""
    d = int(round(d or 0)); c = int(round(c or 0)); gap = int(round(gap or 0))
    f = (flow or "").lower().strip()
    fdir = "IN" if f == "inflow" else "OUT" if f == "outflow" else ""
    strength = "strong" if d >= 70 else "moderate" if d >= 45 else "muted"
    parts = []
    if fdir:
        parts.append(f"Money Movement {d}/100 — this signals {strength} informed-money activity, and that "
                     f"money may be moving {fdir} via the crypto-exposure proxies (spot-ETF 13F + listed "
                     f"crypto-treasury/exchange insider).")
    else:
        parts.append(f"Money Movement {d}/100 — this signals {strength} informed-money activity in the "
                     f"crypto-exposure proxies, with no clear net direction yet.")
    conf = ("the coin's own price has confirmed the move" if c >= 55 else
            "price confirmation is partial" if c >= 35 else "the coin's price has not yet confirmed")
    parts.append(f"Market Confirmation {c}/100 — this signals {conf}.")
    if gap >= 16:
        parts.append(f"Informed money runs {gap} pts ahead of price confirmation — an early read.")
    elif gap <= -16:
        parts.append(f"Price leads the informed read by {abs(gap)} pts — a later-stage read.")
    else:
        parts.append("Informed and price reads are roughly aligned.")
    parts.append("Whether an early read leads realized coin price is recorded, after the fact, in the "
                 "crypto accuracy ledger over time — this is a measurement, not a recommendation.")
    parts.append("Be advised that this summary may be inaccurate and is not intended to be financial, "
                 "legal or investment advice.")
    return " ".join(parts)



def _max_votable(coin: str) -> int:
    """How many of this coin's proxies could EVER cast a vote, given what they are.

    THE REACHABILITY TEST (Board 2026-07-29, proposed §16a stage 0). ETFs and trusts file no
    Form 4s, so on the insider path they are structurally silent — counting them as "proxies"
    inflates apparent coverage and makes a permanently-unreachable read look merely thin. Only
    operating companies (treasury/exchange kinds) can emit an insider vote today. When an
    ETF-flow leg ships, ETFs become votable and this function is what must change with it.
    """
    try:
        import crypto_signals as _cs
        c = _cs.COIN_UNIVERSE.get((coin or "").upper()) or {}
        insider_votable = {"treasury", "exchange"}
        return sum(1 for p in (c.get("proxies") or [])
                   if p.get("kind") in insider_votable)
    except Exception:
        return 0

def compute_crypto_signal(coin: str, name: str, components_current: dict,
                          baselines: Optional[dict] = None, flow: str = "neutral",
                          price: Optional[dict] = None, dm: Optional[dict] = None) -> dict:
    """Baseline-relative dual score → the Money Gradient payload (parity with compute_market_signal)."""
    baselines = baselines or {}
    # §17: a None component = n/a (data leg unavailable, e.g. price throttled) → excluded from the
    # weighted score (renormalized over present components) AND rendered "n/a", never a misleading 0.
    na = {n for n in CRYPTO_LABELS if components_current.get(n) is None}
    scored = {n: mse.score_component(components_current.get(n, 0.0), baselines.get(n))
              for n in CRYPTO_LABELS if n not in na}
    any_calibrating = any(s.get("calibrating") for s in scored.values())
    covered = (dm or {}).get("proxies_covered") or 0

    def _weighted(weights: dict) -> float:
        present = {c: w for c, w in weights.items() if c in scored}
        tot = sum(present.values())
        return (sum(present[c] * scored[c]["score"] / tot for c in present) * 100) if tot else 0.0

    money_movement = round(_weighted(CRYPTO_MM_WEIGHTS), 1)
    market_confirmation = round(_weighted(CRYPTO_MC_WEIGHTS), 1)
    # D8 (founder-ruled 2026-07-20, flag-gated MONEY_MOVEMENT_EXCLUDE): every crypto MM component
    # is proxy-degenerate on all 12 coins today → serve money_movement=null + "market-confirmation
    # only", never a "Money Gradient" headline over zero money data. M is untouched.
    #
    # ⚠ COVERAGE-KEYED ABSENCE (Board master remediation, 2026-07-25 — the Guardian's
    # "right-for-the-wrong-reason trap", Chairman-approved). Today's honest absence rides
    # ENTIRELY on baseline degeneracy, which is downstream of the dead insider parser: the
    # moment INSIDER_PARSER_FIX=1 revives the COIN proxy, baselines de-degenerate and the ten
    # COIN-only coins would silently serve a numeric "Money Movement" backed by ONE shared
    # Coinbase-equity proxy — zero coverage improvement, absence evaporated by accident.
    # So absence is ALSO keyed on coverage, unconditionally: fewer than 2 distinct voting
    # proxies (or a structurally "thin" map) is not a money read, whatever the baselines do.
    # NOTE `proxy_coverage` alone is insufficient — BTC serves "partial" with covered==1 —
    # hence the explicit covered >= 2 requirement. `absence_reason` is served because the
    # two absences are different truths a diligence reader must be able to tell apart.
    # Env kill switch CRYPTO_COVERAGE_GATE=0 for emergency rollback (flag-never-force; the
    # gate changes NOTHING live today — all 12 coins are already absent — it only prevents
    # the silent post-flip revival).
    money_data_absent = False
    absence_reason = None
    absence_class = None
    _cov_gate = os.getenv("CRYPTO_COVERAGE_GATE", "1") == "1"
    if _cov_gate and ((dm or {}).get("proxy_coverage") == "thin" or covered < 2):
        money_data_absent = True
        money_movement = None
        # ⚠ STRUCTURAL vs TRANSIENT (Board 2026-07-29, unanimous). The old single reason
        # "proxy_coverage_thin" let the surface say "not YET available" — a promise about the
        # future the mechanism cannot underwrite. VERIFIED: 5 of the 7 crypto proxies (IBIT,
        # FBTC, GBTC, ETHA, ETHE) are ETFs and trusts, which have NO Form-4 insiders and so can
        # never emit the signal the vote reads. With a floor of 2 voting proxies, 11 of 12 coins
        # can NEVER produce a money read — not today, not ever, under this design.
        # The Guardian's rule: absence is transient only if the instrument AS BUILT has a
        # reachable state. Where it does not, saying "not yet" is a false claim about the future.
        _reachable = int((dm or {}).get("proxies_total") or 0)
        absence_reason = ("single_proxy_structural" if _reachable <= 1
                          else "insufficient_voting_proxies")
        absence_class = ("structural" if _reachable <= 1 or _max_votable(coin) < 2
                         else "transient")
    elif getattr(mse, "MONEY_MOVEMENT_EXCLUDE", False):
        mm_live = [c for c in CRYPTO_MM_WEIGHTS
                   if c in scored and not scored[c].get("degenerate_baseline")]
        if not mm_live:
            money_data_absent = True
            money_movement = None
            absence_reason = "degenerate_baseline"
    gap = None if money_data_absent else round(money_movement - market_confirmation, 1)
    # Reuse the equity Money-Gradient interpretation (movement + facts language, no advice), then append
    # the rich crypto analysis walk (parity with the Market Signal's _market_analysis) — EXCEPT while
    # calibrating, or when the money read is absent (market-confirmation only).
    if money_data_absent:
        interp = {"state": "money_absent",
                  "text": "No proxy money-positioning data for this coin this cycle — "
                          "showing market-confirmation only."}
        _interp_text = interp["text"]
    else:
        interp = mse._interpret_movement(money_movement, market_confirmation, gap, any_calibrating)
        _interp_text = interp["text"]
        if not any_calibrating:
            _interp_text = (_interp_text + "  "
                            + _crypto_analysis(money_movement, market_confirmation, gap, flow)).strip()

    return {
        "item_key": f"crypto:{coin}", "coin": coin, "item_name": name, "section": "Crypto",
        "model_version": "crypto-v1",
        # dual-ring aliases (frontend renders detection/confidence rings)
        "detection": money_movement, "confidence": market_confirmation, "gap": gap,
        "money_movement": money_movement, "market_confirmation": market_confirmation,
        # D8: null money read → render "Market-Confirmation-only", never a Money Gradient headline.
        "money_data_absent": money_data_absent,
        # Which absence this is — "proxy_coverage_thin" (structural: <2 voting proxies) vs
        # "degenerate_baseline" (cold-start: no variance yet). Two different truths.
        "absence_reason": absence_reason,
        # Board 2026-07-29: these MUST live at the top level. They previously sat inside the
        # `dark_matter` block, which the contradiction guard OMITS whenever money is absent —
        # so the surface was structurally unable to tell the user WHY (e.g. "this coin has one
        # proxy"). Two different truths were computed and then discarded at the boundary.
        "absence_class": absence_class,          # "structural" (never) vs "transient" (not now)
        "proxies_total": int((dm or {}).get("proxies_total") or 0),
        "proxies_covered": int(covered or 0),
        "proxies_votable_max": _max_votable(coin),
        "money_floor_required": 2,
        "tier": ("ABSENT" if money_data_absent
                 else mse._level((money_movement + market_confirmation) / 2)),
        "detection_level": ("ABSENT" if money_data_absent else mse._level(money_movement)),
        "confidence_level": mse._level(market_confirmation),
        "detection_fp": mse.MONEY_MOVEMENT_FP, "confidence_fp": mse.MARKET_CONFIRM_FP,
        "gap_state": interp["state"], "interpretation": _interp_text, "calibrating": any_calibrating,
        # ⚠ CONTRADICTION GUARD (Board master remediation, C1 — verified live before the fix:
        # BTC served flow "inflow" + dark_matter intensity 60.0 beside money_movement:null and
        # every MM component absent; traced to a SINGLE AV-fallback proxy vote of five, hence
        # intensity = 100*(0.5+0.5*0.2) = 60.0 exactly). A payload may never emit a direction
        # while the money read it belongs to is absent. This is the single choke point all
        # three platforms inherit — the guard lives here, in the engine, not in three UIs.
        "flow": ("no_data" if money_data_absent else flow),
        # §17 source-display: only render components that contributed; show real value or n/a (never NaN).
        # D7 (2026-07-19): a DEGENERATE zero-on-zero pin (all 12 coins served proxy D=30.0
        # as if measured) serves score:null + a truthful flag; the weighted score is
        # unchanged (score-side exclusion = D8, backtest-gated).
        "components": {
            CRYPTO_LABELS[c]: ({
                "score": None,
                "feeds": ("money_movement" if c in CRYPTO_MM_WEIGHTS else "market_confirmation"),
                "absent": True, "degenerate_baseline": True,
                "baseline_relative": False, "z": None,
                "note": "no proxy positioning data yet (zero-variance baseline)",
            } if c in scored and scored[c].get("degenerate_baseline") else {
                "score": round(scored[c]["score"] * 100, 1),
                "feeds": ("money_movement" if c in CRYPTO_MM_WEIGHTS else "market_confirmation"),
                "baseline_relative": scored[c].get("baseline_relative", False),
                "z": scored[c].get("z"),
            } if c in scored else {
                "score": None, "feeds": "n/a", "not_applicable": True,
                "baseline_relative": False, "z": None,
            }) for c in CRYPTO_LABELS
        },
        # D7 coverage fields (were entirely missing from the coin payload — the UI had
        # nothing to caveat on): same semantics as the equity Market Signal.
        "data_coverage": ("insufficient"
                          if sum(1 for s in scored.values()
                                 if s.get("current", -1) == 0.0 or s.get("degenerate_baseline"))
                          > (len(scored) or 1) // 2 else
                          "partial"
                          if any(s.get("current", -1) == 0.0 or s.get("degenerate_baseline")
                                 for s in scored.values()) else "full"),
        "absent_inputs": sum(1 for s in scored.values()
                             if s.get("current", -1) == 0.0 or s.get("degenerate_baseline")),
        "total_inputs": len(scored) or 1,
        # E1 COMPOSITE DISCLOSURE (Chairman-ruled 2026-07-19): same rule as equities.
        "unmeasured_in_composite": sum(1 for s in scored.values()
                                       if s.get("degenerate_baseline")),
        "composite_note": ("No proxy money-positioning data for this coin — showing "
                           "market-confirmation only; the money read is absent, not zero."
                           if money_data_absent else
                           "Components without measured data are held at the neutral "
                           "baseline in the composite score."
                           if any(s.get("degenerate_baseline") for s in scored.values())
                           else None),
        "price": ({k: price.get(k) for k in ("last_close", "change_7d_pct", "change_30d_pct", "trend", "as_of")}
                  if price and price.get("available") else None),
        # §17: when the money read is ABSENT, the dark_matter block is OMITTED ENTIRELY — a
        # sub-source that did not contribute to the served read is never rendered beside it.
        # This is also what stops the crypto ledger enrolling on the suppressed direction
        # (record_from_serve reads dark_matter.flow; see its own guard for defense in depth).
        "dark_matter": ({"coverage": (dm or {}).get("proxy_coverage"), "flow": (dm or {}).get("flow"),
                         "intensity": (dm or {}).get("intensity"), "proxies_covered": covered}
                        if (dm and dm.get("available") and not money_data_absent) else None),
        "disclaimer": _DISCLAIMER,
    }


def apply_crypto_signal(coin: str, record_this_cycle: bool = True,
                        db_path: str = mse.DB_PATH, conn=None) -> dict:
    """Full pipeline for one coin: signal → components → record cycle → baselines → dual score."""
    coin = coin.upper()
    sig = cs.signal_for(coin, with_dark_matter=True)
    comps = assemble_crypto_components(coin, sig)
    item_key = f"crypto:{coin}"
    if record_this_cycle:
        mse.record_market_cycle(item_key, comps, db_path=db_path, conn=conn)
    baselines = mse.get_market_baselines(item_key, db_path=db_path, conn=conn)
    name = (cs.COIN_UNIVERSE.get(coin) or {}).get("name", coin)
    return compute_crypto_signal(coin, name, comps, baselines,
                                 flow=sig.get("consensus_flow", "neutral"),
                                 price=sig.get("_price"), dm=sig.get("_dark_matter"))


def serve_crypto(coins: Optional[list] = None, record: bool = False, db_path: str = mse.DB_PATH) -> dict:
    """List payload for the /crypto feed. record=False for read-only serves (the scheduler records)."""
    coins = coins or DEFAULT_COINS
    mse.init_market_signal_db(db_path)
    out = []
    for c in coins:
        try:
            out.append(apply_crypto_signal(c, record_this_cycle=record, db_path=db_path))
        except Exception as e:
            print(f"[crypto_money_gradient] {c}: {e}")
    return {"available": CRYPTO_SIGNAL, "held_out": not CRYPTO_SIGNAL,
            "model": "crypto-money-gradient-v1", "section": "Crypto",
            "coins": out, "count": len(out), "disclaimer": _DISCLAIMER}


if __name__ == "__main__":
    import sys, json
    coins = [a.upper() for a in sys.argv[1:] if not a.startswith("-")] or None
    r = serve_crypto(coins, record=("--record" in sys.argv))
    for c in r["coins"]:
        print(f"\n{c['coin']:5} {c['item_name']}  [{c['tier']}]  {c['gap_state']}")
        print(f"   Money Movement (D):      {c['money_movement']}  ({c['detection_level']})")
        print(f"   Market Confirmation (M): {c['market_confirmation']}  ({c['confidence_level']})")
        print(f"   Flow: {c['flow']}   calibrating={c['calibrating']}")
        for label, comp in c["components"].items():
            print(f"      - {label[:46]:46} {comp['score']}  z={comp['z']} br={comp['baseline_relative']}")
