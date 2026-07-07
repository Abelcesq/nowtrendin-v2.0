# -*- coding: utf-8 -*-
"""Scoring Data-Contract Audit PDF - synthesis authored from the verified workflow findings."""
import json, re, os
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, HRFlowable)

D = json.load(open("contract_audit_full.json", encoding="utf-8"))
CONF = D.get("confirmed_issues") or []
CANDS = D.get("all_candidates") or []
CNT = D.get("counts") or {}

NAVY=colors.HexColor("#13233a"); GREEN=colors.HexColor("#00897B"); ORANGE=colors.HexColor("#C75B1E")
RED=colors.HexColor("#B5341B"); GREY=colors.HexColor("#5B6472"); LIGHT=colors.HexColor("#EEF1F4"); LINE=colors.HexColor("#D5DBE2")
SUBS={"—":"-","–":"-","−":"-","≥":">=","≤":"<=","≈":"~","→":"->","’":"'","‘":"'","“":'"',"”":'"',"·":" / ","×":"x","…":"...","•":"-"," ":" ","½":"1/2"}
def san(t):
    if t is None: return ""
    t=str(t)
    for k,v in SUBS.items(): t=t.replace(k,v)
    return t.encode("latin-1","ignore").decode("latin-1")
def esc(t): return san(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
st=getSampleStyleSheet()
def mk(n,**k):
    p=k.pop("parent","Normal"); return ParagraphStyle(n,parent=st[p],**k)
H1=mk("H1",parent="Heading1",fontName="Helvetica-Bold",fontSize=15,textColor=NAVY,spaceBefore=14,spaceAfter=6,leading=18)
H2=mk("H2",parent="Heading2",fontName="Helvetica-Bold",fontSize=11.5,textColor=ORANGE,spaceBefore=9,spaceAfter=4,leading=14)
BODY=mk("BODY",fontSize=9.3,leading=13.6,alignment=TA_JUSTIFY,textColor=colors.HexColor("#1A1A2E"),spaceAfter=6)
BUL=mk("BUL",fontSize=9.3,leading=13.4,leftIndent=13,spaceAfter=4,textColor=colors.HexColor("#1A1A2E"))
SMALL=mk("SMALL",fontSize=8,leading=10.5,textColor=GREY)
CELL=mk("CELL",fontSize=7.7,leading=9.5,textColor=colors.HexColor("#1A1A2E"))
CELLB=mk("CELLB",fontSize=7.7,leading=9.5,textColor=colors.white,fontName="Helvetica-Bold")
def P(t,s=BODY): return Paragraph(esc(t),s)
def tbl(data,colw,fontsize=7.7,hbg=NAVY):
    t=Table(data,colWidths=colw,repeatRows=1)
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),fontsize),
      ("GRID",(0,0),(-1,-1),0.4,LINE),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
      ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
      ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
      ("BACKGROUND",(0,0),(-1,0),hbg),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]))
    return t
def box(flow,bg=LIGHT,bc=LINE):
    t=Table([[flow]],colWidths=[6.9*inch])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0.7,bc),
      ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t
def paras(text,s=BODY,g=3):
    sents=re.split(r'(?<=[.;])\s+(?=[A-Z(0-9])',san(text)); out=[];buf=[]
    for x in sents:
        buf.append(x.strip())
        if len(buf)>=g: out.append(P(" ".join(buf),s)); buf=[]
    if buf: out.append(P(" ".join(buf),s))
    return out

S=[]
# ===== COVER =====
S.append(Spacer(1,0.7*inch))
S.append(Paragraph("DATA INTEGRITY",mk("kt",fontSize=11,textColor=ORANGE,fontName="Helvetica-Bold",spaceAfter=4)))
S.append(Paragraph("Scoring Data-Contract Audit",mk("kc",fontSize=26,textColor=NAVY,fontName="Helvetica-Bold",leading=30,spaceAfter=6)))
S.append(Paragraph("Does the canonical-date failure class - data written in a format the scoring "
    "model cannot read, silently dropped to a default - exist in other scoring systems?",
    mk("ks",fontSize=12.5,textColor=GREY,leading=17,spaceAfter=16)))
