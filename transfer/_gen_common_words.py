"""
Generate transfer/common_words.txt — a static list of the most frequent ENGLISH
common words (nouns/verbs/adjectives/adverbs) used to reject generic single-word
"topics" (suffering, saying, exclusive, …) that volume alone would otherwise
let through. Run locally (needs `wordfreq`); the OUTPUT is committed so the
engine has NO runtime dependency or memory cost beyond the frozenset itself.

PROPER NOUNS we still want as real trend entities (countries + demonyms + major
geography) are SUBTRACTED from the list so 'japan'/'japanese'/'france' survive.
Tech/domain terms are exempted at RUNTIME (against DOMAIN_TERMS), so they need
not be subtracted here.
"""
from wordfreq import top_n_list

TOP_N = 11000   # ~covers everyday English; rarer/technical words fall through (kept)

# ── Proper-noun KEEP set: never treat these frequent words as generic junk ──
COUNTRIES = """
afghanistan albania algeria angola argentina armenia australia austria
azerbaijan bahrain bangladesh belarus belgium bolivia brazil bulgaria
cambodia cameroon canada chile china colombia congo croatia cuba cyprus
czech denmark ecuador egypt england estonia ethiopia europe finland france
georgia germany ghana greece guatemala haiti honduras hungary iceland india
indonesia iran iraq ireland israel italy jamaica japan jordan kazakhstan kenya
korea kosovo kuwait laos latvia lebanon liberia libya lithuania luxembourg
macedonia madagascar malaysia mali malta mexico moldova monaco mongolia
montenegro morocco mozambique myanmar namibia nepal netherlands holland
nicaragua nigeria norway oman pakistan palestine panama paraguay peru
philippines poland portugal qatar romania russia rwanda scotland senegal
serbia singapore slovakia slovenia somalia spain sudan sweden switzerland
syria taiwan tajikistan tanzania thailand tunisia turkey turkmenistan uganda
ukraine uruguay uzbekistan venezuela vietnam wales yemen zambia zimbabwe
america american britain british
""".split()

DEMONYMS = """
afghan albanian algerian angolan argentine argentinian armenian australian
austrian azerbaijani bahraini bangladeshi belarusian belgian bolivian
brazilian bulgarian cambodian cameroonian canadian chilean chinese colombian
congolese croatian cuban cypriot czech danish dutch ecuadorian egyptian
english estonian ethiopian european filipino finnish french georgian german
ghanaian greek guatemalan haitian honduran hungarian icelandic indian
indonesian iranian iraqi irish israeli italian jamaican japanese jordanian
kazakh kenyan korean kosovar kuwaiti laotian latvian lebanese liberian libyan
lithuanian luxembourgish macedonian malagasy malaysian malian maltese mexican
moldovan mongolian montenegrin moroccan mozambican namibian nepali dutch
nicaraguan nigerian norwegian omani pakistani palestinian panamanian
paraguayan peruvian philippine polish portuguese qatari romanian russian
rwandan scottish senegalese serbian singaporean slovak slovenian somali
spanish sudanese swedish swiss syrian taiwanese tajik tanzanian thai tunisian
turkish turkmen ugandan ukrainian uruguayan uzbek venezuelan vietnamese welsh
yemeni zambian zimbabwean
""".split()

GEO_MAJOR = """
africa asia antarctica arctic atlantic pacific mediterranean caribbean
tokyo paris london berlin moscow beijing shanghai delhi mumbai cairo
sydney toronto chicago boston dallas houston seattle miami denver atlanta
manhattan brooklyn hollywood vegas california texas florida ohio georgia
washington oregon nevada arizona alaska hawaii
""".split()

# A few high-frequency tokens that ARE legitimate standalone trend entities and
# happen to be frequent words. (Tech brands are handled via DOMAIN_TERMS at runtime.)
KEEP_EXTRA = """
trump biden obama putin xi modi musk bezos zuckerberg
nato gdp inflation recession tariff tariffs election senate congress
""".split()

# Organizations / acronyms / sports leagues that wordfreq ranks as frequent but
# are PROPER NOUNS — real trend entities, must NOT be treated as common words.
ORGS_ACRONYMS = """
fifa uefa nba nfl mlb nhl ncaa ufc espn olympics olympic worldcup
nasa esa spacex fda cdc sec fbi cia nsa irs doj epa faa
who wto imf opec eu un nato g7 g20 brics
fed treasury senate congress parliament whitehouse pentagon
ipo etf nasdaq dow nyse crypto bitcoin ethereum
""".split()

# Major consumer/tech BRANDS that collide with common English words (apple=fruit,
# amazon=river, meta, shell, visa, gap …) — keep them as entities.
BRANDS = """
apple amazon google meta microsoft tesla netflix disney nvidia intel amd
oracle adobe salesforce uber lyft airbnb spotify paypal stripe coinbase
nike adidas visa mastercard ford toyota honda boeing shell chevron
samsung sony huawei tiktok instagram youtube reddit twitter snapchat
openai anthropic deepmind starbucks mcdonalds walmart costco target
""".split()

KEEP = (set(COUNTRIES) | set(DEMONYMS) | set(GEO_MAJOR) | set(KEEP_EXTRA)
        | set(ORGS_ACRONYMS) | set(BRANDS))

words = []
for w in top_n_list("en", TOP_N):
    w = w.strip().lower()
    if len(w) < 3:            # 1-2 char tokens handled elsewhere
        continue
    if not w.isalpha():       # drop numbers / punctuation / contractions
        continue
    if w in KEEP:
        continue
    words.append(w)

words = sorted(set(words))
with open("common_words.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(words) + "\n")

# Sanity: the screenshot offenders MUST be rejected; the keepers MUST survive.
offenders = ["suffering", "saying", "exclusive", "feeling", "moment", "nothing"]
keepers = ["japan", "japanese", "france", "trump", "chatgpt", "ozempic"]
ws = set(words)
print(f"wrote {len(words)} common words")
print("offenders in list (should be True): ",
      {o: (o in ws) for o in offenders})
print("keepers in list (should be False): ",
      {k: (k in ws) for k in keepers})
