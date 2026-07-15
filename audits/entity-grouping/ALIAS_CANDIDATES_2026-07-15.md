# ENTITY-GROUPING — Alias Candidate Audit Dump (founder review)

**Date:** 2026-07-15 · **Engine:** v239 · **Flag:** ENTITY_GROUPING=OFF (nothing groups until you confirm + flip)
**Board:** audits/board/BOARD_entity-grouping_2026-07-15.md — Option A approved; this dump IS the pre-flip measurement gate.

## How this was produced
- Universe: the RAW served /scores working set (3,049 tokenizable keys; un-grouped).
- Candidate = key whose tokens are a STRICT SUBSET of a 2-4 token key's tokens,
  corroborated by >=2 shared distinct raw_signals titles (evidence-stamped).
- 2,068 containment pairs existed; ALL were checked (exhaustive — no silent cap).
  1,507 were skipped for having no shared evidence; 561 are proposed below as 'pending'.
- Confidence = shared-title overlap vs the smaller key's distinct-title count (internal formula).

## Summary — 561 pending candidates in 381 canonical families
- confidence >= 0.80: **352** · 0.50-0.79: **151** · < 0.50: **58**
- PREVALENCE ANSWER (Challenger/Outsider pre-build item): alias families number in the
  HUNDREDS, not single digits — grouping is a real congestion class, and the
  family-collapsed ledger sensitivity line (report-time only) is worth building next.

## How to resolve (per row, reversible, flag-never-force)
```
POST /aliases/resolve  {"id": <id>, "action": "confirm" | "reject" | "revert"}   (x-internal-key)
```
Nothing changes in any served list until ENTITY_GROUPING=1 is set AND a row is confirmed.
Scores are never merged — a canonical row always shows its OWN score.

## Families (sorted by top confidence; constituents high-to-low)