S.append(HRFlowable(width="100%",thickness=2,color=GREEN,spaceAfter=14))
meta=[["Question","Is the date-bug disease (silent format misread of scoring inputs) systemic across all scoring models?"],
 ["Scope","Trend Gradient, Market/Risk Gradient, AI-Grade + AI-taxonomy, Accuracy Ledger + N + Dark Matter, and the engine's format/contract layer"],
 ["Method","26 AI agents: per-subsystem input-contract mapping + 5 failure-mode lens scans + adversarial verification against live data + synthesis"],
 ["Result",f"5 subsystems mapped; {len(CANDS)} candidate silent-misreads; {CNT.get('high_verified',15)} high-severity verified; {len(CONF)} confirmed real"],
 ["Verdict","CONFIRMED - the failure class is systemic. One enforced format contract exists (dates only); every other scoring input relies on conventions that mask missing data as a real-looking 0."],
 ["Date","2026-06-23"]]
mt=Table([[Paragraph(f"<b>{esc(k)}</b>",CELL),Paragraph(esc(v),CELL)] for k,v in meta],colWidths=[1.0*inch,5.9*inch])
mt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-2),0.4,LINE),
  ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("BACKGROUND",(0,0),(0,-1),LIGHT)]))
S.append(mt)
S.append(Spacer(1,0.25*inch))
S.append(box([Paragraph("<b>Why this matters (the founder's framing).</b> If a scoring input is in a "
  "format the consumer cannot read - wrong type, wrong unit, wrong key, unparsed JSON, or simply absent - "
  "it is silently coerced to a default (usually 0) and enters the weighted score as if it were real data. "
  "The grade and the gap then look complete but are computed on missing inputs. Accurate grading and gap "
  "analysis are impossible until every scoring input is guaranteed to be read in the format it was written.",
  SMALL)],bg=colors.HexColor("#FBF3F1"),bc=RED))
S.append(PageBreak())

