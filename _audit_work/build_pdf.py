# -*- coding: utf-8 -*-
"""Build the NowTrendIn Gradient Score audit PDF from the workflow's verified findings."""
import json, re, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, HRFlowable, KeepTogether)

D = json.load(open("audit_full.json", encoding="utf-8"))
R = D["report"]

# ---- palette ----
NAVY   = colors.HexColor("#13233a")
GREEN  = colors.HexColor("#00897B")
ORANGE = colors.HexColor("#C75B1E")
RED    = colors.HexColor("#B5341B")
GREY   = colors.HexColor("#5B6472")
LIGHT  = colors.HexColor("#EEF1F4")
LINE   = colors.HexColor("#D5DBE2")
BLUE   = colors.HexColor("#2D5BE0")

# ---- unicode -> latin-1 sanitizer (Helvetica can't render these) ----
SUBS = {
    "—":"-","–":"-","−":"-","≥":">=","≤":"<=","≈":"~",
    "→":"->","’":"'","‘":"'","“":'"',"”":'"',"·":" / ",
    "×":"x","…":"...","•":"-"," ":" "," ":" "," ":" ",
    "½":"1/2","≡":"=","≠":"!=","â€”":"-",
}
def san(t):
    if t is None: return ""
    t = str(t)
    for k,v in SUBS.items(): t = t.replace(k,v)
    # strip any remaining non-latin1
    t = t.encode("latin-1","ignore").decode("latin-1")
    return t
def esc(t):  # XML-safe for Paragraph
    return san(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

styles = getSampleStyleSheet()
def mk(name, **kw):
    base = kw.pop("parent","Normal")
    return ParagraphStyle(name, parent=styles[base], **kw)

H1  = mk("H1", parent="Heading1", fontName="Helvetica-Bold", fontSize=15, textColor=NAVY,
         spaceBefore=16, spaceAfter=6, leading=18)
H2  = mk("H2", parent="Heading2", fontName="Helvetica-Bold", fontSize=11.5, textColor=ORANGE,
         spaceBefore=10, spaceAfter=4, leading=14)
BODY= mk("BODY", fontSize=9.3, leading=13.6, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1A1A2E"),
         spaceAfter=6)
BULLET = mk("BULLET", fontSize=9.3, leading=13.4, leftIndent=14, bulletIndent=2, spaceAfter=4,
            textColor=colors.HexColor("#1A1A2E"))
SMALL = mk("SMALL", fontSize=8, leading=10.5, textColor=GREY)
CELL  = mk("CELL", fontSize=7.8, leading=9.6, textColor=colors.HexColor("#1A1A2E"))
CELLB = mk("CELLB", fontSize=7.8, leading=9.6, textColor=colors.white, fontName="Helvetica-Bold")
KICK  = mk("KICK", fontSize=8.5, leading=11, textColor=GREEN, fontName="Helvetica-Bold", spaceAfter=2)

def P(t, s=BODY): return Paragraph(esc(t), s)

def paras(text, s=BODY, group=3):
    """Split a long prose blob into readable ~group-sentence paragraphs."""
    text = san(text)
    sents = re.split(r'(?<=[.;])\s+(?=[A-Z(])', text)
    out, buf = [], []
    for sent in sents:
        buf.append(sent.strip())
        if len(buf) >= group:
            out.append(P(" ".join(buf), s)); buf=[]
    if buf: out.append(P(" ".join(buf), s))
    return out

def tbl(data, colw, header=True, fontsize=7.8, hbg=NAVY):
    t = Table(data, colWidths=colw, repeatRows=1 if header else 0)
    st = [("VALIGN",(0,0),(-1,-1),"TOP"),
          ("FONTSIZE",(0,0),(-1,-1),fontsize),
          ("GRID",(0,0),(-1,-1),0.4,LINE),
          ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
          ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
          ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, LIGHT])]
    if header:
        st += [("BACKGROUND",(0,0),(-1,0),hbg),("TEXTCOLOR",(0,0),(-1,0),colors.white),
               ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]
    t.setStyle(TableStyle(st))
    return t

def box(flowables, bg=LIGHT, bc=LINE):
    inner = Table([[flowables]], colWidths=[6.9*inch])
    inner.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0.7,bc),
        ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return inner

S = []  # story

# ============ COVER ============
S.append(Spacer(1, 0.7*inch))
S.append(Paragraph("THE GRADIENT SCORE", mk("kcovtag", fontSize=11, textColor=ORANGE,
        fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=4)))
