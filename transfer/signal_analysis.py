"""signal_analysis.py — per-item Signal Analysis (enterprise-grade, REPRODUCIBLE).

HELD-OUT / SERVE-PATH ONLY. Imported by the API serve layer to attach a written analysis to a
trend / market / crypto item. It is NEVER imported by scoring, calibration, or any ledger writer —
it only READS finished outputs, so it can never feed back into a score (no circularity).

Design contract (see memory: feedback-enterprise-analysis-standard, feedback-integrity-standard):
  • DETERMINISTIC. Pure function of (item, ledger_report) — no LLM, no DB, no network, no clock,
    no randomness. Same inputs → identical text. Fully auditable; cannot drift or hallucinate.
  • DATA-SUPPORTED. Every sentence is composed from a real score field or a real accuracy-ledger
    statistic. If a value is absent it is omitted — never guessed, never zero-filled, never "N/A"-as-fact.
  • CONFIDENTIAL FORMULA. It states WHAT each metric measures and reports the displayed score + the
    ledger's own track record (with honest denominators) — but never the internal weights, thresholds,
    blend coefficients, or proprietary cut-offs. "The internal weighting is proprietary."
  • MEASUREMENT, NOT ADVICE. No forecast, price target, recommendation, or investment/legal/financial
    advice. Neutral, factual, defensible to hedge-fund counsel, allocators, and sophisticated clients.

build(kind, item, ledger_report) -> dict:
  {title, kind, item, headline, facts:[{label,value}], sections:[{heading,body}], disclaimer, generated}
"""
from typing import Optional


# ── helpers ────────────────────────────────────────────────────────────────────────────────────
def _i(x) -> Optional[int]:
    """Round to int, or None if not a real number."""
    try:
        if x is None or isinstance(x, bool):
            return None
        return int(round(float(x)))
    except (TypeError, ValueError):
        return None


def _first(*vals):
    for v in vals:
        if v not in (None, "", "n/a", "N/A"):
            return v
    return None


def _flow_word(flow) -> str:
    f = (flow or "").lower().strip()
    return "inflow" if f == "inflow" else "outflow" if f == "outflow" else ""


_DISCLAIMER = ("This is a measurement of where money and attention are positioned, drawn from public "
               "disclosures and validated against an external, auditable ground truth. It is not a "
               "forecast, a price target, a recommendation, or investment, legal or financial advice.")


