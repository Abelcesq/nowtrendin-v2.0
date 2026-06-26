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
DEFAULT_COINS = [c.strip().upper() for c in os.getenv("CRYPTO_COINS", "BTC,ETH").split(",") if c.strip()]

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

_DISCLAIMER = ("Measurement of crypto money movement relative to this coin's own baseline. Analysis only — "
               "not financial advice, not a buy/sell signal, and not a price prediction. Whether an early "
               "movement led realized price is recorded, after the fact, by the crypto Accuracy Ledger.")


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
    gap = round(money_movement - market_confirmation, 1)
    # Reuse the equity Money-Gradient interpretation (movement + facts language, no advice).
    interp = mse._interpret_movement(money_movement, market_confirmation, gap, any_calibrating)

    return {
        "item_key": f"crypto:{coin}", "coin": coin, "item_name": name, "section": "Crypto",
        "model_version": "crypto-v1",
        # dual-ring aliases (frontend renders detection/confidence rings)
        "detection": money_movement, "confidence": market_confirmation, "gap": gap,
        "money_movement": money_movement, "market_confirmation": market_confirmation,
        "tier": mse._level((money_movement + market_confirmation) / 2),
        "detection_level": mse._level(money_movement), "confidence_level": mse._level(market_confirmation),
        "detection_fp": mse.MONEY_MOVEMENT_FP, "confidence_fp": mse.MARKET_CONFIRM_FP,
        "gap_state": interp["state"], "interpretation": interp["text"], "calibrating": any_calibrating,
        "flow": flow,
        # §17 source-display: only render components that contributed; show real value or n/a (never NaN).
        "components": {
            CRYPTO_LABELS[c]: ({
                "score": round(scored[c]["score"] * 100, 1),
                "feeds": ("money_movement" if c in CRYPTO_MM_WEIGHTS else "market_confirmation"),
                "baseline_relative": scored[c].get("baseline_relative", False),
                "z": scored[c].get("z"),
            } if c in scored else {
                "score": None, "feeds": "n/a", "not_applicable": True,
                "baseline_relative": False, "z": None,
            }) for c in CRYPTO_LABELS
        },
        "price": ({k: price.get(k) for k in ("last_close", "change_7d_pct", "change_30d_pct", "trend", "as_of")}
                  if price and price.get("available") else None),
        "dark_matter": ({"coverage": (dm or {}).get("proxy_coverage"), "flow": (dm or {}).get("flow"),
                         "intensity": (dm or {}).get("intensity"), "proxies_covered": covered}
                        if dm and dm.get("available") else None),
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
