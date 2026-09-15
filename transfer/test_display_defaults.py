"""Fabricated-default display lint (board 2026-09-15, D11 / Economist prescription 6).

The class this kills: a display-state field silently defaulted to a MEASURED-looking
literal — `tier ?? 'ROUTINE'`, `tier || 'DORMANT'` — which the 2026-09-14 all-pages
audit found SERVED on both platforms and R4 excised. Audits catch classes; lints keep
them dead: any reintroduction anywhere in the two frontends fails the build.

Scope: display-STATE fields only (tier / stage / gap_state / confidence_level /
detection_level / absence_class) followed by `??` or `||` and a quoted LITERAL.
A fallback to undefined/null/a variable is fine (honest absence); a literal band
name is a fabricated reading wearing a measured badge (§16a "silent 30")."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOTS = [os.path.join(HERE, "..", "frontend"),
         os.path.join(HERE, "..", "web-terminal", "src")]
FIELDS = r"(?:tier|stage|gap_state|gapState|confidence_level|confidenceLevel|detection_level|detectionLevel|absence_class|absenceClass)"
# Only a MEASURED-looking band literal is the defect. Membership-tier defaults
# ("consumer"), filter defaults ("all"), and honest absence labels ("NOT MEASURED")
# are legitimate fallbacks and stay unflagged.
BANDS = (r"(?:ROUTINE|DORMANT|MODERATE|ACTIVE|ELEVATED|BUILDING|ACUTE|BACKGROUND|"
         r"BREAKOUT|STRONG|EMERGING|WATCHING|MONITORING)")
PATTERN = re.compile(FIELDS + r"\s*(?:\?\?|\|\|)\s*['\"]" + BANDS + r"['\"]",
                     re.IGNORECASE)
SKIP_DIRS = {"node_modules", "dist", ".expo", "build"}


def main() -> int:
    hits = []
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if not fn.endswith((".ts", ".tsx")):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    lines = open(path, encoding="utf-8").read().splitlines()
                except OSError:
                    continue
                for i, line in enumerate(lines, 1):
                    code = line.split("//", 1)[0]
                    if PATTERN.search(code):
                        rel = os.path.relpath(path, os.path.join(HERE, ".."))
                        hits.append(f"{rel}:{i}: {line.strip()[:110]}")
    print(f"display-default lint: scanned frontend/ + web-terminal/src for "
          f"state-field literal fallbacks — {len(hits)} hit(s)")
    if hits:
        for h in hits:
            print("  FABRICATED DEFAULT:", h)
        print("  A display-state field may fall back to undefined/null (honest absence),"
              " never to a literal band name.")
        return 1
    print("  OK — the class stays dead")
    return 0


if __name__ == "__main__":
    sys.exit(main())
