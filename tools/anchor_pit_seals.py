"""
anchor_pit_seals.py — export PIT seal heads OUTSIDE the database (board P0,
updates-review 2026-08-18, 8-of-9-seat convergence).

The PIT hash chain is tamper-evident but NOT loss-evident: seals live in the
same Postgres they attest, so a truncating restore (or a privileged rewrite +
re-seal) re-verifies clean. This script fetches /diag/pit/anchors and APPENDS
any seal heads / forecast hashes not yet present to
audits/pit-anchors/PIT_SEAL_ANCHORS.md — which is committed to git, the second
anchor. Append-only: existing lines are never modified; a divergence between a
fetched seal and an already-anchored line for the same day is printed as a
LOUD ALARM (that is the detection event this file exists for).

Provenance-grade note (Statistician): the grade-A clock starts the day a seal
head lands in the anchor file — anchoring cannot be done retroactively.

CADENCE: run at every session start (nowtrendin2.0 skill auto-save protocol)
and after every engine deploy. Usage:
    python tools/anchor_pit_seals.py            # INTERNAL_API_KEY from env,
                                                # else `heroku config:get`
Then commit + push the anchor file.
"""
import json
import os
import subprocess
import sys
import urllib.request

ENGINE = "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com"
ANCHOR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "audits", "pit-anchors", "PIT_SEAL_ANCHORS.md")

HEADER = """# PIT SEAL ANCHORS — the external (loss-evidence) anchor
#
# APPEND-ONLY. One line per day-seal: seal_date|row_count|seal_sha256
# One line per sealed forecast: F|item_key|event_date|row_sha256|text_sha256
# Lines are never edited or removed. A fetched seal that DISAGREES with an
# anchored line for the same day = tampering or data loss on the engine DB —
# investigate, never re-anchor over it. Source: GET /diag/pit/anchors.
"""


def _key():
    k = os.getenv("INTERNAL_API_KEY", "").strip()
    if k:
        return k
    out = subprocess.run(
        ["heroku", "config:get", "INTERNAL_API_KEY", "-a", "nowtrendin-v2-engine"],
        capture_output=True, text=True, shell=(os.name == "nt"))
    return (out.stdout or "").strip()


def main():
    key = _key()
    req = urllib.request.Request(ENGINE + "/diag/pit/anchors",
                                 headers={"X-Internal-Key": key})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    if "seals" not in data:
        print(f"FETCH FAILED: {data}")
        return 1

    os.makedirs(os.path.dirname(ANCHOR), exist_ok=True)
    existing = {}
    if os.path.exists(ANCHOR):
        with open(ANCHOR, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing[line.split("|")[0] + "|" + line.split("|")[1]] = line
    else:
        with open(ANCHOR, "w", encoding="utf-8", newline="\n") as f:
            f.write(HEADER)

    new_lines, alarms = [], []
    for s in data.get("seals", []):
        line = f"{s['seal_date']}|{s['row_count']}|{s['seal_sha256']}"
        k = f"{s['seal_date']}|{s['row_count']}"
        prev = next((v for pk, v in existing.items()
                     if pk.split("|")[0] == s["seal_date"]), None)
        if prev is None:
            new_lines.append(line)
        elif prev != line:
            alarms.append(f"SEAL DIVERGENCE {s['seal_date']}: anchored '{prev}' "
                          f"vs fetched '{line}'")
    for fx in data.get("forecasts", []):
        line = (f"F|{fx['item_key']}|{fx['event_date']}|{fx['row_sha256']}"
                f"|{fx.get('text_sha256') or ''}")
        prev = next((v for pk, v in existing.items()
                     if v.startswith(f"F|{fx['item_key']}|{fx['event_date']}|")), None)
        if prev is None:
            new_lines.append(line)
        elif prev != line:
            alarms.append(f"FORECAST DIVERGENCE {fx['item_key']}: anchored "
                          f"'{prev}' vs fetched '{line}'")

    if alarms:
        print("!" * 70)
        for a in alarms:
            print(f"ALARM: {a}")
        print("The engine record no longer matches the anchor — tampering or "
              "loss. DO NOT re-anchor. Investigate.")
        print("!" * 70)
        return 2
    if new_lines:
        with open(ANCHOR, "a", encoding="utf-8", newline="\n") as f:
            for line in new_lines:
                f.write(line + "\n")
        print(f"anchored {len(new_lines)} new line(s):")
        for line in new_lines:
            print(f"  {line}")
        print("Now: git add audits/pit-anchors/PIT_SEAL_ANCHORS.md && commit && push")
    else:
        print("no new seals/forecasts to anchor; existing anchors consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
