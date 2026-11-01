# Extraction prompt

Paste everything below the line into Claude, then paste the output of
`python3 dev_report/nearby.py "<address>"` at the end, where the prompt says to.
If you are copying applications by hand from the Application Information
Centre instead, paste them in any layout, as long as each one has its file
number, address, type, status, date, description and distance from the home.

---

You are writing a one-page "what's coming near this home" report for someone
thinking about buying a house in Toronto. They are not a planner. They should
understand the whole report in 30 seconds.

Below the line `INPUT` is a list of open development applications near one
address, from City of Toronto records. Each `SITE` block is one property, with
its distance and direction from the home. A site can have more than one
application, for example a rezoning, then a site plan, then a condominium
file for the same building. Treat those as one project.

## Step 1: extract (show this as a table first)

One row per project:

| Column | What to write |
|---|---|
| site | street address, plus any "also filed under" addresses |
| distance | metres from the input, rounded to the nearest 10, plus direction |
| use | houses, condo, rental, mixed-use (homes over shops), office, retail, road, park, etc. Only say condo or rental if the description says so. |
| homes | number of homes or units. Count a new house as 1 and a fourplex as 4. Write "not stated" if the text doesn't give it. Never estimate it from floor area. |
| height | storeys. Write "not stated" if the text doesn't give it. |
| stage | one of: *submitted*, *refused – under appeal*, *rezoning approved*, *building details approved*, *minor variance approved*, *waiting for hearing*. See the status guide below. |
| file age | years since the application was submitted, as of the CHECKED date |
| size | Big, Medium or Small. See the rules below. |
| physical change? | no, if it only legalizes something already built, converts an existing building to condo ownership, or is a lot-line or easement change with no new building |
| summary | one plain-English line with no jargon, e.g. "Two-storey garage with a rooftop deck on the laneway." |

### Status guide

Planning applications (file numbers like `22 123729 STE 14 SA`):
- `OZ` is a rezoning and/or Official Plan amendment. It decides what can be
  built: use, height, number of homes.
- `SA` is site plan approval. It settles the building's detailed design. It
  is the last major city step before a building permit.
- `CD` is condominium approval. It is a paperwork step, often filed after
  construction starts.
- `SB` is a plan of subdivision. `PL` is part-lot control, which splits a
  lot into separate parcels.
- *Under Review*, *Application Received* and *Circulated* mean submitted.
- *Council Approved* or *OMB Approved* on an OZ file means rezoning approved.
- *NOAC Issued* means Notice of Approval Conditions. On an SA file, report it
  as building details approved.
- *OMB Appeal* or *Appeal Received* means the case is at the Ontario Land
  Tribunal, which usually takes a year or more to decide.
- *Draft Plan Approved* and *Final Approval Completed* mean approved.

Committee of Adjustment applications (file numbers like `A0615/26TEY` or
`B0051/22TEY`; `A` is a minor variance, `B` is a consent or severance):
- *Accepted*, *Application Received*, *In Process*, *In Progress*,
  *Prepare Notice*, *Notice Prepared*, *Tentatively Scheduled*,
  *Hearing Scheduled*, *Postponed* and *Deferred* mean waiting for hearing.
- *Approved*, *Approved with Conditions*, *Conditional Consent* and
  *Await Expiry Date* mean approved.
- *TLAB Appeal* means appealed to the Toronto Local Appeal Body. If the
  decision was Refused, it is refused – under appeal.

Other GTA municipalities (Brampton, York Region, Oakville) use their own
words for the same stages:
- *Pre Consultation* (Brampton): an early idea discussed with city staff.
  It is not an application yet. Report it as "early proposal".
- *In Review*, *In Circulation*, *Open*, *Submitted*, *Deemed Complete* and
  *In Progress (Review / ...)* mean submitted.
- *In Review-Public Mtg Complete* and *Staff Review Complete* mean
  submitted, public meeting held.
- *Council Approval*, *Approved*, *Draft Approved*, *LPAT Approved*,
  *OMB - Approved* and *In Progress (Finalization / Appeal Period)* mean
  rezoning approved. On a site plan they mean building details approved.
- *Site Plan Agreement Prep*, *Agreement Execution* and *Clearing
  Conditions* mean building details approved, with final paperwork being
  done.
- *Final and Binding* means minor variance approved.
- *Appealed*, *Under Appeal* and *In Appeal* mean at the Ontario Land
  Tribunal.
- *In Progress (Finalization / Construction)* means under construction or
  built.
- Outside Toronto, distances are measured to the nearest edge of the site,
  not its street address.

### Size rules

- **Big:** 13 or more storeys, or 150 or more homes.
- **Medium:** 4 to 12 storeys, 10 to 149 homes, or any new non-house
  building, such as a store, office, school, or road and transit work.
- **Small:** everything house-scale, such as additions, garages, decks,
  laneway and garden suites, new houses, multiplexes of up to 6 units, and
  lot splits.

### Flags

- A Committee of Adjustment file more than 3 years old is probably built,
  abandoned or forgotten. Mark it *old*.
- An approved planning file submitted more than 5 years ago may already be
  built, or may have stalled. Mark it *check: may be built or stalled*. Do
  not guess which.

## Step 2: write the report

Use exactly this format. Keep it under 150 words, not counting the source
line.

```
**What's coming near <ADDRESS>, Toronto** (within <RADIUS>, checked <CHECKED>)
- **Big:** ...
- **Medium:** ...
- **Small:** ...
- **What it means:** ...
- *Source: City of Toronto Application Information Centre (open data), <CHECKED>*
```

Rules:
1. Within each size, list the largest project first. Give each Big or
   Medium project its own bullet: what it is, homes, height, distance and
   direction, stage, and what happens next in plain words. Use several Big
   or Medium bullets if needed, but no more than 3 of each. Group any extras
   into one line.
2. If a size has nothing, say so in one line, e.g. "**Big:** none. No towers
   or large projects proposed within 500 m." A buyer finds that just as
   useful.
3. Small projects get one bullet total. Give the count and the 2 or 3 that
   matter most: the closest, any new homes such as a multiplex or laneway
   house, and anything on the same street. Leave out *old* files and files
   with no physical change, except to say how many you left out.
4. An approval is not construction. For anything approved but not yet
   built, say what still has to happen. For Big projects, add that many
   approved GTA towers are on hold in the current market.
5. Add a single **Also:** bullet only for non-housing items a buyer would
   notice, such as a new road, school or transit work.
6. "What it means" is one or two sentences about daily life: will the street
   itself change, more neighbours or shops, construction noise and roughly
   where, more traffic. Base it only on the input. Do not predict prices or
   property values.
7. Never invent a number. If the input doesn't give homes or height, say
   "size not stated".
8. Use distances rounded to the nearest 10 m and plain directions such as
   "north" or "southeast". Do not give coordinates.

INPUT
<paste the nearby.py output here>
