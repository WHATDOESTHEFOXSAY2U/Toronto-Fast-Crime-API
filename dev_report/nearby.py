"""
"What's coming near this home": the lookup step.

Given one Toronto address, list every open development application within a
radius (default 500 m), from two City of Toronto open datasets that are
refreshed daily:

  * Development Applications: rezonings (OZ), site plans (SA), condo (CD),
    subdivision (SB), part-lot control (PL). Has its own X/Y.
  * Committee of Adjustment Applications (active): minor variances (MV) and
    consents/severances (CO). No coordinates, so geocoded against the
    city's Address Points dataset.

The output is a plain-text block, one entry per site, nearest first. Paste
it under the prompt in extraction_prompt.md and Claude writes the one-page
report.

Usage:
    python3 dev_report/nearby.py "33 Woodlawn Ave E" [--radius 500] [--refresh]
"""

import argparse
import math
import os
import re
import sys
import urllib.request
from datetime import date

import pandas as pd

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CKAN = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
SOURCES = {
    "development-applications.csv":
        CKAN + "/dataset/0aa7e480-9b48-4919-98e0-6af7615b7809/resource/"
               "77f8a66a-bd43-40e6-b6c9-12a2b03a5032/download/development-applications.csv",
    "coa-active.csv":
        CKAN + "/datastore/dump/51fd09cd-99d6-430a-9d42-c24a937b0cb0",
    "address-points-2952.csv":
        CKAN + "/dataset/abedd8bc-e3dd-4d45-8e69-79165a76e4fa/resource/"
               "7d5590f0-cfd5-4381-87d0-baf7dbf4921c/download/address-points-2952.csv",
}

# Statuses that mean the application is finished and won't change anything.
DEAD_PLANNING = {"Closed", "Refused", "OMB Refused", "Appeal Dismissed", "Inactive"}
DEAD_COA = {"Closed", "Refused"}

PLANNING_TYPES = {
    "OZ": "Official Plan / Rezoning",
    "SA": "Site Plan",
    "CD": "Condominium",
    "SB": "Plan of Subdivision",
    "PL": "Part Lot Control",
}
COA_TYPES = {"MV": "Minor Variance", "CO": "Consent (severance)"}

SUFFIXES = {
    "AVENUE": "AVE", "STREET": "ST", "ROAD": "RD", "DRIVE": "DR", "CRESCENT": "CRES",
    "BOULEVARD": "BLVD", "COURT": "CRT", "PLACE": "PL", "LANE": "LANE", "TRAIL": "TRL",
    "CIRCLE": "CRCL", "PARKWAY": "PKWY", "GARDENS": "GDNS", "TERRACE": "TER",
    "SQUARE": "SQ", "GROVE": "GRV", "HEIGHTS": "HTS",
}
DIRS = {"EAST": "E", "WEST": "W", "NORTH": "N", "SOUTH": "S"}


def fetch(name, refresh):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if refresh or not os.path.exists(path):
        print(f"downloading {name} ...", file=sys.stderr)
        urllib.request.urlretrieve(SOURCES[name], path)
    return path


def _clean(v):
    return "" if not isinstance(v, str) and pd.isna(v) else str(v).strip().upper()


def key(num, name, typ, d):
    """Join key, e.g. '33|WOODLAWN|AVE|E'. Direction matters: Dundas St E and
    Dundas St W share house numbers."""
    return "|".join(_clean(v) for v in (num, name, typ, d))


def loose_key(num, name, d):
    """Fallback for records with a blank street type."""
    return "|".join(_clean(v) for v in (num, name, d))


