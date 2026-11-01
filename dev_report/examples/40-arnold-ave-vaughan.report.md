# Worked example: 40 Arnold Ave, Vaughan (Thornhill)

This is a real address on a residential street west of Yonge St, chosen as
a test case. The input is
[`40-arnold-ave-vaughan.input.txt`](40-arnold-ave-vaughan.input.txt), from
`python3 dev_report/gta.py york "40 Arnold Ave, Vaughan, ON"` on Nov 1,
2026. York Region's data covers both sides of Yonge St, so the Markham
projects show up too.

## The report

> **What's coming near 40 Arnold Ave, Vaughan (Thornhill)** (within 500 m, checked Nov 1, 2026)
> - **Big:** two 60-storey towers on an 8-storey base, about 1,330 homes with shops at street level, 340 m east on Yonge St south of Hwy 7 (Markham side). Rezoning approved; the appeal window is still open. It still needs building-detail approval and permits. Construction is years away, and many approved GTA towers are on hold right now.
> - **Big (check):** a 212-home condo at Yonge St and Arnold Ave, 190 m northeast. Its condo paperwork dates from 2013, so the building may already be standing. Worth a look.
> - **Medium:** a new automatic car wash at 7545 Yonge St, 320 m east, under review since 2022. Three older files from 2012 to 2019 (a school redevelopment, a heritage house becoming a pharmacy and café, and an office addition on Centre St) are likely built or stalled.
> - **Small:** 2 current files: a basement converted into residential suites, 500 m southeast, and a house variance on Thorny Brae Dr, 320 m northeast. 3 old house files were left out.
> - **Also:** the city is planning water and sewer capacity for the Yonge–Steeles corridor, 260 m south. This is groundwork for more density along Yonge.
> - **What it means:** Arnold Ave itself stays houses, but Yonge St is being set up as a high-rise corridor. Expect years of tower construction about 300 m east once it starts, and many more neighbours and shops along Yonge.
> - *Source: York Region Open Data, Active Development Applications, Nov 1, 2026*

## Notes from doing this one

- York Region's layer covers every York municipality in one feed, and it is
  current: the newest file arrived Oct 25, 2026. It has applications the
  Region reviews. Minor variances only appear when they were circulated to
  the Region, so the small-project line is less complete than Toronto's.
- Several files are 7 to 14 years old and still marked "In Progress". The
  age rules in the prompt matter even more here than in Toronto.
