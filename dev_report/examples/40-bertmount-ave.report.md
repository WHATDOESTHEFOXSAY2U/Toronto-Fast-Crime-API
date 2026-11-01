# Worked example: 40 Bertmount Ave (Leslieville)

This is a real address on a residential street. It was chosen as a test
case, and as far as we know it is not for sale. The input is
[`40-bertmount-ave.input.txt`](40-bertmount-ave.input.txt), from
`python3 dev_report/nearby.py "40 Bertmount Ave"` on Nov 1, 2026. Below is
what [`extraction_prompt.md`](../extraction_prompt.md) produces from that
input.

## Step 1: extraction

| # | Site | Distance | Use | Homes | Height | Stage | Age (years) | Size | Physical change? | Summary |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1233 Queen St E (also 77 Leslie St, 1243 Queen St E) | 460 m E | mixed-use | 142 | 9 | building details approved | 4.6 | Medium | yes | 9-storey building with 142 homes and a small amount of ground-floor commercial space. |
| 2 | 1001 Queen St E | 290 m SW | mixed-use | 16 | 6 | building details approved | 8.4 | Medium | yes | 6-storey building, 16 homes over ground-floor shops. *Check: may be built or stalled.* |
| 3 | 675 Eastern Ave | 470 m S | road | — | — | building details approved (Dec 2025) | 6.0 | Medium | yes | New private road with public access linking Eastern Ave and Lake Shore Blvd E. |
| 4 | 9 Peyton Lane | 420 m N | houses | 4 | 3 | waiting for hearing | 1.5 | Small | yes | New 3-storey fourplex on the lane, each unit with a garage. |
| 5 | 27 Brooklyn Ave | 50 m SW | houses | 0 | 2 | waiting for hearing | 0.2 | Small | yes | Two-storey laneway garage with a rooftop deck. |
| 6 | 111 Caroline Ave | 190 m S | houses | 0 | 1 | waiting for hearing | 0.0 | Small | yes | One-storey garage. |
| 7 | 111 Bertmount Ave | 210 m N | houses | not stated | not stated | waiting for hearing | 0.0 | Small | yes | House addition, no details published yet. |
| 8 | 45 Jones Ave | 210 m E | houses | 1 | 2 | refused – under appeal | 1.3 | Small | **no** | Legalize a rear addition that was built without a permit. |
| 9 | 31 Bertmount Ave | 50 m E | houses | not stated | not stated | waiting for hearing | 5.0 | Small | yes | New house, no details published. *Old.* |
| 10 | 29 Boston Ave | 290 m SW | houses | 0 | 1 | minor variance approved | 3.1 | Small | yes | Laneway garage. *Old.* |
| 11 | 65 Caroline Ave | 310 m S | houses | 0 | 1 | refused – under appeal | 5.4 | Small | yes | Rear deck with privacy screen. *Old.* |
| 12 | 17 Curzon St | 340 m E | houses | not stated | 3 | waiting for hearing | 6.4 | Small | yes | Third-storey and rear additions. *Old.* |
| 13 | 68 Dagmar Ave | 360 m N | houses | not stated | 3 | minor variance approved | 10.0 | Small | yes | Rear and third-floor additions. *Old.* |
| 14 | 199 Jones Ave | 500 m N | houses | 2 lots | not stated | refused – under appeal | 4.4 | Small | yes | Split one lot into two undersized lots. *Old.* |

## Step 2: the report

> **What's coming near 40 Bertmount Ave, Toronto** (within 500 m, checked Nov 1, 2026)
> - **Big:** none. No towers or large projects proposed within 500 m.
> - **Medium:** 9-storey building, 142 homes with shops on the ground floor, 460 m east at Queen St E and Leslie St. Building details approved. It still needs a building permit, and no start date is on file.
> - **Medium:** 6-storey building, 16 homes above shops, 290 m southwest at 1001 Queen St E. Building details were approved back in 2018, so it may already be built or may have stalled. Worth a walk past.
> - **Small:** 4 current house-scale files. The closest is a two-storey laneway garage with a rooftop deck, 50 m southwest (hearing scheduled). There's also a new fourplex on Peyton Lane, 420 m north, and an addition on Bertmount itself, 210 m north. 7 old or paperwork-only files were left out.
> - **Also:** a new private road with public access linking Eastern Ave and Lake Shore Blvd E, 470 m south, approved Dec 2025.
> - **What it means:** the block itself stays houses. Expect ordinary renovation noise nearby, and a mid-rise at Queen and Leslie that will add about 140 households and some shops, with construction there once it starts.
> - *Source: City of Toronto Application Information Centre (open data), Nov 1, 2026*

## Notes from doing this one

- I didn't cross-check this against the AIC map itself, because the AIC
  site blocks automated access from the environment this was made in. Before
  showing the report to anyone, open the AIC map at this address and compare.
  Ten minutes of that tells you whether the open data misses anything.
- Half the house-scale files are stale. The city's "active" Committee of
  Adjustment list still includes a 2016 file. Without the *old* rule, the
  report would overstate how much is going on.
