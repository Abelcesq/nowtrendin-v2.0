"""
crypto_signals.py — HELD-OUT Crypto Money Gradient research (Phase 1; imported by NOTHING in scoring).

A per-coin MONEY GRADIENT for crypto, mirroring the equity Money Gradient (Market Signal v2) but with
crypto-appropriate sources. We do NOT read on-chain wallet flows directly (that needs a new paid source —
Glassnode/Nansen); v1 reads institutional / informed money via crypto-EXPOSURE PROXY securities:

  MONEY MOVEMENT (Detection / D) — informed money into crypto exposure, via proxies:
    • Spot-crypto ETF 13F flow         IBIT/FBTC/GBTC (BTC) · ETHA/ETHE (ETH) — institutions reporting crypto-ETF positions
    • Crypto-treasury / exchange names MSTR (largest corporate BTC holder) · COIN (Coinbase) — insider Form-4 + 13F
    • (Phase 2) Congress crypto trades (Quiver) · CME BTC/ETH futures positioning + microstructure (Databento GLBX.MDP3)

  MARKET CONFIRMATION (Confidence / M) — the coin's OWN price / volume momentum (the broad crypto market
    confirming the move), via FMP (BTCUSD…) with AV DIGITAL_CURRENCY_DAILY as fallback.

  FLOW (inflow / outflow) — consensus direction of D (proxy accumulation / distribution) and M (price momentum).

Dark Matter for crypto is STRONGEST for BTC (multiple ETFs + MSTR + COIN) and ETH (ETFs + COIN); altcoins
beyond these have only COIN as a proxy — an honest limitation surfaced per coin (`proxy_coverage`).

Discipline: HELD-OUT (imported by nothing in scoring) → research the output → BACKTEST-BEFORE-SHIP against a
crypto accuracy ledger (realized coin price direction) → only then a flag-gated Crypto Money Gradient + /crypto
page + nav. A FACT of where money is moving — NEVER advice, never a buy/sell signal, never a price prediction.
"""
from __future__ import annotations
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    import fmp_data
except Exception:                       # pragma: no cover - import shape varies by entrypoint
    fmp_data = None
try:
    import av_dark_positioning as avdp
except Exception:                       # pragma: no cover
    avdp = None