# ── MONEY GRADIENT (market + crypto share the field shape) ───────────────────────────────────────
def _money(item: dict, ledger: dict, asset: str) -> dict:
    crypto = (asset == "crypto")
    name = _first(item.get("item_name"), item.get("display"), item.get("topic_display"),
                  item.get("coin"), ("this coin" if crypto else "this instrument"))
    d = _i(item.get("detection"))
    c = _i(item.get("confidence"))
    tier = (item.get("tier") or "").strip()
    flow = _flow_word(item.get("flow") or ((item.get("dark_matter") or {}).get("flow")))
    lev = _i(item.get("leverage_health"))
    gap = (d - c) if (d is not None and c is not None) else None

    if crypto:
        source = ("regulated, publicly-disclosed proxies for the coin — institutional holdings (13F) "
                  "in the exchange-traded products that track it, and insider transactions at the major "
                  "listed crypto-treasury and exchange operators")
        confirm_src = "the coin's own realized price"
        unit = "coin"
    else:
        source = ("public regulatory disclosures — SEC Form-4 insider transactions and 13F institutional "
                  "holdings — together with short-interest and funding-market data")
        confirm_src = "the broad market and economic data"
        unit = "instrument"

    sections = []
    facts = []

    # 1) What this measures — concept only; formula stays confidential.
    sections.append({"heading": "What this measures", "body":
        f"The Money Gradient reads two independent dimensions of where capital is positioning, each on a "
        f"0–100 scale relative to this {unit}'s own history. **Money Movement** measures the strength and "
        f"direction of informed positioning, drawn from {source}. **Market Confirmation** measures whether "
        f"{confirm_src} has corroborated that positioning. The two reads are kept deliberately separate so "
        f"the early, informed signal is never diluted by the broad one. The internal weighting that "
        f"produces each score is proprietary; the inputs above are all public filings and market data."})

    # 2) The current read — composed entirely from this item's scores.
    read = []
    if d is not None:
        strength = "strong" if d >= 70 else "moderate" if d >= 45 else "muted"
        if flow:
            read.append(f"For {name}, Money Movement reads {d}/100 — {strength} informed-money activity, "
                        f"with a net {flow} bias in the disclosed transactions.")
        else:
            read.append(f"For {name}, Money Movement reads {d}/100 — {strength} informed-money activity, "
                        f"with no clear net direction in the disclosed transactions.")
        facts.append({"label": "Money Movement", "value": f"{d} / 100"})
    if c is not None:
        conf_phrase = ("broad data has confirmed the move" if c >= 55 else
                       "broad confirmation is partial" if c >= 35 else
                       "the broad market has not yet confirmed")
        read.append(f"Market Confirmation reads {c}/100 — {conf_phrase}.")
        facts.append({"label": "Market Confirmation", "value": f"{c} / 100"})
    if gap is not None:
        if gap >= 16:
            read.append(f"Informed money currently runs {gap} points ahead of broad confirmation — an "
                        f"early-stage read, where positioning precedes corroboration.")
            facts.append({"label": "Lead", "value": f"+{gap} pts (early)"})
        elif gap <= -16:
            read.append(f"Broad data leads the informed read by {abs(gap)} points — a later-stage read.")
            facts.append({"label": "Lead", "value": f"−{abs(gap)} pts (late)"})
        else:
            read.append("The informed and broad reads are roughly aligned.")
            facts.append({"label": "Lead", "value": "aligned"})
    if flow:
        facts.append({"label": "Net flow", "value": flow})
    if lev is not None:
        lev_phrase = ("low debt / healthy balance sheet" if lev >= 60 else
                      "a moderate debt load" if lev >= 40 else "an elevated debt load")
        read.append(f"The reported balance sheet shows {lev_phrase} ({lev}/100 leverage-health) — a fact "
                    f"drawn directly from filings.")
        facts.append({"label": "Leverage-health", "value": f"{lev} / 100"})
    if tier:
        read.append(f"The overall read is classified {tier}.")
        facts.append({"label": "Classification", "value": tier})
    if read:
        sections.append({"heading": "The current read", "body": " ".join(read)})

    # 3) Track record & accountability — adaptive to ledger maturity; honest denominators.
    sections.append({"heading": "Track record & accountability",
                     "body": _track_money(ledger, confirm_src, crypto)})
    facts.extend(_ledger_facts_money(ledger))

    # 4) Scope & limitations.
    scope = ("This is a measurement of positioning disclosed in public filings and validated against an "
             "auditable, externally-defined ground truth — realized price direction. ")
    if crypto:
        scope += ("It reads exchange-traded and corporate proxies for the coin, not on-chain wallet flows, "
                  "which are not yet a licensed input. ")
    scope += "It is descriptive, not prescriptive."
    sections.append({"heading": "Scope & limitations", "body": scope})

    strength_lbl = ("early-stage" if (gap is not None and gap >= 16) else
                    "later-stage" if (gap is not None and gap <= -16) else "balanced")
    headline = f"{tier + ' — ' if tier else ''}{strength_lbl} money read".strip()
    return {"title": "Signal Analysis", "kind": asset, "item": name, "headline": headline,
            "facts": facts, "sections": sections, "disclaimer": _DISCLAIMER,
            "generated": "Reproducible — composed from this item's scores and the accuracy ledger; no model inference."}


