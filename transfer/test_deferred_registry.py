"""C5 sync gate (Chairman-ruled 2026-09-14): the deferred shelf and its engine-readable
mirror may never drift. Three unregistered crypto shelves and an orphaned review date
(K6) lapsed unowned because prose dates had no evaluator; this test makes that state a
BUILD FAILURE. Every `## ` heading in audits/DEFERRED_ITEMS.md must have exactly one
entry in transfer/deferred_registry.DEFERRED_ITEMS (byte-identical heading), every
review_date must be ISO YYYY-MM-DD, and headings must be unique both sides."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "..", "audits", "DEFERRED_ITEMS.md")


def main() -> int:
    sys.path.insert(0, HERE)
    import deferred_registry as dreg

    fails = []
    with open(DOC, encoding="utf-8") as f:
        doc_heads = [l[3:].rstrip("\n").rstrip() for l in f if l.startswith("## ")]
    reg_heads = [e["heading"] for e in dreg.DEFERRED_ITEMS]

    if len(set(doc_heads)) != len(doc_heads):
        fails.append("duplicate headings in DEFERRED_ITEMS.md")
    if len(set(reg_heads)) != len(reg_heads):
        fails.append("duplicate headings in deferred_registry")
    missing = set(doc_heads) - set(reg_heads)
    extra = set(reg_heads) - set(doc_heads)
    for h in sorted(missing):
        fails.append(f"UNREGISTERED shelf item (add to deferred_registry): {h[:90]}")
    for h in sorted(extra):
        fails.append(f"registry entry with no shelf heading (stale — remove or re-add doc): {h[:90]}")
    for e in dreg.DEFERRED_ITEMS:
        rd = e.get("review_date")
        if rd is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rd):
            fails.append(f"non-ISO review_date {rd!r} on: {e['heading'][:60]}")

    print(f"deferred-registry sync: {len(doc_heads)} doc headings, {len(reg_heads)} registry entries, "
          f"{sum(1 for e in dreg.DEFERRED_ITEMS if e.get('review_date'))} dated")
    if fails:
        for f_ in fails:
            print("  FAIL:", f_)
        return 1
    print("  OK — shelf and registry in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