| id | alias (fragment) | canonical | conf | shared titles | sample shared headline |
|---|---|---|---|---|---|
| 3 | `lindsey_graham` | `lindsey_graham_sudden` | 0.99 | 4 of 142/4 | after lindsey graham’s sudden death, conspiracy theories swirl online - the washington pos… |
| 6 | `lindsey_graham` | `darline_graham_lindsey` | 0.99 | 2 of 142/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 18 | `lindsey` | `darline_graham_lindsey` | 0.99 | 2 of 156/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 169 | `darline_graham` | `darline_graham_lindsey` | 0.99 | 2 of 11/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 238 | `darline` | `darline_graham_lindsey` | 0.99 | 2 of 13/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 800 | `graham_lindsey_graham` | `darline_graham_lindsey` | 0.99 | 2 of 2/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 802 | `graham_lindsey` | `darline_graham_lindsey` | 0.99 | 2 of 2/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 8 | `new_york` | `york_highrise` | 0.99 | 5 of 88/5 | buckling support beams seen inside new york high-rise. #bbcnews |
| 14 | `lindsey` | `lindsey_graham_sister` | 0.99 | 25 of 156/25 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 799 | `graham_lindsey_graham` | `lindsey_graham_sister` | 0.99 | 2 of 2/25 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 801 | `graham_lindsey` | `lindsey_graham_sister` | 0.99 | 2 of 2/25 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 4 | `lindsey_graham` | `lindsey_graham_sister` | 0.88 | 21 of 142/25 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 16 | `lindsey` | `graham_lindsey_graham` | 0.99 | 2 of 156/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 19 | `lindsey` | `ally_lindsey` | 0.99 | 3 of 156/3 | trump pays tribute to ally lindsey graham after he dies from ‘sudden’ illness |
| 20 | `lindsey` | `graham_lindsey` | 0.99 | 2 of 156/2 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 23 | `spain` | `spain_and_gibraltar` | 0.99 | 4 of 173/4 | border controls scrapped between spain and gibraltar |
| 769 | `gibraltar` | `spain_and_gibraltar` | 0.645 | 2 of 15/4 | border controls scrapped between spain and gibraltar |
| 26 | `spain` | `wildfires_southern_spain` | 0.99 | 4 of 173/4 | crews battle deadly wildfires in southern spain |
| 154 | `wildfires` | `wildfires_southern_spain` | 0.99 | 4 of 40/4 | crews battle deadly wildfires in southern spain |
| 155 | `southern_spain` | `wildfires_southern_spain` | 0.99 | 4 of 17/4 | crews battle deadly wildfires in southern spain |
| 725 | `wildfires_southern` | `wildfires_southern_spain` | 0.99 | 4 of 5/4 | crews battle deadly wildfires in southern spain |
| 30 | `spain` | `spain_kill` | 0.99 | 5 of 173/5 | wildfires in heat - baked southern spain kill 12 |
| 49 | `semifinals` | `wimbledon_semifinals` | 0.99 | 5 of 34/5 | british wildcard arthur fery through to wimbledon semi-finals after stunning victory |
| 150 | `wimbledon` | `wimbledon_semifinals` | 0.99 | 5 of 101/5 | british wildcard arthur fery through to wimbledon semi-finals after stunning victory |
| 72 | `england` | `england_and_wales` | 0.99 | 5 of 170/5 | homes for sale with stylish bedrooms in england and wales – in pictures |
| 763 | `wales` | `england_and_wales` | 0.99 | 5 of 15/5 | homes for sale with stylish bedrooms in england and wales – in pictures |
| 76 | `america` | `latin_america` | 0.99 | 3 of 79/3 | does donald trump make latin america a good bet? |
| 77 | `america` | `america_financial` | 0.99 | 2 of 79/2 | storm clouds gather over america's financial supremacy |
| 78 | `america` | `america_financial_supremacy` | 0.99 | 2 of 79/2 | storm clouds gather over america's financial supremacy |
| 716 | `supremacy` | `america_financial_supremacy` | 0.99 | 2 of 2/2 | storm clouds gather over america's financial supremacy |
| 829 | `financial_supremacy` | `america_financial_supremacy` | 0.99 | 2 of 2/2 | storm clouds gather over america's financial supremacy |
| 830 | `america_financial` | `america_financial_supremacy` | 0.99 | 2 of 2/2 | storm clouds gather over america's financial supremacy |
| 80 | `widdecombe` | `widdecombe_murder_case` | 0.99 | 4 of 109/4 | ann widdecombe murder case: former conservative mp murder suspect released as police conti… |
| 713 | `widdecombe_murder` | `widdecombe_murder_case` | 0.99 | 4 of 38/4 | ann widdecombe murder case: former conservative mp murder suspect released as police conti… |
| 81 | `widdecombe` | `minister_ann_widdecombe` | 0.99 | 7 of 109/7 | former conservative minister ann widdecombe dies aged 78 |
| 658 | `ann_widdecombe` | `minister_ann_widdecombe` | 0.99 | 7 of 103/7 | former conservative minister ann widdecombe dies aged 78 |
| 82 | `widdecombe` | `widdecombe_killing` | 0.99 | 3 of 109/3 | ann widdecombe killing: police investigating possible leftwing motivation |
| 89 | `suvs` | `suvs_are_growing` | 0.99 | 2 of 6/2 | britain’s cars and suvs are growing bigger – but there is a way to stop this deadly ‘carsp… |
| 103 | `hochul` | `kathy_hochul` | 0.99 | 5 of 10/5 | governor kathy hochul issued an executive order enacting a moratorium on the large, resour… |
| 104 | `shootings` | `fatal_shootings` | 0.99 | 4 of 23/4 | ice halts most traffic stops after fatal shootings |
| 105 | `shootings` | `deadly_shootings` | 0.99 | 6 of 23/6 | calls grow to abolish ice after deadly us shootings / aj #shorts |
| 106 | `trump_ally` | `trump_ally_dies` | 0.99 | 6 of 13/6 | influential sen. lindsey graham, a trump ally, dies after a sudden illness |
| 109 | `strait` | `strait_hormuz_open` | 0.99 | 6 of 140/6 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 122 | `strait_of_hormuz` | `strait_hormuz_open` | 0.875 | 5 of 168/6 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 207 | `strait_hormuz` | `strait_hormuz_open` | 0.875 | 5 of 108/6 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 675 | `hormuz_open` | `strait_hormuz_open` | 0.852 | 4 of 5/6 | iran war: us claims strait of hormuz is 'open' amid strikes |
| 117 | `inflation` | `inflation_data` | 0.99 | 5 of 65/5 | fed rate-hike bets mount before inflation data, warsh testimony - bloomberg.com |
| 119 | `meta_used` | `meta_used_tag` | 0.99 | 2 of 2/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 120 | `ai_to_tag` | `meta_used_tag` | 0.99 | 2 of 2/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 167 | `used_ai` | `meta_used_tag` | 0.99 | 2 of 2/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 256 | `meta` | `meta_used_tag` | 0.99 | 2 of 101/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 126 | `ice_houston` | `killed_ice_houston` | 0.99 | 4 of 7/4 | dhs: man killed by ice in houston not target of operation |
| 127 | `britain` | `great_britain` | 0.99 | 3 of 112/3 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 128 | `britain` | `britain_grid` | 0.99 | 2 of 112/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 130 | `britain` | `britain_grid_operator` | 0.99 | 2 of 112/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 673 | `britain_grid` | `britain_grid_operator` | 0.99 | 2 of 2/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 131 | `britain` | `great_britain_grid` | 0.99 | 2 of 112/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 674 | `britain_grid` | `great_britain_grid` | 0.99 | 2 of 2/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 755 | `great_britain` | `great_britain_grid` | 0.99 | 2 of 3/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 139 | `argentina` | `argentina_match` | 0.99 | 2 of 105/2 | egypt files complaint over referee of argentina match |
| 142 | `senate` | `senate_nominee` | 0.99 | 2 of 139/2 | here's who's vying to replace graham platner as maine democratic senate nominee - cbs news |
| 145 | `senate` | `senate_term` | 0.99 | 8 of 139/8 | darline graham, sister of lindsey graham, chosen to fulfill remainder of his us senate ter… |
| 149 | `senate` | `maine_senate_candidate` | 0.99 | 3 of 139/3 | democrats search for maine senate candidate after allegations force platner out |
| 786 | `maine_senate` | `maine_senate_candidate` | 0.99 | 3 of 38/3 | democrats search for maine senate candidate after allegations force platner out |
| 151 | `wildfires` | `deadly_wildfires` | 0.99 | 5 of 40/5 | crews battle deadly wildfires in southern spain |
| 161 | `deceptive_subscription` | `deceptive_subscription_practices` | 0.99 | 4 of 4/4 | new york city becomes first in the us to ban deceptive subscription practices |
| 162 | `deceptive_subscription` | `ban_deceptive_subscription` | 0.99 | 4 of 4/4 | new york city becomes first in the us to ban deceptive subscription practices |
| 163 | `ban_deceptive` | `ban_deceptive_subscription` | 0.99 | 4 of 4/4 | new york city becomes first in the us to ban deceptive subscription practices |
| 164 | `jurassic` | `jurassic_park` | 0.99 | 8 of 8/12 | 'hero, legend, sweetheart': tributes to jurassic park actor sam neill, who has died aged 7… |
| 165 | `heatwave` | `supplies_heatwave` | 0.99 | 2 of 68/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 166 | `heatwave` | `power_supplies_heatwave` | 0.99 | 2 of 68/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 804 | `supplies_heatwave` | `power_supplies_heatwave` | 0.99 | 2 of 2/2 | great britain’s grid operator issues another warning over power supplies in heatwave |
| 168 | `used_ai` | `meta_used` | 0.99 | 2 of 2/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 257 | `meta` | `meta_used` | 0.99 | 2 of 101/2 | meta used ai to tag workers who took [maternity or disability] leave to be laid off, lawsu… |
| 208 | `rejects` | `court_rejects` | 0.99 | 3 of 15/3 | high court rejects most of ‘dieselgate’ claims brought by 1.6m uk car owners |
| 210 | `semis` | `cup_semis` | 0.99 | 6 of 12/6 | lindsey graham death and world cup semis / reuters world news |
| 251 | `world_cup` | `cup_semis` | 0.53 | 2 of 166/6 | lindsey graham death and world cup semis / reuters world news |
| 224 | `chatgpt` | `chatgpt_work` | 0.99 | 2 of 79/2 | chatgpt work |
| 226 | `tapestry_arrives` | `bayeux_tapestry_arrives` | 0.99 | 6 of 6/6 | bayeux tapestry arrives at british museum in dead of night after top-secret journey from f… |
| 720 | `tapestry` | `bayeux_tapestry_arrives` | 0.99 | 6 of 14/6 | bayeux tapestry arrives at british museum in dead of night after top-secret journey from f… |
| 98 | `bayeux_tapestry` | `bayeux_tapestry_arrives` | 0.875 | 5 of 14/6 | bayeux tapestry arrives at british museum in dead of night after top-secret journey from f… |
| 693 | `bayeux` | `bayeux_tapestry_arrives` | 0.76 | 4 of 9/6 | bayeux tapestry arrives at british museum in dead of night after top-secret journey from f… |
| 229 | `vet_israel` | `committee_vet_israel` | 0.99 | 2 of 2/2 | abc and sbs need ‘oversight’ committee to vet israel coverage, jillian segal tells royal c… |
| 233 | `blanche_confirmation` | `blanche_confirmation_hearing` | 0.99 | 5 of 8/5 | live: senators question acting attorney general todd blanche at confirmation hearing |
| 750 | `blanche` | `blanche_confirmation_hearing` | 0.852 | 4 of 41/5 | live: senators question acting attorney general todd blanche at confirmation hearing |
| 236 | `simo_steps` | `fidji_simo_steps` | 0.99 | 4 of 4/4 | fidji simo steps down from leading openai’s agi work due to illness |
| 237 | `texas` | `texas_man` | 0.99 | 2 of 49/2 | son of texas man killed by ice agent: 'he did not deserve to die' |
| 252 | `world_cup` | `spain_world_cup` | 0.99 | 2 of 166/2 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 862 | `spain_world` | `spain_world_cup` | 0.99 | 2 of 2/2 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 253 | `mariska_hargitay` | `mariska_hargitay_host` | 0.99 | 3 of 4/3 | 2026 emmy nominations announced, mariska hargitay to host awards show |
| 851 | `hargitay_host` | `mariska_hargitay_host` | 0.99 | 3 of 3/3 | 2026 emmy nominations announced, mariska hargitay to host awards show |
| 254 | `meta` | `took_meta` | 0.99 | 2 of 101/2 | the lawyer who took on meta – and won – podcast |
| 255 | `meta` | `meta_glasses` | 0.99 | 7 of 101/7 | lorde says ray-ban meta ai glasses are ‘not sexy’ |
| 258 | `israel` | `israel_settlers` | 0.99 | 12 of 119/12 | an american politician is blocked by israeli settlers in the west bank |
| 259 | `israel` | `aid_to_israel` | 0.99 | 2 of 119/2 | jeffries opposes bid to cut off aid to israel as democrats split |
| 260 | `israel` | `aid_israel` | 0.99 | 2 of 119/2 | jeffries opposes bid to cut off aid to israel as democrats split |
| 262 | `israel` | `detained_israel` | 0.99 | 5 of 119/5 | congressman detained by israeli settlers in the west bank |
| 268 | `election` | `election_agency` | 0.99 | 6 of 62/6 | reports: trump fires members of federal election agency |
| 269 | `election` | `election_commission` | 0.99 | 9 of 62/9 | trump fires democrats on election commission, republican resigns |
| 270 | `election` | `fires_election` | 0.99 | 5 of 62/5 | trump fires election assistance commission members ahead of midterms |
| 271 | `election` | `trump_fires_election` | 0.99 | 5 of 62/5 | trump fires election assistance commission members ahead of midterms |
| 729 | `fires_election` | `trump_fires_election` | 0.99 | 5 of 5/5 | trump fires election assistance commission members ahead of midterms |
| 118 | `trump_fires` | `trump_fires_election` | 0.576 | 2 of 10/5 | trump fires election board democrats - the hill |
| 274 | `turkey` | `summit_turkey` | 0.99 | 5 of 32/5 | carney en route to saudi arabia following nato summit in turkey |
| 275 | `ebola` | `congo_ebola` | 0.99 | 8 of 34/8 | congo ebola orphans struggle to rebuild life after parents’ death |
| 277 | `congo` | `congo_ebola` | 0.904 | 7 of 20/8 | congo ebola orphans struggle to rebuild life after parents’ death |
| 276 | `ebola` | `ebola_outbreak` | 0.99 | 13 of 34/13 | africa cdc says ebola outbreak is “fastest-growing ever”; after 600 deaths since mid-may |
| 278 | `white_house` | `white_house_ufc` | 0.99 | 5 of 47/5 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighting show |
| 676 | `house_ufc` | `white_house_ufc` | 0.99 | 5 of 5/5 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighting show |
| 756 | `ufc` | `white_house_ufc` | 0.99 | 5 of 30/5 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighting show |
| 279 | `white_house` | `white_house_helipad` | 0.99 | 2 of 47/2 | trump shares new details on ‘beautiful’ white house helipad project |
| 281 | `thailand` | `pitch_discovered_thailand` | 0.99 | 2 of 24/2 | new dinosaur species as long as cricket pitch discovered in thailand |
| 691 | `discovered_thailand` | `pitch_discovered_thailand` | 0.99 | 2 of 3/2 | new dinosaur species as long as cricket pitch discovered in thailand |
| 284 | `platner` | `democrat_graham_platner` | 0.99 | 4 of 133/4 | democrat graham platner suspends campaign for key us senate race after assault allegation |
| 668 | `graham_platner` | `democrat_graham_platner` | 0.645 | 2 of 73/4 | democrat graham platner suspends campaign for key us senate race in maine |
| 285 | `platner` | `platner_officially` | 0.99 | 5 of 133/5 | as platner officially ends senate bid, volunteers warn replacement must back same agenda |
| 292 | `cuba` | `cuba_suffers` | 0.99 | 3 of 16/3 | cuba suffers second nationwide blackout in five days |
| 296 | `bipartisan` | `bipartisan_housing_bill` | 0.99 | 8 of 17/8 | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 764 | `bipartisan_housing` | `bipartisan_housing_bill` | 0.99 | 8 of 8/8 | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 297 | `bipartisan` | `bipartisan_housing` | 0.99 | 8 of 17/8 | bipartisan housing bill becomes law despite trump’s refusal to sign it |
| 298 | `carmack` | `john_carmack` | 0.99 | 3 of 3/3 | "my 'microsoft will probably be a good steward of the brand' statement isn't aging well" -… |
| 299 | `declares_iran` | `trump_declares_iran` | 0.99 | 7 of 7/7 | hegseth cancels trip to israel after trump declares iran ceasefire ‘over’ |
| 797 | `declares` | `trump_declares_iran` | 0.891 | 6 of 23/7 | oil surges as trump declares iran deal 'over' |
| 300 | `takeover` | `rival_takeover_bid` | 0.99 | 2 of 20/2 | easyjet accepts rival takeover bid from us investor apollo |
| 688 | `rival_takeover` | `rival_takeover_bid` | 0.99 | 2 of 2/2 | easyjet accepts rival takeover bid from us investor apollo |
| 301 | `takeover` | `rival_takeover` | 0.99 | 2 of 20/2 | easyjet accepts rival takeover bid from us investor apollo |
| 302 | `gang_ringleader` | `grooming_gang_ringleader` | 0.99 | 2 of 2/2 | mahmood to close loophole blocking deportation of rochdale grooming gang ringleader |
| 639 | `ringleader` | `grooming_gang_ringleader` | 0.99 | 2 of 3/2 | mahmood to close loophole blocking deportation of rochdale grooming gang ringleader |
| 303 | `boyle` | `boyle_heights` | 0.99 | 3 of 4/3 | anger grows in boyle heights as warehouse fire leaves stench, flies and vermin in its wake |
| 304 | `qualley` | `margaret_qualley` | 0.99 | 4 of 4/6 | exclusive / jack antonoff and margaret qualley's marriage 'challenges' exposed before spli… |
| 306 | `usiran` | `usiran_war` | 0.99 | 4 of 39/4 | has the us-iran war restarted? / bbc newscast |
| 616 | `bezos` | `bezos_blue_origin` | 0.99 | 3 of 4/3 | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 745 | `bezos_blue` | `bezos_blue_origin` | 0.99 | 3 of 3/3 | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 617 | `bezos` | `bezos_blue` | 0.99 | 3 of 4/3 | bezos' blue origin valued at $130 billion in first outside fundraising round |
| 622 | `widdecombe_death` | `ann_widdecombe_death` | 0.99 | 13 of 14/13 | aberdeen university investigates employee over social media posts celebrating ann widdecom… |
| 659 | `ann_widdecombe` | `ann_widdecombe_death` | 0.99 | 13 of 103/13 | aberdeen university investigates employee over social media posts celebrating ann widdecom… |
| 85 | `widdecombe` | `ann_widdecombe_death` | 0.937 | 12 of 109/13 | ann widdecombe death latest: police launch murder investigation - bbc |
| 687 | `ann_widdecombe_de` | `ann_widdecombe_death` | 0.714 | 3 of 5/13 | ann widdecombe death latest: police launch murder investigation - bbc |
| 623 | `platner_suspends` | `graham_platner_suspends` | 0.99 | 8 of 11/8 | breaking: graham platner suspends campaign for maine senate race amid sexual assault alleg… |
| 283 | `platner` | `graham_platner_suspends` | 0.904 | 7 of 133/8 | breaking: graham platner suspends campaign for maine senate race amid sexual assault alleg… |
| 667 | `graham_platner` | `graham_platner_suspends` | 0.904 | 7 of 73/8 | breaking: graham platner suspends campaign for maine senate race amid sexual assault alleg… |
| 626 | `evals` | `evals_llm` | 0.99 | 6 of 12/6 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against declared commit… |
| 701 | `llm_llm` | `evals_llm` | 0.645 | 3 of 26/6 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against declared commit… |
| 180 | `llm` | `evals_llm` | 0.53 | 2 of 195/6 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against declared commit… |
| 628 | `fatally` | `fatally_shot_ice` | 0.99 | 12 of 30/12 | 'he did not deserve to be reduced to a headline': son of man fatally shot by ice speaks ou… |
| 630 | `ollama` | `llm_ollama` | 0.99 | 10 of 70/10 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-augmented gen… |
| 176 | `llm` | `llm_ollama` | 0.714 | 6 of 195/10 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-augmented gen… |
| 631 | `officially_withdraws` | `platner_officially_withdraws` | 0.99 | 4 of 4/4 | graham platner officially withdraws candidacy for us senate in maine |
| 291 | `platner` | `platner_officially_withdraws` | 0.817 | 3 of 133/4 | graham platner officially withdraws candidacy for us senate in maine |
| 619 | `platner_officially` | `platner_officially_withdraws` | 0.817 | 3 of 5/4 | graham platner officially withdraws candidacy for us senate in maine |
| 632 | `nlp` | `nlp_python` | 0.99 | 8 of 64/8 | aakash15-semwal/semantic-codebase-search-engine semantic search engine for python codebase… |
| 633 | `nlp` | `llm_nlp` | 0.99 | 6 of 64/6 | agentdynarq/rag-pipeline a retrieval-augmented generation (rag) pipeline from scratch: chu… |
| 634 | `nlp` | `nlp_openai` | 0.99 | 3 of 64/3 | baaabaei/finetuning-whisper fine-tuning openai's whisper model for speech-to-text applicat… |
| 220 | `openai` | `nlp_openai` | 0.76 | 2 of 128/3 | messuuu/ask-multiple-pdfs-clean rag-based chatbot to query multiple pdf documents using la… |
| 636 | `fastapi` | `fastapi_llm` | 0.99 | 12 of 122/12 | 89himanshu-dwivedi/rag-chatbot streaming rag chatbot - fastapi, sse, semantic cache, citat… |
| 189 | `llm` | `fastapi_llm` | 0.587 | 5 of 195/12 | cris904fl/rag-practice pipeline rag (retrieval-augmented generation) de práctica: fastapi … |
| 638 | `langgraph` | `langgraph_llm` | 0.99 | 3 of 39/3 | batramayank106/multi-agent-resume-analyzer cv chacha — multi agent resume intelligence pla… |
| 188 | `llm` | `langgraph_llm` | 0.76 | 2 of 195/3 | cksharma11/ai_fundamental_demo a zero-api-key classroom demo showing how client/server, a … |
| 640 | `ringleader` | `gang_ringleader` | 0.99 | 2 of 3/2 | mahmood to close loophole blocking deportation of rochdale grooming gang ringleader |
| 642 | `langchain` | `langchain_llm` | 0.99 | 18 of 75/18 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-augmented gen… |
| 184 | `llm` | `langchain_llm` | 0.568 | 7 of 195/18 | abankar1/rag-glassbox a see-through rag demo: watch every stage of retrieval-augmented gen… |
| 644 | `wally` | `wally_funk_aviation` | 0.99 | 2 of 4/2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 718 | `funk_aviation` | `wally_funk_aviation` | 0.99 | 2 of 2/2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 726 | `wally_funk` | `wally_funk_aviation` | 0.99 | 2 of 3/2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 645 | `wally` | `wally_funk` | 0.99 | 3 of 4/3 | wally funk death: oldest woman to travel into space dies at 87 |
| 646 | `sheikh` | `sheikh_hamad` | 0.99 | 6 of 6/6 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 647 | `postgresql` | `postgresql_python_rag` | 0.99 | 2 of 31/2 | shri30a/longhornai ai-powered campus assistant for ut austin built with next.js, fastapi, … |
| 696 | `python_rag` | `postgresql_python_rag` | 0.99 | 2 of 81/2 | shri30a/longhornai ai-powered campus assistant for ut austin built with next.js, fastapi, … |
| 651 | `kalshi` | `kalshi_traders` | 0.99 | 5 of 11/5 | inflation peaked in may as energy prices fell in june, kalshi traders think |
| 657 | `republic_japan` | `islamic_republic_japan` | 0.99 | 2 of 2/2 | [video] trump at nato meeting: "we had 111 missiles shot by the islamic republic of japan.… |
| 660 | `howe` | `gordie_howe` | 0.99 | 5 of 5/6 | gordie howe bridge set to open on july 27 |
| 708 | `gordie` | `gordie_howe` | 0.99 | 6 of 6/6 | gordie howe bridge set to open on july 27 |
| 664 | `paramountwarner` | `paramountwarner_bros` | 0.99 | 5 of 6/5 | 12 states challenge paramount-warner bros. discovery deal |
| 665 | `farage_resigns` | `nigel_farage_resigns` | 0.99 | 2 of 2/2 | nigel farage resigns as mp |
| 776 | `farage` | `nigel_farage_resigns` | 0.99 | 2 of 86/2 | nigel farage resigns as mp |
| 669 | `graham_platner` | `breaking_graham_platner` | 0.99 | 5 of 73/5 | breaking: graham platner dropped out of the u.s. senate race. maine democrats have until j… |
| 287 | `platner` | `breaking_graham_platner` | 0.852 | 4 of 133/5 | breaking: graham platner dropped out of the u.s. senate race. maine democrats have until j… |
| 671 | `graham_platner` | `graham_platner_officially` | 0.99 | 5 of 73/5 | graham platner officially drops from maine senate race after sex assault claim, setting of… |
| 290 | `platner` | `graham_platner_officially` | 0.852 | 4 of 133/5 | graham platner officially drops from maine senate race after sex assault claim, setting of… |
| 618 | `platner_officially` | `graham_platner_officially` | 0.852 | 4 of 5/5 | graham platner officially drops from maine senate race after sex assault claim, setting of… |
| 677 | `baldoni` | `justin_baldoni` | 0.99 | 11 of 12/11 | justin baldoni addresses blake lively lawsuit in video. 'we are healing' |
| 679 | `platner_drops` | `graham_platner_drops` | 0.99 | 7 of 13/7 | graham platner drops maine senate bid |
| 670 | `graham_platner` | `graham_platner_drops` | 0.891 | 6 of 73/7 | graham platner drops maine senate bid |
| 289 | `platner` | `graham_platner_drops` | 0.793 | 5 of 133/7 | graham platner drops out of maine senate race after sexual assault accusation |
| 683 | `nato` | `nato_chief` | 0.99 | 7 of 140/7 | from 'dear donald' to 'trump trillion': inside nato chief mark rutte's u.s. strategy |
| 684 | `nato` | `nato_allies` | 0.99 | 6 of 140/6 | 'don't fool with us': nato allies put on a united front as they prepare to meet trump |
| 692 | `bayeux` | `bayeux_tapestry` | 0.99 | 9 of 9/14 | after almost 1,000 years, the bayeux tapestry is back on english soil |
| 721 | `tapestry` | `bayeux_tapestry` | 0.941 | 13 of 14/14 | after almost 1,000 years, the bayeux tapestry is back on english soil |
| 695 | `python_rag` | `python_rag_retrievalaugmentedgeneration` | 0.99 | 14 of 81/14 | aryansharmagithub/auditrag rag answers you can verify — citations, faithfulness checks, ex… |
| 96 | `rag` | `python_rag_retrievalaugmentedgeneration` | 0.694 | 8 of 183/14 | aryansharmagithub/auditrag rag answers you can verify — citations, faithfulness checks, ex… |
| 848 | `rag_retrievalaugmentedgeneration` | `python_rag_retrievalaugmentedgeneration` | 0.596 | 6 of 28/14 | djagdalebing/rag-engine hybrid-retrieval rag from first principles: bm25 + dense vectors +… |
| 705 | `hassabis` | `demis_hassabis` | 0.99 | 4 of 4/4 | deepmind chief demis hassabis calls for us-led body to test ‘frontier’ ai models |
| 706 | `demis` | `demis_hassabis` | 0.99 | 4 of 4/4 | deepmind chief demis hassabis calls for us-led body to test ‘frontier’ ai models |
| 707 | `ayatollah` | `ayatollah_ali_khamenei` | 0.99 | 6 of 9/6 | iran buries supreme leader ayatollah ali khamenei |
| 806 | `ali_khamenei` | `ayatollah_ali_khamenei` | 0.645 | 3 of 11/6 | thousands attend final funeral prayers for iran's ayatollah ali khamenei |
| 736 | `khamenei` | `ayatollah_ali_khamenei` | 0.53 | 2 of 33/6 | iran buries supreme leader ayatollah ali khamenei |
| 715 | `supremacy` | `financial_supremacy` | 0.99 | 2 of 2/2 | storm clouds gather over america's financial supremacy |
| 719 | `funk_aviation` | `funk_aviation_pioneer` | 0.99 | 2 of 2/2 | wally funk, aviation pioneer and oldest woman to go into space, dies at 87 |
| 722 | `tapestry` | `tapestry_arrives` | 0.99 | 6 of 14/6 | bayeux tapestry arrives at british museum in dead of night after top-secret journey from f… |
| 723 | `assassinate` | `assassinate_trump` | 0.99 | 3 of 7/3 | israel shared intelligence with us of iranian plot to assassinate trump, sources say - cnn |
| 728 | `hanged` | `woman_hanged` | 0.99 | 4 of 4/4 | last woman to be hanged in the uk pardoned 70 years on— ruth ellis, the last woman to be h… |
| 731 | `diarrhea` | `diarrhea_parasite` | 0.99 | 9 of 28/9 | 31 states are reporting cases of ‘explosive diarrhea’ parasite as outbreak continues to gr… |
| 779 | `parasite` | `diarrhea_parasite` | 0.913 | 8 of 28/9 | cyclospora, the ‘explosive diarrhea’ parasite, cases reported in at least 31 states: see t… |
| 732 | `khalifa` | `hamad_bin_khalifa` | 0.99 | 5 of 5/5 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 832 | `bin_khalifa` | `hamad_bin_khalifa` | 0.852 | 4 of 5/5 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 735 | `india_tourists` | `india_tourists_killed` | 0.99 | 5 of 8/5 | 15 indian tourists killed when a speedboat capsizes in southern vietnam |
| 742 | `wildfire` | `wildfire_smoke` | 0.99 | 5 of 62/5 | canada wildfire smoke to spread across the us - here’s what to expect |
| 757 | `ufc` | `house_ufc` | 0.99 | 5 of 30/5 | 8 men indicted in planned drone and sniper attack on white house ufc cage-fighting show |
| 758 | `ufc` | `ufc_event` | 0.99 | 3 of 30/3 | eight charged over alleged conspiracy to attack white house ufc event |
| 761 | `procession` | `funeral_procession` | 0.99 | 5 of 6/5 | funeral procession for iran's late supreme leader ali khamenei in iraq / dw news |
| 762 | `11yearold` | `11yearold_girl` | 0.99 | 2 of 4/2 | protests engulf indian state after rape and murder of 11-year-old girl |
| 765 | `soar` | `expected_to_soar` | 0.99 | 2 of 11/2 | cancer cases expected to soar worldwide, who report finds |
| 766 | `soar` | `expected_soar` | 0.99 | 2 of 11/2 | cancer cases expected to soar worldwide, who report finds |
| 767 | `sen_lindsey` | `sen_lindsey_graham` | 0.99 | 33 of 33/35 | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey graham's c… |
| 21 | `lindsey` | `sen_lindsey_graham` | 0.832 | 27 of 156/35 | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey graham's c… |
| 7 | `lindsey_graham` | `sen_lindsey_graham` | 0.734 | 22 of 142/35 | bloomberg this weekend / sen. lindsey graham dead, centcom launches strikes on iran |
| 768 | `sinks` | `boat_sinks` | 0.99 | 5 of 9/5 | 1 dead and 3 missing after boat sinks near alcatraz island |
| 774 | `farage` | `farage_resignation` | 0.99 | 3 of 86/3 | reeves to approve farage’s resignation, saying ‘if he wants to spend summer arguing with a… |
| 777 | `farage` | `farage_resigns` | 0.99 | 2 of 86/2 | nigel farage resigns as mp |
| 778 | `parasite` | `diarrheacausing_parasite` | 0.99 | 6 of 28/6 | a diarrhea-causing parasite infects more than 1,000 in the u.s. |
| 781 | `ryanair` | `ryanair_plane` | 0.99 | 8 of 21/8 | 'if we die, we die together': wife of man nearly sucked out of ryanair plane speaks of ord… |
| 782 | `monuments` | `national_monuments` | 0.99 | 6 of 8/6 | president trump drastically shrinks grand staircase-escalante and bears ears national monu… |
| 788 | `manhattan` | `manhattan_highrise` | 0.99 | 3 of 9/3 | manhattan high-rise is still unstable after columns buckle, forcing evacuations |
| 789 | `killings` | `ice_killings` | 0.99 | 2 of 4/2 | congressman seth magaziner's floor speech on the latest ice killings. |
| 790 | `shortages` | `fuel_shortages` | 0.99 | 7 of 9/7 | jackdaw boss warns of winter fuel shortages if gas field not approved |
| 791 | `court_justices` | `supreme_court_justices` | 0.99 | 4 of 4/4 | knives out at us supreme court as justices’ squabbles go public |
| 620 | `justices` | `supreme_court_justices` | 0.817 | 3 of 8/4 | knives out at us supreme court as justices’ squabbles go public |
| 795 | `new_fed` | `new_fed_chair` | 0.99 | 2 of 3/2 | trump's new fed chair just crushed gold, silver, bitcoin |
| 805 | `alleges` | `lawsuit_alleges` | 0.99 | 3 of 9/3 | musicians shortchanged by ai deals with labels, lawsuit alleges |
| 807 | `alcatraz` | `alcatraz_island` | 0.99 | 9 of 14/9 | 1 dead and 2 missing after pontoon boat fire near alcatraz island off san francisco |
| 808 | `nevada` | `nevada_governor` | 0.99 | 4 of 6/4 | 'i'm joe lombardo': nevada governor pulled over in traffic stop |
| 809 | `squawk` | `morning_squawk` | 0.99 | 6 of 7/6 | bank earnings, warsh heads to the hill, chipotle's mexico push and more in morning squawk |
| 810 | `cnbc_daily` | `cnbc_daily_open` | 0.99 | 9 of 10/9 | cnbc daily open: a chip off the ai block |
| 221 | `cnbc` | `cnbc_daily_open` | 0.913 | 8 of 38/9 | cnbc daily open: a chip off the ai block |
| 812 | `arwa` | `arwa_mahdawi` | 0.99 | 3 of 3/3 | ali g is back. i really wish he wasn’t / arwa mahdawi |
| 817 | `mahdawi` | `arwa_mahdawi` | 0.99 | 3 of 3/3 | ali g is back. i really wish he wasn’t / arwa mahdawi |
| 813 | `bancshares` | `bancshares_inc` | 0.99 | 3 of 3/3 | federal reserve board issues enforcement action with employee of bank of eufaula and s n b… |
| 814 | `eufaula` | `bank_eufaula` | 0.99 | 2 of 2/2 | federal reserve board issues enforcement action with employee of bank of eufaula and s n b… |
| 816 | `burry` | `michael_burry` | 0.99 | 3 of 3/3 | do not buy stocks! (michael burry’s final warning) |
| 820 | `democrat_gazette` | `arkansas_democrat_gazette` | 0.99 | 5 of 5/5 | america's first 250 years / arkansas democrat gazette |
| 825 | `bonnie` | `bonnie_tyler_singer` | 0.99 | 4 of 32/4 | bonnie tyler, singer famed for ‘total eclipse of the heart,’ dies at 75 |
| 835 | `bonnie_tyler` | `bonnie_tyler_singer` | 0.99 | 4 of 36/4 | bonnie tyler, singer famed for ‘total eclipse of the heart,’ dies at 75 |
| 826 | `bonnie` | `bonnie_tyler` | 0.99 | 32 of 32/36 | 'total eclipse of the heart' and four other essential bonnie tyler songs |
| 827 | `pmqs` | `final_pmqs` | 0.99 | 7 of 9/7 | keir starmer greeted with applause as he wraps up his final pmqs as uk prime minister. #bb… |
| 836 | `hacks_breaks` | `hacks_breaks_record` | 0.99 | 2 of 2/2 | 'hacks' breaks record for most emmy nominations for a comedy in a single year |
| 837 | `revamp` | `troubled_revamp` | 0.99 | 2 of 3/2 | crews draining the lincoln memorial reflecting pool again as part of troubled revamp |
| 838 | `manuscripts` | `manuscripts_from_ucla` | 0.99 | 3 of 3/4 | california man steals historic chinese manuscripts from ucla, using fake names, dummy docu… |
| 840 | `hynix` | `hynix_rises` | 0.99 | 2 of 42/2 | sk hynix rises 13% in nasdaq debut. chairman tells cnbc 'demand is enormous' |
| 846 | `reich` | `robert_reich` | 0.99 | 3 of 3/3 | the nato summit exposed the real source of trump’s power / robert reich |
| 847 | `prairie` | `house_the_prairie` | 0.99 | 6 of 6/7 | 'little house on the prairie' boss on netflix show's woke backlash, moving towns in season… |
| 850 | `hillsborough` | `hillsborough_law` | 0.99 | 5 of 6/5 | bill for hillsborough law set to be approved by mps |
| 852 | `clair` | `salsa_clair` | 0.99 | 4 of 4/4 | 2 victims of fatal shooting at salsa on st. clair identified, police say they knew each ot… |
| 842 | `salsa` | `salsa_clair` | 0.817 | 3 of 4/4 | 2 victims of fatal shooting at salsa on st. clair identified, police say they knew each ot… |
| 853 | `closes_strait` | `closes_strait_hormuz` | 0.99 | 7 of 8/7 | analysis: us bombs iranian port cities as irgc closes strait of hormuz |
| 206 | `strait_hormuz` | `closes_strait_hormuz` | 0.891 | 6 of 108/7 | analysis: us bombs iranian port cities as irgc closes strait of hormuz |
| 108 | `strait` | `closes_strait_hormuz` | 0.694 | 4 of 140/7 | breaking: us bombs iranian port cities as irgc closes strait of hormuz |
| 121 | `strait_of_hormuz` | `closes_strait_hormuz` | 0.694 | 4 of 168/7 | iran closes strait of hormuz, us launches fresh strikes |
| 854 | `highrise_risk` | `highrise_risk_collapse` | 0.99 | 2 of 2/2 | live: mamdani and hochul speak after manhattan high-rise at risk of collapse was stabilize… |
| 856 | `goldman` | `goldman_sachs` | 0.99 | 4 of 9/4 | goldman sachs limits prediction market betting for employees |
| 864 | `sachs` | `goldman_sachs` | 0.99 | 3 of 3/4 | goldman sachs limits prediction market betting for employees |
| 858 | `outage` | `network_outage` | 0.99 | 5 of 49/5 | australia news live: telstra warns of ‘secondary issue’ after yesterday’s network outage; … |
| 859 | `soaring` | `soaring_temperatures` | 0.99 | 5 of 13/5 | 11 die in spanish wildfire amid soaring temperatures |
| 863 | `straits` | `straits_times` | 0.99 | 8 of 9/8 | #showbiz: zizi kirana battles two months of insomnia after gruelling humanitarian missions… |
| 868 | `addictive` | `addictive_design` | 0.99 | 4 of 12/4 | eu accuses meta of failing to tackle mental health risks of ‘addictive design’ |
| 780 | `burnham` | `andy_burnham` | 0.977 | 51 of 111/52 | a big week for us banks and andy burnham |
| 637 | `senator_lindsey` | `senator_lindsey_graham` | 0.96 | 22 of 23/23 | "great american, patriot, friend, fearless leader": us officials and world leaders mourn p… |
| 15 | `lindsey` | `senator_lindsey_graham` | 0.81 | 17 of 156/23 | "great american, patriot, friend, fearless leader": us officials and world leaders mourn p… |
| 5 | `lindsey_graham` | `senator_lindsey_graham` | 0.72 | 14 of 142/23 | "great american, patriot, friend, fearless leader": us officials and world leaders mourn p… |
| 143 | `senate` | `maine_senate` | 0.954 | 36 of 139/38 | bernie sanders joins calls for platner to withdraw from maine senate race |
| 273 | `apple` | `apple_sues` | 0.952 | 17 of 77/18 | apple sues openai alleging theft of top-secret information |
| 666 | `sues` | `apple_sues` | 0.913 | 16 of 26/18 | apple sues openai alleging theft of top-secret information |
| 686 | `neill` | `sam_neill` | 0.952 | 17 of 18/22 | 'hero, legend, sweetheart': tributes to jurassic park actor sam neill, who has died aged 7… |
| 133 | `mcconnell` | `mitch_mcconnell` | 0.945 | 43 of 66/46 | ailing mitch mcconnell is preparing to return to work, scott jennings tells cnn host |
| 83 | `widdecombe` | `widdecombe_death` | 0.941 | 13 of 109/14 | ann widdecombe death latest: police launch murder investigation - bbc |
| 682 | `nato` | `nato_summit` | 0.938 | 37 of 140/40 | carney en route to saudi arabia following nato summit in turkey |
| 681 | `nato` | `nato_leaders` | 0.937 | 12 of 140/13 | danish pm says greenland is 'not for sale' as trump joins nato leaders in turkey |
| 84 | `widdecombe` | `widdecombe_murder` | 0.936 | 35 of 109/38 | 'widdecombe murder inquiry' and 'strike norse' |
| 648 | `machinelearning` | `llm_machinelearning` | 0.932 | 11 of 74/12 | freeautomation-tech/agent-memory-kit memory patterns, context strategies, and persistence … |
| 178 | `llm` | `llm_machinelearning` | 0.645 | 6 of 195/12 | freeautomation-tech/agent-memory-kit memory patterns, context strategies, and persistence … |
| 239 | `darline` | `darline_graham` | 0.927 | 10 of 13/11 | darline graham , lindsey graham sister , to be sworn in as senator / what to know |
| 288 | `platner` | `platner_suspends` | 0.927 | 10 of 133/11 | breaking: graham platner suspends campaign for maine senate race amid sexual assault alleg… |
| 689 | `ceasefire` | `ceasefire_with_iran` | 0.927 | 10 of 94/11 | nato leaders meet in ankara as us ceasefire with iran teeters |
| 711 | `iran_trade` | `iran_trade_strikes` | 0.927 | 10 of 27/11 | cnbc daily open: mideast tensions on the boil again as u.s., iran trade strikes |
| 307 | `us_and_iran` | `iran_trade_strikes` | 0.614 | 5 of 27/11 | live updates: trump says ceasefire ‘over’ after us and iran trade strikes - cnn |
| 53 | `iran` | `iran_trade_strikes` | 0.425 | 2 of 183/11 | us and iran trade strikes, dispute whether hormuz is open |
| 147 | `senate` | `senate_race` | 0.923 | 37 of 139/41 | 6 potential replacements for graham platner if he drops out of senate race - the washingto… |
| 662 | `us_senate` | `senate_race` | 0.551 | 4 of 11/41 | barabak: what's in a name? a confounding u.s. senate race |
| 50 | `semifinals` | `cup_semifinals` | 0.921 | 9 of 34/10 | england defeats norway for world cup semifinals spot |
| 245 | `world_cup` | `cup_semifinals` | 0.645 | 5 of 166/10 | england, argentina, france and spain set for world cup semifinals |
| 66 | `conor` | `conor_mcgregor` | 0.921 | 27 of 30/34 | conor mcgregor and max holloway meet again at ufc 329 |
| 22 | `mcgregor` | `conor_mcgregor` | 0.852 | 20 of 25/34 | conor mcgregor and max holloway meet again at ufc 329 |
| 222 | `cnbc` | `cnbc_daily` | 0.921 | 9 of 38/10 | cnbc daily open: a chip off the ai block |
| 792 | `buffett` | `warren_buffett` | 0.921 | 9 of 13/10 | billionaire warren buffett stops donations to bill gates charity |
| 107 | `strait` | `strait_hormuz` | 0.92 | 97 of 140/108 | 'don't talk about it': trump tells journalists to stop asking about strait of hormuz after… |
| 652 | `binface` | `count_binface` | 0.917 | 34 of 38/38 | a cunning stunt - can count binface win? |
| 86 | `widdecombe` | `ann_widdecombe` | 0.916 | 92 of 109/103 | andy burnham calls for ‘serious review’ of mp security after ann widdecombe murder |
| 213 | `anthropic` | `anthropic_claude` | 0.913 | 16 of 115/18 | 12122j/mcpvet mcp security scanner — vet a model context protocol server before you add it… |
| 204 | `claude` | `anthropic_claude` | 0.875 | 15 of 186/18 | 12122j/mcpvet mcp security scanner — vet a model context protocol server before you add it… |
| 272 | `humanoid` | `humanoid_robots` | 0.913 | 8 of 11/9 | alibaba-affiliate ant group rushes into humanoid robots with a dozen deals in 18 months |
| 9 | `lindsey` | `lindsey_graham` | 0.912 | 126 of 156/142 | "great american, patriot, friend, fearless leader": us officials and world leaders mourn p… |
| 102 | `araujo` | `lorenzo_salgado_araujo` | 0.904 | 7 of 10/8 | "a government that conceals its identity cannot demand perfect recognition from frightened… |
| 114 | `blockade` | `naval_blockade` | 0.904 | 7 of 36/8 | iran live updates: us carries out latest round of strikes, resumes naval blockade |
| 775 | `farage` | `nigel_farage` | 0.902 | 34 of 86/39 | a timeline of nigel farage’s £5mn gift and his return to politics |
| 785 | `maine_senate` | `maine_senate_race` | 0.9 | 20 of 38/23 | a defiant platner exits maine senate race |
| 819 | `senate_race` | `maine_senate_race` | 0.9 | 20 of 41/23 | a defiant platner exits maine senate race |
| 146 | `senate` | `maine_senate_race` | 0.87 | 19 of 139/23 | bernie sanders joins calls for platner to withdraw from maine senate race |
| 1 | `lindsey_graham` | `lindsey_graham_death` | 0.898 | 13 of 142/15 | donald trump suggests there was no foul play in lindsey graham’s death amid conspiracies –… |
| 10 | `lindsey` | `lindsey_graham_death` | 0.852 | 12 of 156/15 | donald trump suggests there was no foul play in lindsey graham’s death amid conspiracies –… |
| 855 | `lindsey_graham_de` | `lindsey_graham_death` | 0.576 | 2 of 5/15 | lindsey graham death and world cup semis / reuters world news |
| 230 | `allstar` | `allstar_game` | 0.898 | 13 of 28/15 | 'one day in september' chronicles how baseball's all-star game was born |
| 132 | `nolan` | `christopher_nolan` | 0.896 | 19 of 41/22 | 'the odyssey' stars on being cast and working with christopher nolan |
| 643 | `singer_bonnie` | `singer_bonnie_tyler` | 0.891 | 6 of 7/9 | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 834 | `bonnie_tyler` | `singer_bonnie_tyler` | 0.837 | 7 of 36/9 | 'heartbroken' catherine zeta-jones leads tributes to singer bonnie tyler |
| 824 | `bonnie` | `singer_bonnie_tyler` | 0.76 | 6 of 32/9 | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 798 | `declares` | `declares_iran` | 0.891 | 6 of 23/7 | oil surges as trump declares iran deal 'over' |
| 823 | `bonnie` | `singer_bonnie` | 0.891 | 6 of 32/7 | 'total eclipse of the heart' singer bonnie tyler dies aged 75 |
| 730 | `diarrhea` | `explosive_diarrhea` | 0.886 | 17 of 28/20 | 31 states are reporting cases of ‘explosive diarrhea’ parasite as outbreak continues to gr… |
| 751 | `blanche` | `todd_blanche` | 0.886 | 17 of 41/20 | all about todd blanche: at best, misleading; at worst, disingenuous |
| 228 | `semifinal` | `cup_semifinal` | 0.884 | 11 of 46/13 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 250 | `world_cup` | `cup_semifinal` | 0.725 | 8 of 166/13 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 11 | `lindsey` | `lindsey_graham_dies` | 0.881 | 16 of 156/19 | 'trump whisperer' lindsey graham dies suddenly / abc news |
| 2 | `lindsey_graham` | `lindsey_graham_dies` | 0.699 | 11 of 142/19 | 'trump whisperer' lindsey graham dies suddenly / abc news |
| 655 | `quarterfinal` | `cup_quarterfinal` | 0.881 | 16 of 36/19 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 200 | `cursor` | `codex_cursor` | 0.875 | 5 of 42/6 | favorpan/ai-tool-weekly-review structured weekly review for ai coding tools — analyze clau… |
| 215 | `codex` | `codex_cursor` | 0.875 | 5 of 90/6 | favorpan/ai-tool-weekly-review structured weekly review for ai coding tools — analyze clau… |
| 771 | `pleads` | `pleads_not_guilty` | 0.875 | 10 of 19/12 | abu trica pleads not guilty before a us federal court |
| 772 | `iceinvolved` | `iceinvolved_shooting` | 0.875 | 5 of 6/6 | live updates: ice-involved shooting in maine kills one person - cnn |
| 867 | `creed` | `creed_black_flag` | 0.875 | 5 of 7/6 | assassin's creed black flag resynced - a remake worthy of the wait |
| 27 | `spain` | `spain_wildfire` | 0.87 | 19 of 173/23 | 'we escaped spanish wildfire, but our friends lost their lives' |
| 743 | `wildfire` | `spain_wildfire` | 0.81 | 17 of 62/23 | 'we escaped spanish wildfire, but our friends lost their lives' |
| 31 | `spain` | `southern_spain` | 0.868 | 14 of 173/17 | at least 11 dead in southern spain wildfire amid heatwave |
| 746 | `warsh` | `kevin_warsh` | 0.868 | 14 of 38/17 | *the federal reserve fomc presser & rate decision / kevin warsh* |
| 649 | `inference` | `llm_inference` | 0.859 | 47 of 58/81 | adityaguhaa/nexusagent-mac turn your mac into an autonomous ai researcher using local llms… |
| 694 | `for_llm` | `llm_inference` | 0.596 | 3 of 7/81 | johnscheuer/inference-cost-calculator cost analysis tool for llm inference: $/token across… |
| 704 | `llm_llm` | `llm_inference` | 0.433 | 5 of 26/81 | cognizenorg/compatcanary one command to test openai-compatible apis for streaming, tools, … |
| 187 | `llm` | `llm_inference` | 0.402 | 12 of 195/81 | codewithfourtix/ember a from-scratch llm inference engine in rust: run a qwen2.5 model on … |
| 286 | `platner` | `graham_platner` | 0.858 | 59 of 133/73 | 'this movement was never about one person': maine democrats look to move on from graham pl… |
| 13 | `lindsey` | `lindsey_graham_de` | 0.852 | 4 of 156/5 | lindsey graham dead at 71 |
| 24 | `spain` | `trade_with_spain` | 0.852 | 4 of 173/5 | can trump really cut off trade with spain? |
| 79 | `widdecombe` | `ann_widdecombe_de` | 0.852 | 4 of 109/5 | ann widdecombe death latest: police launch murder investigation - bbc |
| 112 | `blockade` | `blockade_iran` | 0.852 | 8 of 36/10 | asx rises after us reimposes naval blockade on iran — as it happened |
| 61 | `iran` | `blockade_iran` | 0.783 | 7 of 183/10 | asx rises after us reimposes naval blockade on iran — as it happened |
| 123 | `grok` | `grok_build` | 0.852 | 4 of 20/5 | channely/ai-no-tun run chatgpt codex remote, grok build and other ai tools through clash o… |
| 144 | `senate` | `senate_seat` | 0.852 | 8 of 139/10 | graham platner, controversial maine us senate seat candidate, off ballot |
| 661 | `us_senate` | `senate_seat` | 0.438 | 2 of 11/10 | lindsey graham’s sister sworn in to fill his us senate seat |
| 153 | `wildfires` | `wildfires_southern` | 0.852 | 4 of 40/5 | crews battle deadly wildfires in southern spain |
| 305 | `usiran` | `renewed_usiran` | 0.852 | 4 of 39/5 | renewed us-iran war is hitting gulf countries hard |
| 697 | `nigel_farage` | `nigel_farage_clacton` | 0.852 | 4 of 39/5 | britain backs count binface to beat nigel farage in clacton by-election, poll shows |
| 773 | `farage` | `nigel_farage_clacton` | 0.714 | 3 of 86/5 | britain backs count binface to beat nigel farage in clacton by-election, poll shows |
| 734 | `khalifa` | `bin_khalifa` | 0.852 | 4 of 5/5 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 787 | `buckle` | `columns_buckle` | 0.852 | 4 of 5/5 | live: new york building will be stabilized after columns buckle |
| 818 | `altman` | `sam_altman` | 0.852 | 4 of 6/5 | elon musk and sam altman spar on x after apple files openai lawsuit |
| 861 | `assassin` | `assassin_creed` | 0.852 | 4 of 5/5 | assassin's creed: why pop culture is hooked to pirates |
| 866 | `creed` | `assassin_creed` | 0.852 | 4 of 7/5 | assassin's creed: why pop culture is hooked to pirates |
| 17 | `lindsey` | `sen_lindsey` | 0.844 | 26 of 156/33 | 'history will judge the complicit': the weeknight hosts reflect on sen. lindsey graham's c… |
| 87 | `france` | `tour_france` | 0.842 | 11 of 157/14 | cooling logistics more important than tactics at tour de france / new straits times |
| 216 | `gemini` | `google_gemini` | 0.842 | 11 of 84/14 | akshay2266/isometric-mto-generator isometric drawing → automated mto generator: an ai-powe… |
| 52 | `google` | `google_gemini` | 0.546 | 5 of 63/14 | anuragv28/enterprise-ai-knowledge-hub enterprise ai knowledge hub using retrieval-augmente… |
| 202 | `claude` | `chatgpt_claude` | 0.837 | 7 of 186/9 | 988hj7tczd-oss/awesome-ai-tools-ranking 🏆 ai 工具实时排行榜 — 200+ 模型用户投票驱动 ai-agents ai-ranking … |
| 223 | `chatgpt` | `chatgpt_claude` | 0.837 | 7 of 79/9 | 988hj7tczd-oss/awesome-ai-tools-ranking 🏆 ai 工具实时排行榜 — 200+ 模型用户投票驱动 ai-agents ai-ranking … |
| 282 | `platner` | `platner_drops` | 0.831 | 10 of 133/13 | graham platner drops out of maine senate race after sexual assault accusation |
| 783 | `erling` | `erling_haaland` | 0.831 | 20 of 26/28 | cold war steve on … erling haaland’s high-street invasion for norway v england |
| 724 | `haaland` | `erling_haaland` | 0.62 | 13 of 35/28 | cutting off erling haaland is key but norway are not just a one-man team / emma hayes |
| 140 | `argentina` | `england_argentina` | 0.828 | 13 of 105/17 | argentina's message to england: be ready. #worldcup #england #argentina #bbcnews |
| 74 | `england` | `england_argentina` | 0.665 | 9 of 170/17 | england vs. argentina: a football rivalry full of history |
| 71 | `england` | `england_norway` | 0.817 | 3 of 170/4 | the high-flying england vs. norway world cup bet that's got everyone talking |
| 111 | `strait` | `strait_of_hormuz` | 0.817 | 105 of 140/168 | 'don't talk about it': trump tells journalists to stop asking about strait of hormuz after… |
| 116 | `vows` | `denmark_vows_defend` | 0.817 | 3 of 32/4 | denmark pm vows to defend greenland after trump revives push for u.s. control |
| 793 | `denmark` | `denmark_vows_defend` | 0.817 | 3 of 6/4 | denmark pm vows to defend greenland after trump revives push for u.s. control - cnbc |
| 129 | `britain` | `britain_first_financial` | 0.817 | 3 of 112/4 | south sea bubble: the shoemaker’s son who sparked britain’s first financial crisis |
| 152 | `wildfires` | `spain_wildfires` | 0.817 | 9 of 40/12 | 'this landscape is completely charred': inside the village at epicentre of spain's wildfir… |
| 29 | `spain` | `spain_wildfires` | 0.645 | 6 of 173/12 | british expats feared dead during spanish wildfires as residents flee popular tourist spot |
| 201 | `doj` | `trump_doj` | 0.817 | 3 of 18/4 | 'whiff of jim crow:' yale students and faculty fight to stop deal with trump's doj |
| 267 | `thani` | `khalifa_thani` | 0.817 | 3 of 4/5 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 733 | `khalifa` | `khalifa_thani` | 0.714 | 3 of 5/5 | former emir of qatar sheikh hamad bin khalifa al thani dies aged 74 |
| 295 | `singapore` | `singapore_temasek` | 0.817 | 3 of 16/4 | crypto still 'off the table' for singapore's temasek, four years after ftx flop |
| 621 | `justices` | `court_justices` | 0.817 | 3 of 8/4 | knives out at us supreme court as justices’ squabbles go public |
| 650 | `inference` | `inference_llm` | 0.817 | 3 of 58/4 | jajmangold/fni8-serve w8a8 (int8 dp4a) inference server for nvidia volta / cmp 100-210, ov… |
| 653 | `coco` | `coco_gauff` | 0.817 | 3 of 5/4 | karolina muchova beats coco gauff in epic tie-break to reach wimbledon final |
| 656 | `mundial` | `del_mundial` | 0.817 | 12 of 35/16 | así ha sido la celebración de la familia real por el pase de españa a la final del mundial |
| 712 | `alltime` | `alltime_high` | 0.817 | 3 of 7/4 | june home sales disappoint as prices reach an all-time high |
| 714 | `llmsecurity` | `llm_llmsecurity` | 0.817 | 3 of 14/4 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection risks. zero-… |
| 186 | `llm` | `llm_llmsecurity` | 0.645 | 2 of 195/4 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection risks. zero-… |
| 703 | `llm_llm` | `llm_llmsecurity` | 0.645 | 2 of 26/4 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection risks. zero-… |
| 749 | `blanche` | `blanche_confirmation` | 0.817 | 6 of 41/8 | blanche confirmation ‘far from a certain thing’: fmr. federal prosecutor previews key hear… |
| 753 | `screenings` | `world_cup_screenings` | 0.817 | 3 of 4/6 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 754 | `screenings` | `cup_screenings` | 0.817 | 3 of 4/4 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 770 | `pleads` | `hearn_pleads` | 0.817 | 3 of 19/4 | alleged reflecting pool vandal david hearn pleads not guilty; lawyer calls him 'scapegoat' |
| 828 | `assassin_creed` | `assassin_creed_black` | 0.817 | 3 of 5/4 | all swords in assassin's creed black flag resynced and how to get them |
| 865 | `creed` | `assassin_creed_black` | 0.817 | 3 of 7/4 | assassin's creed black flag resynced - a remake worthy of the wait |
| 860 | `assassin` | `assassin_creed_black` | 0.645 | 2 of 5/4 | assassin’s creed black flag resynced review – bootyful high seas adventure, now with 20% m… |
| 831 | `tankers` | `oil_tankers` | 0.817 | 6 of 17/8 | russian attacks kill 6, wound 29, as ukrainian forces target oil tankers |
| 99 | `korea` | `south_korea` | 0.811 | 20 of 42/27 | anne’s royal meet and greet with a robot during south korea tour |
| 821 | `generativeai` | `generativeai_llm` | 0.806 | 11 of 96/15 | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai tools, agents… |
| 174 | `llm` | `generativeai_llm` | 0.76 | 10 of 195/15 | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai tools, agents… |
| 709 | `ai_llm` | `generativeai_llm` | 0.76 | 10 of 19/15 | ahdpe/awesome-ai-tools-2026 a curated, practical guide to the most useful ai tools, agents… |
| 833 | `modelcontextprotocol` | `mcp_modelcontextprotocol` | 0.804 | 19 of 46/26 | ahmedvnabil/humanitarian-mcp model context protocol server for humanitarian open data — un… |
| 148 | `senate` | `senate_campaign` | 0.802 | 8 of 139/11 | dem. graham plattner suspends senate campaign. what happens now? |
| 663 | `us_senate` | `senate_campaign` | 0.425 | 2 of 11/11 | graham platner ends u.s. senate campaign in maine |
| 240 | `fifa` | `fifa_world_cup` | 0.8 | 21 of 71/29 | "we were too sloppy technically": mbappe rues france's shortcomings after fifa world cup s… |
| 48 | `fifa_world` | `fifa_world_cup` | 0.728 | 18 of 29/29 | barcelona reach verbal agreement to sign germany international who did not make fifa world… |
| 246 | `world_cup` | `fifa_world_cup` | 0.395 | 4 of 166/29 | "we were too sloppy technically": mbappe rues france's shortcomings after fifa world cup s… |
| 100 | `korea` | `korea_times` | 0.793 | 10 of 42/14 | 100 university of seoul students embark on overseas study tours - the korea times |
| 28 | `spain` | `spain_belgium` | 0.783 | 7 of 173/10 | live: fans gather in brussels to watch spain v belgium world cup match |
| 12 | `lindsey` | `senator_lindsey` | 0.78 | 16 of 156/23 | "great american, patriot, friend, fearless leader": us officials and world leaders mourn p… |
| 739 | `khamenei` | `khamenei_funeral` | 0.778 | 9 of 33/13 | ali khamenei funeral: iran bids farewell to longtime supreme leader |
| 101 | `korea` | `the_korea_times` | 0.774 | 11 of 42/16 | 100 university of seoul students embark on overseas study tours - the korea times |
| 293 | `africa` | `south_africa` | 0.769 | 17 of 35/25 | another noakhali man shot dead in south africa |
| 25 | `spain` | `spain_sanchez` | 0.76 | 2 of 173/3 | spanish pm sanchez condemns predecessor's racist remarks on french football team |
| 32 | `epstein` | `epstein_files` | 0.76 | 4 of 34/6 | blanche faces grilling on epstein files, $1.8b fund & more in ag hearing |
| 55 | `iran` | `iran_tensions` | 0.76 | 2 of 183/3 | kalshi traders think gas prices will stay higher for longer as u.s.-iran tensions heat bac… |
| 67 | `england` | `norway_england` | 0.76 | 8 of 170/12 | cold war steve on … erling haaland’s high-street invasion for norway v england |
| 740 | `norway` | `norway_england` | 0.702 | 7 of 79/12 | get 40/1 odds on kane or haaland to have a shot in norway vs england |
| 93 | `rag` | `rag_react` | 0.76 | 6 of 183/9 | 1killermouse/poker-mind-gto-lab ai-assisted chinese texas hold'em gto trainer with rag coa… |
| 94 | `rag` | `rag_semanticsearch` | 0.76 | 4 of 183/6 | dephekt/cci-blackbook-mcp mcp server for semantic search over scanned / image-heavy pdfs: … |
| 690 | `semanticsearch` | `rag_semanticsearch` | 0.645 | 3 of 12/6 | dephekt/cci-blackbook-mcp mcp server for semantic search over scanned / image-heavy pdfs: … |
| 125 | `yamal` | `lamine_yamal` | 0.76 | 4 of 6/10 | lamine yamal está na final da copa do mundo. |
| 205 | `claude` | `claude_desktop` | 0.76 | 4 of 186/6 | mienetic/mnema 🧠 mnema — long-term memory for ai via mcp × vector db. solves the context-w… |
| 227 | `semifinal` | `world_cup_semifinal` | 0.76 | 14 of 46/21 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 249 | `world_cup` | `world_cup_semifinal` | 0.596 | 9 of 166/21 | bruce buffer announces france vs . spain world cup semifinal ⚽️ |
| 235 | `agentic` | `agentic_workflow` | 0.76 | 6 of 81/9 | canadiancowboy/a2x ai-native programming language and runtime. sigma isa, omega compiler, … |
| 242 | `agentic_ai` | `agentic_workflow` | 0.53 | 3 of 65/9 | di37/evalsurfer skill-first, agent-native evaluation protocol for ai apps agent-skills ai … |
| 232 | `workflow` | `agentic_workflow` | 0.453 | 2 of 27/9 | nothingnesses/agent-scaffold scaffold a repeatable agent workflow (front-load context, pla… |
| 280 | `thailand` | `discovered_thailand` | 0.76 | 2 of 24/3 | new dinosaur species as long as cricket pitch discovered in thailand |
| 294 | `africa` | `south_africa_world` | 0.76 | 2 of 35/3 | south africa world cup midfielder adams dies aged 25 |
| 625 | `finetuning` | `finetuning_llm` | 0.76 | 4 of 30/6 | baaabaei/fine-tuninng-qwen-2.5-vl fine-tuning qwen 2.5 vision-language model for custom ta… |
| 627 | `fatally` | `fatally_shoots` | 0.76 | 8 of 30/12 | an ice officer fatally shoots a mexican national in houston during an attempted traffic st… |
| 741 | `bélgica` | `españa_bélgica` | 0.76 | 2 of 9/3 | españa - bélgica, el partido de cuartos del mundial en imágenes |
| 744 | `wildfire` | `wildfire_kills` | 0.76 | 2 of 62/3 | fast-spreading wildfire kills at least 12 in southern spain |
| 794 | `senate_campaign` | `maine_senate_campaign` | 0.76 | 2 of 11/3 | graham platner ends maine senate campaign after sexual assault allegation |
| 796 | `new_fed` | `fed_chair` | 0.76 | 2 of 3/13 | trump's new fed chair just crushed gold, silver, bitcoin |
| 839 | `manuscripts` | `historic_china_manuscripts` | 0.76 | 2 of 3/3 | california man steals historic chinese manuscripts from ucla, using fake names, dummy docu… |
| 654 | `quarterfinal` | `world_cup_quarterfinal` | 0.742 | 16 of 36/25 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 624 | `hollywood` | `hollywood_reporter` | 0.739 | 7 of 27/11 | christopher nolan addresses ‘the odyssey’ backlash, explains why film uses modern dialogue… |
| 97 | `rag` | `rag_retrievalaugmentedgeneration_semanticsearch` | 0.731 | 5 of 183/8 | devbratghosh/enterprise-rag-assistant-v1.0 enterprise-grade retrieval-augmented generation… |
| 849 | `rag_retrievalaugmentedgeneration` | `rag_retrievalaugmentedgeneration_semanticsearch` | 0.559 | 3 of 28/8 | gpat22/langgraph-multi-agent-research-assistant designed and developed a multi-agent retri… |
| 51 | `semifinals` | `world_cup_semifinals` | 0.722 | 11 of 34/18 | england, argentina, france and spain set for world cup semifinals |
| 243 | `world_cup` | `world_cup_semifinals` | 0.453 | 4 of 166/18 | england, argentina, france and spain set for world cup semifinals |
| 44 | `ukraine` | `ukraine_targets` | 0.714 | 3 of 150/5 | gas queues grow as ukraine targets russia's fuel supply |
| 46 | `ukraine` | `ukraine_license` | 0.714 | 3 of 150/5 | trump offers ukraine license to manufacture patriots |
| 47 | `ukraine` | `ukraine_strikes` | 0.714 | 3 of 150/5 | american-made technology guiding ukraine's strikes into russia - cbs news |
| 56 | `iran` | `blockade_iran_ports` | 0.714 | 3 of 183/5 | oil rises as u.s. continues to strike tehran, reinstates blockade of iranian ports |
| 115 | `blockade` | `blockade_iran_ports` | 0.714 | 3 of 36/5 | trump says u.s. military will reimpose blockade on iranian ports - the washington post |
| 717 | `blockade_iran` | `blockade_iran_ports` | 0.714 | 3 of 10/5 | oil rises as u.s. continues to strike tehran, reinstates blockade of iranian ports |
| 265 | `russia` | `russia_strike` | 0.714 | 3 of 136/5 | people flee as russian strike hits near ukraine coffee shop |
| 752 | `trump_threatens` | `trump_threatens_iran` | 0.714 | 3 of 22/5 | trump threatens iran after ayatollah ali khamenei's funeral saw open calls for his killing |
| 759 | `holloway` | `max_holloway` | 0.714 | 3 of 11/5 | conor mcgregor and max holloway meet again at ufc 329 |
| 218 | `openai` | `llm_openai` | 0.699 | 11 of 128/19 | aiplaza-app/aiplaza-prompts open prompt gallery (writing, marketing, business, coding) — t… |
| 191 | `llm` | `llm_openai` | 0.482 | 5 of 195/19 | himynameisdavidkim/prompt-triwizard-skill llm prompt engineering for agent pipelines · wri… |
| 70 | `england` | `argentina_england` | 0.694 | 4 of 170/7 | argentina vs england schedule, tv channel for world cup match today |
| 137 | `argentina` | `argentina_england` | 0.596 | 3 of 105/7 | argentina vs england schedule, tv channel for world cup match today |
| 113 | `blockade` | `hormuz_blockade` | 0.694 | 4 of 36/7 | iran-us war latest: trump threatens to hit civilian targets in iran as us resumes strait o… |
| 124 | `china` | `china_economy` | 0.694 | 4 of 136/7 | china's economy picks up in june on rebounding u.s. exports, analysts say |
| 185 | `llm` | `llm_prompt` | 0.694 | 4 of 195/7 | harveyya/intent-engineering intent engineering: the engineering discipline for the human s… |
| 266 | `russia` | `russia_strikes` | 0.694 | 4 of 136/7 | 'felt like the whole building had been lifted up': ukraine residents recount russian strik… |
| 760 | `sinner` | `jannik_sinner` | 0.694 | 4 of 19/7 | jannik sinner beats alexander zverev to win wimbledon again |
| 748 | `bellingham` | `jude_bellingham` | 0.683 | 5 of 20/9 | bellingham best player at world cup - rooney |
| 738 | `khamenei` | `ali_khamenei` | 0.676 | 6 of 33/11 | ali khamenei funeral: iran bids farewell to longtime supreme leader |
| 190 | `llm` | `llm_python` | 0.668 | 8 of 195/15 | charumathid380/ai-chatbot a minimal conversational ai app using streamlit for the frontend… |
| 710 | `ai_llm` | `llm_python` | 0.438 | 3 of 19/15 | charumathid380/ai-chatbot a minimal conversational ai app using streamlit for the frontend… |
| 196 | `ai_agent` | `hermes_agent` | 0.668 | 8 of 199/15 | aaron-arn/samaritain samaritain — a self-improving ai agent by aaron dalibard. the name co… |
| 678 | `hermes` | `hermes_agent` | 0.622 | 7 of 17/15 | elevatormusic/hermes-classic-gold-pack classic gold theme + noir neko pets + custom status… |
| 38 | `agent` | `hermes_agent` | 0.438 | 3 of 189/15 | mr-ds-ml-85/strikedb strikedb is a unified database architecture for the ai era, where rel… |
| 203 | `claude` | `claude_code` | 0.656 | 96 of 186/190 | 0ss/unc 🦥 your ai agent, but lazy in the good way. writes less, spends less, ships more. t… |
| 217 | `claude_ai` | `claude_code` | 0.587 | 5 of 12/190 | alikwan/claude-code-agent-team battle-tested multi-agent dev team for claude code — 9 spec… |
| 45 | `ukraine` | `ukraine_make` | 0.645 | 2 of 150/4 | can ukraine make patriot missiles? |
| 68 | `england` | `argentina_and_england` | 0.645 | 4 of 170/8 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 138 | `argentina` | `argentina_and_england` | 0.645 | 4 of 105/8 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 110 | `strait` | `closes_strait` | 0.645 | 4 of 140/8 | breaking: us bombs iranian port cities as irgc closes strait of hormuz |
| 134 | `india` | `india_tourists` | 0.645 | 4 of 138/8 | indian tourists among 15 killed as speedboat capsizes in vietnam |
| 136 | `argentina` | `loss_to_argentina` | 0.645 | 2 of 105/4 | egyptian fa questions ‘fairness’ of loss to argentina amid refereeing furore |
| 231 | `zverev` | `alexander_zverev` | 0.645 | 4 of 12/8 | arthur fery's wimbledon run ended by alexander zverev in semi-finals |
| 234 | `agentic` | `agentic_coding` | 0.645 | 2 of 81/4 | arturkorb3/cli-agent zero-dependency, provider-neutral cli coding agent for node.js with a… |
| 261 | `israel` | `killed_israel_strike` | 0.645 | 2 of 119/4 | aid worker who organised world cup screenings in gaza killed in israeli strike |
| 263 | `samsung` | `samsung_galaxy` | 0.645 | 4 of 23/8 | samsung galaxy s26 ultra review: its huge screen blocks shoulder surfers from spying on yo… |
| 641 | `muchova` | `muchova_beats_gauff` | 0.645 | 2 of 8/4 | muchova beats gauff to reach wimbledon final |
| 747 | `infantino` | `gianni_infantino` | 0.645 | 2 of 14/4 | gianni infantino hints at expansion to 64-team world cup before 2030 event |
| 811 | `viking` | `viking_row` | 0.645 | 2 of 5/4 | norway fan reveals why he refuses to do 'stupid' viking row |
| 815 | `españa` | `francia_españa` | 0.645 | 2 of 50/4 | francia - españa, cable rojo y cable azul |
| 822 | `francia` | `francia_españa` | 0.645 | 2 of 31/4 | francia - españa, cable rojo y cable azul |
| 857 | `reinstates` | `trump_reinstates` | 0.645 | 2 of 7/4 | oil prices leap and stocks fall as trump reinstates hormuz blockade on iranian shipping |
| 199 | `ai_agent` | `autonomous_agent` | 0.618 | 12 of 199/26 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability-first reb… |
| 43 | `agent` | `autonomous_agent` | 0.486 | 7 of 189/26 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability-first reb… |
| 845 | `agent_ai` | `autonomous_agent` | 0.353 | 2 of 33/26 | axisrobo/aep aep: agent event protocol — open async event layer for agents, tools, memory,… |
| 92 | `rag` | `retrievalaugmented_generation_rag` | 0.614 | 5 of 183/11 | avaneeshravi21/personal-rag-chatbot a retrieval-augmented generation (rag) chatbot with hy… |
| 841 | `retrievalaugmented` | `retrievalaugmented_generation_rag` | 0.614 | 5 of 16/11 | agentdynarq/rag-pipeline a retrieval-augmented generation (rag) pipeline from scratch: chu… |
| 57 | `iran` | `iran_war` | 0.602 | 28 of 183/64 | 'forever war' risk, us sea drones & more: military experts on iran war |
| 73 | `england` | `england_world_cup` | 0.596 | 9 of 170/21 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 248 | `world_cup` | `england_world_cup` | 0.431 | 4 of 166/21 | 'animals', hand of god and beckham: argentina and england's world cup rivalry |
| 170 | `llm` | `models_llm` | 0.596 | 3 of 195/7 | fareedkhan-dev/glm-5.2-in-c glm-5.2, a 744 billion parameter mixture of experts model, in … |
| 173 | `llm` | `llm_localfirst` | 0.596 | 3 of 195/7 | luoziyan100/lumen 独立研究者的 ai 研究工作台:读论文,把报告写进真实工作区 / local-first ai research workbench ai-ag… |
| 219 | `openai` | `openai_codex` | 0.596 | 3 of 128/7 | busybee3333/sol-governed-codex sol-governed multi-agent coding workflow for openai codex w… |
| 214 | `codex` | `openai_codex` | 0.497 | 2 of 90/7 | busybee3333/sol-governed-codex sol-governed multi-agent coding workflow for openai codex w… |
| 629 | `fatally` | `ice_fatally` | 0.596 | 3 of 30/7 | backlash erupts after ice fatally shoots texas father |
| 784 | `tuchel` | `thomas_tuchel` | 0.596 | 3 of 18/7 | la paradoja de thomas tuchel: el planteamiento que dibuja en la pizarra no es la idea que … |
| 91 | `rag` | `python_rag` | 0.581 | 33 of 183/81 | aayushi-jha2018/mini-rag-pipeline a small, self-contained retrieval-augmented generation (… |
| 615 | `us_and_iran` | `iran_trade` | 0.581 | 11 of 27/27 | ceasefire cracks as us and iran trade airstrikes / abc news |
| 65 | `iran` | `iran_trade` | 0.351 | 2 of 183/27 | us and iran trade strikes, dispute whether hormuz is open |
| 40 | `agent` | `agent_autonomous` | 0.576 | 2 of 189/5 | imomkar/autodoc-agent an autonomous ai proposal generation agent using python, fastapi, an… |
| 63 | `iran` | `attacks_iran` | 0.576 | 2 of 183/5 | us attacks iran and tehran retaliates across the middle east, threatening a return to all-… |
| 672 | `deschamps` | `didier_deschamps` | 0.576 | 2 of 8/5 | 'extremely happy' deschamps gets the farewell game no-one wants |
| 685 | `fined` | `media_fined` | 0.576 | 2 of 9/5 | virgin media fined after hanging up on customers trying to cancel contracts |
| 727 | `yankee_stadium` | `yankee_stadium_concert` | 0.576 | 2 of 5/5 | chaos outside jay-z's yankee stadium concert after security breach delays |
| 737 | `khamenei` | `khamenei_burial` | 0.576 | 2 of 33/5 | iranians vow to stand firm as khamenei burial nears |
| 803 | `mou` | `trump_says_mou` | 0.576 | 2 of 5/5 | trump says mou is 'over', calls iranian leaders 'scum' following latest strikes |
| 198 | `ai_agent` | `coding_agent` | 0.565 | 10 of 199/26 | 10hq/grok-webui browser workspace for grok coding agent — thinking timeline, tools, git pu… |
| 41 | `agent` | `coding_agent` | 0.406 | 4 of 189/26 | hogan-tech/brand-loom open-source marketing skills that run on any model — with a hosted b… |
| 225 | `ai_coding` | `coding_agent` | 0.353 | 2 of 28/26 | kopon1/gen-z lowkey just works. your ai coding agent, but it says less and writes less. sa… |
| 33 | `agent` | `ice_agent` | 0.53 | 4 of 189/12 | colombian national killed by ice agent during operation in maine |
| 58 | `iran` | `trump_iran` | 0.53 | 2 of 183/6 | a dangerous blind spot in donald trump’s iran war strategy |
| 157 | `trump` | `trump_iran` | 0.53 | 2 of 192/6 | a dangerous blind spot in donald trump’s iran war strategy |
| 75 | `switzerland` | `argentina_switzerland` | 0.53 | 2 of 28/6 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 135 | `argentina` | `argentina_switzerland` | 0.53 | 2 of 105/6 | argentina vs switzerland: live watch party of the 2026 world cup quarterfinal |
| 264 | `russia` | `russia_oil` | 0.53 | 5 of 136/15 | russian oil sanctions: relief for india as us cuts proposed tariff from 500% to 100% |
| 635 | `tour_france` | `tour_de_france_2026` | 0.53 | 2 of 14/6 | tour de france 2026: stage 11 updates as riders head from vichy to nevers – live |
| 211 | `ai_tools` | `llm_tools` | 0.518 | 6 of 166/19 | chefcohen/corroborate-mcp honest claim corroboration for ai agents (mcp server): syndicati… |
| 702 | `llm_llm` | `llm_tools` | 0.482 | 5 of 26/19 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, disciplined projec… |
| 181 | `llm` | `llm_tools` | 0.445 | 4 of 195/19 | ansham1/ai_research_assistant_agent autonomous ai research assistant that can analyze docu… |
| 90 | `rag` | `rag_pipeline` | 0.512 | 4 of 183/13 | aayushi-jha2018/mini-rag-pipeline a small, self-contained retrieval-augmented generation (… |
| 64 | `iran` | `iran_attacks` | 0.507 | 3 of 183/10 | trump demands payment to protect gulf nations from iranian attacks |
| 680 | `retrieval` | `retrieval_augmented_generation` | 0.503 | 5 of 17/71 | jidnyasadthakre07/researchgpt-hybrid-rag-system production-ready hybrid rag application co… |
| 39 | `agent` | `agent_memory` | 0.501 | 7 of 189/24 | bobcatsfan33/loomdb an agent-native database. sessions are branches an agent can fork, mer… |
| 197 | `ai_agent` | `agent_memory` | 0.415 | 4 of 199/24 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, disciplined projec… |
| 844 | `agent_ai` | `agent_memory` | 0.357 | 2 of 33/24 | aloim/mosyn named after mnemosyne, the greek goddess of memory. shared, disciplined projec… |
| 209 | `ai_agents` | `llm_agents` | 0.501 | 7 of 200/24 | alexcard3/honest-signal a method for keeping ai-assisted research honest: pre-registration… |
| 183 | `llm` | `llm_agents` | 0.415 | 4 of 195/24 | can llm agents develop precognition? |
| 59 | `iran` | `new_strikes_iran` | 0.497 | 4 of 183/14 | trump backs down on hormuz toll, launches new strikes on iran / abc news |
| 62 | `iran` | `iran_conflict` | 0.497 | 2 of 183/7 | middle east experts assess latest escalation in u.s.-iran conflict |
| 69 | `england` | `england_and_argentina` | 0.497 | 2 of 170/7 | england and argentina renew football’s fiercest grudge match |
| 141 | `argentina` | `england_and_argentina` | 0.497 | 2 of 105/7 | england and argentina renew football’s fiercest grudge match |
| 88 | `france` | `france_spain` | 0.497 | 2 of 157/7 | france vs spain: the 2026 world cup’s best attack meets its best defence - opta analyst |
| 193 | `ai_agent` | `llm_agent` | 0.497 | 4 of 199/14 | navig-me/local-marketing local-only, agent-agnostic marketing/outreach skill: sqlite crm, … |
| 35 | `agent` | `llm_agent` | 0.448 | 3 of 189/14 | ancs21/codemode-workers expose any api to an llm agent as two sandboxed mcp tools (search … |
| 175 | `llm` | `llm_agent` | 0.399 | 2 of 195/14 | ancs21/codemode-workers expose any api to an llm agent as two sandboxed mcp tools (search … |
| 698 | `llm_llm` | `llm_agent` | 0.399 | 2 of 26/14 | aerkn1/jobhunt stateless automated job discovery and scoring service based on your cv ai a… |
| 60 | `iran` | `strikes_iran` | 0.49 | 22 of 183/80 | live updates: us launches fourth night of strikes on iran and restarts naval blockade / cn… |
| 160 | `trump` | `trump_administration` | 0.49 | 8 of 192/29 | eu rejects trump administration claims that icc threatens us sovereignty |
| 156 | `trump` | `trump_threatens` | 0.488 | 6 of 192/22 | hurricane trump threatens to blow china off course |
| 37 | `agent` | `agent_skill` | 0.484 | 4 of 189/15 | hanlulong/econ-paper-review-skill ai referee reports for economics papers — an agent skill… |
| 195 | `ai_agent` | `agent_skill` | 0.438 | 3 of 199/15 | atdy/maoxuan-product-agent 从《矛盾论》《实践论》完整推理结构蒸馏的中文产品决策 agent skill，支持 codex、claude code、cur… |
| 34 | `agent` | `multi_agent` | 0.478 | 8 of 189/31 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability-first reb… |
| 192 | `ai_agent` | `multi_agent` | 0.478 | 8 of 199/31 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability-first reb… |
| 843 | `agent_ai` | `multi_agent` | 0.389 | 4 of 33/31 | ovsilya/multi-agent-support-platform slack-native multi-agent ai support platform (fastapi… |
| 244 | `world_cup` | `world_cup_2026` | 0.477 | 9 of 166/35 | adityaraj1969/nexus-ai nexus ai is a next-generation smart stadium platform designed for t… |
| 171 | `llm` | `tools_llm` | 0.472 | 4 of 195/16 | bufferbrew/craftsman agent-discipline toolkit for claude code — minimal-diff coding, root-… |
| 212 | `ai_tools` | `tools_llm` | 0.429 | 3 of 166/16 | bufferbrew/craftsman agent-discipline toolkit for claude code — minimal-diff coding, root-… |
| 36 | `agent` | `agent_skills` | 0.47 | 15 of 189/61 | adamhjort/lovable-porting-agent a model-neutral agent skill and cli toolkit for moving lov… |
| 194 | `ai_agent` | `agent_skills` | 0.379 | 7 of 199/61 | 0ss/unc 🦥 your ai agent, but lazy in the good way. writes less, spends less, ships more. t… |
| 182 | `llm` | `cache_llm` | 0.462 | 4 of 195/17 | codewithfourtix/ember a from-scratch llm inference engine in rust: run a qwen2.5 model on … |
| 699 | `llm_llm` | `llm_evaluation` | 0.459 | 6 of 26/31 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against declared commit… |
| 177 | `llm` | `llm_evaluation` | 0.367 | 3 of 195/31 | dimaggi-ai/ontology-debt ontology debt: audit an llm's world-model against declared commit… |
| 159 | `trump` | `trump_wants` | 0.453 | 2 of 192/9 | hiltzik: trump wants to let companies make fewer disclosures, thus keeping investors in th… |
| 241 | `github` | `github_actions` | 0.453 | 2 of 21/9 | adding new workflows in github actions |
| 95 | `rag` | `rag_retrievalaugmentedgeneration` | 0.448 | 6 of 183/28 | ansham1/ai_research_assistant_agent autonomous ai research assistant that can analyze docu… |
| 172 | `llm` | `local_llm` | 0.442 | 8 of 195/39 | alex663028/pulse-agent pulse — hermes-style self-improving ai agent. reliability-first reb… |
| 158 | `trump` | `trump_accounts` | 0.438 | 2 of 192/10 | trump accounts program offers $1,000 seed for every eligible child born during his term |
| 179 | `llm` | `llm_security` | 0.438 | 5 of 195/25 | ai-blockchain-ventures/agentverify open-source security scanner for ai agents — checks age… |
| 700 | `llm_llm` | `llm_security` | 0.383 | 3 of 26/25 | foxck016077/agentaudit scan your ai agent prompts & transcripts for injection risks. zero-… |
| 54 | `iran` | `iran_strikes` | 0.425 | 4 of 183/22 | iran strikes, lindsey graham, apple takes openai to court and more in morning squawk |
| 247 | `world_cup` | `2026_world_cup` | 0.406 | 2 of 166/13 | france vs. spain odds, prediction, time: 2026 world cup semifinal picks from expert on 19-… |
| 42 | `agent` | `multi_agent_systems` | 0.392 | 2 of 189/15 | abhinoob1501/ramanujan autonomous ml research engineer - a multi-agent system that forms h… |

---
*Display-only layer (Board condition 1-7). Held-out wall verified live: scoring admission,*
*calibration, ledger enrollment, and the sweep contain zero references to entity_grouping.*