S.append(Paragraph("Independent Engineering Audit", mk("kcov", fontSize=27, textColor=NAVY,
        fontName="Helvetica-Bold", leading=31, spaceAfter=6)))
S.append(Paragraph("Does NowTrendIn's data accurately reflect the current market and its "
        "&quot;human attention, before it arrives&quot; claim?", mk("ksub", fontSize=12.5,
        textColor=GREY, leading=17, spaceAfter=18)))
S.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=14))
meta = [
 ["Subject", "NowTrendIn 2.0 Gradient Score, the Detection/Confidence gap, and Market Signal tiers"],
 ["Reviewer frame", "Engineer auditing for a venture-capital / investment-bank diligence team"],
 ["Method", "24 AI agents: intended-vs-actual model mapping (code = source of truth), live-data "
            "diagnosis, adversarially-verified no-gap falsification test, external-benchmark research"],
 ["Data basis", "Live engine snapshot 2026-06-22/23: 2,103 scored topics, a 100-topic stratified "
                "no-gap sample, 88 Market Signal instruments. Single-day - directionally decisive, "
                "not a multi-week out-of-sample validation."],
 ["Operating period", "~2-4 weeks of live scoring at time of audit"],
 ["Date", "2026-06-23"],
]
mt = Table([[Paragraph(f"<b>{esc(k)}</b>", CELL), Paragraph(esc(v), CELL)] for k,v in meta],
           colWidths=[1.25*inch, 5.65*inch])
mt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-2),0.4,LINE),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("BACKGROUND",(0,0),(0,-1),LIGHT)]))
S.append(mt)
S.append(Spacer(1, 0.3*inch))
S.append(box([Paragraph("<b>Integrity stance of this audit.</b> Findings are reported to the "
    "product's own standard: accuracy over impressiveness, no circular metrics, reputable/licensed "
    "sources only, and measurement - not advice. Where the engine is honest and correct, this report "
    "says so; where it fails, it cites the live numbers and the basis for the determination.", SMALL)],
    bg=colors.HexColor("#F3FAF8"), bc=GREEN))
S.append(PageBreak())

# ============ EXEC SUMMARY ============
S.append(Paragraph("Executive Summary", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
# headline verdict box
S.append(box([
    Paragraph("VERDICT: NOT YET DEFENSIBLE AS AN UNQUALIFIED &quot;ATTENTION BEFORE IT ARRIVES&quot; INSTRUMENT.",
              mk("vh", fontSize=10.5, fontName="Helvetica-Bold", textColor=RED, spaceAfter=4)),
    Paragraph("The instrument fails its own no-gap credibility floor on the day's single most important "
        "confirmed event and on a systematic class of already-arrived topics - while the core "
        "&quot;lead&quot; claim remains unproven (accuracy ledger at 0.0% honest hit rate). The design is "
        "structurally honest and the top tier works; the mid-mainstream band and the market tiers do not.",
        SMALL)], bg=colors.HexColor("#FBF3F1"), bc=RED))
S.append(Spacer(1,8))
for f in paras(R["executive_summary"], group=2): S.append(f)
S.append(PageBreak())

# ============ 1. WHAT IT IS ============
S.append(Paragraph("1. What the Gradient Score Is", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
for f in paras(R["what_it_is"], group=2): S.append(f)
S.append(Spacer(1,6))
S.append(Paragraph("Displayed stage cutoffs (Detection-derived)", H2))
stage_cut = [["Stage (internal key)","User label","Detection cutoff","Meaning"],
 ["BREAKOUT",">= 85","Breakout","Arrived / confirmed, act now"],
 ["STRONG","70 - 84","Strong","Strong, broadly corroborated"],
 ["EMERGING","55 - 69","INDICATING","Detected, not yet broadly confirmed"],
 ["MARGINAL / WATCHING","35 - 54","Marginal","Weak / watch"],
 ["MONITORING","< 35","Monitoring","Below signal floor"],
 ["ANOMALY (flag)","Det 16+ over Conf","Anomaly","Orthogonal flag, not a strength band"]]
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(stage_cut)],
             [1.5*inch,1.0*inch,1.4*inch,3.0*inch]))
S.append(PageBreak())

# ============ 2. FACTORS & WEIGHTING ============
S.append(Paragraph("2. Data Factors and How They Are Weighed", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
S.append(Paragraph("Live code weights (six-component, N excluded, renormalized to 1.0)", H2))
w = [["Component","Detection","Confidence","Overall","What it measures"],
 ["G - Gradient Strength","0.375","0.122","0.244","Niche-to-mainstream engagement density (fires earliest)"],
 ["D - Dark Matter","0.216","0.044","0.133","Inferred hidden/private-conversation signal (first-timer ratio, asymmetry)"],
 ["I - Inertia","0.182","0.278","0.222","Consecutive accelerating 6h windows (best sustain predictor)"],
 ["M - Medium/Platform","0.102","0.222","0.167","Cross-platform diffusion breadth"],
 ["C - Confidence Decay","0.057","0.067","0.078","Freshness / age (Heisenberg-exempt)"],
 ["P - Persistence","0.068","0.267","0.156","Cycles held above EMERGING (self-referential - see note)"]]
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(w)],
             [1.55*inch,0.72*inch,0.78*inch,0.62*inch,3.23*inch]))
