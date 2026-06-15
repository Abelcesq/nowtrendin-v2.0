"""One-off: re-score positioning + sustainability from existing risk_signals.
Run: heroku run python maint_risk.py -a nowtrendin
"""
import financial_risk_gradient as r

# Verify sustainability works for one ticker first (fast feedback).
demo = r.compute_sustainability("AAPL")
print("AAPL sustainability:", demo)

n = r.score_all_risks()
print("scored:", n)
print("DONE")
