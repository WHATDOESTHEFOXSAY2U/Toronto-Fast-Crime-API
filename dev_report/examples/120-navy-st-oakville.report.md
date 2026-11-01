# Worked example: 120 Navy St, Oakville

This is a real address in downtown Oakville, chosen as a test case. The input
is [`120-navy-st-oakville.input.txt`](120-navy-st-oakville.input.txt), from
`python3 dev_report/gta.py oakville "120 Navy St, Oakville, ON"` on Nov 1,
2026.

## The report

> **What's coming near 120 Navy St, Oakville** (within 500 m, checked Nov 1, 2026)
> - **Big:** 12-storey buildings with about 293 homes and shops on the ground floor, 100 m north at Randall, Navy and Church St. Building details approved; final conditions are being cleared. Next comes a building permit. Many approved GTA projects are on hold, so timing is uncertain.
> - **Big:** a 10-storey building with 152 homes over shops, 330 m southwest at 42 Lakeshore Rd W. Now at the Ontario Land Tribunal, which usually takes a year or more to decide.
> - **Big:** a 222-suite retirement home, 460 m southwest at 152 Wilson St. Submitted April 2026, under review. Height not stated.
> - **Medium:** 10 three-storey townhouses, 150 m southeast at Robinson and Water St. Rezoning approved; final conditions are being cleared.
> - **Medium:** a new Oakville Central Library at 193 Church St, 240 m north. Under review.
> - **Small:** a 4-storey, 3-unit building at 110 Chisholm St, 330 m southwest (approved), and a third-storey addition at 86 Wilson St, 460 m south.
> - **Also:** 18 more paid parking spaces at 125 Randall St, and heritage rules being set for the area around the Erchless Estate, 320 m southeast.
> - **What it means:** the blocks around this street are adding several hundred homes in mid-rise buildings. Expect construction a block north, more people and shops on Navy and Church St, and busier streets downtown.
> - *Source: Town of Oakville Open Data, Planning and Development Applications, Nov 1, 2026*

## Notes from doing this one

- Oakville's data is the cleanest of the four: home counts come as numbers
  (proposed and approved), not buried in text. It was updated Oct 31, 2026.
- It has no minor variances or severances, so house-scale changes are
  undercounted.
