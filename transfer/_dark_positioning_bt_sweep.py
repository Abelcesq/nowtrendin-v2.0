"""Multi-angle sweep of the Congress signal: horizons x (net vs buy-only). One process so
prices/bulk are fetched once and reused. No-lookahead (Filed date) throughout."""
import sys, math
sys.path.insert(0, "transfer")
import dark_positioning_backtest as bt
from datetime import datetime, timedelta
from collections import defaultdict

WINDOW = 90
TOP = 35
START = "2021-06-01"
bulk = bt.congress_bulk()
cnt = defaultdict(int)
for r in bulk:
    t = (r.get("Ticker") or "").upper().strip()
    if t and t.isalpha() and len(t) <= 5:
        cnt[t] += 1
universe = [t for t, _ in sorted(cnt.items(), key=lambda kv: -kv[1])[:TOP]]
net_fn, _ = bt.signals_by_ticker_date(WINDOW)

def dates_for(horizon):
    out = []
    d = datetime.strptime(START, "%Y-%m-%d")
    cutoff = datetime.utcnow() - timedelta(days=horizon + 7)
    for _ in range(70):
        if d > cutoff: break
        out.append(d.strftime("%Y-%m-%d"))
        d = (d.replace(day=1) + timedelta(days=32)).replace(day=1)
    return out

def avg(xs): return sum(xs) / len(xs) if xs else 0.0
def ic(nets, rets):
    def rank(xs):
        o = sorted(range(len(xs)), key=lambda i: xs[i]); rk=[0]*len(xs)
        for p,i in enumerate(o): rk[i]=p
        return rk
    rn, rr = rank(nets), rank(rets); mn, mr = avg(rn), avg(rr)
    num = sum((rn[i]-mn)*(rr[i]-mr) for i in range(len(nets)))
    den = math.sqrt(sum((x-mn)**2 for x in rn)*sum((x-mr)**2 for x in rr)) or 1
    return num/den

print(f"universe={len(universe)} window={WINDOW}d  (no-lookahead, Filed<=T)")
print(f"{'horizon':>7} {'mode':>9} {'N':>5} {'buy%':>7} {'sell%':>7} {'spread%':>8} {'IC':>7} {'buyHit%':>8}")
for H in (21, 63, 126, 252):
    DATES = dates_for(H)
    rows = []  # (net, buyintensity, ret)
    for t in universe:
        for T in DATES:
            b, s = net_fn(t, T)
            if b + s < 3:
                continue
            ret = bt.fwd_return(t, T, H)
            if ret is None:
                continue
            rows.append((b - s, b - s if b > s else 0, ret, b, s))
    if len(rows) < 20:
        print(f"{H:>7} {'(few obs)':>9} {len(rows):>5}")
        continue
    # NET mode
    buy = [r for n,bi,r,b,s in rows if n > 0]; sell = [r for n,bi,r,b,s in rows if n < 0]
    sp = 100*(avg(buy)-avg(sell)); icv = ic([n for n,bi,r,b,s in rows], [r for n,bi,r,b,s in rows])
    bh = 100*avg([1 if x>0 else 0 for x in buy])
    print(f"{H:>7} {'net':>9} {len(rows):>5} {100*avg(buy):>7.2f} {100*avg(sell):>7.2f} {sp:>8.2f} {icv:>7.3f} {bh:>8.1f}")
    # BUY-ONLY mode: strong-buy (net>0, buys>=2) vs the rest
    strongbuy = [r for n,bi,r,b,s in rows if n > 0 and b >= 2]
    rest = [r for n,bi,r,b,s in rows if not (n > 0 and b >= 2)]
    sp2 = 100*(avg(strongbuy)-avg(rest))
    bh2 = 100*avg([1 if x>0 else 0 for x in strongbuy])
    print(f"{H:>7} {'buy>=2':>9} {len(strongbuy):>5} {100*avg(strongbuy):>7.2f} {100*avg(rest):>7.2f} {sp2:>8.2f} {'-':>7} {bh2:>8.1f}")