S.append(Paragraph("Detection leads on the earliest-firing components (G + D); Confidence leads on the "
    "slowest-to-confirm (I + P + M). N (in-app demand) is verifiably 0.0 in all three composites.", SMALL))
S.append(Spacer(1,6))
for f in paras(R["factors_and_weighting"], group=2): S.append(f)
S.append(PageBreak())

# ============ 3. DISTRIBUTION ============
S.append(Paragraph("3. Distribution, Saturation, and Separation", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
S.append(Paragraph("Per-stage distribution across the 2,103-topic live snapshot", H2))
ps = D["trend_stats"]["per_stage"]
rows = [["Stage","Count","Det median","Conf median","Gap median","Det range","Conf range"]]
for r in ps:
    rows.append([san(r["stage"]).replace(" (is_gravitational_anomaly=1)"," (flag)"),
                 str(r["count"]), str(r["det_median"]), str(r["conf_median"]),
                 str(r["gap_median"]), san(r["det_range"]), san(r["conf_range"])])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(rows)],
             [1.45*inch,0.55*inch,0.75*inch,0.8*inch,0.7*inch,0.95*inch,0.95*inch]))
S.append(Spacer(1,5))
S.append(Paragraph("<b>Reads as:</b> the score is NOT collapsed - stage medians ladder monotonically "
    "(Det 90.5 / 74.1 / 46.0 / 32.8 / 17.3) and 520 of 595 Detection/Confidence values are distinct. "
    "But note the inversion in the middle of the curve: at EMERGING and WATCHING the <b>gap median is "
    "~-22</b> (Confidence well above Detection) - the opposite of the intended &quot;early = Detection "
    "leads.&quot; The gap converges to ~0 only for genuinely-arrived BREAKOUT topics (median -0.8).", BODY))
S.append(PageBreak())

# ============ 4. ERROR ANALYSIS ============
S.append(Paragraph("4. Critical Error Analysis", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
S.append(Paragraph("4a. The no-gap falsification test", H2))
for f in paras(R["error_analysis"], group=2): S.append(f)

# mainstream collapse table
S.append(Spacer(1,6))
S.append(Paragraph("4b. The mainstream-collapse signature (live sample)", H2))
S.append(Paragraph("Already-arrived nations and mega-caps collapse to a near-identical ~45 Det / ~67 "
    "Conf EMERGING signature with a uniform ~-22 gap - Confidence exceeding Detection on topics that "
    "have unambiguously arrived:", SMALL))
samp = {r["topic"].lower(): r for r in D["sample100"]}
collapse_keys = ["china","india","russia","france","apple","openai","korea","obama"]
crows = [["Topic","Stage","Detection","Confidence","Gap","Mentions","Platforms"]]
for k in collapse_keys:
    r = samp.get(k)
    if r: crows.append([r["topic"],san(r["stage"]),str(r["det"]),str(r["conf"]),str(r["gap"]),
                        str(r.get("mentions","")),str(r.get("platforms",""))])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(crows)],
             [1.4*inch,1.1*inch,0.85*inch,0.95*inch,0.6*inch,0.85*inch,0.85*inch], hbg=RED))

