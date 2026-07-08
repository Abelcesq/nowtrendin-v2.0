"""
date_utils.py — the ONE canonical date/time normalizer for the whole engine.

CANONICAL RULE (do not deviate):
  • Every DATE stored, sorted, matched, or scored on is ISO 'YYYY-MM-DD' — the
    PRIMARY canonical value. Use to_iso_date() for date-semantic columns
    (detection_date, breakout_date, signal_date, snapshot_date, the cycle date …).
  • TIME is SECONDARY. Where a precise instant is genuinely needed (audit/heartbeat
    timestamps, dedup, timeout age), use to_iso_dt() ->
    'YYYY-MM-DDTHH:MM:SS+00:00'. The date is always the leading sort component.
  • Parsers try WHOLE-STRING formats FIRST and never naive-split on a space — that
    bug sliced 'May 22, 2026' -> 'May' and silently dropped 13 accuracy-ledger rows.

Tolerated inputs (both functions): ISO date, ISO datetime (with 'Z' or offset),
'Mon DD, YYYY' (%b), 'Month DD, YYYY' (%B), 'MM/DD/YYYY', compact GDELT-basic
'YYYYMMDDTHHMMSSZ', compact date 'YYYYMMDD', epoch seconds (10-digit) / millis
(13-digit), and datetime/date objects. Returns None on empty/unparseable so the
caller can decide (skip / default / quarantine) — it NEVER returns a corrupt date.
"""
from __future__ import annotations
from datetime import datetime, date, timezone
from typing import Optional

# whole-string DATE formats — tried first, no space-splitting
# NOTE (board fix 2026-07-08, Chairman-ruled): slash dates are NOT in this table —
# they go through _parse_slash_date below, which keeps US MM/DD/YYYY as the canonical
# interpretation but REFUSES the ambiguous case instead of silently mis-reading
# European DD/MM input (03/04/2026 read as March 4 when a French feed meant April 3 —
# a silent mis-canonicalization, the one failure §14 exists to prevent). Unambiguous
# day>12 forms parse in whichever order is valid; ambiguous both-fields-≤12-and-unequal
# returns None → the ingestion gate QUARANTINES it for human review, per the canon.
_DATE_FORMATS = ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%Y%m%d")


def _parse_slash_date(s: str):
    """US-canonical slash-date parser with ambiguity refusal (see note above).
    Accepts M/D/YYYY and MM/DD/YYYY; also accepts an unambiguous D/M/YYYY (day>12)
    from European sources, normalized to the same canonical YYYY-MM-DD."""
    parts = s.split("/")
    if len(parts) != 3:
        return None
    try:
        a, b, y = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None
    if y < 1000:
        return None
    try:
        if b > 12 and a <= 12:      # unambiguous US MM/DD/YYYY
            return datetime(y, a, b, tzinfo=timezone.utc)
        if a > 12 and b <= 12:      # unambiguous European DD/MM/YYYY
            return datetime(y, b, a, tzinfo=timezone.utc)
        if a == b and a <= 12:      # 5/5/2026 — same date either way
            return datetime(y, a, b, tzinfo=timezone.utc)
    except ValueError:
        return None
    return None                     # both ≤12 and unequal → AMBIGUOUS → quarantine
# explicit DATETIME formats (incl. compact GDELT-basic with no separators)
_DT_FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M",
               "%Y-%m-%d %H:%M:%S", "%Y%m%dT%H%M%S")


def _to_datetime(value) -> Optional[datetime]:
    """Parse any tolerated input into a tz-aware UTC datetime, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    s = str(value).strip()
    if not s:
        return None

    # epoch seconds (10) / millis (13). 8-digit 'YYYYMMDD' is NOT epoch — handled
    # below by _DATE_FORMATS, so restrict the epoch branch to 10/13-digit strings.
    if s.isdigit() and len(s) in (10, 13):
        try:
            iv = int(s)
            if len(s) == 13:
                iv //= 1000
            return datetime.fromtimestamp(iv, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            pass

    # whole-string DATE formats first (never split on space)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    # slash dates: US-canonical with ambiguity refusal (board fix 2026-07-08)
    if "/" in s:
        _sd = _parse_slash_date(s)
        if _sd is not None:
            return _sd

    # ISO datetime via fromisoformat (handles 'Z' and offsets)
    z = s[:-1] + "+00:00" if s.endswith("Z") else s
    try:
        dt = datetime.fromisoformat(z)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # explicit datetime formats incl. compact GDELT-basic '20260606T171500'
    base = s[:-1] if s.endswith("Z") else s
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(base, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def to_iso_date(value, default_today: bool = False) -> Optional[str]:
    """Canonical PRIMARY date 'YYYY-MM-DD'. None if unparseable, unless
    default_today=True (then today's UTC date). Never returns a corrupt value."""
    dt = _to_datetime(value)
    if dt is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d") if default_today else None
    return dt.date().isoformat()


def to_iso_dt(value, default_now: bool = False) -> Optional[str]:
    """Canonical SECONDARY timestamp 'YYYY-MM-DDTHH:MM:SS+00:00' (UTC). None if
    unparseable, unless default_now=True. A bare 'YYYY-MM-DD' becomes midnight UTC,
    which keeps the date as the leading sort component (no reordering)."""
    dt = _to_datetime(value)
    if dt is None:
        return datetime.now(timezone.utc).isoformat() if default_now else None
    return dt.astimezone(timezone.utc).isoformat()


def source_has_time(value) -> bool:
    """True iff the raw value carries a time-of-day component (a 'T' separator or a
    space + ':'), i.e. it is NOT a bare date. A bare 'YYYY-MM-DD' / 'May 22, 2026'
    returns False."""
    raw = "" if value is None else str(value).strip()
    return bool(raw) and (("T" in raw) or (" " in raw and ":" in raw))


def iso_time_of(value, default_now: bool = True) -> str:
    """Canonical SECONDARY time-of-day 'HH:MM:SS' (UTC, 24h). If the source carries
    a time, returns ITS time; otherwise returns the current fetch time (default_now)
    or '' — so going-forward rows are always populated in a uniform 'HH:MM:SS'."""
    if source_has_time(value):
        full = to_iso_dt(value)
        if full and "T" in full:
            return full.split("T", 1)[1][:8]   # 'HH:MM:SS' (drop any +00:00 offset)
    return datetime.now(timezone.utc).strftime("%H:%M:%S") if default_now else ""


def is_iso_date(s) -> bool:
    """True iff s is already a canonical 'YYYY-MM-DD' string."""
    return isinstance(s, str) and len(s) == 10 and s[4] == "-" and s[7] == "-" \
        and to_iso_date(s) == s


def canonical_date_of(value) -> Optional[str]:
    """Pull the canonical 'YYYY-MM-DD' out of ANY date/datetime value — the
    primary key used for sorting/scoring (time disregarded). Alias of to_iso_date."""
    return to_iso_date(value)