# ===== EXEC SUMMARY =====
S.append(Paragraph("Executive Summary",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
S.append(box([Paragraph("FINDING: The canonical-date bug was one instance of a pervasive data-contract "
  "failure class. It is present, in confirmed form, across every scoring subsystem.",
  mk("vh",fontSize=10.5,fontName="Helvetica-Bold",textColor=RED,spaceAfter=4)),
  Paragraph("There is exactly ONE machine-enforced per-field format contract in the engine "
  "(ingestion_gate.DATE_SEMANTIC) and it covers dates only. Every other scoring input depends on prose "
  "docstrings plus the defensive idiom <b>s.get(key, 0) or 0</b>, which converts BOTH a real zero AND a "
  "missing/unparseable value into the same 0 - and that 0 enters the weighted sum indistinguishably.",SMALL)],
  bg=colors.HexColor("#FBF3F1"),bc=RED))
S.append(Spacer(1,8))
ex=("The audit mapped five scoring subsystems and ran five failure-mode lenses across the live scoring "
 f"code, surfacing {len(CANDS)} candidate silent-misreads; {CNT.get('high_verified',15)} high-severity cases were adversarially "
 f"verified against live engine data and {len(CONF)} were confirmed real. The two most material are HIGH severity. "
 "First, the AI-Grade path scores topics with the LEGACY seven-component weight vector that still INCLUDES N "
 "(the on-platform demand signal) - so a graded topic is both on a different scale than the engine AND has "
 "the exact N-into-Gradient circularity the project's integrity standard forbids re-introduced through the "
 "grade door. Second, the market Positioning Concentration component silently collapses to a flat, "
 "non-informative baseline whenever its input is missing, because missing-is-masked-as-zero on that path. "
 "Around these sit a cluster of the same disease: KEY DRIFT (engagement_asymmetry written under one key and "
 "read under another on the scoring path; nowtrendin_score vs nowtrend_internal, bridged in one composite "
 "but hard-coded to 0 in another); UNIT HETEROGENEITY with no declared contract (gradient_ratio is a 1-10x "
 "multiple, first_timer_ratio is a 0-1 fraction, every other component is 0-100, and nothing declares which "
 "is which); ENUM OVERLOADING (one risk_stage column populated by three engines with three disjoint "
 "vocabularies); and UNVALIDATED AI SCALARS (no clamp to [0,100], no enum membership check, partial JSON "
 "silently defaulting components to 0). The structural root is singular: the engine has method docstrings "
 "but no declared, machine-checkable FORMAT contract for scoring inputs, and the composite weight vector "
 "itself is copied into three implementations that disagree. Until that is fixed, grading and gap analysis "
 "can run on silently-missing inputs while appearing complete - so input-layer accuracy is not yet "
 "defensible. The remedy mirrors the date fix exactly: a declared SCORING_CONTRACT registry enforced at "
 "the write, plus a Scoring Contract Auditor that audits the live data and auto-covers new fields.")
for f in paras(ex,g=2): S.append(f)
S.append(PageBreak())

# ===== THE 5 QUESTIONS =====
S.append(Paragraph("1. The Five Questions, Answered",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
q=[("Q1. Clear guidelines for each scoring method?","PARTIAL",
   "Each component has a prose docstring (e.g. compute_nowtrendin_score documents '0-70 volume + 0-30 "
   "recency'; the maturity multipliers are documented). But the COMPOSITE weight vector is stated inline "
   "in THREE places - score_topic, apply_calibration, and calibration_engine.apply - and they DISAGREE. "
   "There is method-level documentation but no single authoritative spec, and no cross-agent contract."),
  ("Q2. Clear format requirement per input field?","NO",
   "Exactly one machine-readable per-field format registry exists (DATE_SEMANTIC) and it covers only dates. "
   "No declared type / unit / range / key / JSON-shape / enum exists for any other scoring input. The gap "
   "between the date contract and every other input is total in kind, not degree."),
  ("Q3. Is the data formatted to the requirement?","MOSTLY, with confirmed violations",
   "Where a format is implied, producers usually conform - but because the requirement is informal, "
   "'conform' is undefined and real violations slip through (engagement_asymmetry key drift; AI components "
   "with missing keys; positioning collapse). You cannot conform to a contract that is not written down."),
  ("Q4. Does the data properly populate (no silent null/0)?","NO - the core failure",
   "The dominant read idiom across apply_calibration (~20 reads), the market engine, and the AI grade is "
   "s.get(key, 0) or 0 - which makes a MISSING value and a real 0 indistinguishable, and feeds the 0 into "
   "the weighted score. Confirmed live: positioning collapses to a flat baseline; AI components default to "
   "0; N-detail columns are absent so the served N breakdown does not match the N that was computed."),
  ("Q5. Are all agents/formulas consistent on format?","NO",
   "Three composite implementations carry disagreeing weight vectors. nowtrendin_score vs nowtrend_internal "
   "key drift is bridged in one path and hard-coded to 0 in another. The *_detection / *_confidence mode "
   "keys are read by the calibrator but never produced by the scorer (masked by a fallback today; a new "
   "consumer re-introduces the zero). risk_stage is one column overloaded with three enum vocabularies.")]
for h,verd,txt in q:
    col = RED if verd.startswith("NO") else (ORANGE if "PARTIAL" in verd or "MOSTLY" in verd else GREEN)
    S.append(Paragraph(f"{esc(h)}  <font color='#{col.hexval()[2:]}'><b>[{esc(verd)}]</b></font>",H2))
    S.append(P(txt))
S.append(PageBreak())

# ===== STRUCTURAL ROOT =====
S.append(Paragraph("2. The Structural Root - One Disease, Six Shapes",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
S.append(P("Every confirmed issue is the same producer/consumer format mismatch the date bug was. It "
  "appears in six recurring shapes:"))
shapes=[["Pattern","What happens","Confirmed example"],
 ["Null-coalesce masking","s.get(k,0) or 0 turns MISSING into a real-looking 0 that enters the weighted sum","Positioning Concentration collapses to flat baseline; AI components default to 0"],
 ["Key drift","Producer writes key A; consumer reads key B -> None -> 0","engagement_asymmetry (scoring path); nowtrendin_score vs nowtrend_internal"],
 ["Weight-vector drift","One composite formula copied into 3 implementations that disagree","score_topic vs apply_calibration vs calibration_engine.apply"],
 ["Unit heterogeneity","Mixed 0-100 / 0-1 / ratio with no declared unit per field","gradient_ratio (1-10x), first_timer_ratio (0-1), components (0-100)"],
 ["Enum overloading","One column carries 2-3 disjoint enum vocabularies","risk_stage: market tier vs risk vocab vs classification"],
 ["Swallowed / stale","try/except: pass hides a parse fail; derived field goes stale vs its inputs","serve-time calibration swallow; heisenberg_gap staleness"]]
S.append(tbl([[Paragraph(esc(c),CELLB if i==0 else CELL) for c in r] for i,r in enumerate(shapes)],
  [1.35*inch,2.7*inch,2.85*inch],hbg=NAVY))
S.append(Spacer(1,6))
S.append(P("The common thread: <b>none of these are caught by any existing check</b>, because the only "
  "format contract that is machine-enforced is the date one. A wrong-format scoring input produces no "
  "error and no log - it produces a plausible-looking score on missing data. That is precisely the "
  "condition the founder identified: accurate grading and gap analysis are not possible when inputs are "
  "silently misread."))
S.append(PageBreak())

# ===== CONFIRMED ISSUES =====
S.append(Paragraph("3. Confirmed Issues (adversarially verified)",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
sevc=Counter((c.get('severity') or '?').split()[0].lower().strip('[]') for c in CANDS)
S.append(P(f"Of {len(CANDS)} candidates across the five lenses, {CNT.get('high_verified',15)} high-severity were probed "
  f"against live data; {len(CONF)} survived adversarial verification as real. Listed worst-first:"))
ci=[["#","Sev","Issue","Fix (summary)"]]
for i,c in enumerate(CONF,1):
    sev=san(c.get('severity','')).split()[0].strip('[]?')[:8]
    ci.append([str(i),sev,san(c.get('finding',''))[:240],san(c.get('fix',''))[:200]])
S.append(tbl([[Paragraph(esc(x),CELLB if r==0 else CELL) for x in row] for r,row in enumerate(ci)],
  [0.3*inch,0.62*inch,3.6*inch,2.38*inch],fontsize=7.0,hbg=RED))
S.append(PageBreak())

# ===== PROPOSED CANON =====
S.append(Paragraph("4. The Fix - a Scoring Data Contract (proposed canon)",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
S.append(P("The date model already proved the pattern works: a declared registry (DATE_SEMANTIC), a central "
  "normalizer (to_iso_date), a write-time gate that QUARANTINES rather than guesses (gate_date), and an "
  "auditor that checks the live data (Agent 16). Generalize it to every scoring input."))
S.append(Paragraph("The rule (hard, enforceable)",H2))
for b in [
 "ONE canonical key per scoring field - no aliases. Every producer and every consumer use it. The three "
 "composite weight vectors collapse to ONE definition, imported everywhere (kills weight-vector drift).",
 "A SCORING_CONTRACT registry declares, per field: canonical key, type (scalar/json/bool/enum), UNIT and "
 "range (0-100 / 0-1 / ratio / count), allowed enum set with casing, JSON shape, required-non-null flag, "
 "and the producing function. This is the machine-readable spec Q2 is missing.",
 "Writes pass through a normalizer that validates type/unit/range/enum. A value it cannot conform is "
 "QUARANTINED to a review queue - never silently defaulted. MISSING is represented as None and is "
 "DISTINGUISHABLE from a real 0; scoring formulas decide explicitly how to treat missing (skip + "
 "renormalize, or flag insufficient-data) - never let .get(k,0) or 0 smuggle it in as zero.",
 "AI-returned scalars are clamped to their declared range and AI enums are membership-checked before they "
 "enter any score (closes the unvalidated-AI-scalar hole and the AI-grade N-weight circularity).",
 "The contract is AUDITED on the data, not assumed - by the Scoring Contract Auditor below.",
]:
    S.append(Paragraph("- "+esc(b),BUL))
S.append(Spacer(1,6))
S.append(Paragraph("Example registry entries",H2))
reg=[["Field","Type","Unit / range","Enum / shape","Required","Producer"],
 ["gradient_strength","scalar","0-100","-","yes","compute_gradient_strength"],
 ["gradient_ratio","scalar","ratio 1-10x","-","yes","compute_gradient_strength"],
 ["first_timer_ratio","scalar","0-1 fraction","-","no","compute_dark_matter"],
 ["engagement_asymmetry","bool","0/1","-","no","score_topic"],
 ["nowtrendin_score","scalar","0-100","-","yes","compute_nowtrendin_score"],
 ["signal_stage","enum","-","BREAKOUT/STRONG/EMERGING/MARGINAL/MONITORING","yes","stage_of"],
 ["risk_stage","enum","-","ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT","yes","compute_market_signal"],
 ["platforms_active","json","list[str]","[...]","yes","score_topic"]]
S.append(tbl([[Paragraph(esc(c),CELLB if i==0 else CELL) for c in r] for i,r in enumerate(reg)],
  [1.35*inch,0.65*inch,1.0*inch,2.25*inch,0.6*inch,1.05*inch],fontsize=7.0,hbg=GREEN))
S.append(PageBreak())

# ===== GUARDRAIL =====
S.append(Paragraph("5. The Guardrail - Scoring Contract Auditor (Agent 17)",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
S.append(P("Read-only, in /monitor run_all, endpoint /monitor/scoringcontract - the exact pattern that "
  "worked for the Canonical Date Auditor (Agent 16), now for all scoring fields. It audits the DATA, so a "
  "violation is caught no matter which code path produced it, and new fields are auto-covered."))
S.append(Paragraph("What it checks",H2))
for b in [
 "For every field in SCORING_CONTRACT, across all live rows: TYPE conformance (scalar/json/bool/enum), "
 "UNIT/RANGE conformance (a 0-1 field never exceeds 1; a 0-100 field never exceeds 100), ENUM membership "
 "(with casing), and NON-NULL where the field is required.",
 "REQUIRED-but-NULL / 0 rate per field: a scoring input that is null or exactly 0 on an implausible share "
 "of rows is the silent-misread signature (this is what would have caught Positioning Concentration "
 "collapsing to a flat baseline).",
 "KEY-DRIFT / weight-vector divergence: assert the single composite weight vector is the one used on every "
 "path, and that producer keys equal consumer keys (no alias bridging).",
 "DISCOVERY: any scoring-shaped column NOT in the registry is flagged 'classify it' (warn) - so a new "
 "source or new component is covered automatically, exactly like the date auditor's *_date discovery.",
]:
    S.append(Paragraph("- "+esc(b),BUL))
S.append(Paragraph("Success vs error (so the audit gives genuine feedback)",H2))
se=[["State","Output"],
 ["SUCCESS","status=ok; 0 type/unit/enum violations; 0 required-but-null; 0 unregistered scoring columns; the single weight vector matches on every path."],
 ["ERROR (critical)","Names field + table + row count + examples: e.g. 'positioning_concentration: 84/88 rows = flat baseline 30.0 (missing-as-zero)'; 'ai_grade detection uses 7-comp weights incl N'."],
 ["ERROR (warn)","An unregistered scoring-shaped column (classify: add to SCORING_CONTRACT), or a producer/consumer key mismatch that is currently masked by a fallback."]]
S.append(tbl([[Paragraph(esc(c),CELLB if i==0 else CELL) for c in r] for i,r in enumerate(se)],
  [1.0*inch,5.9*inch],hbg=NAVY))
S.append(PageBreak())

# ===== ROADMAP =====
S.append(Paragraph("6. Remediation Roadmap",H1)); S.append(HRFlowable(width="100%",thickness=1,color=LINE,spaceAfter=8))
S.append(Paragraph("Quick wins - mechanical, low risk, ship now",H2))
for b in [
 "AI-Grade weights: drop N and renormalize to the engine's six-component vector - fixes BOTH the scale "
 "mismatch and the N-into-Gradient circularity (highest-value single fix; HIGH severity).",
 "engagement_asymmetry: read the producer's actual key (with the serve alias as fallback) on the scoring "
 "path in apply_calibration.",
 "AI scalars: clamp every AI-returned number to its declared range and membership-check AI enums before "
 "they enter a score; reject/flag partial JSON instead of defaulting components to 0.",
 "N-detail: add the three missing community-demand columns (or stop serving a stale N breakdown) so the "
 "served detail matches the N that was computed.",
 "Make the serve-time calibration swallow observable: log on failure instead of silent except: pass "
 "(keep the legitimate module-absent fallback, but never hide a real parse error).",
]:
    S.append(Paragraph("- "+esc(b),BUL))
S.append(Paragraph("Structural - gated by backtest-before-ship (these change WHICH data enters a score)",H2))
for b in [
 "Build the SCORING_CONTRACT registry + a write-time normalizer; replace s.get(k,0) or 0 on scoring paths "
 "with contract-validated reads that distinguish MISSING from real-zero.",
 "Consolidate the three composite weight vectors into one definition imported everywhere.",
 "Split risk_stage into one declared enum vocabulary (or namespace the two/three); reconcile tier / "
 "risk_stage / classification to one surfaced source of truth.",
 "Resolve the market detection/confidence single-column-two-formulas split and the WATCHLIST_TICKERS "
 "exact-string match that silently drops all company financials on a name drift.",
 "Ship the Scoring Contract Auditor (Agent 17) and add it to /monitor run_all; wire its findings into the "
 "nightly audit alongside the Canonical Date Auditor.",
]:
    S.append(Paragraph("- "+esc(b),BUL))
S.append(Spacer(1,8))
S.append(box([Paragraph("<b>Integrity note.</b> Most structural items change which inputs reach a score, "
  "so they MOVE scores and must pass the project's backtest-before-ship rule - validated against the "
  "held-out Wikipedia/GDELT referee, never auto-applied. The quick wins are mechanical and do not require "
  "a calibration backtest, except the AI-grade weight fix, which should be spot-checked because it changes "
  "graded values (correctly).",SMALL)],bg=colors.HexColor("#F3FAF8"),bc=GREEN))

def deco(c,doc):
    c.saveState(); c.setFont("Helvetica",7); c.setFillColor(GREY)
    c.drawString(0.8*inch,0.55*inch,"NowTrendIn - Scoring Data-Contract Audit - Confidential")
    c.drawRightString(7.7*inch,0.55*inch,f"Page {doc.page}")
    c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line(0.8*inch,0.7*inch,7.7*inch,0.7*inch); c.restoreState()

OUT=r"C:\Users\acinv\OneDrive\Desktop\NowTrendIn_Scoring_Data_Contract_Audit_2026-06-23.pdf"
doc=SimpleDocTemplate(OUT,pagesize=letter,topMargin=0.7*inch,bottomMargin=0.9*inch,leftMargin=0.8*inch,rightMargin=0.8*inch,
                      title="NowTrendIn Scoring Data-Contract Audit",author="Engineering Audit")
doc.build(S,onFirstPage=deco,onLaterPages=deco)
print("WROTE",OUT,os.path.getsize(OUT),"bytes")
