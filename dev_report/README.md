# What's coming near this home

This is a test of whether buyers, agents or investors would pay for a
one-page report on development applications within 500 m of an address.
It is deliberately not wired into the API yet. The point is to put a few
real reports in front of people first.

## Data

There are two City of Toronto open datasets, both refreshed daily. Checked
Nov 1, 2026, neither is marked retired, and both hold the same records the
[Application Information Centre](https://www.toronto.ca/aic/) shows.

| Dataset | Covers | Location |
|---|---|---|
| [Development Applications](https://open.toronto.ca/dataset/development-applications/) | rezonings and Official Plan amendments (OZ), site plans (SA), condo (CD), subdivision (SB), part-lot control (PL) | own X/Y (NAD27 MTM 10), matched to address points |
| [Committee of Adjustment Applications](https://open.toronto.ca/dataset/committee-of-adjustment-applications/) (active) | minor variances (MV), consents/severances (CO) | address only, geocoded with [Address Points](https://open.toronto.ca/dataset/address-points-municipal-toronto-one-address-repository/) |

The Development Applications dataset does **not** include Committee of
Adjustment files, even though its description says it does. The second
dataset fills that gap.

## Beyond Toronto

`gta.py` does the same lookup for other GTA municipalities. It uses their
public ArcGIS map services, which return everything within N metres of a
point directly, so nothing is bulk-downloaded. Addresses are geocoded with
Esri's public World Geocoder.

| Source | Covers | Records | Last updated (as of Nov 1, 2026) | Gaps |
|---|---|---|---|---|
| City of Brampton | rezonings/OPAs/subdivisions, site plans, condo plans, minor variances, consents, pre-consultations | ~16,600 incl. history | Oct 31, 2026 | full history, so it needs heavy filtering |
| York Region | active applications across Vaughan, Markham, Richmond Hill, Aurora, Newmarket, King, etc. | ~5,500 active | newest file Oct 25, 2026 | minor variances only where circulated to the Region |
| Town of Oakville | site plans, rezonings, OPAs, subdivisions, with home counts as numbers | 713 | Oct 31, 2026 | no minor variances or severances |

Not found in open data: Mississauga, Durham Region (Pickering, Ajax,
Whitby, Oshawa) and Burlington. Milton publishes subdivisions only.

```bash
pip install pyproj shapely
python3 dev_report/gta.py york     "40 Arnold Ave, Vaughan, ON"
python3 dev_report/gta.py oakville "120 Navy St, Oakville, ON"
python3 dev_report/gta.py brampton "25 Royce Ave, Brampton, ON"
```

Worked examples for each are in [`examples/`](examples/).

## Run it (Toronto)

```bash
pip install pandas pyproj
python3 dev_report/nearby.py "40 Bertmount Ave"     # city spelling, e.g. "Ave E"
python3 dev_report/nearby.py "40 Bertmount Ave" --radius 750 --refresh
```

The first run downloads about 200 MB into `dev_report/.cache/`, which is
gitignored. Paste the output under [`extraction_prompt.md`](extraction_prompt.md)
in Claude to get the report. See
[`examples/40-bertmount-ave.report.md`](examples/40-bertmount-ave.report.md)
for a full worked run.

## Test plan

1. Run 3 or 4 real addresses on different kinds of street: a house street
   next to a main street, a midtown street near the subway, and an
   inner-suburb street. Cross-check each against the AIC map.
2. Show the reports to an agent, someone house-hunting, and someone who
   bought recently. Ask:
   - Would this have changed your decision, or what you offered?
   - What's missing, or what would you not trust?
   - Would you pay for it? Is $29.99 (Neighbourly's permit report) too much,
     about right, or cheap?
   - Agents only: would you put this in a listing package?
3. If an agent says yes to the listing package, automate it. If everyone
   shrugs, try investors or small developers before building more.

## Known gaps

- **Building permits** aren't included, so garden suites and laneway houses
  that need no variance never show up.
- **City projects** (transit, road reconstruction) and anything outside the
  City of Toronto aren't included.
- **The "active" Committee of Adjustment list is stale.** It includes files
  from 2016. The prompt marks files over 3 years old as *old* and leaves
  them out.
- **Some applications can't be placed on the map.** About 200 city-wide
  have addresses that don't match the address points and are skipped (the
  script prints the count).
- **Distances can be off by about 20 m.** They are measured from the
  application's street address, not the edge of the site, so a large site
  can be closer than reported.