def place(df, points, num, name, typ, d):
    """Attach x/y from the address points: exact key first, then loose key
    (only where the loose key is unambiguous)."""
    exact = points.drop_duplicates("key").set_index("key")[["x", "y"]]
    loose = points.drop_duplicates(["loose", "key"])
    loose = loose[~loose.loose.duplicated(keep=False)].set_index("loose")[["x", "y"]]
    k = [key(*r) for r in zip(df[num], df[name], df[typ], df[d])]
    lk = [loose_key(*r) for r in zip(df[num], df[name], df[d])]
    xy = exact.reindex(k).values
    xy_loose = loose.reindex(lk).values
    fill = pd.isna(xy[:, 0])
    xy[fill] = xy_loose[fill]
    df["x"], df["y"] = xy[:, 0], xy[:, 1]
    return df


def load_address_points(refresh):
    path = fetch("address-points-2952.csv", refresh)
    a = pd.read_csv(path, low_memory=False, usecols=[
        "ADDRESS_NUMBER", "LINEAR_NAME", "LINEAR_NAME_TYPE", "LINEAR_NAME_DIR",
        "ADDRESS_FULL", "geometry"])
    xy = a.geometry.str.extract(r"\[\[?\s*([-\d.]+),\s*([-\d.]+)")
    a["x"] = xy[0].astype(float)  # EPSG:2952, MTM zone 10, metres
    a["y"] = xy[1].astype(float)
    a["key"] = [key(*r) for r in zip(a.ADDRESS_NUMBER, a.LINEAR_NAME,
                                     a.LINEAR_NAME_TYPE, a.LINEAR_NAME_DIR)]
    a["loose"] = [loose_key(*r) for r in zip(a.ADDRESS_NUMBER, a.LINEAR_NAME,
                                             a.LINEAR_NAME_DIR)]
    a["full_key"] = a.ADDRESS_FULL.str.upper().str.replace(r"\s+", " ", regex=True).str.strip()
    return a.drop(columns="geometry")


def normalise_address(text):
    words = re.sub(r"[.,]", " ", text.upper()).split()
    words = [SUFFIXES.get(w, DIRS.get(w, w)) for w in words]
    return " ".join(w.title() if not w.isdigit() else w for w in words).upper()


def geocode(points, address):
    hit = points[points.full_key == normalise_address(address)]
    if hit.empty:
        sys.exit(f"Address not found in City of Toronto Address Points: {address!r}\n"
                 "Use the city's spelling, e.g. '33 Woodlawn Ave E'.")
    r = hit.iloc[0]
    return r.ADDRESS_FULL, r.x, r.y