# Greenspan + fragmentation
S.append(Spacer(1,8))
S.append(Paragraph("4c. Two adversarially-confirmed errors + the decisive event", H2))
gr = samp.get("alan greenspan")
hl = [["Case","Det","Conf","Gap / Stage","Finding"]]
if gr: hl.append(["Alan Greenspan (died 6/22, the day's #1 story)",str(gr["det"]),str(gr["conf"]),
        f"+{gr['gap']} / {san(gr['stage'])}","Largest positive gap in the sample; a confirmed obituary read as a speculative early lead - the exact broken state the no-gap principle names."])
h1r=samp.get("hormuz"); h2r=samp.get("strait of hormuz")
if h1r and h2r:
    hl.append([f"'hormuz' vs 'strait of hormuz' (same story)",f"{h1r['det']} / {h2r['det']}",
        f"{h1r['conf']} / {h2r['conf']}","STRONG vs WATCHING",
        "CONFIRMED ERROR (medium): surface-form fragmentation - no alias-consolidation layer, so the canonical phrase collapses to WATCHING while the short token reads STRONG."])
hl.append(["'belgium vs iran' (real 6/21 WC fixture)","10.2","17.7","MONITORING",
    "CONFIRMED ERROR (low): under-weight, but explainable by the documented, fix-pending M/D reweighting (CLAUDE.md sec 15)."])
hl.append(["mcp family (stored heisenberg_gap)","74.5","73.0","stored gap -23","DATA-INTEGRITY BUG: stored gap contradicts Det-Conf (=+1.5) by ~24 pts - breaks the 'both scores explain each other' test."])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(hl)],
             [1.75*inch,0.7*inch,0.7*inch,0.85*inch,2.9*inch], hbg=RED))

# accurate examples
S.append(Spacer(1,8))
S.append(Paragraph("4d. Where the engine is genuinely correct (accurate examples)", H2))
ax = [["Topic","Det","Conf","Gap","Why it is correct"]]
for e in D["no_gap"]["accurate_examples"][:8]:
    ax.append([san(e["topic"]),str(e["det"]),str(e["conf"]),str(e["gap"]),
               san(e["why_correct"])[:150]])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(ax)],
             [1.05*inch,0.55*inch,0.6*inch,0.55*inch,4.15*inch], hbg=GREEN))
S.append(Paragraph("The top tier passes cleanly (trump 94.6/94.2, FIFA 93.7/93.7, election 94.7/94.3, "
    "canada 90/91.7) and niche topics correctly sit LOW on BOTH axes (SpaceX-IPO 24.9/25.4, fastapi "
    "46.2/48.6) - the engine does not fabricate confidence. The failure is one-directional: it strips "
    "score from mid-mainstream topics; it does not invent it for niche ones.", SMALL))
S.append(PageBreak())

# ============ 5. MARKET SIGNAL ============
S.append(Paragraph("5. Market Signal Categories", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
ms = D["market_stats"]
S.append(Paragraph("Tier distribution across the live 88-instrument universe", H2))
td = [["Tier","Count","% of universe"]]
tot = ms.get("total_instruments") or sum(x["count"] for x in ms["tier_distribution"])
for x in ms["tier_distribution"]:
    td.append([san(x["tier"]), str(x["count"]), f"{100*x['count']/max(tot,1):.1f}%"])
td.append(["calibrating=true (overlay)", str(round((ms.get('pct_calibrating') or 0)*tot/100)) if (ms.get('pct_calibrating') or 0)>1 else f"{ms.get('pct_calibrating')}%", f"{ms.get('pct_calibrating')}%"])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(td)],
             [2.6*inch,1.2*inch,1.4*inch], hbg=NAVY))
S.append(Paragraph("<b>87 of 88 instruments (98.9%) are ROUTINE</b> - the user-facing tier carries "
    "essentially zero information. The baseline-relative z-score design is genuinely good (it fixes the "
    "mega-cap size-bias) and cold-start honesty is real, but as surfaced the tiers do not separate "
    "instruments, and three tier fields (tier / risk_stage / classification) disagree on the same row.", BODY))
S.append(Spacer(1,6))
for f in paras(R["market_signal_analysis"], group=2): S.append(f)
S.append(PageBreak())

# ============ 6. BENCHMARKS ============
S.append(Paragraph("6. External Benchmarks and a Non-Circular Calibration Loop", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
S.append(Paragraph("Candidate external attention anchors", H2))
bm = [["Benchmark","Measures","Cost / licensing","Non-circular?","Use"]]
for b in D["benchmarks"]["benchmarks"]:
    bm.append([san(b["name"])[:46], san(b["measures"])[:120], san(b["cost_licensing"])[:60],
               san(b["non_circular"])[:60], san(b["how_to_use"])[:90]])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(bm)],
             [1.25*inch,1.7*inch,1.05*inch,1.05*inch,1.15*inch], fontsize=7.0, hbg=NAVY))
