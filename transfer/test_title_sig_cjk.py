# -*- coding: utf-8 -*-
"""ENFORCER for the _title_sig CJK character window (ruling 5, fails-open CJK quorum —
BOARD_resume-audit_2026-09-14.md, Expansionist memo).

THE DEFECT. `_title_sig` collapses wire-syndication by lowercased/normalized text cut to
the FIRST 10 WORDS — space-tokenized. CJK/Japanese/Thai headlines carry no ASCII spaces,
so the word window is a no-op and the signature degenerates to EXACT-STRING matching:
five CJK mastheads carrying ONE wire story with slightly different suffixes count as five
distinct stories in `mainstream_breadth`'s min(distinct outlets, distinct titles) — the
§15a quorum FAILS OPEN in the largest non-Latin markets, while English correctly stays a
Dark-Matter trigger.

THE FIX UNDER TEST. Flag `TITLE_SIG_CJK` (default OFF — score-affecting, founder flip
only): a spaceless, no-space-script-dominant title truncates by CHARACTER window (first
20 non-space chars post-normalization) instead of the word window.

THE HARD PROPERTY (the board's backtest precondition, proven here against a frozen
verbatim copy of the pre-change algorithm):
  * flag OFF -> byte-identical to the old code for ALL inputs (Latin, CJK, Thai, mixed);
  * flag ON  -> byte-identical to the old code for every input containing an ASCII space
    or containing only Latin text. Only spaceless no-space-script titles change, at all.

Run: python test_title_sig_cjk.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import dual_pathway as dp  # noqa: E402

_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def frozen_original_sig(t: str) -> str:
    """VERBATIM copy of _title_sig as it stood BEFORE this change (post the 2026-08-20
    unicode fix). The identity oracle — do not "improve" it; its job is to be the past."""
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^\w ]+", " ", t, flags=re.UNICODE)
    t = t.replace("_", " ")
    return " ".join(t.split()[:10])


# ── Corpora ──────────────────────────────────────────────────────────────────
# ~30 varied ASCII/Latin titles: punctuation, unicode quotes/dashes, numerals,
# diacritics, underscores, >10-word titles, single words, empty-ish inputs.
LATIN_CORPUS = [
    "Belgium vs. Iran — 2026 World Cup preview",
    "Belgium vs Iran: 2026 World Cup preview",
    "Fed holds rates steady at 5.25%–5.50% for a third straight meeting",
    "Apple unveils iPhone 17 with “curved” display",
    "Apple unveils iPhone 17 with 'curved' display",
    "Mbappé signs record extension",
    "Mbappe signs record extension",
    "Oil prices jump 4% after OPEC+ output cut",
    "S&P 500 closes above 6,000 for the first time",
    "Bitcoin",
    "bitcoin",
    "BREAKING: Magnitude-7.1 earthquake strikes off Japan's Pacific coast",
    "Q3 earnings: what analysts expect from the 'Magnificent Seven' this season overall",
    "why_snake_case_headlines_exist_on_some_feeds",
    "  leading and trailing whitespace  ",
    "One two three four five six seven eight nine ten eleven twelve",
    "one two three four five six seven eight nine ten ELEVEN TWELVE!!",
    "El País: la economía española crece un 2,4 % en el tercer trimestre",
    "Zürich re-elects mayor in landslide",
    "naïve approach to café-culture economics faces its reckoning",
    "COVID-19 variant tracking resumes in U.S. hospitals",
    "U.K. inflation falls to 2.1%, lowest since 2021",
    "'AI bubble' talk grows as valuations stretch — but revenue follows",
    "NASA's Artemis III crew named; landing site TBD",
    "Real Madrid 3-1 Manchester City (agg. 5-3)",
    "€100bn defence fund clears final hurdle in Brussels",
    "50 Cent announces farewell tour",
    "A",
    "",
    "The quick brown fox jumps over the lazy dog near the riverbank at dawn",
    "Tesla    multiple   internal    spaces",
    "semi—colon; and em—dash both appear… here",
]

# Same wire story, four Japanese masthead variants (suffix/particle/punctuation drift —
# no ASCII spaces, per real JP headline convention). Shared story text well past the
# 20-char window, so the drift falls outside it.
JP_WIRE = [
    "トヨタ自動車が新型の電気自動車を2027年春に発売すると発表",
    "トヨタ自動車が新型の電気自動車を2027年春に発売すると発表した【朝日新聞】",
    "トヨタ自動車が新型の電気自動車を2027年春に発売へ、関係者が明らかに",
    "トヨタ自動車が新型の電気自動車を2027年春に発売すると発表(共同)",
]
JP_OTHER = "日銀が政策金利を0.75%へ引き上げると決定、17年ぶりの水準に"

# Same wire story, four Chinese masthead variants.
ZH_WIRE = [
    "苹果公司宣布将于明年初在中国市场推出新款折叠屏手机",
    "苹果公司宣布将于明年初在中国市场推出新款折叠屏手机。",
    "苹果公司宣布将于明年初在中国市场推出新款折叠屏手机(新浪科技)",
    "苹果公司宣布将于明年初在中国市场推出新款折叠屏手机，售价未定",
]
ZH_OTHER = "特斯拉上海超级工厂第三季度交付量创下历史新高引发关注"

# Korean: compact spaceless headline style (tickers/pushes) — collapses under the flag.
# NOTE: normal spaced Korean headlines take the word-window path and already work.
KO_WIRE = [
    "삼성전자3분기영업이익10조원돌파실적개선세뚜렷",
    "삼성전자3분기영업이익10조원돌파실적개선세뚜렷(연합뉴스)",
    "삼성전자3분기영업이익10조원돌파실적개선세뚜렷…반도체회복",
]
KO_SPACED = "삼성전자 3분기 영업이익 10조원 돌파, 반도체 회복세 뚜렷"

# Thai (no spaces between words).
TH_WIRE = [
    "รัฐบาลไทยประกาศมาตรการกระตุ้นเศรษฐกิจรอบใหม่วงเงินห้าแสนล้านบาท",
    "รัฐบาลไทยประกาศมาตรการกระตุ้นเศรษฐกิจรอบใหม่วงเงินห้าแสนล้านบาท(ไทยรัฐ)",
    "รัฐบาลไทยประกาศมาตรการกระตุ้นเศรษฐกิจรอบใหม่ล่าสุด",
]
TH_OTHER = "ธนาคารแห่งประเทศไทยคงอัตราดอกเบี้ยนโยบายไว้ที่ระดับเดิม"

ALL_INPUTS = (LATIN_CORPUS + JP_WIRE + [JP_OTHER] + ZH_WIRE + [ZH_OTHER]
              + KO_WIRE + [KO_SPACED] + TH_WIRE + [TH_OTHER]
              + ["iPhone 17 発表", "iPhone17を正式発表、日本では11月発売に決定"])


def main() -> int:
    print("TITLE_SIG CJK WINDOW — ruling 5: the quorum must not fail open by script")
    print("=" * 72)
    saved_flag = dp.TITLE_SIG_CJK

    try:
        # ── (a) flag OFF: byte-identity with the frozen original on ALL inputs ──
        dp.TITLE_SIG_CJK = False
        diffs = [t for t in ALL_INPUTS if dp._title_sig(t) != frozen_original_sig(t)]
        check("t1 flag OFF -> byte-identical to pre-change code for ALL inputs "
              f"({len(ALL_INPUTS)} incl. CJK/Thai/mixed)",
              not diffs, f"first diff: {diffs[:1]}")

        # The defect itself, demonstrated: flag off, one JP wire story = 4 'stories'.
        off_sigs = {dp._title_sig(t) for t in JP_WIRE}
        check("t2 flag OFF reproduces the defect (4 JP wire variants -> 4 signatures)",
              len(off_sigs) == len(JP_WIRE), f"got {len(off_sigs)}")

        # ── (b) flag ON: identity on every space-containing or Latin-only input ──
        dp.TITLE_SIG_CJK = True
        ascii_safe = LATIN_CORPUS + [KO_SPACED, "iPhone 17 発表"]
        diffs = [t for t in ascii_safe if dp._title_sig(t) != frozen_original_sig(t)]
        check("t3 flag ON -> byte-identical on ASCII/Latin + space-containing corpus "
              f"({len(ascii_safe)} inputs)", not diffs, f"first diff: {diffs[:1]}")

        # ── (c) flag ON: same-wire CJK variants collapse; different stories don't ──
        jp = {dp._title_sig(t) for t in JP_WIRE}
        check("t4 JP: 4 same-wire variants -> ONE signature", len(jp) == 1, str(jp))
        check("t5 JP: a genuinely different story -> a DIFFERENT signature",
              dp._title_sig(JP_OTHER) not in jp, "different stories collided")

        zh = {dp._title_sig(t) for t in ZH_WIRE}
        check("t6 ZH: 4 same-wire variants -> ONE signature", len(zh) == 1, str(zh))
        check("t7 ZH: a genuinely different story -> a DIFFERENT signature",
              dp._title_sig(ZH_OTHER) not in zh, "different stories collided")

        ko = {dp._title_sig(t) for t in KO_WIRE}
        check("t8 KO: spaceless compact variants -> ONE signature", len(ko) == 1, str(ko))

        # ── (d) Thai ──
        th = {dp._title_sig(t) for t in TH_WIRE}
        check("t9 TH: same-wire variants -> ONE signature", len(th) == 1, str(th))
        check("t10 TH: a genuinely different story -> a DIFFERENT signature",
              dp._title_sig(TH_OTHER) not in th, "different stories collided")

        # ── (e) mixed script: space-containing stays on the old path; spaceless
        #        CJK-dominant mixed text still produces a sane, non-empty signature ──
        check("t11 mixed 'iPhone 17 発表' (has spaces) -> flag-on == flag-off",
              dp._title_sig("iPhone 17 発表") == frozen_original_sig("iPhone 17 発表"))
        m = dp._title_sig("iPhone17を正式発表、日本では11月発売に決定")
        check("t12 mixed spaceless CJK-dominant -> non-empty, bounded signature",
              bool(m) and len(m) <= 20 + 0, repr(m))
        # Latin-only spaceless never takes the char window (CJK char floor).
        check("t13 spaceless Latin ('Bitcoin') -> old path even with flag ON",
              dp._title_sig("Bitcoin") == frozen_original_sig("Bitcoin"))

        # ── END TO END: the quorum count itself (mainstream_breadth) ──
        def rows(titles):
            return [{"platform": "newsapi_org", "platform_tier": "mainstream",
                     "source_name": f"outlet_{i}", "title": t, "engagement_raw": 120}
                    for i, t in enumerate(titles)]
        five = rows(JP_WIRE + [JP_WIRE[0] + "、続報"])   # 5 outlets, ONE wire story
        dp.TITLE_SIG_CJK = False
        n_off = dp.mainstream_breadth(five)["n_news_independent"]
        dp.TITLE_SIG_CJK = True
        n_on = dp.mainstream_breadth(five)["n_news_independent"]
        check("t14 quorum: 5 CJK mastheads / 1 wire story counts 5 flag-off (the "
              "fail-open), 1 flag-on", n_off == 5 and n_on == 1,
              f"off={n_off} on={n_on}")

        # ── SOURCE GUARDS: the gate must stay OFF by default and stay commented ──
        src = open(os.path.join(_HERE, "dual_pathway.py"), encoding="utf-8").read()
        check("t15 flag defaults OFF in source (founder flip only)",
              'os.getenv("TITLE_SIG_CJK", "0") == "1"' in src,
              "default is not '0' — score-affecting flag must not self-enable")
        check("t16 the ruling citation is present at the flag",
              "BOARD_resume-audit_2026-09-14.md" in src, "citation removed")
    finally:
        dp.TITLE_SIG_CJK = saved_flag

    print("=" * 72)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
