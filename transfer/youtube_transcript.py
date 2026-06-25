"""
YouTube transcript — HELD-OUT research module (imported by NOTHING in scoring).

The official YouTube Data API cannot download captions for videos we don't own (captions.download
needs the channel owner's OAuth). This pulls a video's auto-captions via `youtube-transcript-api`
(the public timedtext mechanism the web player uses) so we can read what a quality analyst actually
SAID — enriching the creator Dark-Matter signal (Meet Kevin et al.) beyond the video TITLE.

⚠ UNOFFICIAL: not the Data API; ToS gray area; can break when YouTube changes the endpoint. So:
  • HELD-OUT — feeds no score yet. Research → backtest-before-ship before any integration.
  • Degrades gracefully when the library or a transcript is unavailable (returns available:False).
  • Requires `youtube-transcript-api` (add to requirements before deploy). Measurement of the
    analyst's expressed content — NOT our advice.

Use: fetch_transcript(video_id) → text; analyze(video_id, tickers) → which tickers the analyst
discusses + how much + a rough expressed lean (a content MEASUREMENT, not a recommendation).
"""
from __future__ import annotations
import re
from collections import Counter
from typing import Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    _LIB = True
except Exception:
    _LIB = False

_CACHE: dict = {}

# Rough expressed-lean lexicons — a MEASUREMENT of how the analyst is framing a name, not advice.
_BULLISH = {"buy", "buying", "bullish", "long", "accumulate", "accumulating", "undervalued",
            "breakout", "rally", "upside", "calls", "moon", "load", "dip"}
_BEARISH = {"sell", "selling", "bearish", "short", "shorting", "overvalued", "crash", "dump",
            "downside", "puts", "collapse", "bubble", "top", "warning"}


def available() -> bool:
    return _LIB


def fetch_transcript(video_id: str) -> Optional[str]:
    """Full transcript text for a video id, or None. Cached per process."""
    if not _LIB or not video_id:
        return None
    if video_id in _CACHE:
        return _CACHE[video_id]
    text = None
    try:
        parts = []
        # v1.x API: instance .fetch() → iterable of snippet objects (.text). v0.x: classmethod
        # .get_transcript() → list of {text}. Support both so a lib upgrade can't silently break us.
        try:
            fetched = YouTubeTranscriptApi().fetch(video_id, languages=["en", "en-US"])
            for s in fetched:
                parts.append(getattr(s, "text", None) or (s.get("text") if isinstance(s, dict) else ""))
        except AttributeError:
            raw = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US"])
            parts = [p.get("text", "") for p in raw]
        text = re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip() or None
    except Exception as e:
        print(f"[yt-transcript] {video_id}: {e}")
        text = None
    _CACHE[video_id] = text
    return text


def _cashtags(text: str) -> Counter:
    """$TICKER cashtags an analyst explicitly calls out (the cleanest mention signal)."""
    return Counter(m.upper() for m in re.findall(r"\$([A-Za-z]{1,5})\b", text or ""))


def analyze(video_id: str, tickers: Optional[list] = None, transcript: str = "") -> dict:
    """What the analyst discusses in one video. tickers = optional symbols (+ we also pick up any
    $cashtags). Returns per-ticker mention counts + a rough expressed lean (bullish/bearish word
    balance across the whole transcript). HELD-OUT — a content measurement, not advice or a score."""
    text = transcript or fetch_transcript(video_id)
    if not text:
        return {"available": False, "reason": "no transcript", "video_id": video_id}
    low = f" {text.lower()} "
    mentions: dict = {}
    cash = _cashtags(text)
    for t, n in cash.items():
        mentions[t] = mentions.get(t, 0) + n
    for t in (tickers or []):
        tu = (t or "").upper().strip()
        if not tu:
            continue
        # word-boundary count of the bare symbol (cashtags already counted above)
        c = len(re.findall(rf"(?<![A-Za-z$]){re.escape(tu)}(?![A-Za-z])", text, re.IGNORECASE))
        if c:
            mentions[tu] = mentions.get(tu, 0) + c
    bull = sum(low.count(f" {w} ") for w in _BULLISH)
    bear = sum(low.count(f" {w} ") for w in _BEARISH)
    tot = bull + bear
    lean = ("bullish" if tot and bull / tot > 0.6 else
            "bearish" if tot and bear / tot > 0.6 else "mixed" if tot else "neutral")
    return {
        "available": True, "held_out": True, "video_id": video_id,
        "word_count": len(text.split()),
        "tickers_mentioned": dict(sorted(mentions.items(), key=lambda kv: -kv[1])),
        "expressed_lean": lean, "bullish_terms": bull, "bearish_terms": bear,
        "note": "HELD-OUT — analyst CONTENT measurement (unofficial captions). Not in any score; "
                "not advice. Research → backtest-before-ship before feeding the Dark-Matter signal.",
    }


if __name__ == "__main__":
    import sys, json
    vid = sys.argv[1] if len(sys.argv) > 1 else "dQw4w9WgXcQ"
    print("library available:", available())
    print(json.dumps(analyze(vid, tickers=["NVDA", "AAPL", "TSLA"]), indent=2)[:900])
