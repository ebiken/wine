# Seed data validation (web check)

**Scope:** `winedb/data/seed/*.yaml` checked against public sources (TTB/Federal Register, producer sites, Wikipedia, regional associations) on **2026-04-06**.

**Note:** This file lists items that **differ from** or **need clarification vs** commonly cited current data. Absence from this list does not mean every field was verified line-by-line (the AVA file alone has hundreds of entries, many with `null` dates).

---

## Confirmed accurate (spot checks)

| File | Item | Notes |
|------|------|--------|
| `wines.yaml` | 2021 Lucia Estate Cuvee: 2,256 cases, blend 60/23/17, Fall 2022 release | Matches Pisoni/Lucia tech sheet material ([blog.pisonivineyards.com tech sheet](https://blog.pisonivineyards.com/tech-sheets/2021-lucia-pinot-noir-estate-cuvee/)). |
| `wineries.yaml` | Morgan Winery founded 1982; Double L planted 1996 | Consistent with Morgan’s own history pages. |
| `ava.yaml` | North Coast `ttb_approval_date: 1983-09-21` | Matches widespread references (e.g. Wikipedia) to **21 Sep 1983**. |
| `ava.yaml` | Nashoba Valley & Nine Lakes `ttb_approval_date: 2026-04-23` | Matches **effective date** of final rules; see caveat below. |
| `persons.yaml` | Julien Howsepian as Kosta Browne winemaker | Confirmed on [kostabrowne.com/winemaker](https://kostabrowne.com/winemaker) (appointed **2019**). |

---

## `ava.yaml` — update or clarify

### Monterey AVA — `total_acres` / `planted_acres` / `ttb_approval_date`

- **Seed:** `total_acres: 40000`, `planted_acres: 45000`, `ttb_approval_date: "1984-01-01"`.
- **Issue:** Planted acreage **cannot** exceed total AVA area; the pair is internally inconsistent.
- **Web (typical ranges):** Total area is often given on the order of **hundreds of thousands of acres** (e.g. Wikipedia cites ~640,000 acres / ~1,000 sq mi for the AVA; another common figure is ~360,000 acres depending on source/era). Planted vineyard area is commonly cited around **~40,000 acres**, not 45,000.
- **TTB date:** Sources cite establishment **16 July 1984** (with later amendments), not `1984-01-01`.
- **Action:** Replace total/planted with TTB-aligned or single-source figures; fix `ttb_approval_date` to the actual final-rule date (confirm on [TTB AVA materials](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/established-avas)).

### Napa Valley AVA — `total_acres` / `planted_acres`

- **Seed:** `total_acres: 479000`, `planted_acres: 45000`.
- **Web:** Napa Valley AVA total area is widely reported around **~252,000–253,000 acres**; planted vineyard area **~47,000 acres** (e.g. Napa Valley Vintners fast facts, Wikipedia).
- **Action:** Correct `total_acres` (479,000 does not match standard Napa AVA totals). Consider updating `planted_acres` to ~47k if you want parity with trade-body figures.

### Howell Mountain AVA — `ttb_approval_date`

- **Seed:** `"1983-11-30"`.
- **Web:** Established **30 December 1983** (month is **December**, not November) — TTB/Wikipedia/Howell Mountain association materials agree.
- **Action:** Set to `1983-12-30` (or exact TTB citation).

### Los Carneros AVA — `parent_ava` / `ttb_approval_date` / geography

- **Seed:** `parent_ava: Napa Valley`, `county: null`, `ttb_approval_date: "1983-08-17"`.
- **Web:** Carneros spans **Napa and Sonoma**; hierarchically it is described as lying within **Napa Valley**, **Sonoma Valley**, and **North Coast** (see [Wikipedia](https://en.wikipedia.org/wiki/Los_Carneros_AVA), TTB exhibit PDFs). TTB list often uses **18 Aug 1983** (off by one day from seed — confirm primary source).
- **Action:** If the schema allows only one parent, document the simplification in seed comments; otherwise model cross-county/parent reality. Verify exact establishment date against TTB.

### Wild Horse Valley AVA — `county`

- **Seed:** `county: Napa`.
- **Web:** AVA **straddles Napa and Solano** counties (Wikipedia, CFR references).
- **Action:** Use `null`, a multi-county representation, or split if the schema supports it.

### Santa Cruz Mountains AVA — `parent_ava`

- **Seed:** `parent_ava: null`.
- **Web:** Treated as part of the **Central Coast** macro-AVA / region in TTB and regional marketing (e.g. Wikipedia lists it under Central Coast).
- **Action:** Set `parent_ava: Central Coast` if parent links are meant to mirror TTB nesting.

### Champlain Valley of New York — `ttb_approval_date`

- **Seed:** `"2016-08-21"`.
- **Web:** Federal Register final rule published **22 Aug 2016**; effective **21 Sep 2016** ([Federal Register document](https://www.federalregister.gov/documents/2016/08/22/2016-19992/establishment-of-the-champlain-valley-of-new-york-viticultural-area)).
- **Action:** Use `2016-08-22` if the field stores publication date, or `2016-09-21` if it stores effective date — align field meaning across all AVAs.

### Nashoba Valley (MA) & Nine Lakes of East Tennessee — field meaning

- **Seed:** `ttb_approval_date: "2026-04-23"` for both.
- **Web:** TTB **established** both in rules published **24 Mar 2026**; **effective 23 Apr 2026** ([Nashoba FR](https://www.federalregister.gov/documents/2026/03/24/2026-05730/establishment-of-the-nashoba-valley-viticultural-area), [Nine Lakes FR](https://www.federalregister.gov/documents/2026/03/24/2026-05731/establishment-of-the-nine-lakes-of-east-tennessee-viticultural-area)).
- **Action:** If `ttb_approval_date` means “effective date,” current values are fine; if it means “establishment/published,” use **2026-03-24** or document the column semantics in the YAML header.

### Santa Lucia Highlands — description / acreage context

- **Seed:** `total_acres: 21772`, `planted_acres: 5000`; description cites bench elevations **1,200–2,200 ft** and “117th appellation.”
- **Web:** “117th AVA” and **May 1992** establishment check out (Wikipedia). Total ~22k acres is in-family with sources. **Elevation:** official site copy describes vineyard elevations from roughly **40 ft up to ~2,330 ft** across the AVA ([santaluciahighlands.com](https://www.santaluciahighlands.com/vineyards/overview-of-our-vineyards/)), so the 1,200–2,200 band is **not** the full vertical range—tighten wording or cite it as a typical planting band, not the AVA’s full limits.

---

## `vineyards.yaml` — update

### Sleepy Hollow Vineyard — `total_acres`

- **Seed:** `total_acres: 175`.
- **Web (Talbott / Gallo brand site):** The estate is described as spanning **~500 acres** of varied terrain, with **565 planted acres** across North/West/South parcels ([talbottvineyards.com/sleepy-hollow-vineyard](https://www.talbottvineyards.com/sleepy-hollow-vineyard/)).
- **Action:** Replace 175 with **~500** (gross) and/or add a separate planted-acres field if the schema gains one; 175 is not consistent with producer documentation.

### Garys’ Vineyard — `elevation_ft_low` / `elevation_ft_high`

- **Seed:** `300` / `400`.
- **Web:** Producer/regional copy often cites **up to ~400 ft** site elevation while also saying the site sits **~500 ft above the Salinas Valley floor** (different datums). 
- **Action:** Reconcile elevation fields with a single definition (MSL vs “above valley floor”) and cite the source in the description.

---

## `persons.yaml` / `wineries.yaml` — update (Talbott)

### David Coventry — tenure at Talbott

- **Seed:** Biography and winery text imply he is current head winemaker from **2016**.
- **Web:** Press coverage describes him joining Talbott around **2017**; later articles state he **left** Talbott. The **current** Talbott site names **Kamee Knutson** as winemaker for Sleepy Hollow ([talbottvineyards.com](https://www.talbottvineyards.com/sleepy-hollow-vineyard/)).
- **Action:** Update biographies and winery descriptions: Coventry **~2017–** (end date TBD from HR/press), add **Kamee Knutson** if the persons table should reflect current leadership.

### Julien Howsepian — biography detail

- **Seed:** “Head Winemaker” without year.
- **Web:** Named Kosta Browne’s (third) winemaker in **2019** ([kostabrowne.com/winemaker](https://kostabrowne.com/winemaker)).
- **Action:** Optional enrichment: add **2019** appointment to biography for precision.

---

## `grape_varieties.yaml` — optional / low priority

### Catawba — `name_synonyms`

- **Seed:** `"Arkansas, Michigan, Cherokee"`.
- **Web:** UC Davis FPS and other databases list **Arkansas**, **Michigan**, **Cherokee**, etc. as **historic synonyms** for Catawba—not US state references.
- **Action:** No change required for accuracy; consider expanding or annotating so readers do not misread them as geography.

### Muscadine — `color: white`

- **Seed:** `color: white` for the variety name “Muscadine.”
- **Web:** *Vitis rotundifolia* includes **bronze and dark-skinned** cultivars; treating “Muscadine” as uniformly white is misleading.
- **Action:** Use `null`, `mixed`, or model specific cultivars (e.g. Carlos, Noble) with correct colors.

---

## Suggested follow-up (not fully audited)

- **AVA file:** Fill `ttb_approval_date: null` entries from [TTB AVA establishment list](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/ava-establishment-dates) in a bulk pass.
- **Hierarchy:** Reconcile all parent links against TTB nesting (e.g. Los Carneros, Santa Cruz Mountains, multi-state AVAs).
- **Wines:** Spot-check remaining `production_cases` / `release_date` fields against current tech sheets where still null.

---

## Sources (representative)

- TTB: [Established AVAs](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/established-avas), [AVA establishment dates](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/ava-establishment-dates)
- Federal Register: Nashoba Valley (2026-05730), Nine Lakes (2026-05731), Champlain Valley NY (2016-19992)
- Producers: [Pisoni/Lucia blog](https://blog.pisonivineyards.com/), [Talbott Sleepy Hollow](https://www.talbottvineyards.com/sleepy-hollow-vineyard/), [Kosta Browne winemaker](https://kostabrowne.com/winemaker), [Morgan Winery history](https://www.morganwinery.com/about-us/winemaking-history/)
- Reference: Wikipedia pages for Napa Valley AVA, Monterey AVA, Howell Mountain AVA, Los Carneros AVA, Wild Horse Valley AVA, Santa Cruz Mountains AVA, Santa Lucia Highlands AVA
