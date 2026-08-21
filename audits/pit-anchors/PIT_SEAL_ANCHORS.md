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
F|FCAST-F7-quarterly-benchmarks-Q1-2026-11-30|2026-08-19|c298322ba49f5f6d72d595c49c05f795ca1081d1d21eb0619d2b0d268e1b6c37|9fbd47cbc86d2f631fae206a278c20d095321ef21608b49fe41fe77ac58358b9
2026-08-19|60373|7f7c5d78b2242e2d8e43cecdfc45886963516253511dcedbce96d61f6324a5a8
2026-08-20|68818|30027dc08cc6c0a4054194f3630f711755a8268c7419c71eb2eaa68736d307de
F|PREREG-referee-decomposition-2026-08-20|2026-08-20|572adc8fa5690f3cb09ab32d1b94103015edf61c8398a038ee02d258817616d4|2d99c8de3191d4e714cdb1780f8b8b9828a7f2e28f372f7b865531aabdd7c069
F|PREREG-shadow-trial-2026|2026-08-20|e90af6df909de1393fc580622fecca53bdacf7a0cb056d0ec5b54a2c7789cf98|25b69ffc8e88d393348b73081477c586ff5ba7fa49d822541534ac9b497f6e3e
F|PREREG-shadow-trial-2026-ERRATUM-01|2026-08-20|6f9ed05fb268d68efd2d3c4afb0ee4c4376e4446dc62a0e32afa9512da3eeabc|2b34596ca0426f45fbaf8900e4aeb343be542af9e0ec3b7a84aed82a25192bf0
F|D-KILL-CRITERION-2026-08-20|2026-08-20|caf62911f2f35d8c0c046788ca3f873a3562c7b76f78dc6a420f21936263c235|403b6a7e86fb20794c8637ecdcc25d57c97be3fcc1a94f45d78407ebf6f4c448
