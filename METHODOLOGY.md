# Weekly Trends — Methodology v3 (broad-scan + routine/signal classification)

## 1. Data collection (one call per country, not per query)
For each country listed in config/regions.json:
  https://serpapi.com/search?engine=google_trends_trending_now&geo=<COUNTRY>&hl=<LANG>&category_id=b&api_key=$SERPAPI_API_KEY
Then repeat with category_id=t.
(b = Business, t = Sci/Tech — filters out sports/celebrity noise at the source.)

Each call returns ~15-30 trending queries WITH traffic estimates and related queries already
included. Budget: 17 countries × 2 categories = ~34 calls/week, plus up to 10 optional
deep-dive calls (Step 8) = ~44/week max. Free tier is 250/month (~60/week), so check
plan_searches_left first; if under 60, drop the category_id=t pass and keep Business only.

If a call errors or returns nothing for a country, mark that country no_data for the week and
continue. Never fabricate entries to fill a gap.

## 2. Pool assembly
Merge all countries into one candidate pool (expect 150-400 raw items). Deduplicate by English
meaning after Step 3, not by string match — the same trend surfaces under different wording in
different languages and must collapse into one entry.

## 3. Translate to English (mandatory)
For every candidate, write a plain English gloss of its meaning, not a transliteration:
  "как сэкономить заряд на айфоне" -> "iPhone battery saving tips"
The final report shows ONLY the English gloss. Never print the original-language string or
name the source language anywhere in the report.

## 4. Classify: NOISE / ROUTINE / SIGNAL
Judgment step, not a keyword script.

- NOISE — celebrity, sports, politics, or a news event with no plausible thing a business could
  be built around (a person's name, a match score, "election results"). Discard; do not score,
  do not ledger.
- ROUTINE — evergreen daily-life demand: either obviously perennial on sight ("where to buy
  groceries", "how to apply for a driver's licence", "restaurant near me"), or present in the
  ledger 8+ weeks with a flat pattern. Real demand, zero trend signal. Ledger it, list it as
  one line of context, never feature it as a finding.
- SIGNAL — a hypothesis about an emerging trend. Requires EITHER:
  (a) not in the ledger before AND tied to a specific nameable product, technology, service, or
      format — not a generic need. "AI video editing tool" qualifies; "how to make money" does not.
  OR
  (b) in the ledger under 8 weeks AND still growing week-over-week — a sustained climb, not a
      single spike that already decayed.

When a candidate is genuinely ambiguous between ROUTINE and SIGNAL, classify it ROUTINE and note
it in the ⚠️ section. A missed signal costs one week; a false signal pollutes the ledger for
months and gets tracked as a trend that never existed.

## 5. Update data/query_ledger.json — every run, this is the memory
Schema, keyed by stable English slug:
{
  "iphone-battery-saving-tips": {
    "first_seen": "2026-08-08",
    "status": "signal",
    "weekly": {
      "2026-08-08": {"interest_avg": 62, "regions": {"RU": 100, "KZ": 36}, "traffic": 20000}
    }
  }
}
status is one of: routine | signal | confirmed_trend | decayed

Transition rules:
- signal + growth 3 consecutive weeks -> confirmed_trend
- signal or confirmed_trend + decline 2 consecutive weeks -> decayed (kept for history, dropped
  from active hypotheses)
- routine never promotes on ordinary weekly noise; only a sustained 3-week climb moves it to
  signal, and note the reclassification explicitly in the report
- decayed can return to signal if it climbs 3 consecutive weeks again — note it as a returning
  signal, they matter

Append this week's data point to every candidate's weekly map, including routine entries.

## 6. Regional distribution tables
For every active SIGNAL and CONFIRMED_TREND entry, build a markdown table:
- rows = English query gloss
- columns = US | EU | LatAm | CIS | Asia | AfricaME | Russia | WoW %
- cells = interest value 0-100 for the week (blank if no data for that region)
- WoW % = change in interest_avg vs last week's ledger entry; blank on first week

Russia is a separate column from CIS by design: the point is to see whether Russian-language
search picks up an emerging trend at the same time as other regions or lags behind it. When a
signal appears in other regions but is absent or much weaker in the Russia column, say so
explicitly and give the lag in weeks if the ledger shows when it first appeared elsewhere.

## 7. Report structure
Bilingual, Russian block first, then English block. Query names and tables are English in BOTH
blocks — only the surrounding commentary is translated.

- 🆕 New signal hypotheses this week
- 📈 Growing signals (2+ weeks, still rising) — include the regional table here
- ✅ Confirmed trends (3+ consecutive weeks of growth) — the real "new AI moment" candidates
- 🏛️ Routine demand (one line each, context only)
- 📉 Decayed (previously flagged, now declining — worth knowing what NOT to chase)
- ⚠️ Ambiguous / data problems (no_data countries, suspected geo-normalisation artifacts,
  classification judgment calls)

Note explicitly when a high interest value likely comes from Google Trends normalisation on a
small absolute volume (a tiny country scoring 100) rather than real demand — flag it, don't
build a hypothesis on it.

If a section is empty this week, write one line saying so. Do not pad it.

## 8. Optional deep-dive (only for the top 3-5 SIGNAL candidates, only if quota allows)
For a candidate worth verifying further, use the per-query engine for a proper regional read:
  engine=google_trends&q=<QUERY>&data_type=GEO_MAP_0&date=today%203-m
and optionally data_type=RELATED_QUERIES for the strongest region. This is verification, not
discovery — never use it to build the pool.

## Do not
- Never show the source language of a query, or the original-language string, in the report.
- Never promote ROUTINE to SIGNAL on presence alone — it needs the growth pattern above.
- Never use the per-query engine as the discovery mechanism; trending_now is the source.
- Never fabricate a number when data is missing — mark no_data.
