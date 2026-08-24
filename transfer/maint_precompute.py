"""Release-phase + manual maintenance: prune anomaly_log, precompute serve_payloads.

Ruling 2c(a), board round 4: this runs in the Heroku RELEASE PHASE (see Procfile),
so every deploy rebuilds the payload cache with the NEW code before the new dynos
serve — the deploy-version window (a binary serving blobs built by another binary)
is closed at the process level, and the schema stamp (2c(c)) closes it at the
data level for anything this phase misses.

The Executioner's condition (2c(b)) is honoured in the function itself:
_precompute_serve_payloads is non-destructive — new payloads are built in memory
first and swapped in one transaction, so a mid-release failure leaves yesterday's
payloads serving instead of a NULL wasteland (the 2026-07-06 outage class).

RELEASE-SAFE BY CONTRACT: this script always exits 0. A failed maintenance pass
must not block the deploy — the in-cycle worker precompute self-heals within one
cycle, and blocking a deploy on cache warmth would turn a cache into a
single point of failure. Failures are printed loudly for the release log.

Manual run: heroku run python maint_precompute.py -a nowtrendin-v2-engine
"""
import os
import sys
import traceback


def main() -> int:
    try:
        import gravitational_anomaly_detector as g
        try:
            print("anomaly_log pruned:", g._prune_anomaly_log(30))
        except Exception:
            print("[maint] anomaly_log prune FAILED (continuing):")
            traceback.print_exc()
        n = g._precompute_serve_payloads(int(os.getenv("PRECOMPUTE_TOP_N", "600")))
        print(f"serve_payloads written: {n} (schema {g.PAYLOAD_SCHEMA_VERSION})")
        print("DONE")
    except Exception:
        print("[maint] precompute FAILED — stored payloads untouched (the swap "
              "is transactional); worker cycle will retry:")
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