# ── Coin universe + crypto-exposure proxies ────────────────────────────────────────────────
# kind: etf (spot-crypto ETF 13F) · treasury (corp holding the coin) · exchange (crypto venue).
# weight: how directly the proxy tracks THIS coin's institutional flow (1.0 = a dedicated spot ETF).
COIN_UNIVERSE: dict = {
    "BTC": {
        "name": "Bitcoin", "fmp": "BTCUSD", "av": "BTC",
        #: F1 (Board 2026-08-05, 4 seats independently; Chairman-ordered): the fund
        #: class's voice in D is PINNED — roster growth redistributes within the
        #: class, never grows it. Changing this number is a deliberate ruling.
        "etf_class_budget": 4.2,
        "proxies": [
            {"ticker": "IBIT", "kind": "etf",      "weight": 1.0},   # BlackRock spot BTC ETF (largest)
            {"ticker": "FBTC", "kind": "etf",      "weight": 0.8},   # Fidelity spot BTC ETF
            {"ticker": "GBTC", "kind": "etf",      "weight": 0.7},   # Grayscale BTC trust/ETF
            # Stage 0 (Board 2026-08-01, [cold-start-stated]): roster breadth for the ETF
            # share-flow leg. AUM+NAV verified on our FMP plan for every ticker below.
            {"ticker": "ARKB", "kind": "etf",      "weight": 0.6},   # ARK 21Shares spot BTC
            {"ticker": "BITB", "kind": "etf",      "weight": 0.6},   # Bitwise spot BTC
            {"ticker": "HODL", "kind": "etf",      "weight": 0.5},   # VanEck spot BTC
            {"ticker": "MSTR", "kind": "treasury", "weight": 0.9},   # MicroStrategy — largest corp BTC holder
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},   # Coinbase — broad crypto exposure
        ],
    },
    "ETH": {
        "name": "Ethereum", "fmp": "ETHUSD", "av": "ETH",
        "etf_class_budget": 3.0,   # F1 pinned (see BTC note)
        "proxies": [
            {"ticker": "ETHA", "kind": "etf",      "weight": 1.0},   # BlackRock spot ETH ETF
            {"ticker": "ETHE", "kind": "etf",      "weight": 0.7},   # Grayscale ETH trust/ETF
            {"ticker": "FETH", "kind": "etf",      "weight": 0.8},   # Fidelity spot ETH (Stage 0)
            {"ticker": "ETHW", "kind": "etf",      "weight": 0.5},   # Bitwise spot ETH (Stage 0)
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},
        ],
    },
    "SOL": {
        "name": "Solana", "fmp": "SOLUSD", "av": "SOL",
        "etf_class_budget": 2.0,   # F1 pinned (see BTC note)
        "proxies": [
            # Stage 0 (2026-08-01): US spot SOL ETFs now exist and our FMP plan serves their
            # AUM+NAV (verified: BSOL $588M, GSOL $95M, TSOL $3M). They vote ONLY when the
            # ETF share-flow leg ships (CRYPTO_ETF_FLOW); until then SOL remains honestly
            # structural — _max_votable counts ETFs iff the flag is on (Guardian condition:
            # absence_class describes the instrument AS DEPLOYED, never as committed).
            {"ticker": "BSOL", "kind": "etf",      "weight": 1.0},   # Bitwise spot SOL (largest)
            {"ticker": "GSOL", "kind": "etf",      "weight": 0.7},   # Grayscale SOL
            {"ticker": "TSOL", "kind": "etf",      "weight": 0.3},   # 21Shares SOL — BELOW the
            # AUM voting floor; snapshots for evidence, must not vote (Board: quantization
            # noise 0.14%/day + ~2.3% creation-basket granularity at $3M AUM).
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},
        ],
    },
    "XRP": {
        "name": "XRP", "fmp": "XRPUSD", "av": "XRP",
        "etf_class_budget": 1.8,   # F1 pinned (see BTC note)
        "proxies": [
            # Stage 0 (2026-08-01): US spot XRP ETFs verified on our plan (XRPC $272M,
            # TOXR $124M). Same deployment rule as SOL above.
            {"ticker": "XRPC", "kind": "etf",      "weight": 1.0},   # Canary XRP (largest)
            {"ticker": "TOXR", "kind": "etf",      "weight": 0.8},   # 21Shares XRP
            {"ticker": "COIN", "kind": "exchange", "weight": 0.4},
        ],
    },
    "DOGE": {
        "name": "Dogecoin", "fmp": "DOGEUSD", "av": "DOGE",
        "proxies": [
            {"ticker": "COIN", "kind": "exchange", "weight": 0.3},
        ],
    },
    # Additional majors (FMP price verified). Proxy = COIN only (broad crypto-exposure) → Dark Matter
    # is THIN / shared for alts: Money Movement reads institutional crypto sentiment via Coinbase, while
    # Market Confirmation (price/volume) is coin-specific. Per-coin proxies improve as spot ETFs list.
    "BNB":  {"name": "BNB",          "fmp": "BNBUSD",  "av": "BNB",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.3}]},
    "ADA":  {"name": "Cardano",      "fmp": "ADAUSD",  "av": "ADA",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "AVAX": {"name": "Avalanche",    "fmp": "AVAXUSD", "av": "AVAX",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "LINK": {"name": "Chainlink",    "fmp": "LINKUSD", "av": "LINK",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "DOT":  {"name": "Polkadot",     "fmp": "DOTUSD",  "av": "DOT",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "LTC":  {"name": "Litecoin",     "fmp": "LTCUSD",  "av": "LTC",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "BCH":  {"name": "Bitcoin Cash", "fmp": "BCHUSD",  "av": "BCH",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
}

PRICE_LOOKBACK_DAYS = int(os.getenv("CRYPTO_PRICE_LOOKBACK_DAYS", "45"))

# ── C3: SUPPLY SEMANTICS (per-asset, Lewis doctrine) — curated REFERENCE metadata ─────────
# Chairman-ruled 2026-08-05 with an OWNER attached: the weekly /improve-system audit reviews
# these stamps (checklist line), and any coin's protocol upgrade triggers a re-verify. Board
# condition honored: sourced from CURRENT protocol documentation, never from the book (the
# Challenger's catch — Lewis's 2018 ETH mechanics predate the merge and EIP-1559).
# schedule: fixed_schedule (hard cap, algorithmic) · policy_changeable (issuance amendable
# by protocol upgrade) · pre_mined (fixed genesis supply, no ongoing issuance) ·
# deflationary_burn (supply engineered to shrink). max_supply None = NO cap exists — FDV is
# UNDEFINED and must render "no max supply", never a fabricated number (§17).
SUPPLY_MODEL: dict = {
    "BTC":  {"schedule": "fixed_schedule", "max_supply": 21_000_000,
             "notes": "halving schedule; hard cap 21M",
             "source": "Bitcoin protocol documentation", "as_of": "2026-08-05"},
    "ETH":  {"schedule": "policy_changeable", "max_supply": None,
             "notes": "post-merge PoS issuance + EIP-1559 fee burn; no cap; policy has "
                      "changed by upgrade repeatedly",
             "source": "ethereum.org protocol documentation", "as_of": "2026-08-05"},
    "SOL":  {"schedule": "policy_changeable", "max_supply": None,
             "notes": "disinflationary schedule toward ~1.5% terminal inflation; no cap",
             "source": "Solana protocol documentation", "as_of": "2026-08-05"},
    "XRP":  {"schedule": "pre_mined", "max_supply": 100_000_000_000,
             "notes": "100B created at genesis, escrowed releases; supply only shrinks "
                      "via fee burn",
             "source": "XRPL documentation", "as_of": "2026-08-05"},
    "DOGE": {"schedule": "policy_changeable", "max_supply": None,
             "notes": "no cap; ~5B new DOGE per year fixed absolute issuance",
             "source": "Dogecoin protocol documentation", "as_of": "2026-08-05"},
    "BNB":  {"schedule": "deflationary_burn", "max_supply": None,
             "notes": "auto-burn from 200M genesis toward a 100M target; FDV undefined "
                      "in the capped-supply sense",
             "source": "BNB Chain documentation", "as_of": "2026-08-05"},
    "ADA":  {"schedule": "fixed_schedule", "max_supply": 45_000_000_000,
             "notes": "hard cap 45B", "source": "Cardano documentation", "as_of": "2026-08-05"},
    "AVAX": {"schedule": "fixed_schedule", "max_supply": 720_000_000,
             "notes": "hard cap 720M; fees burned",
             "source": "Avalanche documentation", "as_of": "2026-08-05"},
    "LINK": {"schedule": "pre_mined", "max_supply": 1_000_000_000,
             "notes": "1B created at genesis; no ongoing issuance",
             "source": "Chainlink documentation", "as_of": "2026-08-05"},
    "DOT":  {"schedule": "policy_changeable", "max_supply": None,
             "notes": "inflationary, parameters governance-amendable; no cap",
             "source": "Polkadot documentation", "as_of": "2026-08-05"},
    "LTC":  {"schedule": "fixed_schedule", "max_supply": 84_000_000,
             "notes": "hard cap 84M; halving schedule",
             "source": "Litecoin protocol documentation", "as_of": "2026-08-05"},
    "BCH":  {"schedule": "fixed_schedule", "max_supply": 21_000_000,
             "notes": "hard cap 21M; halving schedule",
             "source": "Bitcoin Cash protocol documentation", "as_of": "2026-08-05"},
}

# ── C1: SIZE BANDS by circulating-supply network value (Burniske's sizing doctrine) ───────
# PRE-DECLARED crypto-native edges (Board condition: the $10B/$2B equity convention makes
# every top-12 coin "large" — no discriminating power). Chosen 2026-08-05 so the tracked
# universe splits meaningfully; the band describes VOLATILITY/LIQUIDITY CHARACTER as the
# historical property of the size class — never quality, never a forward-looking claim.
CRYPTO_BANDS = (  # (floor_usd, label)
    (100e9, "mega"), (10e9, "large"), (1e9, "mid"), (0, "small"))
CRYPTO_SUPPLY_FACTS = os.getenv("CRYPTO_SUPPLY_FACTS", "1") == "1"


def supply_facts(coin: str) -> Optional[dict]:
    """C1+C2 (Chairman-ruled 2026-08-05): network value (circulating cap), size band,
    circulating-vs-FDV and % of max supply — the per-asset-metric doctrine on display.
    DISPLAY-ONLY (never a scoring input). §17: returns None when live data is absent —
    the section is omitted, never fabricated. FDV for uncapped coins is honestly
    'no max supply', never a made-up denominator."""
    if not CRYPTO_SUPPLY_FACTS or not fmp_data:
        return None
    c = COIN_UNIVERSE.get(coin.upper())
    if not c:
        return None
    try:
        q = fmp_data.coin_quote(c["fmp"])
    except Exception:
        q = None
    if not q:
        return None
    cap, price = q["market_cap"], q["price"]
    band = next(lbl for floor, lbl in CRYPTO_BANDS if cap >= floor)
    sm = SUPPLY_MODEL.get(coin.upper()) or {}
    maxs = sm.get("max_supply")
    circ = q["circulating_supply"]
    out = {
        "network_value_usd": round(cap),          # Burniske: price × circulating supply
        "circulating_supply": round(circ),
        "size_band": band,
        "band_basis": "circulating-supply network value; bands pre-declared 2026-08-05 "
                      "(mega ≥$100B, large ≥$10B, mid ≥$1B, small <$1B)",
        "supply_schedule": sm.get("schedule"),
        "supply_notes": sm.get("notes"),
        "supply_source": sm.get("source"),
        "supply_as_of": sm.get("as_of"),
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "caveat": "circulating supply is the vendor-reported figure and includes "
                  "provably-lost coins where they cannot be distinguished — network "
                  "value can overstate spendable supply",
    }
    if maxs:
        out["max_supply"] = maxs
        out["fdv_usd"] = round(price * maxs)      # fully diluted valuation
        out["pct_of_max_outstanding"] = round(100.0 * circ / maxs, 1)
    else:
        out["max_supply"] = None
        out["fdv_usd"] = None
        out["fdv_note"] = "no max supply (" + (sm.get("schedule") or "uncapped") + \
                          ") — FDV is undefined for this asset, not omitted by error"
    return out
# AV 13F institutional self-throttles 13s/call → too slow for the LIVE roster (the page would hang).
# Default to the FAST Finviz-insider-only Dark Matter; set CRYPTO_FULL_DM=1 to add AV 13F (slow, for
# background research only). Finviz insider (uncapped) is the primary D read either way.
CRYPTO_FULL_DM = os.getenv("CRYPTO_FULL_DM", "0") == "1"


def available() -> dict:
    """Which data legs are wired (held-out plumbing check)."""
    return {
        "price_fmp": bool(fmp_data and getattr(fmp_data, "FMP_API_KEY", "")),
        "dark_matter_av": bool(avdp and avdp.available()),
    }


# ── MARKET CONFIRMATION (M): the coin's own price/volume momentum ────────────────────────────
def _pct(a: float, b: float) -> Optional[float]:
    return None if not b else (a - b) / b * 100.0


def _closest_on_or_before(series: dict, target: str) -> Optional[float]:
    """Latest close at or before `target` (handles weekends/gaps; crypto trades 7d but FMP can gap)."""
    keys = sorted(k for k in series if k <= target)
    return series[keys[-1]] if keys else None


_AV_PRICE_CACHE: dict = {}


def _av_crypto_series(coin: str) -> Optional[dict]:
    """AV DIGITAL_CURRENCY_DAILY → {date: close_usd}. Fallback when FMP is throttled (free-tier 429).
    AV has headroom now that Finviz owns the insider pulls. Cached per process (daily series)."""
    import time as _t
    key = os.getenv("ALPHAVANTAGE_RESEARCH_KEY") or os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not key:
        return None
    sym = (COIN_UNIVERSE.get(coin.upper()) or {}).get("av") or coin.upper()
    ent = _AV_PRICE_CACHE.get(sym)
    if ent and (_t.time() - ent["ts"] < 21600):       # 6h cache
        return ent["data"]
    import json as _json, urllib.request as _ur, urllib.parse as _up
    url = "https://www.alphavantage.co/query?" + _up.urlencode(
        {"function": "DIGITAL_CURRENCY_DAILY", "symbol": sym, "market": "USD", "apikey": key})
    out = None
    try:
        with _ur.urlopen(url, timeout=20) as r:
            d = _json.loads(r.read().decode("utf-8"))
        ts = d.get("Time Series (Digital Currency Daily)") or {}
        parsed = {}
        for date, row in ts.items():
            v = row.get("4. close") or row.get("4a. close (USD)")
            try:
                parsed[date] = float(v)
            except (TypeError, ValueError):
                continue
        out = parsed or None
    except Exception as e:
        print(f"[crypto av-price] {sym}: {e}")
    _AV_PRICE_CACHE[sym] = {"data": out, "ts": _t.time()}
    return out


def price_momentum(coin: str) -> dict:
    """The coin's price trend = the broad crypto market CONFIRMING (or not) the move. A measurement.
    FMP primary; AV DIGITAL_CURRENCY_DAILY fallback when FMP is throttled (free-tier 429)."""
    c = COIN_UNIVERSE.get(coin.upper())
    if not c:
        return {"available": False, "reason": "unknown coin"}
    today = datetime.now(timezone.utc).date()
    frm = (today - timedelta(days=PRICE_LOOKBACK_DAYS)).isoformat()
    series, src = None, ""
    if fmp_data and getattr(fmp_data, "FMP_API_KEY", ""):
        series = fmp_data.historical_close(c["fmp"], frm=frm, to=today.isoformat())
        if series:
            src = "fmp"
    if not series:                                     # FMP empty/throttled → AV crypto fallback
        series = _av_crypto_series(coin)
        if series:
            src = "alphavantage"
    if not series:
        return {"available": False, "reason": "no price series (FMP+AV)", "symbol": c["fmp"]}
    dates = sorted(series)
    last_d = dates[-1]
    last = series[last_d]
    d7 = (datetime.fromisoformat(last_d).date() - timedelta(days=7)).isoformat()
    d30 = (datetime.fromisoformat(last_d).date() - timedelta(days=30)).isoformat()
    c7 = _closest_on_or_before(series, d7)
    c30 = _closest_on_or_before(series, d30)
    m7 = _pct(last, c7) if c7 else None
    m30 = _pct(last, c30) if c30 else None
    trend = "flat"
    if m7 is not None:
        trend = "up" if m7 > 1.0 else "down" if m7 < -1.0 else "flat"
    # Confirmation strength 0-100: scaled |7d move|, bonus when 7d and 30d agree (sustained, not a blip).
    base = min(100.0, abs(m7) * 6.0) if m7 is not None else 0.0   # ~16.7% move → 100
    aligned = m7 is not None and m30 is not None and (m7 > 0) == (m30 > 0)
    confirmation = round(min(100.0, base * (1.15 if aligned else 0.85)), 1)
    return {
        "available": True, "symbol": c["fmp"], "source": src, "as_of": last_d, "last_close": round(last, 4),
        "change_7d_pct": None if m7 is None else round(m7, 2),
        "change_30d_pct": None if m30 is None else round(m30, 2),
        "trend": trend, "aligned_7d_30d": aligned, "confirmation": confirmation,
    }


# ── MONEY MOVEMENT (D): informed money via proxy securities ─────────────────────────────────
#: --- ETF SHARE-FLOW LEG (Stage 1; Board 2026-08-01) - flag-gated, DEFAULT OFF ---------
#: The two-sided crypto money read: net creations (+) / redemptions (-) of the spot funds.
#: BRIDGE CONSTANTS (16a stage-1 CALIBRATING read - explicitly NOT the destination): the
#: Board rejected these numbers as 4-day-derived and pre-declared the replacement - per-fund
#: floors read off a >=30-trading-day study via the committed formula, then a robust z on the
#: coin's own aggregate flow (see audits/board/CRYPTO_FLOW_SPEC_v1_2026-08-02.md). Tuning
#: these quietly instead of running that study is the forbidden path.
CRYPTO_ETF_FLOW = os.getenv("CRYPTO_ETF_FLOW", "0") == "1"
ETF_VOTE_MIN_AUM = float(os.getenv("ETF_VOTE_MIN_AUM", "50000000"))    # $50M eligibility floor
ETF_VOTE_FLOOR_PCT = float(os.getenv("ETF_VOTE_FLOOR_PCT", "0.10"))    # per-day materiality
ETF_VOTE_SCALE_PCT = float(os.getenv("ETF_VOTE_SCALE_PCT", "1.0"))     # |delta| where vote = +/-1


def _etf_flow_vote(ticker: str):
    """(vote, detail) for one spot-fund proxy from recorded share-count deltas.

    Vote semantics, PRE-DECLARED (Board conditions):
      - fund below ETF_VOTE_MIN_AUM -> None (INELIGIBLE - a $3M fund's creation basket is
        ~2.3% of its shares; it would vote on quantization, so it never votes at all);
      - stale / discontinuity / no data -> None (no read, not a zero);
      - |delta| below the floor -> vote 0.0, IN the denominator - a measured quiet day is
        information (the sub-floor rule the Challenger required be declared: unanimous
        sub-floor days read as measured-neutral, never as absence);
      - else sign(delta) * min(1, |delta|/scale) - magnitude-scaled, never the binary latch
        that broke the insider vote ($250K and $250M reading identically).
    """
    import etf_flow
    d = etf_flow.latest_delta(ticker)
    detail = {"etf_flow": d}
    if not d.get("available"):
        return None, detail
    aum = d.get("aum_latest") or 0.0
    if aum < ETF_VOTE_MIN_AUM:
        detail["etf_flow"] = {**d, "ineligible": f"AUM ${aum:,.0f} below "
                              f"${ETF_VOTE_MIN_AUM:,.0f} voting floor"}
        return None, detail
    delta = d["delta_pct_per_day"]
    if abs(delta) < ETF_VOTE_FLOOR_PCT:
        return 0.0, detail
    vote = (1.0 if delta > 0 else -1.0) * min(1.0, abs(delta) / ETF_VOTE_SCALE_PCT)
    return round(vote, 3), detail


def _proxy_vote(sig: dict) -> Optional[float]:
    """Signed [-1,1] directional vote for ONE proxy from av_dark_positioning.signal_for output.
    Insider: BUYING (signal=='accumulation') → +1; routine net selling is low-information → no insider
    vote (insider net is structurally sell-dominated, so it's not treated as bearish). Institutional
    13F is genuinely two-sided → +1/-1 on net share flow. None = no usable signal."""
    if not sig:
        return None
    votes = []
    ins = sig.get("insider") or {}
    if ins.get("available") and ins.get("signal") == "accumulation":
        votes.append(1.0)                       # rare, high-conviction insider BUY
    inst = sig.get("institutional") or {}
    if inst.get("available"):
        ns = inst.get("net_shares") or 0
        if ns > 0:
            votes.append(1.0)
        elif ns < 0:
            votes.append(-1.0)
    if not votes:
        return None
    return sum(votes) / len(votes)


def proxy_dark_matter(coin: str, max_proxies: Optional[int] = None) -> dict:
    """Aggregate informed-money direction across the coin's crypto-exposure proxies.
    Returns a weighted net direction (inflow/outflow), an intensity 0-100, and per-proxy detail.
    HELD-OUT — a FACT from filings, not advice. `max_proxies` trims AV calls during testing."""
    c = COIN_UNIVERSE.get(coin.upper())
    if not c:
        return {"available": False, "reason": "unknown coin"}
    if not (avdp and avdp.source_available()):
        return {"available": False, "reason": "no dark-positioning source configured (AV or Finviz)"}
    proxies = c["proxies"][: max_proxies] if max_proxies else c["proxies"]
    detail = []
    num = 0.0          # weighted signed direction
    den = 0.0          # sum of weights that produced a usable vote
    etf_votes = []     # (proxy, vote, aum) — sized AFTER the loop (A1 AUM-relative weights)
    for p in proxies:
        if p.get("kind") == "etf" and CRYPTO_ETF_FLOW:
            # The share-flow leg: two-sided, price-independent, from recorded snapshots
            # only - no network call on this path (prewarm serves crypto; S13).
            vote, _fd = _etf_flow_vote(p["ticker"])
            _f = _fd.get("etf_flow") or {}
            detail.append({
                "ticker": p["ticker"], "kind": p["kind"], "weight": p["weight"],
                "vote": vote,
                "etf_flow_delta_pct": _f.get("delta_pct_per_day"),
                "etf_flow_note": _f.get("reason") or _f.get("ineligible"),
                "aum_usd": _f.get("aum_latest"),
                "has_data": vote is not None,
            })
            if vote is not None:
                # A1 (Chairman 2026-08-05, grounded in the per-asset-metric doctrine —
                # funds are measured by AUM, coins by circulating-supply cap): each fund
                # is tracked separately and its vote is sized by its AUM share WITHIN the
                # coin's fund class, folded after the loop. An $80B fund's redemption day
                # and a $60M fund's must not read as equal votes. NOT circular: every
                # fund of one coin tracks the same coin price, so the price multiplies
                # all AUMs equally and CANCELS in the relative weights.
                etf_votes.append((p, vote, float(_f.get("aum_latest") or 0.0)))
            continue
        if True:
            sig = avdp.signal_for(p["ticker"], name=p["ticker"], with_institutional=CRYPTO_FULL_DM)
            vote = _proxy_vote(sig)
            ins = (sig or {}).get("insider") or {}
            inst = (sig or {}).get("institutional") or {}
            detail.append({
                "ticker": p["ticker"], "kind": p["kind"], "weight": p["weight"],
                "vote": vote, "combined_flow": (sig or {}).get("combined_flow"),
                "insider_net_usd": ins.get("net_usd"), "inst_net_shares": inst.get("net_shares"),
                "has_data": vote is not None,
            })
        if vote is not None:
            num += p["weight"] * vote
            den += p["weight"]

    # A1: fold the fund class in ONE step, each fund sized by its AUM share within the
    # class. F1 FIX (Board 2026-08-05 — found independently by FOUR seats; Chairman-
    # ordered): the budget was Σ weights of the funds that VOTED, so roster growth grew
    # the class's voice against insider-equity and a stale fund shrank it — availability,
    # not information, moved the mix. The budget is now the coin's PINNED
    # `etf_class_budget` constant (fallback: Σ over the FULL configured roster) — a
    # fixed design intent for how much of D the fund class carries. Whenever ANY fund
    # votes, the class speaks with its full pinned voice; funds redistribute WITHIN it
    # by AUM share. Measured-quiet (vote 0.0) funds stay in the denominator.
    if etf_votes:
        class_budget = float(c.get("etf_class_budget") or
                             sum(p["weight"] for p in c["proxies"]
                                 if p.get("kind") == "etf"))
        aum_sum = sum(a for _, _, a in etf_votes)
        if aum_sum > 0:
            class_vote = sum(v * (a / aum_sum) for _, v, a in etf_votes)
        else:
            class_vote = sum(v for _, v, _ in etf_votes) / len(etf_votes)
        num += class_budget * class_vote
        den += class_budget

    covered = sum(1 for d in detail if d["has_data"])
    total = len(c["proxies"])
    net = (num / den) if den else 0.0
    flow = "inflow" if net > 0.15 else "outflow" if net < -0.15 else ("mixed" if den else "no_data")

    # VENUE CLASSES (A1, the gate-5 fix): coverage/diffusion is measured over KINDS of
    # venue — insider-equity filings = one class, fund share-flow = one class — never
    # over instrument count. Flipping 6 funds live must not read as diffusion: adding
    # thermometers is not a temperature change. Coverage-invariant by construction, so
    # the next fund (or a future non-US ETP) never moves a score by existing.
    kinds_reachable = set()
    for p in c["proxies"]:
        if p.get("kind") == "etf":
            if CRYPTO_ETF_FLOW:
                kinds_reachable.add("etf_flow")
        else:
            kinds_reachable.add("insider_equity")
    kinds_active = {("etf_flow" if d["kind"] == "etf" else "insider_equity")
                    for d in detail if d["has_data"]}

    if CRYPTO_ETF_FLOW:
        # Intensity's coverage confidence also moves to the class basis — the fund-count
        # basis would jump 1→6 at the flip on roster alone (the same artifact).
        coverage_conf = (len(kinds_active) / len(kinds_reachable)) if kinds_reachable else 0.0
    else:
        # Flag off: byte-identical legacy behavior.
        coverage_conf = covered / total if total else 0.0
    intensity = round(min(100.0, abs(net) * 100.0 * (0.5 + 0.5 * coverage_conf)), 1)

    # F6 (Board 2026-08-05, Challenger): the venue-class principle applies to the
    # SIBLING coverage fields too — `proxy_coverage` graded on instrument count would
    # keep the thermometer artifact alive in the exact field the ledger's enrollment
    # gate consults. Flag on: strong = both venue kinds reporting; partial = one;
    # thin = none. `proxies_covered` keeps its honest instrument-count meaning (it is
    # labeled as such) for display and the >=2-fund corroboration check.
    if CRYPTO_ETF_FLOW:
        pcov = ("strong" if len(kinds_active) >= 2 else
                "partial" if kinds_active else "thin")
    else:
        pcov = "strong" if total >= 4 and covered >= 2 else "thin" if total <= 1 else "partial"
    out = {
        "available": den > 0, "flow": flow, "net_direction": round(net, 3), "intensity": intensity,
        "proxies_covered": covered, "proxies_total": total,
        "proxy_coverage": pcov,
        "detail": detail,
    }
    if CRYPTO_ETF_FLOW:
        out["coverage_basis"] = "venue_classes"
        out["venue_classes_active"] = sorted(kinds_active)
        out["venue_classes_reachable"] = sorted(kinds_reachable)
        if etf_votes:
            # Gate-6 latency stamps (spec §5): a creation is money ARRIVING, observed at
            # T+1. Lead 0-1 is parity, never prescience; never subtracted back.
            out["flow_basis"] = "etf_creations"
            out["signal_latency_days"] = 1
    return out


# ── Combined per-coin Money Gradient ────────────────────────────────────────────────────────
def signal_for(coin: str, with_dark_matter: bool = True, max_proxies: Optional[int] = None) -> dict:
    """Per-coin Crypto Money Gradient = Money Movement (D, proxies) + Market Confirmation (M, price).
    HELD-OUT research output — a measurement of where money is moving, NEVER advice."""
    coin = coin.upper()
    c = COIN_UNIVERSE.get(coin)
    if not c:
        return {"available": False, "reason": "unknown coin", "coin": coin}
    m = price_momentum(coin)
    d = proxy_dark_matter(coin, max_proxies=max_proxies) if with_dark_matter else {"available": False, "reason": "skipped"}

    # Overall flow = consensus of D (informed) and M (market). D leads (it's the early read); M confirms.
    d_flow = d.get("flow") if d.get("available") else None
    m_trend = m.get("trend") if m.get("available") else None
    m_dir = {"up": "inflow", "down": "outflow", "flat": "neutral"}.get(m_trend or "")
    if d_flow in ("inflow", "outflow") and m_dir in ("inflow", "outflow"):
        consensus = d_flow if d_flow == m_dir else "divergent"
    else:
        consensus = d_flow or m_dir or "no_data"

    out_sig = {
        "available": bool(m.get("available") or d.get("available")),
        "coin": coin, "name": c["name"], "held_out": True,
        "money_movement": {                       # D — informed money (proxies)
            "flow": d.get("flow"), "intensity": d.get("intensity"),
            "coverage": d.get("proxy_coverage"), "proxies_covered": d.get("proxies_covered"),
            "available": d.get("available", False),
        },
        "market_confirmation": {                  # M — the coin's own price
            "trend": m.get("trend"), "strength": m.get("confirmation"),
            "change_7d_pct": m.get("change_7d_pct"), "change_30d_pct": m.get("change_30d_pct"),
            "available": m.get("available", False),
        },
        "consensus_flow": consensus,
        "_price": m, "_dark_matter": d,
        "note": "HELD-OUT crypto research (proxy-based Dark Matter + price momentum). NOT in any score yet; "
                "backtest-before-ship. A FACT of where money is moving — not advice, not a prediction.",
    }
    # Gate-6 latency stamps ride to the top-level payload (and from there to ledger
    # rows) whenever the fund-flow leg contributed — spec §5: T+1, parity never
    # prescience, never subtracted back.
    if d.get("flow_basis"):
        out_sig["flow_basis"] = d["flow_basis"]
        out_sig["signal_latency_days"] = d.get("signal_latency_days")
    return out_sig


def research(coins: Optional[list] = None, with_dark_matter: bool = False,
             max_proxies: Optional[int] = None, pace_sec: float = 1.5) -> dict:
    """Run signal_for over the universe. `with_dark_matter=False` keeps it to cheap FMP price calls;
    enable it (paced, AV 25/day) only when researching the proxy Dark Matter. `pace_sec` spaces the
    per-coin FMP price calls so the free-tier burst limit (HTTP 429) isn't tripped on a multi-coin run."""
    coins = coins or list(COIN_UNIVERSE)
    out = []
    for i, c in enumerate(coins):
        out.append(signal_for(c, with_dark_matter=with_dark_matter, max_proxies=max_proxies))
        if pace_sec and i < len(coins) - 1:
            time.sleep(pace_sec)
    return {"held_out": True, "available": available(), "count": len(out), "signals": out,
            "note": "Held-out crypto Money Gradient research — NOT integrated into any score. Backtest-before-ship."}


if __name__ == "__main__":
    import sys, json
    dm = "--dm" in sys.argv
    mp = None
    for a in sys.argv:
        if a.startswith("--max="):
            mp = int(a.split("=", 1)[1])
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    coins = [a.upper() for a in args] or None
    print("available:", available())
    r = research(coins, with_dark_matter=dm, max_proxies=mp)
    for s in r["signals"]:
        mm, mc = s.get("money_movement", {}), s.get("market_confirmation", {})
        print(f"\n{s.get('coin'):5} {s.get('name','')}")
        print(f"   Market Confirmation (M): {mc.get('trend')} strength={mc.get('strength')} "
              f"7d={mc.get('change_7d_pct')}% 30d={mc.get('change_30d_pct')}%")
        print(f"   Money Movement (D):      flow={mm.get('flow')} intensity={mm.get('intensity')} "
              f"coverage={mm.get('coverage')} ({mm.get('proxies_covered')} proxies)")
        print(f"   Consensus flow:          {s.get('consensus_flow')}")
        if dm and s.get("_dark_matter", {}).get("detail"):
            for d in s["_dark_matter"]["detail"]:
                print(f"      - {d['ticker']:5} {d['kind']:9} vote={d['vote']} "
                      f"insider=${d.get('insider_net_usd')} inst_sh={d.get('inst_net_shares')}")
