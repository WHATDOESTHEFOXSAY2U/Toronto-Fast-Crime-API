# Worked example: 25 Royce Ave, Brampton

This is a real address on a residential street just south of Queen St W,
chosen as a test case. The input is
[`25-royce-ave-brampton.input.txt`](25-royce-ave-brampton.input.txt), from
`python3 dev_report/gta.py brampton "25 Royce Ave, Brampton, ON"` on Nov 1,
2026.

## The report

> **What's coming near 25 Royce Ave, Brampton** (within 500 m, checked Nov 1, 2026)
> - **Big:** a 22-storey building, 274 homes with 3 shops at the base, 90 m northeast on Henderson Ave. The public meeting has been held and the rezoning is still under review. If it's approved, construction is years away, and many approved GTA towers are on hold.
> - **Big:** a two-phase project at Henderson Ave and Haggert Ave S, 80 to 170 m southeast. Phase 1 is 148 stacked townhouses (approved; agreement being drawn up). Phase 2 is a 13-storey building with 293 homes (under review). Up to 441 homes are allowed on the site.
> - **Medium:** an 8-storey building, 109 homes over shops, 340 m southwest at 30 McLaughlin Rd S. Building details approved; agreement being signed.
> - **Medium:** an 8-storey, 153-room hotel with a banquet hall, 480 m northwest at 126 Nelson St W. City staff review complete.
> - **Medium:** a seniors' campus with a 4-storey long-term care home and a 6-storey seniors' rental building, 490 m southwest on McLaughlin Rd S. Height variance approved in 2023.
> - **Small:** 3 current house-scale files, including an early proposal for a fourplex on Royce Ave itself, 220 m southwest, and a sunroom 100 m west. About a dozen older files (lot splits, second units, home businesses) were left out.
> - **What it means:** this street sits beside one of Brampton's busier growth spots. Expect several years of construction 100 to 200 m away on Henderson and Haggert, about 700 new households within a few minutes' walk, and more traffic nearby.
> - *Source: City of Brampton Open Data, Planning & Land Use Development, Nov 1, 2026*

## Notes from doing this one

- Brampton publishes the most of the four: rezonings, site plans, condo
  plans, minor variances, severances, and even pre-consultations, which
  surface projects before they are formal applications. It was updated
  Oct 31, 2026.
- Because it is the full history back to the 1990s, the script drops
  closed, withdrawn and registered files (93 here) and approved files over
  6 years old (69 here). The prompt then leaves out Committee of
  Adjustment files over 3 years old.
- Two files from 2018 have been "In Review" with the note "Deferred
  Indefinitely". The data says open, but they aren't really live.
