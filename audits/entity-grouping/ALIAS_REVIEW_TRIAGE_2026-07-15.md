# ENTITY-GROUPING — 559 Pending Candidates, TRIAGED for founder review

**2026-07-15 · engine v240 · fold LIVE (2 confirmed: conor + mcgregor -> conor_mcgregor)**

Triage is a REVIEW AID only — nothing below is confirmed or rejected until you rule.
Buckets:
- **A — likely CONFIRM (79)**: confidence >=0.80, clean 2-token canonical, alias unambiguous (one family).
- **B — NEEDS JUDGMENT (308)**: canonical looks like a headline fragment, or the alias is proposed into MULTIPLE families (one-canonical-per-alias — you must pick), or 3+-token canonical.
- **C — likely REJECT (172)**: confidence <0.50 or fewer than 3 shared titles (thin evidence).

Resolve: `POST /aliases/resolve {"id": N, "action": "confirm"|"reject"}` — or just tell me
your decisions (e.g. "confirm all A", "confirm ids 12,84", "reject bucket C") and I'll execute.

## A — LIKELY CONFIRM (79)

| id | alias (fragment) | canonical | conf | shared | ambig | sample shared headline |
|---|---|---|---|---|---|---|
| 103 | `hochul` | `kathy_hochul` | 0.99 | 5 |  | governor kathy hochul issued an executive order enacting a moratorium on the lar… |
| 117 | `inflation` | `inflation_data` | 0.99 | 5 |  | fed rate-hike bets mount before inflation data, warsh testimony - bloomberg.com |
| 164 | `jurassic` | `jurassic_park` | 0.99 | 8 |  | 'hero, legend, sweetheart': tributes to jurassic park actor sam neill, who has d… |
| 208 | `rejects` | `court_rejects` | 0.99 | 3 |  | high court rejects most of ‘dieselgate’ claims brought by 1.6m uk car owners |
| 210 | `semis` | `cup_semis` | 0.99 | 6 |  | lindsey graham death and world cup semis / reuters world news |
| 274 | `turkey` | `summit_turkey` | 0.99 | 5 |  | carney en route to saudi arabia following nato summit in turkey |
| 292 | `cuba` | `cuba_suffers` | 0.99 | 3 |  | cuba suffers second nationwide blackout in five days |
| 298 | `carmack` | `john_carmack` | 0.99 | 3 |  | "my 'microsoft will probably be a good steward of the brand' statement isn't agi… |
| 303 | `boyle` | `boyle_heights` | 0.99 | 3 |  | anger grows in boyle heights as warehouse fire leaves stench, flies and vermin i… |
| 304 | `qualley` | `margaret_qualley` | 0.99 | 4 |  | exclusive / jack antonoff and margaret qualley's marriage 'challenges' exposed b… |
| 626 | `evals` | `evals_llm` | 0.99 | 6 |  | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against decla… |
| 630 | `ollama` | `llm_ollama` | 0.99 | 10 |  | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-aug… |
| 636 | `fastapi` | `fastapi_llm` | 0.99 | 12 |  | 89himanshu-dwivedi/rag-chatbot streaming rag chatbot - fastapi, sse, semantic ca… |
| 638 | `langgraph` | `langgraph_llm` | 0.99 | 3 |  | batramayank106/multi-agent-resume-analyzer cv chacha — multi agent resume intell… |
| 642 | `langchain` | `langchain_llm` | 0.99 | 18 |  | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-aug… |
| 646 | `sheikh` | `sheikh_hamad` | 0.99 | 6 |  | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 651 | `kalshi` | `kalshi_traders` | 0.99 | 5 |  | inflation peaked in may as energy prices fell in june, kalshi traders think |
| 660 | `howe` | `gordie_howe` | 0.99 | 5 |  | gordie howe bridge set to open on july 27 |
| 664 | `paramountwarner` | `paramountwarner_bros` | 0.99 | 5 |  | 12 states challenge paramount-warner bros. discovery deal |
| 677 | `baldoni` | `justin_baldoni` | 0.99 | 11 |  | justin baldoni addresses blake lively lawsuit in video. 'we are healing' |
| 705 | `hassabis` | `demis_hassabis` | 0.99 | 4 |  | deepmind chief demis hassabis calls for us-led body to test ‘frontier’ ai models |
| 706 | `demis` | `demis_hassabis` | 0.99 | 4 |  | deepmind chief demis hassabis calls for us-led body to test ‘frontier’ ai models |
| 708 | `gordie` | `gordie_howe` | 0.99 | 6 |  | gordie howe bridge set to open on july 27 |
| 723 | `assassinate` | `assassinate_trump` | 0.99 | 3 |  | israel shared intelligence with us of iranian plot to assassinate trump, sources… |
| 728 | `hanged` | `woman_hanged` | 0.99 | 4 |  | last woman to be hanged in the uk pardoned 70 years on— ruth ellis, the last wom… |
| 761 | `procession` | `funeral_procession` | 0.99 | 5 |  | funeral procession for iran's late supreme leader ali khamenei in iraq / dw news |
| 768 | `sinks` | `boat_sinks` | 0.99 | 5 |  | 1 dead and 3 missing after boat sinks near alcatraz island |
| 781 | `ryanair` | `ryanair_plane` | 0.99 | 8 |  | 'if we die, we die together': wife of man nearly sucked out of ryanair plane spe… |
| 782 | `monuments` | `national_monuments` | 0.99 | 6 |  | president trump drastically shrinks grand staircase-escalante and bears ears nat… |
| 790 | `shortages` | `fuel_shortages` | 0.99 | 7 |  | jackdaw boss warns of winter fuel shortages if gas field not approved |
| 805 | `alleges` | `lawsuit_alleges` | 0.99 | 3 |  | musicians shortchanged by ai deals with labels, lawsuit alleges |
| 807 | `alcatraz` | `alcatraz_island` | 0.99 | 9 |  | 1 dead and 2 missing after pontoon boat fire near alcatraz island off san franci… |
| 808 | `nevada` | `nevada_governor` | 0.99 | 4 |  | 'i'm joe lombardo': nevada governor pulled over in traffic stop |
| 809 | `squawk` | `morning_squawk` | 0.99 | 6 |  | bank earnings, warsh heads to the hill, chipotle's mexico push and more in morni… |
| 812 | `arwa` | `arwa_mahdawi` | 0.99 | 3 |  | ali g is back. i really wish he wasn’t / arwa mahdawi |
| 813 | `bancshares` | `bancshares_inc` | 0.99 | 3 |  | federal reserve board issues enforcement action with employee of bank of eufaula… |
| 816 | `burry` | `michael_burry` | 0.99 | 3 |  | do not buy stocks! (michael burry’s final warning) |
| 817 | `mahdawi` | `arwa_mahdawi` | 0.99 | 3 |  | ali g is back. i really wish he wasn’t / arwa mahdawi |
| 846 | `reich` | `robert_reich` | 0.99 | 3 |  | the nato summit exposed the real source of trump’s power / robert reich |
| 850 | `hillsborough` | `hillsborough_law` | 0.99 | 5 |  | bill for hillsborough law set to be approved by mps |
| 852 | `clair` | `salsa_clair` | 0.99 | 4 |  | 2 victims of fatal shooting at salsa on st. clair identified, police say they kn… |
| 856 | `goldman` | `goldman_sachs` | 0.99 | 4 |  | goldman sachs limits prediction market betting for employees |
| 858 | `outage` | `network_outage` | 0.99 | 5 |  | australia news live: telstra warns of ‘secondary issue’ after yesterday’s networ… |
| 859 | `soaring` | `soaring_temperatures` | 0.99 | 5 |  | 11 die in spanish wildfire amid soaring temperatures |
| 863 | `straits` | `straits_times` | 0.99 | 8 |  | #showbiz: zizi kirana battles two months of insomnia after gruelling humanitaria… |
| 864 | `sachs` | `goldman_sachs` | 0.99 | 3 |  | goldman sachs limits prediction market betting for employees |
| 868 | `addictive` | `addictive_design` | 0.99 | 4 |  | eu accuses meta of failing to tackle mental health risks of ‘addictive design’ |
| 780 | `burnham` | `andy_burnham` | 0.977 | 51 |  | a big week for us banks and andy burnham |
| 273 | `apple` | `apple_sues` | 0.952 | 17 |  | apple sues openai alleging theft of top-secret information |
| 686 | `neill` | `sam_neill` | 0.952 | 17 |  | 'hero, legend, sweetheart': tributes to jurassic park actor sam neill, who has d… |
| 133 | `mcconnell` | `mitch_mcconnell` | 0.945 | 43 |  | ailing mitch mcconnell is preparing to return to work, scott jennings tells cnn … |
| 648 | `machinelearning` | `llm_machinelearning` | 0.932 | 11 |  | freeautomation-tech/agent-memory-kit memory patterns, context strategies, and pe… |
| 792 | `buffett` | `warren_buffett` | 0.921 | 9 |  | billionaire warren buffett stops donations to bill gates charity |
| 652 | `binface` | `count_binface` | 0.917 | 34 |  | a cunning stunt - can count binface win? |
| 213 | `anthropic` | `anthropic_claude` | 0.913 | 16 |  | 12122j/mcpvet mcp security scanner — vet a model context protocol server before … |
| 272 | `humanoid` | `humanoid_robots` | 0.913 | 8 |  | alibaba-affiliate ant group rushes into humanoid robots with a dozen deals in 18… |
| 666 | `sues` | `apple_sues` | 0.913 | 16 |  | apple sues openai alleging theft of top-secret information |
| 277 | `congo` | `congo_ebola` | 0.904 | 7 |  | congo ebola orphans struggle to rebuild life after parents’ death |
| 230 | `allstar` | `allstar_game` | 0.898 | 13 |  | 'one day in september' chronicles how baseball's all-star game was born |
| 132 | `nolan` | `christopher_nolan` | 0.896 | 19 |  | 'the odyssey' stars on being cast and working with christopher nolan |
| 200 | `cursor` | `codex_cursor` | 0.875 | 5 |  | favorpan/ai-tool-weekly-review structured weekly review for ai coding tools — an… |
| 772 | `iceinvolved` | `iceinvolved_shooting` | 0.875 | 5 |  | live updates: ice-involved shooting in maine kills one person - cnn |
| 746 | `warsh` | `kevin_warsh` | 0.868 | 14 |  | *the federal reserve fomc presser & rate decision / kevin warsh* |
| 123 | `grok` | `grok_build` | 0.852 | 4 |  | channely/ai-no-tun run chatgpt codex remote, grok build and other ai tools throu… |
| 787 | `buckle` | `columns_buckle` | 0.852 | 4 |  | live: new york building will be stabilized after columns buckle |
| 818 | `altman` | `sam_altman` | 0.852 | 4 |  | elon musk and sam altman spar on x after apple files openai lawsuit |
| 216 | `gemini` | `google_gemini` | 0.842 | 11 |  | akshay2266/isometric-mto-generator isometric drawing → automated mto generator: … |
| 783 | `erling` | `erling_haaland` | 0.831 | 20 |  | cold war steve on … erling haaland’s high-street invasion for norway v england |
| 201 | `doj` | `trump_doj` | 0.817 | 3 |  | 'whiff of jim crow:' yale students and faculty fight to stop deal with trump's d… |
| 267 | `thani` | `khalifa_thani` | 0.817 | 3 |  | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 295 | `singapore` | `singapore_temasek` | 0.817 | 3 |  | crypto still 'off the table' for singapore's temasek, four years after ftx flop |
| 653 | `coco` | `coco_gauff` | 0.817 | 3 |  | karolina muchova beats coco gauff in epic tie-break to reach wimbledon final |
| 656 | `mundial` | `del_mundial` | 0.817 | 12 |  | así ha sido la celebración de la familia real por el pase de españa a la final d… |
| 712 | `alltime` | `alltime_high` | 0.817 | 3 |  | june home sales disappoint as prices reach an all-time high |
| 714 | `llmsecurity` | `llm_llmsecurity` | 0.817 | 3 |  | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection ri… |
| 831 | `tankers` | `oil_tankers` | 0.817 | 6 |  | russian attacks kill 6, wound 29, as ukrainian forces target oil tankers |
| 842 | `salsa` | `salsa_clair` | 0.817 | 3 |  | 2 victims of fatal shooting at salsa on st. clair identified, police say they kn… |
| 821 | `generativeai` | `generativeai_llm` | 0.806 | 11 |  | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai too… |
| 833 | `modelcontextprotocol` | `mcp_modelcontextprotocol` | 0.804 | 19 |  | ahmedvnabil/humanitarian-mcp model context protocol server for humanitarian open… |

