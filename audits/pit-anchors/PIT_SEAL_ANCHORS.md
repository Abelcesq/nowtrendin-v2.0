# PIT SEAL ANCHORS — the external (loss-evidence) anchor
#
# APPEND-ONLY. One line per day-seal: seal_date|row_count|seal_sha256
# One line per sealed forecast: F|item_key|event_date|row_sha256|text_sha256
# Lines are never edited or removed. A fetched seal that DISAGREES with an
# anchored line for the same day = tampering or data loss on the engine DB —
# investigate, never re-anchor over it. Source: GET /diag/pit/anchors.
2026-08-18|8481|85f54a877a30e32a696f882722fb04eb9f77977d0a01777fc59570f99aa5e4d2
F|FCAST-F5-first-paying-licensee-structure-f|2026-08-18|9531d484d29840c26097104ee5f2ba9383696f38570a1bca41307934795f619c|465d9f3d7c5fb848968d5eabb0a0868e18683065559f730a9e3d4494250e4fb2
F|FCAST-F6-point-convention-F1-F4|2026-08-19|3e755832de65ce419ddaad8e8033ce20ba3c9a7fc79efaf95cb3573564233a19|881becd6b17707ea0d075f4bc9699aa82b1608fc272743727d20e932dd8c17cc