def _track_money(ledger: dict, confirm_src: str, crypto: bool) -> str:
    ledger = ledger or {}
    resolved = _i(ledger.get("resolved")) or 0
    pending = _i(ledger.get("pending")) or 0
    cr = ledger.get("confirm_rate_pct")
    lead = ledger.get("median_lead_days")
    timeout = _i(ledger.get("timeout_days"))
    ground = ("the coin's realized price direction" if crypto else "realized end-of-day price direction")
    lead_clause = f", at a median lead of {lead} days" if lead is not None else ""
    win = f" ({timeout}-day validation window)" if timeout else ""
    if resolved <= 0:
        return ("Every reading is written, the moment it is made, into a falsifiable accuracy ledger and "
                f"later resolved against {ground}, counting misses alongside hits. This ledger is currently "
                f"accruing its first resolved cases: {pending} detection(s) are in flight and will be scored "
                f"as the validation window{(' of ' + str(timeout) + ' days') if timeout else ''} elapses. We "
                "report the confirmed-direction rate together with its full denominator the moment cases "
                "resolve — we do not publish a rate we cannot yet stand behind.")
    body = ("Every reading is written, the moment it is made, into a falsifiable accuracy ledger and "
            f"resolved against {ground}{win}, counting misses alongside hits. To date {resolved} reading(s) "
            f"have resolved ({pending} still in flight)")
    if cr is not None:
        body += f"; of those, {cr}% moved in the detected direction{lead_clause}."
    else:
        body += "."
    if _i(ledger.get("resolved")) is not None and ledger.get("small_sample"):
        body += " This remains an early sample and is weighed as such."
    return body


def _ledger_facts_money(ledger: dict):
    ledger = ledger or {}
    resolved = _i(ledger.get("resolved"))
    pending = _i(ledger.get("pending"))
    cr = ledger.get("confirm_rate_pct")
    out = []
    if resolved is not None or pending is not None:
        out.append({"label": "Ledger", "value": f"{resolved or 0} resolved · {pending or 0} in flight"})
    if cr is not None:
        out.append({"label": "Confirmed direction", "value": f"{cr}%"})
    return out


# ── GRADIENT SCORE (trend) ───────────────────────────────────────────────────────────────────────
def _trend(item: dict, ledger: dict) -> dict:
    name = _first(item.get("topic_display"), item.get("display"), item.get("topic_key"), "this topic")
    # Canonical headline Detection/Confidence are the served 'det'/'conf' (calibrated display values);
    # detection_score/confidence_score are raw and may be null for established topics.
    d = _i(_first(item.get("det"), item.get("detection_score"), item.get("detection")))
    c = _i(_first(item.get("conf"), item.get("confidence_score"), item.get("confidence")))
    stage = (_first(item.get("stage"), item.get("signal_stage")) or "").strip()
    cat = (item.get("category") or "").strip()
    n = _first(item.get("nowtrendin_score"), item.get("n"))
    mainstream_confirmed = item.get("mainstream_confirmed")  # True / False / None(unknown)
    times = _i(item.get("times_scored"))

    sections, facts = [], []

    # 1) What this measures — concept + the non-circularity guarantee; formula confidential.
    sections.append({"heading": "What this measures", "body":
        "The Gradient Score measures where public attention is moving before a topic becomes mainstream, "
        "on a 0–100 scale relative to the topic's own baseline. **Detection** reads the strength of the "
        "early attention signal; **Confidence** reads how well that signal is corroborated across "
        "independent, vetted sources. A separate platform indicator reflects how often the topic is "
        "surfaced as a tracked signal — it is never folded back into the Gradient Score, so the early read "
        "is never validated by engagement with itself. The internal model that combines these inputs is "
        "proprietary; every source is a vetted publisher or licensed data provider."})

    # 2) The current read.
    read = []
    if d is not None:
        strength = "strong" if d >= 70 else "moderate" if d >= 45 else "muted"
        read.append(f"For {name}, Detection reads {d}/100 — a {strength} attention signal.")
        facts.append({"label": "Detection", "value": f"{d} / 100"})
    if c is not None:
        corr = ("well corroborated across independent sources" if c >= 55 else
                "partially corroborated" if c >= 35 else "thinly corroborated so far")
        read.append(f"Confidence reads {c}/100 — {corr}.")
        facts.append({"label": "Confidence", "value": f"{c} / 100"})
    if stage:
        # Only assert mainstream status when we actually have the field — never guess it from a default.
        if mainstream_confirmed is True:
            clause = " and mainstream coverage has begun to confirm it"
        elif mainstream_confirmed is False:
            clause = " and it has not yet been confirmed by mainstream coverage"
        else:
            clause = ""
        read.append(f"The signal is at the {stage} stage{clause}.")
        facts.append({"label": "Stage", "value": stage})
    if cat:
        read.append(f"It is currently classified under {cat}.")
        facts.append({"label": "Category", "value": cat})
    if n is not None:
        facts.append({"label": "Platform indicator (N)", "value": f"{_i(n)}"})
    if times:
        read.append(f"This topic has been re-observed {times} times in our record.")
    if read:
        sections.append({"heading": "The current read", "body": " ".join(read)})

    # 3) Track record & accountability — the trends ledger, framed precisely so it cannot misread.
    sections.append({"heading": "Track record & accountability", "body": _track_trend(ledger)})
    facts.extend(_ledger_facts_trend(ledger))

    # 4) Scope & limitations.
    sections.append({"heading": "Scope & limitations", "body":
        "This is a measurement of attention movement, drawn from vetted publishers and licensed data and "
        "validated against an external benchmark. The stage and tier labels are descriptive — they say "
        "where attention is, not what to do."})

    headline = (f"{stage} stage" if stage else "Attention read") + (
        f" — {'strong' if (d or 0) >= 70 else 'moderate' if (d or 0) >= 45 else 'muted'} signal" if d is not None else "")
    return {"title": "Signal Analysis", "kind": "trend", "item": name, "headline": headline,
            "facts": facts, "sections": sections, "disclaimer": _DISCLAIMER,
            "generated": "Reproducible — composed from this topic's scores and the accuracy ledger; no model inference."}