## B — NEEDS JUDGMENT (308)

| id | alias (fragment) | canonical | conf | shared | ambig | sample shared headline |
|---|---|---|---|---|---|---|
| 3 | `lindsey_graham` | `lindsey_graham_sudden` | 0.99 | 4 | x7 | after lindsey graham’s sudden death, conspiracy theories swirl online - the wash… |
| 8 | `new_york` | `york_highrise` | 0.99 | 5 |  | buckling support beams seen inside new york high-rise. #bbcnews |
| 14 | `lindsey` | `lindsey_graham_sister` | 0.99 | 25 | x13 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 19 | `lindsey` | `ally_lindsey` | 0.99 | 3 | x13 | trump pays tribute to ally lindsey graham after he dies from ‘sudden’ illness |
| 23 | `spain` | `spain_and_gibraltar` | 0.99 | 4 | x9 | border controls scrapped between spain and gibraltar |
| 26 | `spain` | `wildfires_southern_spain` | 0.99 | 4 | x9 | crews battle deadly wildfires in southern spain |
| 30 | `spain` | `spain_kill` | 0.99 | 5 | x9 | wildfires in heat - baked southern spain kill 12 |
| 49 | `semifinals` | `wimbledon_semifinals` | 0.99 | 5 | x3 | british wildcard arthur fery through to wimbledon semi-finals after stunning vic… |
| 72 | `england` | `england_and_wales` | 0.99 | 5 | x8 | homes for sale with stylish bedrooms in england and wales – in pictures |
| 76 | `america` | `latin_america` | 0.99 | 3 | x3 | does donald trump make latin america a good bet? |
| 80 | `widdecombe` | `widdecombe_murder_case` | 0.99 | 4 | x8 | ann widdecombe murder case: former conservative mp murder suspect released as po… |
| 81 | `widdecombe` | `minister_ann_widdecombe` | 0.99 | 7 | x8 | former conservative minister ann widdecombe dies aged 78 |
| 82 | `widdecombe` | `widdecombe_killing` | 0.99 | 3 | x8 | ann widdecombe killing: police investigating possible leftwing motivation |
| 104 | `shootings` | `fatal_shootings` | 0.99 | 4 | x2 | ice halts most traffic stops after fatal shootings |
| 105 | `shootings` | `deadly_shootings` | 0.99 | 6 | x2 | calls grow to abolish ice after deadly us shootings / aj #shorts |
| 106 | `trump_ally` | `trump_ally_dies` | 0.99 | 6 |  | influential sen. lindsey graham, a trump ally, dies after a sudden illness |
| 109 | `strait` | `strait_hormuz_open` | 0.99 | 6 | x5 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 126 | `ice_houston` | `killed_ice_houston` | 0.99 | 4 |  | dhs: man killed by ice in houston not target of operation |
| 127 | `britain` | `great_britain` | 0.99 | 3 | x5 | great britain’s grid operator issues another warning over power supplies in heat… |
| 145 | `senate` | `senate_term` | 0.99 | 8 | x8 | darline graham, sister of lindsey graham, chosen to fulfill remainder of his us … |
| 149 | `senate` | `maine_senate_candidate` | 0.99 | 3 | x8 | democrats search for maine senate candidate after allegations force platner out |
| 150 | `wimbledon` | `wimbledon_semifinals` | 0.99 | 5 |  | british wildcard arthur fery through to wimbledon semi-finals after stunning vic… |
| 151 | `wildfires` | `deadly_wildfires` | 0.99 | 5 | x4 | crews battle deadly wildfires in southern spain |
| 154 | `wildfires` | `wildfires_southern_spain` | 0.99 | 4 | x4 | crews battle deadly wildfires in southern spain |
| 155 | `southern_spain` | `wildfires_southern_spain` | 0.99 | 4 |  | crews battle deadly wildfires in southern spain |
| 161 | `deceptive_subscription` | `deceptive_subscription_practices` | 0.99 | 4 | x2 | new york city becomes first in the us to ban deceptive subscription practices |
| 162 | `deceptive_subscription` | `ban_deceptive_subscription` | 0.99 | 4 | x2 | new york city becomes first in the us to ban deceptive subscription practices |
| 163 | `ban_deceptive` | `ban_deceptive_subscription` | 0.99 | 4 |  | new york city becomes first in the us to ban deceptive subscription practices |
| 226 | `tapestry_arrives` | `bayeux_tapestry_arrives` | 0.99 | 6 |  | bayeux tapestry arrives at british museum in dead of night after top-secret jour… |
| 233 | `blanche_confirmation` | `blanche_confirmation_hearing` | 0.99 | 5 |  | live: senators question acting attorney general todd blanche at confirmation hea… |
| 236 | `simo_steps` | `fidji_simo_steps` | 0.99 | 4 |  | fidji simo steps down from leading openai’s agi work due to illness |
| 253 | `mariska_hargitay` | `mariska_hargitay_host` | 0.99 | 3 |  | 2026 emmy nominations announced, mariska hargitay to host awards show |
| 255 | `meta` | `meta_glasses` | 0.99 | 7 | x4 | lorde says ray-ban meta ai glasses are ‘not sexy’ |
| 258 | `israel` | `israel_settlers` | 0.99 | 12 | x5 | an american politician is blocked by israeli settlers in the west bank |
| 262 | `israel` | `detained_israel` | 0.99 | 5 | x5 | congressman detained by israeli settlers in the west bank |
| 268 | `election` | `election_agency` | 0.99 | 6 | x4 | reports: trump fires members of federal election agency |
| 269 | `election` | `election_commission` | 0.99 | 9 | x4 | trump fires democrats on election commission, republican resigns |
| 270 | `election` | `fires_election` | 0.99 | 5 | x4 | trump fires election assistance commission members ahead of midterms |
| 271 | `election` | `trump_fires_election` | 0.99 | 5 | x4 | trump fires election assistance commission members ahead of midterms |
| 275 | `ebola` | `congo_ebola` | 0.99 | 8 | x2 | congo ebola orphans struggle to rebuild life after parents’ death |
| 276 | `ebola` | `ebola_outbreak` | 0.99 | 13 | x2 | africa cdc says ebola outbreak is “fastest-growing ever”; after 600 deaths since… |
| 278 | `white_house` | `white_house_ufc` | 0.99 | 5 | x2 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighti… |
| 284 | `platner` | `democrat_graham_platner` | 0.99 | 4 | x10 | democrat graham platner suspends campaign for key us senate race after assault a… |
| 285 | `platner` | `platner_officially` | 0.99 | 5 | x10 | as platner officially ends senate bid, volunteers warn replacement must back sam… |
| 296 | `bipartisan` | `bipartisan_housing_bill` | 0.99 | 8 | x2 | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 297 | `bipartisan` | `bipartisan_housing` | 0.99 | 8 | x2 | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 299 | `declares_iran` | `trump_declares_iran` | 0.99 | 7 |  | hegseth cancels trip to israel after trump declares iran ceasefire ‘over’ |
| 306 | `usiran` | `usiran_war` | 0.99 | 4 | x2 | has the us-iran war restarted? / bbc newscast |
| 616 | `bezos` | `bezos_blue_origin` | 0.99 | 3 | x2 | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 617 | `bezos` | `bezos_blue` | 0.99 | 3 | x2 | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 622 | `widdecombe_death` | `ann_widdecombe_death` | 0.99 | 13 |  | aberdeen university investigates employee over social media posts celebrating an… |
| 623 | `platner_suspends` | `graham_platner_suspends` | 0.99 | 8 |  | breaking: graham platner suspends campaign for maine senate race amid sexual ass… |
| 628 | `fatally` | `fatally_shot_ice` | 0.99 | 12 | x3 | 'he did not deserve to be reduced to a headline': son of man fatally shot by ice… |
| 631 | `officially_withdraws` | `platner_officially_withdraws` | 0.99 | 4 |  | graham platner officially withdraws candidacy for us senate in maine |
| 632 | `nlp` | `nlp_python` | 0.99 | 8 | x3 | aakash15-semwal/semantic-codebase-search-engine semantic search engine for pytho… |
| 633 | `nlp` | `llm_nlp` | 0.99 | 6 | x3 | agentdynarq/rag-pipeline a retrieval-augmented generation (rag) pipeline from sc… |
| 634 | `nlp` | `nlp_openai` | 0.99 | 3 | x3 | baaabaei/finetuning-whisper fine-tuning openai's whisper model for speech-to-tex… |
| 645 | `wally` | `wally_funk` | 0.99 | 3 | x2 | wally funk death: oldest woman to travel into space dies at 87 |
| 658 | `ann_widdecombe` | `minister_ann_widdecombe` | 0.99 | 7 | x2 | former conservative minister ann widdecombe dies aged 78 |
| 659 | `ann_widdecombe` | `ann_widdecombe_death` | 0.99 | 13 | x2 | aberdeen university investigates employee over social media posts celebrating an… |
| 669 | `graham_platner` | `breaking_graham_platner` | 0.99 | 5 | x5 | breaking: graham platner dropped out of the u.s. senate race. maine democrats ha… |
| 671 | `graham_platner` | `graham_platner_officially` | 0.99 | 5 | x5 | graham platner officially drops from maine senate race after sex assault claim, … |
| 676 | `house_ufc` | `white_house_ufc` | 0.99 | 5 |  | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighti… |
| 679 | `platner_drops` | `graham_platner_drops` | 0.99 | 7 |  | graham platner drops maine senate bid |
| 683 | `nato` | `nato_chief` | 0.99 | 7 | x4 | from 'dear donald' to 'trump trillion': inside nato chief mark rutte's u.s. stra… |
| 684 | `nato` | `nato_allies` | 0.99 | 6 | x4 | 'don't fool with us': nato allies put on a united front as they prepare to meet … |
| 692 | `bayeux` | `bayeux_tapestry` | 0.99 | 9 | x2 | after almost 1,000 years, the bayeux tapestry is back on english soil |
| 695 | `python_rag` | `python_rag_retrievalaugmentedgeneration` | 0.99 | 14 | x2 | aryansharmagithub/auditrag rag answers you can verify — citations, faithfulness … |
| 707 | `ayatollah` | `ayatollah_ali_khamenei` | 0.99 | 6 |  | iran buries supreme leader ayatollah ali khamenei |
| 713 | `widdecombe_murder` | `widdecombe_murder_case` | 0.99 | 4 |  | ann widdecombe murder case: former conservative mp murder suspect released as po… |
| 720 | `tapestry` | `bayeux_tapestry_arrives` | 0.99 | 6 | x3 | bayeux tapestry arrives at british museum in dead of night after top-secret jour… |
| 722 | `tapestry` | `tapestry_arrives` | 0.99 | 6 | x3 | bayeux tapestry arrives at british museum in dead of night after top-secret jour… |
| 725 | `wildfires_southern` | `wildfires_southern_spain` | 0.99 | 4 |  | crews battle deadly wildfires in southern spain |
| 729 | `fires_election` | `trump_fires_election` | 0.99 | 5 |  | trump fires election assistance commission members ahead of midterms |
| 731 | `diarrhea` | `diarrhea_parasite` | 0.99 | 9 | x2 | 31 states are reporting cases of ‘explosive diarrhea’ parasite as outbreak conti… |
| 732 | `khalifa` | `hamad_bin_khalifa` | 0.99 | 5 | x3 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 735 | `india_tourists` | `india_tourists_killed` | 0.99 | 5 |  | 15 indian tourists killed when a speedboat capsizes in southern vietnam |
| 742 | `wildfire` | `wildfire_smoke` | 0.99 | 5 | x3 | canada wildfire smoke to spread across the us - here’s what to expect |
| 745 | `bezos_blue` | `bezos_blue_origin` | 0.99 | 3 |  | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 756 | `ufc` | `white_house_ufc` | 0.99 | 5 | x3 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighti… |
| 757 | `ufc` | `house_ufc` | 0.99 | 5 | x3 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighti… |
| 758 | `ufc` | `ufc_event` | 0.99 | 3 | x3 | eight charged over alleged conspiracy to attack white house ufc event |
| 763 | `wales` | `england_and_wales` | 0.99 | 5 |  | homes for sale with stylish bedrooms in england and wales – in pictures |
| 764 | `bipartisan_housing` | `bipartisan_housing_bill` | 0.99 | 8 |  | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 767 | `sen_lindsey` | `sen_lindsey_graham` | 0.99 | 33 |  | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey … |
| 774 | `farage` | `farage_resignation` | 0.99 | 3 | x5 | reeves to approve farage’s resignation, saying ‘if he wants to spend summer argu… |
| 778 | `parasite` | `diarrheacausing_parasite` | 0.99 | 6 | x2 | a diarrhea-causing parasite infects more than 1,000 in the u.s. |
| 786 | `maine_senate` | `maine_senate_candidate` | 0.99 | 3 | x2 | democrats search for maine senate candidate after allegations force platner out |
| 788 | `manhattan` | `manhattan_highrise` | 0.99 | 3 |  | manhattan high-rise is still unstable after columns buckle, forcing evacuations |
| 791 | `court_justices` | `supreme_court_justices` | 0.99 | 4 |  | knives out at us supreme court as justices’ squabbles go public |
| 810 | `cnbc_daily` | `cnbc_daily_open` | 0.99 | 9 |  | cnbc daily open: a chip off the ai block |
| 820 | `democrat_gazette` | `arkansas_democrat_gazette` | 0.99 | 5 |  | america's first 250 years / arkansas democrat gazette |
| 825 | `bonnie` | `bonnie_tyler_singer` | 0.99 | 4 | x4 | bonnie tyler, singer famed for ‘total eclipse of the heart,’ dies at 75 |
| 826 | `bonnie` | `bonnie_tyler` | 0.99 | 32 | x4 | 'total eclipse of the heart' and four other essential bonnie tyler songs |
| 827 | `pmqs` | `final_pmqs` | 0.99 | 7 |  | keir starmer greeted with applause as he wraps up his final pmqs as uk prime min… |
| 835 | `bonnie_tyler` | `bonnie_tyler_singer` | 0.99 | 4 | x2 | bonnie tyler, singer famed for ‘total eclipse of the heart,’ dies at 75 |
| 838 | `manuscripts` | `manuscripts_from_ucla` | 0.99 | 3 | x2 | california man steals historic chinese manuscripts from ucla, using fake names, … |
| 847 | `prairie` | `house_the_prairie` | 0.99 | 6 |  | 'little house on the prairie' boss on netflix show's woke backlash, moving towns… |
| 851 | `hargitay_host` | `mariska_hargitay_host` | 0.99 | 3 |  | 2026 emmy nominations announced, mariska hargitay to host awards show |
| 853 | `closes_strait` | `closes_strait_hormuz` | 0.99 | 7 |  | analysis: us bombs iranian port cities as irgc closes strait of hormuz |
| 637 | `senator_lindsey` | `senator_lindsey_graham` | 0.96 | 22 |  | "great american, patriot, friend, fearless leader": us officials and world leade… |
| 143 | `senate` | `maine_senate` | 0.954 | 36 | x8 | bernie sanders joins calls for platner to withdraw from maine senate race |
| 83 | `widdecombe` | `widdecombe_death` | 0.941 | 13 | x8 | ann widdecombe death latest: police launch murder investigation - bbc |
| 721 | `tapestry` | `bayeux_tapestry` | 0.941 | 13 | x3 | after almost 1,000 years, the bayeux tapestry is back on english soil |
| 682 | `nato` | `nato_summit` | 0.938 | 37 | x4 | carney en route to saudi arabia following nato summit in turkey |
| 85 | `widdecombe` | `ann_widdecombe_death` | 0.937 | 12 | x8 | ann widdecombe death latest: police launch murder investigation - bbc |
| 681 | `nato` | `nato_leaders` | 0.937 | 12 | x4 | danish pm says greenland is 'not for sale' as trump joins nato leaders in turkey |
| 84 | `widdecombe` | `widdecombe_murder` | 0.936 | 35 | x8 | 'widdecombe murder inquiry' and 'strike norse' |
| 239 | `darline` | `darline_graham` | 0.927 | 10 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 288 | `platner` | `platner_suspends` | 0.927 | 10 | x10 | breaking: graham platner suspends campaign for maine senate race amid sexual ass… |
| 689 | `ceasefire` | `ceasefire_with_iran` | 0.927 | 10 |  | nato leaders meet in ankara as us ceasefire with iran teeters |
| 711 | `iran_trade` | `iran_trade_strikes` | 0.927 | 10 |  | cnbc daily open: mideast tensions on the boil again as u.s., iran trade strikes |
| 147 | `senate` | `senate_race` | 0.923 | 37 | x8 | 6 potential replacements for graham platner if he drops out of senate race - the… |
| 50 | `semifinals` | `cup_semifinals` | 0.921 | 9 | x3 | england defeats norway for world cup semifinals spot |
| 222 | `cnbc` | `cnbc_daily` | 0.921 | 9 | x2 | cnbc daily open: a chip off the ai block |
| 107 | `strait` | `strait_hormuz` | 0.92 | 97 | x5 | 'don't talk about it': trump tells journalists to stop asking about strait of ho… |
| 86 | `widdecombe` | `ann_widdecombe` | 0.916 | 92 | x8 | andy burnham calls for ‘serious review’ of mp security after ann widdecombe murd… |
| 221 | `cnbc` | `cnbc_daily_open` | 0.913 | 8 | x2 | cnbc daily open: a chip off the ai block |
| 779 | `parasite` | `diarrhea_parasite` | 0.913 | 8 | x2 | cyclospora, the ‘explosive diarrhea’ parasite, cases reported in at least 31 sta… |
| 9 | `lindsey` | `lindsey_graham` | 0.912 | 126 | x13 | "great american, patriot, friend, fearless leader": us officials and world leade… |
| 102 | `araujo` | `lorenzo_salgado_araujo` | 0.904 | 7 |  | "a government that conceals its identity cannot demand perfect recognition from … |
| 114 | `blockade` | `naval_blockade` | 0.904 | 7 | x4 | iran live updates: us carries out latest round of strikes, resumes naval blockad… |
| 283 | `platner` | `graham_platner_suspends` | 0.904 | 7 | x10 | breaking: graham platner suspends campaign for maine senate race amid sexual ass… |
| 667 | `graham_platner` | `graham_platner_suspends` | 0.904 | 7 | x5 | breaking: graham platner suspends campaign for maine senate race amid sexual ass… |
| 775 | `farage` | `nigel_farage` | 0.902 | 34 | x5 | a timeline of nigel farage’s £5mn gift and his return to politics |
| 785 | `maine_senate` | `maine_senate_race` | 0.9 | 20 | x2 | a defiant platner exits maine senate race |
| 819 | `senate_race` | `maine_senate_race` | 0.9 | 20 |  | a defiant platner exits maine senate race |
| 1 | `lindsey_graham` | `lindsey_graham_death` | 0.898 | 13 | x7 | donald trump suggests there was no foul play in lindsey graham’s death amid cons… |
| 206 | `strait_hormuz` | `closes_strait_hormuz` | 0.891 | 6 | x2 | analysis: us bombs iranian port cities as irgc closes strait of hormuz |
| 643 | `singer_bonnie` | `singer_bonnie_tyler` | 0.891 | 6 |  | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 670 | `graham_platner` | `graham_platner_drops` | 0.891 | 6 | x5 | graham platner drops maine senate bid |
| 797 | `declares` | `trump_declares_iran` | 0.891 | 6 | x2 | oil surges as trump declares iran deal 'over' |
| 798 | `declares` | `declares_iran` | 0.891 | 6 | x2 | oil surges as trump declares iran deal 'over' |
| 823 | `bonnie` | `singer_bonnie` | 0.891 | 6 | x4 | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 730 | `diarrhea` | `explosive_diarrhea` | 0.886 | 17 | x2 | 31 states are reporting cases of ‘explosive diarrhea’ parasite as outbreak conti… |
| 751 | `blanche` | `todd_blanche` | 0.886 | 17 | x3 | all about todd blanche: at best, misleading; at worst, disingenuous |
| 228 | `semifinal` | `cup_semifinal` | 0.884 | 11 | x2 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 11 | `lindsey` | `lindsey_graham_dies` | 0.881 | 16 | x13 | 'trump whisperer' lindsey graham dies suddenly / abc news |
| 655 | `quarterfinal` | `cup_quarterfinal` | 0.881 | 16 | x2 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 4 | `lindsey_graham` | `lindsey_graham_sister` | 0.88 | 21 | x7 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 98 | `bayeux_tapestry` | `bayeux_tapestry_arrives` | 0.875 | 5 |  | bayeux tapestry arrives at british museum in dead of night after top-secret jour… |
| 122 | `strait_of_hormuz` | `strait_hormuz_open` | 0.875 | 5 | x2 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 204 | `claude` | `anthropic_claude` | 0.875 | 15 | x4 | 12122j/mcpvet mcp security scanner — vet a model context protocol server before … |
| 207 | `strait_hormuz` | `strait_hormuz_open` | 0.875 | 5 | x2 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 215 | `codex` | `codex_cursor` | 0.875 | 5 | x2 | favorpan/ai-tool-weekly-review structured weekly review for ai coding tools — an… |
| 771 | `pleads` | `pleads_not_guilty` | 0.875 | 10 | x2 | abu trica pleads not guilty before a us federal court |
| 867 | `creed` | `creed_black_flag` | 0.875 | 5 | x3 | assassin's creed black flag resynced - a remake worthy of the wait |
| 27 | `spain` | `spain_wildfire` | 0.87 | 19 | x9 | 'we escaped spanish wildfire, but our friends lost their lives' |
| 146 | `senate` | `maine_senate_race` | 0.87 | 19 | x8 | bernie sanders joins calls for platner to withdraw from maine senate race |
| 31 | `spain` | `southern_spain` | 0.868 | 14 | x9 | at least 11 dead in southern spain wildfire amid heatwave |
| 649 | `inference` | `llm_inference` | 0.859 | 47 | x2 | adityaguhaa/nexusagent-mac turn your mac into an autonomous ai researcher using … |
| 286 | `platner` | `graham_platner` | 0.858 | 59 | x10 | 'this movement was never about one person': maine democrats look to move on from… |
| 10 | `lindsey` | `lindsey_graham_death` | 0.852 | 12 | x13 | donald trump suggests there was no foul play in lindsey graham’s death amid cons… |
| 13 | `lindsey` | `lindsey_graham_de` | 0.852 | 4 | x13 | lindsey graham dead at 71 |
| 24 | `spain` | `trade_with_spain` | 0.852 | 4 | x9 | can trump really cut off trade with spain? |
| 79 | `widdecombe` | `ann_widdecombe_de` | 0.852 | 4 | x8 | ann widdecombe death latest: police launch murder investigation - bbc |
| 112 | `blockade` | `blockade_iran` | 0.852 | 8 | x4 | asx rises after us reimposes naval blockade on iran — as it happened |
| 144 | `senate` | `senate_seat` | 0.852 | 8 | x8 | graham platner, controversial maine us senate seat candidate, off ballot |
| 153 | `wildfires` | `wildfires_southern` | 0.852 | 4 | x4 | crews battle deadly wildfires in southern spain |
| 287 | `platner` | `breaking_graham_platner` | 0.852 | 4 | x10 | breaking: graham platner dropped out of the u.s. senate race. maine democrats ha… |
| 290 | `platner` | `graham_platner_officially` | 0.852 | 4 | x10 | graham platner officially drops from maine senate race after sex assault claim, … |
| 305 | `usiran` | `renewed_usiran` | 0.852 | 4 | x2 | renewed us-iran war is hitting gulf countries hard |
| 618 | `platner_officially` | `graham_platner_officially` | 0.852 | 4 | x2 | graham platner officially drops from maine senate race after sex assault claim, … |
| 675 | `hormuz_open` | `strait_hormuz_open` | 0.852 | 4 |  | iran war: us claims strait of hormuz is 'open' amid strikes |
| 697 | `nigel_farage` | `nigel_farage_clacton` | 0.852 | 4 |  | britain backs count binface to beat nigel farage in clacton by-election, poll sh… |
| 734 | `khalifa` | `bin_khalifa` | 0.852 | 4 | x3 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 750 | `blanche` | `blanche_confirmation_hearing` | 0.852 | 4 | x3 | live: senators question acting attorney general todd blanche at confirmation hea… |
| 832 | `bin_khalifa` | `hamad_bin_khalifa` | 0.852 | 4 |  | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 861 | `assassin` | `assassin_creed` | 0.852 | 4 | x2 | assassin's creed: why pop culture is hooked to pirates |
| 866 | `creed` | `assassin_creed` | 0.852 | 4 | x3 | assassin's creed: why pop culture is hooked to pirates |
| 17 | `lindsey` | `sen_lindsey` | 0.844 | 26 | x13 | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey … |
| 87 | `france` | `tour_france` | 0.842 | 11 | x2 | cooling logistics more important than tactics at tour de france / new straits ti… |
| 202 | `claude` | `chatgpt_claude` | 0.837 | 7 | x4 | 988hj7tczd-oss/awesome-ai-tools-ranking 🏆 ai 工具实时排行榜 — 200+ 模型用户投票驱动 ai-agents a… |
| 223 | `chatgpt` | `chatgpt_claude` | 0.837 | 7 | x2 | 988hj7tczd-oss/awesome-ai-tools-ranking 🏆 ai 工具实时排行榜 — 200+ 模型用户投票驱动 ai-agents a… |
| 834 | `bonnie_tyler` | `singer_bonnie_tyler` | 0.837 | 7 | x2 | 'heartbroken' catherine zeta-jones leads tributes to singer bonnie tyler |
| 21 | `lindsey` | `sen_lindsey_graham` | 0.832 | 27 | x13 | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey … |
| 282 | `platner` | `platner_drops` | 0.831 | 10 | x10 | graham platner drops out of maine senate race after sexual assault accusation |
| 140 | `argentina` | `england_argentina` | 0.828 | 13 | x7 | argentina's message to england: be ready. #worldcup #england #argentina #bbcnews |
| 71 | `england` | `england_norway` | 0.817 | 3 | x8 | the high-flying england vs. norway world cup bet that's got everyone talking |
| 111 | `strait` | `strait_of_hormuz` | 0.817 | 105 | x5 | 'don't talk about it': trump tells journalists to stop asking about strait of ho… |
| 116 | `vows` | `denmark_vows_defend` | 0.817 | 3 |  | denmark pm vows to defend greenland after trump revives push for u.s. control |
| 129 | `britain` | `britain_first_financial` | 0.817 | 3 | x5 | south sea bubble: the shoemaker’s son who sparked britain’s first financial cris… |
| 152 | `wildfires` | `spain_wildfires` | 0.817 | 9 | x4 | 'this landscape is completely charred': inside the village at epicentre of spain… |
| 291 | `platner` | `platner_officially_withdraws` | 0.817 | 3 | x10 | graham platner officially withdraws candidacy for us senate in maine |
| 619 | `platner_officially` | `platner_officially_withdraws` | 0.817 | 3 | x2 | graham platner officially withdraws candidacy for us senate in maine |
| 620 | `justices` | `supreme_court_justices` | 0.817 | 3 | x2 | knives out at us supreme court as justices’ squabbles go public |
| 621 | `justices` | `court_justices` | 0.817 | 3 | x2 | knives out at us supreme court as justices’ squabbles go public |
| 650 | `inference` | `inference_llm` | 0.817 | 3 | x2 | jajmangold/fni8-serve w8a8 (int8 dp4a) inference server for nvidia volta / cmp 1… |
| 749 | `blanche` | `blanche_confirmation` | 0.817 | 6 | x3 | blanche confirmation ‘far from a certain thing’: fmr. federal prosecutor preview… |
| 753 | `screenings` | `world_cup_screenings` | 0.817 | 3 | x2 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 754 | `screenings` | `cup_screenings` | 0.817 | 3 | x2 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 770 | `pleads` | `hearn_pleads` | 0.817 | 3 | x2 | alleged reflecting pool vandal david hearn pleads not guilty; lawyer calls him '… |
| 793 | `denmark` | `denmark_vows_defend` | 0.817 | 3 |  | denmark pm vows to defend greenland after trump revives push for u.s. control - … |
| 828 | `assassin_creed` | `assassin_creed_black` | 0.817 | 3 |  | all swords in assassin's creed black flag resynced and how to get them |
| 865 | `creed` | `assassin_creed_black` | 0.817 | 3 | x3 | assassin's creed black flag resynced - a remake worthy of the wait |
| 99 | `korea` | `south_korea` | 0.811 | 20 | x3 | anne’s royal meet and greet with a robot during south korea tour |
| 15 | `lindsey` | `senator_lindsey_graham` | 0.81 | 17 | x13 | "great american, patriot, friend, fearless leader": us officials and world leade… |
| 743 | `wildfire` | `spain_wildfire` | 0.81 | 17 | x3 | 'we escaped spanish wildfire, but our friends lost their lives' |
| 148 | `senate` | `senate_campaign` | 0.802 | 8 | x8 | dem. graham plattner suspends senate campaign. what happens now? |
| 240 | `fifa` | `fifa_world_cup` | 0.8 | 21 |  | "we were too sloppy technically": mbappe rues france's shortcomings after fifa w… |
| 100 | `korea` | `korea_times` | 0.793 | 10 | x3 | 100 university of seoul students embark on overseas study tours - the korea time… |
| 289 | `platner` | `graham_platner_drops` | 0.793 | 5 | x10 | graham platner drops out of maine senate race after sexual assault accusation |
| 28 | `spain` | `spain_belgium` | 0.783 | 7 | x9 | live: fans gather in brussels to watch spain v belgium world cup match |
| 61 | `iran` | `blockade_iran` | 0.783 | 7 | x13 | asx rises after us reimposes naval blockade on iran — as it happened |
| 12 | `lindsey` | `senator_lindsey` | 0.78 | 16 | x13 | "great american, patriot, friend, fearless leader": us officials and world leade… |
| 739 | `khamenei` | `khamenei_funeral` | 0.778 | 9 | x4 | ali khamenei funeral: iran bids farewell to longtime supreme leader |
| 101 | `korea` | `the_korea_times` | 0.774 | 11 | x3 | 100 university of seoul students embark on overseas study tours - the korea time… |
| 293 | `africa` | `south_africa` | 0.769 | 17 | x2 | another noakhali man shot dead in south africa |
| 32 | `epstein` | `epstein_files` | 0.76 | 4 |  | blanche faces grilling on epstein files, $1.8b fund & more in ag hearing |
| 67 | `england` | `norway_england` | 0.76 | 8 | x8 | cold war steve on … erling haaland’s high-street invasion for norway v england |
| 93 | `rag` | `rag_react` | 0.76 | 6 | x8 | 1killermouse/poker-mind-gto-lab ai-assisted chinese texas hold'em gto trainer wi… |
| 94 | `rag` | `rag_semanticsearch` | 0.76 | 4 | x8 | dephekt/cci-blackbook-mcp mcp server for semantic search over scanned / image-he… |
| 125 | `yamal` | `lamine_yamal` | 0.76 | 4 |  | lamine yamal está na final da copa do mundo. |
| 174 | `llm` | `generativeai_llm` | 0.76 | 10 | x22 | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai too… |
| 205 | `claude` | `claude_desktop` | 0.76 | 4 | x4 | mienetic/mnema 🧠 mnema — long-term memory for ai via mcp × vector db. solves the… |
| 227 | `semifinal` | `world_cup_semifinal` | 0.76 | 14 | x2 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 235 | `agentic` | `agentic_workflow` | 0.76 | 6 | x2 | canadiancowboy/a2x ai-native programming language and runtime. sigma isa, omega … |
| 625 | `finetuning` | `finetuning_llm` | 0.76 | 4 |  | baaabaei/fine-tuninng-qwen-2.5-vl fine-tuning qwen 2.5 vision-language model for… |
| 627 | `fatally` | `fatally_shoots` | 0.76 | 8 | x3 | an ice officer fatally shoots a mexican national in houston during an attempted … |
| 693 | `bayeux` | `bayeux_tapestry_arrives` | 0.76 | 4 | x2 | bayeux tapestry arrives at british museum in dead of night after top-secret jour… |
| 709 | `ai_llm` | `generativeai_llm` | 0.76 | 10 | x2 | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai too… |
| 824 | `bonnie` | `singer_bonnie_tyler` | 0.76 | 6 | x4 | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 654 | `quarterfinal` | `world_cup_quarterfinal` | 0.742 | 16 | x2 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 624 | `hollywood` | `hollywood_reporter` | 0.739 | 7 |  | christopher nolan addresses ‘the odyssey’ backlash, explains why film uses moder… |
| 7 | `lindsey_graham` | `sen_lindsey_graham` | 0.734 | 22 | x7 | bloomberg this weekend / sen. lindsey graham dead, centcom launches strikes on i… |
| 97 | `rag` | `rag_retrievalaugmentedgeneration_semanticsearch` | 0.731 | 5 | x8 | devbratghosh/enterprise-rag-assistant-v1.0 enterprise-grade retrieval-augmented … |
| 48 | `fifa_world` | `fifa_world_cup` | 0.728 | 18 |  | barcelona reach verbal agreement to sign germany international who did not make … |
| 250 | `world_cup` | `cup_semifinal` | 0.725 | 8 | x10 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 51 | `semifinals` | `world_cup_semifinals` | 0.722 | 11 | x3 | england, argentina, france and spain set for world cup semifinals |
| 5 | `lindsey_graham` | `senator_lindsey_graham` | 0.72 | 14 | x7 | "great american, patriot, friend, fearless leader": us officials and world leade… |
| 44 | `ukraine` | `ukraine_targets` | 0.714 | 3 | x4 | gas queues grow as ukraine targets russia's fuel supply |
| 46 | `ukraine` | `ukraine_license` | 0.714 | 3 | x4 | trump offers ukraine license to manufacture patriots |
| 47 | `ukraine` | `ukraine_strikes` | 0.714 | 3 | x4 | american-made technology guiding ukraine's strikes into russia - cbs news |
| 56 | `iran` | `blockade_iran_ports` | 0.714 | 3 | x13 | oil rises as u.s. continues to strike tehran, reinstates blockade of iranian por… |
| 115 | `blockade` | `blockade_iran_ports` | 0.714 | 3 | x4 | trump says u.s. military will reimpose blockade on iranian ports - the washingto… |
| 176 | `llm` | `llm_ollama` | 0.714 | 6 | x22 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-aug… |
| 265 | `russia` | `russia_strike` | 0.714 | 3 | x3 | people flee as russian strike hits near ukraine coffee shop |
| 687 | `ann_widdecombe_de` | `ann_widdecombe_death` | 0.714 | 3 |  | ann widdecombe death latest: police launch murder investigation - bbc |
| 717 | `blockade_iran` | `blockade_iran_ports` | 0.714 | 3 |  | oil rises as u.s. continues to strike tehran, reinstates blockade of iranian por… |
| 733 | `khalifa` | `khalifa_thani` | 0.714 | 3 | x3 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 752 | `trump_threatens` | `trump_threatens_iran` | 0.714 | 3 |  | trump threatens iran after ayatollah ali khamenei's funeral saw open calls for h… |
| 759 | `holloway` | `max_holloway` | 0.714 | 3 |  | conor mcgregor and max holloway meet again at ufc 329 |
| 773 | `farage` | `nigel_farage_clacton` | 0.714 | 3 | x5 | britain backs count binface to beat nigel farage in clacton by-election, poll sh… |
| 740 | `norway` | `norway_england` | 0.702 | 7 |  | get 40/1 odds on kane or haaland to have a shot in norway vs england |
| 2 | `lindsey_graham` | `lindsey_graham_dies` | 0.699 | 11 | x7 | 'trump whisperer' lindsey graham dies suddenly / abc news |
| 218 | `openai` | `llm_openai` | 0.699 | 11 | x3 | aiplaza-app/aiplaza-prompts open prompt gallery (writing, marketing, business, c… |
| 70 | `england` | `argentina_england` | 0.694 | 4 | x8 | argentina vs england schedule, tv channel for world cup match today |
| 96 | `rag` | `python_rag_retrievalaugmentedgeneration` | 0.694 | 8 | x8 | aryansharmagithub/auditrag rag answers you can verify — citations, faithfulness … |
| 108 | `strait` | `closes_strait_hormuz` | 0.694 | 4 | x5 | breaking: us bombs iranian port cities as irgc closes strait of hormuz |
| 113 | `blockade` | `hormuz_blockade` | 0.694 | 4 | x4 | iran-us war latest: trump threatens to hit civilian targets in iran as us resume… |
| 121 | `strait_of_hormuz` | `closes_strait_hormuz` | 0.694 | 4 | x2 | iran closes strait of hormuz, us launches fresh strikes |
| 124 | `china` | `china_economy` | 0.694 | 4 |  | china's economy picks up in june on rebounding u.s. exports, analysts say |
| 185 | `llm` | `llm_prompt` | 0.694 | 4 | x22 | harveyya/intent-engineering intent engineering: the engineering discipline for t… |
| 266 | `russia` | `russia_strikes` | 0.694 | 4 | x3 | 'felt like the whole building had been lifted up': ukraine residents recount rus… |
| 760 | `sinner` | `jannik_sinner` | 0.694 | 4 |  | jannik sinner beats alexander zverev to win wimbledon again |
| 748 | `bellingham` | `jude_bellingham` | 0.683 | 5 |  | bellingham best player at world cup - rooney |
| 738 | `khamenei` | `ali_khamenei` | 0.676 | 6 | x4 | ali khamenei funeral: iran bids farewell to longtime supreme leader |
| 190 | `llm` | `llm_python` | 0.668 | 8 | x22 | charumathid380/ai-chatbot a minimal conversational ai app using streamlit for th… |
| 196 | `ai_agent` | `hermes_agent` | 0.668 | 8 | x8 | aaron-arn/samaritain samaritain — a self-improving ai agent by aaron dalibard. t… |
| 74 | `england` | `england_argentina` | 0.665 | 9 | x8 | england vs. argentina: a football rivalry full of history |
| 203 | `claude` | `claude_code` | 0.656 | 96 | x4 | 0ss/unc 🦥 your ai agent, but lazy in the good way. writes less, spends less, shi… |
| 29 | `spain` | `spain_wildfires` | 0.645 | 6 | x9 | british expats feared dead during spanish wildfires as residents flee popular to… |
| 68 | `england` | `argentina_and_england` | 0.645 | 4 | x8 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 110 | `strait` | `closes_strait` | 0.645 | 4 | x5 | breaking: us bombs iranian port cities as irgc closes strait of hormuz |
| 134 | `india` | `india_tourists` | 0.645 | 4 |  | indian tourists among 15 killed as speedboat capsizes in vietnam |
| 138 | `argentina` | `argentina_and_england` | 0.645 | 4 | x7 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 178 | `llm` | `llm_machinelearning` | 0.645 | 6 | x22 | freeautomation-tech/agent-memory-kit memory patterns, context strategies, and pe… |
| 231 | `zverev` | `alexander_zverev` | 0.645 | 4 |  | arthur fery's wimbledon run ended by alexander zverev in semi-finals |
| 245 | `world_cup` | `cup_semifinals` | 0.645 | 5 | x10 | england, argentina, france and spain set for world cup semifinals |
| 263 | `samsung` | `samsung_galaxy` | 0.645 | 4 |  | samsung galaxy s26 ultra review: its huge screen blocks shoulder surfers from sp… |
| 690 | `semanticsearch` | `rag_semanticsearch` | 0.645 | 3 |  | dephekt/cci-blackbook-mcp mcp server for semantic search over scanned / image-he… |
| 701 | `llm_llm` | `evals_llm` | 0.645 | 3 | x7 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against decla… |
| 806 | `ali_khamenei` | `ayatollah_ali_khamenei` | 0.645 | 3 |  | thousands attend final funeral prayers for iran's ayatollah ali khamenei |
| 678 | `hermes` | `hermes_agent` | 0.622 | 7 |  | elevatormusic/hermes-classic-gold-pack classic gold theme + noir neko pets + cus… |
| 724 | `haaland` | `erling_haaland` | 0.62 | 13 |  | cutting off erling haaland is key but norway are not just a one-man team / emma … |
| 199 | `ai_agent` | `autonomous_agent` | 0.618 | 12 | x8 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability… |
| 92 | `rag` | `retrievalaugmented_generation_rag` | 0.614 | 5 | x8 | avaneeshravi21/personal-rag-chatbot a retrieval-augmented generation (rag) chatb… |
| 307 | `us_and_iran` | `iran_trade_strikes` | 0.614 | 5 | x2 | live updates: trump says ceasefire ‘over’ after us and iran trade strikes - cnn |
| 841 | `retrievalaugmented` | `retrievalaugmented_generation_rag` | 0.614 | 5 |  | agentdynarq/rag-pipeline a retrieval-augmented generation (rag) pipeline from sc… |
| 57 | `iran` | `iran_war` | 0.602 | 28 | x13 | 'forever war' risk, us sea drones & more: military experts on iran war |
| 73 | `england` | `england_world_cup` | 0.596 | 9 | x8 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 137 | `argentina` | `argentina_england` | 0.596 | 3 | x7 | argentina vs england schedule, tv channel for world cup match today |
| 170 | `llm` | `models_llm` | 0.596 | 3 | x22 | fareedkhan-dev/glm-5.2-in-c glm-5.2, a 744 billion parameter mixture of experts … |
| 173 | `llm` | `llm_localfirst` | 0.596 | 3 | x22 | luoziyan100/lumen 独立研究者的 ai 研究工作台:读论文,把报告写进真实工作区 / local-first ai research workb… |
| 219 | `openai` | `openai_codex` | 0.596 | 3 | x3 | busybee3333/sol-governed-codex sol-governed multi-agent coding workflow for open… |
| 249 | `world_cup` | `world_cup_semifinal` | 0.596 | 9 | x10 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 629 | `fatally` | `ice_fatally` | 0.596 | 3 | x3 | backlash erupts after ice fatally shoots texas father |
| 694 | `for_llm` | `llm_inference` | 0.596 | 3 |  | johnscheuer/inference-cost-calculator cost analysis tool for llm inference: $/to… |
| 784 | `tuchel` | `thomas_tuchel` | 0.596 | 3 |  | la paradoja de thomas tuchel: el planteamiento que dibuja en la pizarra no es la… |
| 848 | `rag_retrievalaugmentedgeneration` | `python_rag_retrievalaugmentedgeneration` | 0.596 | 6 | x2 | djagdalebing/rag-engine hybrid-retrieval rag from first principles: bm25 + dense… |
| 189 | `llm` | `fastapi_llm` | 0.587 | 5 | x22 | cris904fl/rag-practice pipeline rag (retrieval-augmented generation) de práctica… |
| 217 | `claude_ai` | `claude_code` | 0.587 | 5 |  | alikwan/claude-code-agent-team battle-tested multi-agent dev team for claude cod… |
| 91 | `rag` | `python_rag` | 0.581 | 33 | x8 | aayushi-jha2018/mini-rag-pipeline a small, self-contained retrieval-augmented ge… |
| 615 | `us_and_iran` | `iran_trade` | 0.581 | 11 | x2 | ceasefire cracks as us and iran trade airstrikes / abc news |
| 184 | `llm` | `langchain_llm` | 0.568 | 7 | x22 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-aug… |
| 198 | `ai_agent` | `coding_agent` | 0.565 | 10 | x8 | 10hq/grok-webui browser workspace for grok coding agent — thinking timeline, too… |
| 849 | `rag_retrievalaugmentedgeneration` | `rag_retrievalaugmentedgeneration_semanticsearch` | 0.559 | 3 | x2 | gpat22/langgraph-multi-agent-research-assistant designed and developed a multi-a… |
| 662 | `us_senate` | `senate_race` | 0.551 | 4 | x3 | barabak: what's in a name? a confounding u.s. senate race |
| 52 | `google` | `google_gemini` | 0.546 | 5 |  | anuragv28/enterprise-ai-knowledge-hub enterprise ai knowledge hub using retrieva… |
| 33 | `agent` | `ice_agent` | 0.53 | 4 | x11 | colombian national killed by ice agent during operation in maine |
| 242 | `agentic_ai` | `agentic_workflow` | 0.53 | 3 |  | di37/evalsurfer skill-first, agent-native evaluation protocol for ai apps agent-… |
| 264 | `russia` | `russia_oil` | 0.53 | 5 | x3 | russian oil sanctions: relief for india as us cuts proposed tariff from 500% to … |
| 211 | `ai_tools` | `llm_tools` | 0.518 | 6 | x2 | chefcohen/corroborate-mcp honest claim corroboration for ai agents (mcp server):… |
| 90 | `rag` | `rag_pipeline` | 0.512 | 4 | x8 | aayushi-jha2018/mini-rag-pipeline a small, self-contained retrieval-augmented ge… |
| 64 | `iran` | `iran_attacks` | 0.507 | 3 | x13 | trump demands payment to protect gulf nations from iranian attacks |
| 680 | `retrieval` | `retrieval_augmented_generation` | 0.503 | 5 |  | jidnyasadthakre07/researchgpt-hybrid-rag-system production-ready hybrid rag appl… |
| 39 | `agent` | `agent_memory` | 0.501 | 7 | x11 | bobcatsfan33/loomdb an agent-native database. sessions are branches an agent can… |
| 209 | `ai_agents` | `llm_agents` | 0.501 | 7 |  | alexcard3/honest-signal a method for keeping ai-assisted research honest: pre-re… |

## C — LIKELY REJECT (172)

| id | alias (fragment) | canonical | conf | shared | ambig | sample shared headline |
|---|---|---|---|---|---|---|
| 6 | `lindsey_graham` | `darline_graham_lindsey` | 0.99 | 2 | x7 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 16 | `lindsey` | `graham_lindsey_graham` | 0.99 | 2 | x13 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 18 | `lindsey` | `darline_graham_lindsey` | 0.99 | 2 | x13 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 20 | `lindsey` | `graham_lindsey` | 0.99 | 2 | x13 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 77 | `america` | `america_financial` | 0.99 | 2 | x3 | storm clouds gather over america's financial supremacy |
| 78 | `america` | `america_financial_supremacy` | 0.99 | 2 | x3 | storm clouds gather over america's financial supremacy |
| 89 | `suvs` | `suvs_are_growing` | 0.99 | 2 |  | britain’s cars and suvs are growing bigger – but there is a way to stop this dea… |
| 119 | `meta_used` | `meta_used_tag` | 0.99 | 2 |  | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 120 | `ai_to_tag` | `meta_used_tag` | 0.99 | 2 |  | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 128 | `britain` | `britain_grid` | 0.99 | 2 | x5 | great britain’s grid operator issues another warning over power supplies in heat… |
| 130 | `britain` | `britain_grid_operator` | 0.99 | 2 | x5 | great britain’s grid operator issues another warning over power supplies in heat… |
| 131 | `britain` | `great_britain_grid` | 0.99 | 2 | x5 | great britain’s grid operator issues another warning over power supplies in heat… |
| 139 | `argentina` | `argentina_match` | 0.99 | 2 | x7 | egypt files complaint over referee of argentina match |
| 142 | `senate` | `senate_nominee` | 0.99 | 2 | x8 | here's who's vying to replace graham platner as maine democratic senate nominee … |
| 165 | `heatwave` | `supplies_heatwave` | 0.99 | 2 | x2 | great britain’s grid operator issues another warning over power supplies in heat… |
| 166 | `heatwave` | `power_supplies_heatwave` | 0.99 | 2 | x2 | great britain’s grid operator issues another warning over power supplies in heat… |
| 167 | `used_ai` | `meta_used_tag` | 0.99 | 2 | x2 | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 168 | `used_ai` | `meta_used` | 0.99 | 2 | x2 | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 169 | `darline_graham` | `darline_graham_lindsey` | 0.99 | 2 |  | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 224 | `chatgpt` | `chatgpt_work` | 0.99 | 2 | x2 | chatgpt work |
| 229 | `vet_israel` | `committee_vet_israel` | 0.99 | 2 |  | abc and sbs need ‘oversight’ committee to vet israel coverage, jillian segal tel… |
| 237 | `texas` | `texas_man` | 0.99 | 2 |  | son of texas man killed by ice agent: 'he did not deserve to die' |
| 238 | `darline` | `darline_graham_lindsey` | 0.99 | 2 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 252 | `world_cup` | `spain_world_cup` | 0.99 | 2 | x10 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 254 | `meta` | `took_meta` | 0.99 | 2 | x4 | the lawyer who took on meta – and won – podcast |
| 256 | `meta` | `meta_used_tag` | 0.99 | 2 | x4 | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 257 | `meta` | `meta_used` | 0.99 | 2 | x4 | meta used ai to tag workers who took [maternity or disability] leave to be laid … |
| 259 | `israel` | `aid_to_israel` | 0.99 | 2 | x5 | jeffries opposes bid to cut off aid to israel as democrats split |
| 260 | `israel` | `aid_israel` | 0.99 | 2 | x5 | jeffries opposes bid to cut off aid to israel as democrats split |
| 279 | `white_house` | `white_house_helipad` | 0.99 | 2 | x2 | trump shares new details on ‘beautiful’ white house helipad project |
| 281 | `thailand` | `pitch_discovered_thailand` | 0.99 | 2 | x2 | new dinosaur species as long as cricket pitch discovered in thailand |
| 300 | `takeover` | `rival_takeover_bid` | 0.99 | 2 | x2 | easyjet accepts rival takeover bid from us investor apollo |
| 301 | `takeover` | `rival_takeover` | 0.99 | 2 | x2 | easyjet accepts rival takeover bid from us investor apollo |
| 302 | `gang_ringleader` | `grooming_gang_ringleader` | 0.99 | 2 |  | mahmood to close loophole blocking deportation of rochdale grooming gang ringlea… |
| 639 | `ringleader` | `grooming_gang_ringleader` | 0.99 | 2 | x2 | mahmood to close loophole blocking deportation of rochdale grooming gang ringlea… |
| 640 | `ringleader` | `gang_ringleader` | 0.99 | 2 | x2 | mahmood to close loophole blocking deportation of rochdale grooming gang ringlea… |
| 644 | `wally` | `wally_funk_aviation` | 0.99 | 2 | x2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 647 | `postgresql` | `postgresql_python_rag` | 0.99 | 2 |  | shri30a/longhornai ai-powered campus assistant for ut austin built with next.js,… |
| 657 | `republic_japan` | `islamic_republic_japan` | 0.99 | 2 |  | [video] trump at nato meeting: "we had 111 missiles shot by the islamic republic… |
| 665 | `farage_resigns` | `nigel_farage_resigns` | 0.99 | 2 |  | nigel farage resigns as mp |
| 673 | `britain_grid` | `britain_grid_operator` | 0.99 | 2 | x2 | great britain’s grid operator issues another warning over power supplies in heat… |
| 674 | `britain_grid` | `great_britain_grid` | 0.99 | 2 | x2 | great britain’s grid operator issues another warning over power supplies in heat… |
| 688 | `rival_takeover` | `rival_takeover_bid` | 0.99 | 2 |  | easyjet accepts rival takeover bid from us investor apollo |
| 691 | `discovered_thailand` | `pitch_discovered_thailand` | 0.99 | 2 |  | new dinosaur species as long as cricket pitch discovered in thailand |
| 696 | `python_rag` | `postgresql_python_rag` | 0.99 | 2 | x2 | shri30a/longhornai ai-powered campus assistant for ut austin built with next.js,… |
| 715 | `supremacy` | `financial_supremacy` | 0.99 | 2 | x2 | storm clouds gather over america's financial supremacy |
| 716 | `supremacy` | `america_financial_supremacy` | 0.99 | 2 | x2 | storm clouds gather over america's financial supremacy |
| 718 | `funk_aviation` | `wally_funk_aviation` | 0.99 | 2 | x2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 719 | `funk_aviation` | `funk_aviation_pioneer` | 0.99 | 2 | x2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 726 | `wally_funk` | `wally_funk_aviation` | 0.99 | 2 |  | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 755 | `great_britain` | `great_britain_grid` | 0.99 | 2 |  | great britain’s grid operator issues another warning over power supplies in heat… |
| 762 | `11yearold` | `11yearold_girl` | 0.99 | 2 |  | protests engulf indian state after rape and murder of 11-year-old girl |
| 765 | `soar` | `expected_to_soar` | 0.99 | 2 | x2 | cancer cases expected to soar worldwide, who report finds |
| 766 | `soar` | `expected_soar` | 0.99 | 2 | x2 | cancer cases expected to soar worldwide, who report finds |
| 776 | `farage` | `nigel_farage_resigns` | 0.99 | 2 | x5 | nigel farage resigns as mp |
| 777 | `farage` | `farage_resigns` | 0.99 | 2 | x5 | nigel farage resigns as mp |
| 789 | `killings` | `ice_killings` | 0.99 | 2 |  | congressman seth magaziner's floor speech on the latest ice killings. |
| 795 | `new_fed` | `new_fed_chair` | 0.99 | 2 | x2 | trump's new fed chair just crushed gold, silver, bitcoin |
| 799 | `graham_lindsey_graham` | `lindsey_graham_sister` | 0.99 | 2 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 800 | `graham_lindsey_graham` | `darline_graham_lindsey` | 0.99 | 2 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 801 | `graham_lindsey` | `lindsey_graham_sister` | 0.99 | 2 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 802 | `graham_lindsey` | `darline_graham_lindsey` | 0.99 | 2 | x2 | darline graham , lindsey graham sister , to be sworn in as senator / what to kno… |
| 804 | `supplies_heatwave` | `power_supplies_heatwave` | 0.99 | 2 |  | great britain’s grid operator issues another warning over power supplies in heat… |
| 814 | `eufaula` | `bank_eufaula` | 0.99 | 2 |  | federal reserve board issues enforcement action with employee of bank of eufaula… |
| 829 | `financial_supremacy` | `america_financial_supremacy` | 0.99 | 2 |  | storm clouds gather over america's financial supremacy |
| 830 | `america_financial` | `america_financial_supremacy` | 0.99 | 2 |  | storm clouds gather over america's financial supremacy |
| 836 | `hacks_breaks` | `hacks_breaks_record` | 0.99 | 2 |  | 'hacks' breaks record for most emmy nominations for a comedy in a single year |
| 837 | `revamp` | `troubled_revamp` | 0.99 | 2 |  | crews draining the lincoln memorial reflecting pool again as part of troubled re… |
| 840 | `hynix` | `hynix_rises` | 0.99 | 2 |  | sk hynix rises 13% in nasdaq debut. chairman tells cnbc 'demand is enormous' |
| 854 | `highrise_risk` | `highrise_risk_collapse` | 0.99 | 2 |  | live: mamdani and hochul speak after manhattan high-rise at risk of collapse was… |
| 862 | `spain_world` | `spain_world_cup` | 0.99 | 2 |  | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 25 | `spain` | `spain_sanchez` | 0.76 | 2 | x9 | spanish pm sanchez condemns predecessor's racist remarks on french football team |
| 55 | `iran` | `iran_tensions` | 0.76 | 2 | x13 | kalshi traders think gas prices will stay higher for longer as u.s.-iran tension… |
| 188 | `llm` | `langgraph_llm` | 0.76 | 2 | x22 | cksharma11/ai_fundamental_demo a zero-api-key classroom demo showing how client/… |
| 220 | `openai` | `nlp_openai` | 0.76 | 2 | x3 | messuuu/ask-multiple-pdfs-clean rag-based chatbot to query multiple pdf document… |
| 280 | `thailand` | `discovered_thailand` | 0.76 | 2 | x2 | new dinosaur species as long as cricket pitch discovered in thailand |
| 294 | `africa` | `south_africa_world` | 0.76 | 2 | x2 | south africa world cup midfielder adams dies aged 25 |
| 741 | `bélgica` | `españa_bélgica` | 0.76 | 2 |  | españa - bélgica, el partido de cuartos del mundial en imágenes |
| 744 | `wildfire` | `wildfire_kills` | 0.76 | 2 | x3 | fast-spreading wildfire kills at least 12 in southern spain |
| 794 | `senate_campaign` | `maine_senate_campaign` | 0.76 | 2 |  | graham platner ends maine senate campaign after sexual assault allegation |
| 796 | `new_fed` | `fed_chair` | 0.76 | 2 | x2 | trump's new fed chair just crushed gold, silver, bitcoin |
| 839 | `manuscripts` | `historic_china_manuscripts` | 0.76 | 2 | x2 | california man steals historic chinese manuscripts from ucla, using fake names, … |
| 45 | `ukraine` | `ukraine_make` | 0.645 | 2 | x4 | can ukraine make patriot missiles? |
| 136 | `argentina` | `loss_to_argentina` | 0.645 | 2 | x7 | egyptian fa questions ‘fairness’ of loss to argentina amid refereeing furore |
| 186 | `llm` | `llm_llmsecurity` | 0.645 | 2 | x22 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection ri… |
| 234 | `agentic` | `agentic_coding` | 0.645 | 2 | x2 | arturkorb3/cli-agent zero-dependency, provider-neutral cli coding agent for node… |
| 261 | `israel` | `killed_israel_strike` | 0.645 | 2 | x5 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 641 | `muchova` | `muchova_beats_gauff` | 0.645 | 2 |  | muchova beats gauff to reach wimbledon final |
| 668 | `graham_platner` | `democrat_graham_platner` | 0.645 | 2 | x5 | democrat graham platner suspends campaign for key us senate race in maine |
| 703 | `llm_llm` | `llm_llmsecurity` | 0.645 | 2 | x7 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection ri… |
| 747 | `infantino` | `gianni_infantino` | 0.645 | 2 |  | gianni infantino hints at expansion to 64-team world cup before 2030 event |
| 769 | `gibraltar` | `spain_and_gibraltar` | 0.645 | 2 |  | border controls scrapped between spain and gibraltar |
| 811 | `viking` | `viking_row` | 0.645 | 2 |  | norway fan reveals why he refuses to do 'stupid' viking row |
| 815 | `españa` | `francia_españa` | 0.645 | 2 |  | francia - españa, cable rojo y cable azul |
| 822 | `francia` | `francia_españa` | 0.645 | 2 |  | francia - españa, cable rojo y cable azul |
| 857 | `reinstates` | `trump_reinstates` | 0.645 | 2 |  | oil prices leap and stocks fall as trump reinstates hormuz blockade on iranian s… |
| 860 | `assassin` | `assassin_creed_black` | 0.645 | 2 | x2 | assassin’s creed black flag resynced review – bootyful high seas adventure, now … |
| 40 | `agent` | `agent_autonomous` | 0.576 | 2 | x11 | imomkar/autodoc-agent an autonomous ai proposal generation agent using python, f… |
| 63 | `iran` | `attacks_iran` | 0.576 | 2 | x13 | us attacks iran and tehran retaliates across the middle east, threatening a retu… |
| 118 | `trump_fires` | `trump_fires_election` | 0.576 | 2 |  | trump fires election board democrats - the hill |
| 672 | `deschamps` | `didier_deschamps` | 0.576 | 2 |  | 'extremely happy' deschamps gets the farewell game no-one wants |
| 685 | `fined` | `media_fined` | 0.576 | 2 |  | virgin media fined after hanging up on customers trying to cancel contracts |
| 727 | `yankee_stadium` | `yankee_stadium_concert` | 0.576 | 2 |  | chaos outside jay-z's yankee stadium concert after security breach delays |
| 737 | `khamenei` | `khamenei_burial` | 0.576 | 2 | x4 | iranians vow to stand firm as khamenei burial nears |
| 803 | `mou` | `trump_says_mou` | 0.576 | 2 |  | trump says mou is 'over', calls iranian leaders 'scum' following latest strikes |
| 855 | `lindsey_graham_de` | `lindsey_graham_death` | 0.576 | 2 |  | lindsey graham death and world cup semis / reuters world news |
| 58 | `iran` | `trump_iran` | 0.53 | 2 | x13 | a dangerous blind spot in donald trump’s iran war strategy |
| 75 | `switzerland` | `argentina_switzerland` | 0.53 | 2 |  | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 135 | `argentina` | `argentina_switzerland` | 0.53 | 2 | x7 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 157 | `trump` | `trump_iran` | 0.53 | 2 | x5 | a dangerous blind spot in donald trump’s iran war strategy |
| 180 | `llm` | `evals_llm` | 0.53 | 2 | x22 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against decla… |
| 251 | `world_cup` | `cup_semis` | 0.53 | 2 | x10 | lindsey graham death and world cup semis / reuters world news |
| 635 | `tour_france` | `tour_de_france_2026` | 0.53 | 2 |  | tour de france 2026: stage 11 updates as riders head from vichy to nevers – live |
| 736 | `khamenei` | `ayatollah_ali_khamenei` | 0.53 | 2 | x4 | iran buries supreme leader ayatollah ali khamenei |
| 59 | `iran` | `new_strikes_iran` | 0.497 | 4 | x13 | trump backs down on hormuz toll, launches new strikes on iran / abc news |
| 62 | `iran` | `iran_conflict` | 0.497 | 2 | x13 | middle east experts assess latest escalation in u.s.-iran conflict |
| 69 | `england` | `england_and_argentina` | 0.497 | 2 | x8 | england and argentina renew football’s fiercest grudge match |
| 88 | `france` | `france_spain` | 0.497 | 2 | x2 | france vs spain: the 2026 world cup’s best attack meets its best defence - opta … |
| 141 | `argentina` | `england_and_argentina` | 0.497 | 2 | x7 | england and argentina renew football’s fiercest grudge match |
| 193 | `ai_agent` | `llm_agent` | 0.497 | 4 | x8 | navig-me/local-marketing local-only, agent-agnostic marketing/outreach skill: sq… |
| 214 | `codex` | `openai_codex` | 0.497 | 2 | x2 | busybee3333/sol-governed-codex sol-governed multi-agent coding workflow for open… |
| 60 | `iran` | `strikes_iran` | 0.49 | 22 | x13 | live updates: us launches fourth night of strikes on iran and restarts naval blo… |
| 160 | `trump` | `trump_administration` | 0.49 | 8 | x5 | eu rejects trump administration claims that icc threatens us sovereignty |
| 156 | `trump` | `trump_threatens` | 0.488 | 6 | x5 | hurricane trump threatens to blow china off course |
| 43 | `agent` | `autonomous_agent` | 0.486 | 7 | x11 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability… |
| 37 | `agent` | `agent_skill` | 0.484 | 4 | x11 | hanlulong/econ-paper-review-skill ai referee reports for economics papers — an a… |
| 191 | `llm` | `llm_openai` | 0.482 | 5 | x22 | himynameisdavidkim/prompt-triwizard-skill llm prompt engineering for agent pipel… |
| 702 | `llm_llm` | `llm_tools` | 0.482 | 5 | x7 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, discipli… |
| 34 | `agent` | `multi_agent` | 0.478 | 8 | x11 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability… |
| 192 | `ai_agent` | `multi_agent` | 0.478 | 8 | x8 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability… |
| 244 | `world_cup` | `world_cup_2026` | 0.477 | 9 | x10 | adityaraj1969/nexus-ai nexus ai is a next-generation smart stadium platform desi… |
| 171 | `llm` | `tools_llm` | 0.472 | 4 | x22 | bufferbrew/craftsman agent-discipline toolkit for claude code — minimal-diff cod… |
| 36 | `agent` | `agent_skills` | 0.47 | 15 | x11 | adamhjort/lovable-porting-agent a model-neutral agent skill and cli toolkit for … |
| 182 | `llm` | `cache_llm` | 0.462 | 4 | x22 | codewithfourtix/ember a from-scratch llm inference engine in rust: run a qwen2.5… |
| 699 | `llm_llm` | `llm_evaluation` | 0.459 | 6 | x7 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against decla… |
| 159 | `trump` | `trump_wants` | 0.453 | 2 | x5 | hiltzik: trump wants to let companies make fewer disclosures, thus keeping inves… |
| 232 | `workflow` | `agentic_workflow` | 0.453 | 2 |  | nothingnesses/agent-scaffold scaffold a repeatable agent workflow (front-load co… |
| 241 | `github` | `github_actions` | 0.453 | 2 |  | adding new workflows in github actions |
| 243 | `world_cup` | `world_cup_semifinals` | 0.453 | 4 | x10 | england, argentina, france and spain set for world cup semifinals |
| 35 | `agent` | `llm_agent` | 0.448 | 3 | x11 | ancs21/codemode-workers expose any api to an llm agent as two sandboxed mcp tool… |
| 95 | `rag` | `rag_retrievalaugmentedgeneration` | 0.448 | 6 | x8 | ansham1/ai_research_assistant_agent autonomous ai research assistant that can an… |
| 181 | `llm` | `llm_tools` | 0.445 | 4 | x22 | ansham1/ai_research_assistant_agent autonomous ai research assistant that can an… |
| 172 | `llm` | `local_llm` | 0.442 | 8 | x22 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability… |
| 38 | `agent` | `hermes_agent` | 0.438 | 3 | x11 | mr-ds-ml-85/strikedb strikedb is a unified database architecture for the ai era,… |
| 158 | `trump` | `trump_accounts` | 0.438 | 2 | x5 | trump accounts program offers $1,000 seed for every eligible child born during h… |
| 179 | `llm` | `llm_security` | 0.438 | 5 | x22 | ai-blockchain-ventures/agentverify open-source security scanner for ai agents — … |
| 195 | `ai_agent` | `agent_skill` | 0.438 | 3 | x8 | atdy/maoxuan-product-agent 从《矛盾论》《实践论》完整推理结构蒸馏的中文产品决策 agent skill，支持 codex、claud… |
| 661 | `us_senate` | `senate_seat` | 0.438 | 2 | x3 | lindsey graham’s sister sworn in to fill his us senate seat |
| 710 | `ai_llm` | `llm_python` | 0.438 | 3 | x2 | charumathid380/ai-chatbot a minimal conversational ai app using streamlit for th… |
| 704 | `llm_llm` | `llm_inference` | 0.433 | 5 | x7 | cognizenorg/compatcanary one command to test openai-compatible apis for streamin… |
| 248 | `world_cup` | `england_world_cup` | 0.431 | 4 | x10 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 212 | `ai_tools` | `tools_llm` | 0.429 | 3 | x2 | bufferbrew/craftsman agent-discipline toolkit for claude code — minimal-diff cod… |
| 53 | `iran` | `iran_trade_strikes` | 0.425 | 2 | x13 | us and iran trade strikes, dispute whether hormuz is open |
| 54 | `iran` | `iran_strikes` | 0.425 | 4 | x13 | iran strikes, lindsey graham, apple takes openai to court and more in morning sq… |
| 663 | `us_senate` | `senate_campaign` | 0.425 | 2 | x3 | graham platner ends u.s. senate campaign in maine |
| 183 | `llm` | `llm_agents` | 0.415 | 4 | x22 | can llm agents develop precognition? |
| 197 | `ai_agent` | `agent_memory` | 0.415 | 4 | x8 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, discipli… |
| 41 | `agent` | `coding_agent` | 0.406 | 4 | x11 | hogan-tech/brand-loom open-source marketing skills that run on any model — with … |
| 247 | `world_cup` | `2026_world_cup` | 0.406 | 2 | x10 | france vs. spain odds, prediction, time: 2026 world cup semifinal picks from exp… |
| 187 | `llm` | `llm_inference` | 0.402 | 12 | x22 | codewithfourtix/ember a from-scratch llm inference engine in rust: run a qwen2.5… |
| 175 | `llm` | `llm_agent` | 0.399 | 2 | x22 | ancs21/codemode-workers expose any api to an llm agent as two sandboxed mcp tool… |
| 698 | `llm_llm` | `llm_agent` | 0.399 | 2 | x7 | aerkn1/jobhunt stateless automated job discovery and scoring service based on yo… |
| 246 | `world_cup` | `fifa_world_cup` | 0.395 | 4 | x10 | "we were too sloppy technically": mbappe rues france's shortcomings after fifa w… |
| 42 | `agent` | `multi_agent_systems` | 0.392 | 2 | x11 | abhinoob1501/ramanujan autonomous ml research engineer - a multi-agent system th… |
| 843 | `agent_ai` | `multi_agent` | 0.389 | 4 | x3 | ovsilya/multi-agent-support-platform slack-native multi-agent ai support platfor… |
| 700 | `llm_llm` | `llm_security` | 0.383 | 3 | x7 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection ri… |
| 194 | `ai_agent` | `agent_skills` | 0.379 | 7 | x8 | 0ss/unc 🦥 your ai agent, but lazy in the good way. writes less, spends less, shi… |
| 177 | `llm` | `llm_evaluation` | 0.367 | 3 | x22 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against decla… |
| 844 | `agent_ai` | `agent_memory` | 0.357 | 2 | x3 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, discipli… |
| 225 | `ai_coding` | `coding_agent` | 0.353 | 2 |  | kopon1/gen-z lowkey just works. your ai coding agent, but it says less and write… |
| 845 | `agent_ai` | `autonomous_agent` | 0.353 | 2 | x3 | axisrobo/aep aep: agent event protocol — open async event layer for agents, tool… |
| 65 | `iran` | `iran_trade` | 0.351 | 2 | x13 | us and iran trade strikes, dispute whether hormuz is open |
