"""Manual one-off: prune anomaly_log + precompute serve_payloads now.
Run: heroku run python maint_precompute.py -a nowtrendin
"""
import gravitational_anomaly_detector as g

print("anomaly_log pruned:", g._prune_anomaly_log(30))
print("serve_payloads written:", g._precompute_serve_payloads(600))
print("DONE")