def bearing(dx, dy):
    deg = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    return ["north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"][int((deg + 22.5) // 45) % 8]


def addr(num, name, typ, d):
    parts = [str(p).strip() for p in (num, name, typ, d)
             if isinstance(p, str) and p.strip()]
    return " ".join(parts).title()


def planning_apps(points, refresh):
    from pyproj import Transformer
    d = pd.read_csv(fetch("development-applications.csv", refresh), low_memory=False)
    d = d[~d.STATUS.str.strip().isin(DEAD_PLANNING)].copy()
    # The dataset's own X/Y are NAD27 MTM 10 (EPSG:2019). Prefer the address
    # point for the same street address, fall back to converting the X/Y.
    d = place(d, points, "STREET_NUM", "STREET_NAME", "STREET_TYPE", "STREET_DIRECTION")
    t = Transformer.from_crs(2019, 2952, always_xy=True)
    miss = d.x.isna() & d.X.notna()
    if miss.any():
        d.loc[miss, "x"], d.loc[miss, "y"] = t.transform(d.loc[miss, "X"].values,
                                                         d.loc[miss, "Y"].values)
    return pd.DataFrame({
        "kind": "planning",
        "file": d["APPLICATION#"].str.strip(),
        "type": d.APPLICATION_TYPE.map(PLANNING_TYPES).fillna(d.APPLICATION_TYPE),
        "address": [addr(*r) for r in zip(d.STREET_NUM, d.STREET_NAME,
                                          d.STREET_TYPE, d.STREET_DIRECTION)],
        "status": d.STATUS.str.strip(),
        "date": d.DATE_SUBMITTED.str[:10],
        "description": d.DESCRIPTION.fillna("").str.strip(),
        "link": d.APPLICATION_URL,
        "x": d.x, "y": d.y,
    })


def coa_apps(points, refresh):
    c = pd.read_csv(fetch("coa-active.csv", refresh), low_memory=False)
    c = c[~c.STATUSDESC.str.strip().isin(DEAD_COA)].copy()
    c = place(c, points, "STREET_NUM", "STREET_NAME", "STREET_TYPE", "STREET_DIRECTION")
    decision = c.C_OF_A_DESCISION.fillna("").str.strip()
    status = c.STATUSDESC.str.strip() + decision.map(lambda s: f" (decision: {s})" if s else "")
    work = c.WORK_TYPE.fillna("").str.strip()
    return pd.DataFrame({
        "kind": "coa",
        "file": c["REFERENCE_FILE#"].str.strip(),
        "type": c.APPLICATION_TYPE.map(COA_TYPES).fillna(c.APPLICATION_TYPE)
                + work.map(lambda s: f", {s}" if s else ""),
        "address": [addr(*r) for r in zip(c.STREET_NUM, c.STREET_NAME,
                                          c.STREET_TYPE, c.STREET_DIRECTION)],
        "status": status,
        "date": c.IN_DATE.str[:10],
        "description": c.DESCRIPTION.fillna("").str.strip(),
        "link": "",
        "x": c.x, "y": c.y,
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("address")
    ap.add_argument("--radius", type=float, default=500, help="metres (default 500)")
    ap.add_argument("--refresh", action="store_true", help="re-download the city data")
    args = ap.parse_args()

    points = load_address_points(args.refresh)
    home, hx, hy = geocode(points, args.address)

    apps = pd.concat([planning_apps(points, args.refresh), coa_apps(points, args.refresh)])
    unplaced = int(apps.x.isna().sum())
    apps = apps.dropna(subset=["x"])
    apps["dist"] = ((apps.x - hx) ** 2 + (apps.y - hy) ** 2) ** 0.5
    near = apps[apps.dist <= args.radius].drop_duplicates(["kind", "file", "address"])

    # A big project is often filed under several street addresses (one row
    # each). Keep one row per file, at its nearest address, and list the rest.
    near = near.sort_values("dist")
    near["fid"] = near.file.where(near.file.notna() & (near.file != ""),
                                  near.kind + ":" + near.address)
    also = near.groupby(["kind", "fid"]).address.agg(lambda s: list(dict.fromkeys(s))[1:])
    near = near.drop_duplicates(["kind", "fid"])

    print(f"HOME: {home}, Toronto")
    print(f"RADIUS: {args.radius:.0f} m")
    print(f"CHECKED: {date.today():%b %-d, %Y}")
    print("SOURCE: City of Toronto Open Data, Development Applications + "
          "Committee of Adjustment Applications (both refreshed daily; "
          "same records as the Application Information Centre)")
    print(f"OPEN APPLICATIONS FOUND: {len(near)}")
    print()

    # One block per site: a tower usually has a rezoning, a site plan and a
    # condo file at the same address, and they are one project.
    sites = near.groupby("address", sort=False)
    order = sites.dist.min().sort_values().index
    for i, site in enumerate(order, 1):
        g = sites.get_group(site).sort_values("date")
        r = g.loc[g.dist.idxmin()]
        print(f"=== SITE {i}: {site} | {r.dist:.0f} m {bearing(r.x - hx, r.y - hy)}")
        for _, a in g.iterrows():
            file_no = a.file if isinstance(a.file, str) and a.file else "(file number not published)"
            print(f"- {file_no} | {a.type} | {a.status} | submitted {a.date}")
            extra = also.get((a.kind, a.fid), [])
            if extra:
                print(f"  also filed under: {', '.join(extra)}")
            if a.link:
                print(f"  {a.link}")
            print(f"  {a.description or '(no description published yet)'}")
        print()

    if unplaced:
        print(f"(note: {unplaced} open applications city-wide could not be placed on "
              "the map and were skipped)", file=sys.stderr)


if __name__ == "__main__":
    main()