S.append(Spacer(1,6))
for f in paras(R["benchmarks_and_calibration"], group=2): S.append(f)
S.append(PageBreak())

# ============ 7. RECOMMENDATIONS ============
S.append(Paragraph("7. Recommendations", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
rec = san(R["recommendations"])
def split_items(blob):
    items = re.split(r'\s*\(\d+\)\s*', blob)
    return [i.strip() for i in items if i.strip()]
# split on the two headers
qw, rg = rec, ""
m = re.search(r'RESEARCH-GATED', rec)
if m:
    qw = rec[:m.start()]; rg = rec[m.start():]
qw = qw.replace("QUICK WINS (ship-able now, no research gate, each integrity-preserving):","").strip()
S.append(Paragraph("Quick wins - shippable now, no research gate, each integrity-preserving", H2))
for it in split_items(qw):
    S.append(Paragraph("- "+esc(it), BULLET))
if rg:
    rg = rg.replace("RESEARCH-GATED (require backtest-before-ship, must not bypass integrity):","").strip()
    S.append(Spacer(1,6))
    S.append(Paragraph("Research-gated - require backtest-before-ship, must not bypass integrity", H2))
    for it in split_items(rg):
        S.append(Paragraph("- "+esc(it), BULLET))
S.append(PageBreak())

# ============ 8. VERDICT ============
S.append(Paragraph("8. Verdict", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
for f in paras(R["verdict"], group=2): S.append(f)
S.append(Spacer(1,10))
S.append(box([Paragraph("<b>What must be true before the &quot;before it arrives&quot; claim is "
    "defensible to an institutional buyer:</b> (1) the heisenberg_gap and surface-form fragmentation "
    "bugs are fixed; (2) the dual-pathway anti-collapse protection extends across the full mainstream "
    "band; (3) a held-out, non-circular Wikipedia + GDELT no-gap anchor is wired and shows acceptable "
    "false-early precision; (4) the market tier fields and cold-start flags are reconciled into one "
    "coherent surface; (5) the accuracy ledger clears its own published success bar so the lead is "
    "denominator-backed.", SMALL)], bg=colors.HexColor("#F3FAF8"), bc=GREEN))

# ============ APPENDIX ============
S.append(PageBreak())
S.append(Paragraph("Appendix A - 100-topic no-gap sample (live engine, 2026-06-22/23)", H1))
S.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))
S.append(Paragraph("Stratified across stages. Gap = Detection - Confidence. Sorted by Detection desc.", SMALL))
sm = sorted(D["sample100"], key=lambda r: -(r.get("det") or 0))
ar = [["Topic","Stage","Det","Conf","Gap","Ment.","Plat.","N"]]
for r in sm:
    ar.append([san(r["topic"])[:30],san(r["stage"])[:10],str(r["det"]),str(r["conf"]),
               str(r["gap"]),str(r.get("mentions","")),str(r.get("platforms","")),str(r.get("n",""))])
S.append(tbl([[Paragraph(esc(c), CELLB if i==0 else CELL) for c in row] for i,row in enumerate(ar)],
             [1.95*inch,0.95*inch,0.55*inch,0.6*inch,0.55*inch,0.6*inch,0.55*inch,0.5*inch], fontsize=6.8))

# ---- footer/header ----
def deco(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7); canvas.setFillColor(GREY)
    canvas.drawString(0.8*inch, 0.55*inch, "NowTrendIn - Gradient Score Audit - Confidential")
    canvas.drawRightString(7.7*inch, 0.55*inch, f"Page {doc.page}")
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.4)
    canvas.line(0.8*inch, 0.7*inch, 7.7*inch, 0.7*inch)
    canvas.restoreState()

OUT = r"C:\Users\acinv\OneDrive\Desktop\NowTrendIn_Gradient_Score_Audit_2026-06-23.pdf"
doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.9*inch,
                        leftMargin=0.8*inch, rightMargin=0.8*inch,
                        title="NowTrendIn Gradient Score Audit", author="Engineering Audit")
doc.build(S, onFirstPage=deco, onLaterPages=deco)
print("WROTE", OUT, os.path.getsize(OUT), "bytes")