def _track_trend(ledger: dict) -> str:
    ledger = ledger or {}
    resolved = _i(_first(ledger.get("sample_size"), ledger.get("resolved")))
    pending = _i(_first(ledger.get("still_pending"), ledger.get("pending")))
    led = _i(ledger.get("hits_led"))
    lead = _first(ledger.get("median_lead_days"), ledger.get("medianLead"))
    if not resolved:
        return ("Each early detection is written into a falsifiable accuracy ledger and later tested against "
                "an external benchmark — the date the topic broke out on Google Trends — counting every miss. "
                f"The resolved sample is still accruing ({pending or 0} detections in flight); we publish the "
                "ledger in full, with its denominator, rather than a selected statistic.")
    body = ("Each early detection is written into a falsifiable accuracy ledger and tested against an external "
            "benchmark — the date the topic broke out on Google Trends — counting every miss. The strict bar "
            "we hold ourselves to is whether our detection PRECEDED that external breakout. Across "
            f"{resolved} resolved detections to date ({pending or 0} still in flight), ")
    if led is not None:
        body += (f"{led} preceded the breakout outright; on that conservative bar the methodology is in active "
                 "calibration")
    else:
        body += "the methodology is in active calibration on that conservative bar"
    if lead is not None:
        body += f", and when a detection does lead, the median lead is {lead} days"
    body += ". We publish the ledger in full, with its denominator, rather than a selected statistic."
    return body


def _ledger_facts_trend(ledger: dict):
    ledger = ledger or {}
    resolved = _i(_first(ledger.get("sample_size"), ledger.get("resolved")))
    pending = _i(_first(ledger.get("still_pending"), ledger.get("pending")))
    led = _i(ledger.get("hits_led"))
    lead = _first(ledger.get("median_lead_days"), ledger.get("medianLead"))
    out = []
    if resolved is not None or pending is not None:
        v = f"{resolved or 0} resolved"
        if led is not None:
            v += f" · {led} led"
        v += f" · {pending or 0} in flight"
        out.append({"label": "Ledger", "value": v})
    if lead is not None:
        out.append({"label": "Median lead (when it leads)", "value": f"{lead} days"})
    return out


# ── entry point ──────────────────────────────────────────────────────────────────────────────────
def build(kind: str, item: dict, ledger_report: Optional[dict] = None) -> dict:
    """kind: 'trend' | 'market' | 'crypto'. item: the finished score dict. ledger_report: the matching
    accuracy-ledger report dict (generate_honest_report / market or crypto report). Pure + deterministic."""
    k = (kind or "").lower().strip()
    item = item or {}
    ledger_report = ledger_report or {}
    if k == "trend":
        return _trend(item, ledger_report)
    if k == "crypto":
        return _money(item, ledger_report, asset="crypto")
    return _money(item, ledger_report, asset="market")
