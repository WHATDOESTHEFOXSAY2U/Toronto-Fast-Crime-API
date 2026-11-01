"""
"What's coming near this home", the lookup step for GTA municipalities outside
the City of Toronto (Toronto uses nearby.py).

Each source is a public ArcGIS map service published by the municipality or
region. Those services answer "everything within N metres of this point"
directly, so nothing is bulk-downloaded. The output has the same format as
nearby.py and goes under extraction_prompt.md.

Covered:
  brampton  City of Brampton open data: rezonings/OPAs/subdivisions, site
            plans, condo plans, minor variances, consents, pre-consultations
  york      York Region "Active Development Applications": Vaughan, Markham,
            Richmond Hill, Aurora, Newmarket, King, etc. Files circulated
            to the Region, so coverage of local minor variances is partial.
  oakville  Town of Oakville planning applications: site plans, rezonings,
            OPAs, subdivisions, with structured unit counts

Usage:
    python3 dev_report/gta.py brampton "10 Elizabeth St N, Brampton"
    python3 dev_report/gta.py york "10 Main St, Markham" --radius 750
"""

import argparse
import json
import math
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

from pyproj import Transformer
from shapely.geometry import Point, shape

UTM = 26917  # NAD83 / UTM zone 17N, metres
GEOCODER = ("https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/"
            "findAddressCandidates")

BRAMPTON = ("https://services3.arcgis.com/rl7ACuZkiFsmDA2g/arcgis/rest/services/"
            "Planning_Land_Use_Development/FeatureServer")
YORK = ("https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/"
        "DevelopmentApplicationStatusAndTeams/MapServer/0")
OAKVILLE = ("https://services5.arcgis.com/QJebCdoMf4PF8fJP/arcgis/rest/services/"
            "Planning_and_Development_Applications/FeatureServer/0")

# Status words meaning the file is finished: built, registered, abandoned,
# or moved to another file. Matched case-insensitively as substrings.
DEAD = ("closed", "withdrawn", "inactive", "lapsed", "invalid", "expired",
        "null & void", "transferred", "registered", "substantially complete",
        "denied", "assumed", "cancel")


def _brampton(a):
    desc = (a.get("PROPOSAL_DESCRIPTION") or a.get("DESCRIPTION") or "").strip()
    return {
        "file": a.get("FILE_NUMBER"),
        "type": a.get("APPLICATION_TYPE"),
        "status": a.get("STATUS"),
        "date": a.get("DATE_RECEIVED"),
        "address": a.get("LOCATION"),
        "description": desc,
        "homes": None,
    }


def _york(a):
    local = a.get("EXT_REF_NUM")
    stage = " / ".join(s for s in (a.get("APPL_STAGE"), a.get("APPL_STEP")) if s)
    return {
        "file": local or a.get("REG_FILE_NUM"),
        "type": a.get("APPL_TYPE"),
        "status": f"{a.get('APPL_STATUS')} ({stage})" if stage else a.get("APPL_STATUS"),
        "date": a.get("DATE_RECVD"),
        "address": ", ".join(s for s in (a.get("ADDRESS"), a.get("MUN_NAME")) if s),
        "description": " ".join(s for s in (a.get("APPL_DESC"), a.get("LOCATION")
                                           and f"(Location: {a['LOCATION']})") if s),
        "homes": None,
    }


def _oakville(a):
    approved, proposed = a.get("Approved_Total___of_Units"), a.get("Proposed_Total___of_Units")
    homes = approved or proposed
    status = a.get("Status") or ""
    if a.get("Council_Decision"):
        cd = a["Council_Decision"]
        cd = to_date(cd).isoformat() if isinstance(cd, (int, float)) else cd
        status += f" (council decision {cd})"
    return {
        "file": a.get("FolderNumber") or f"folder {a.get('FolderRSN')}",
        "type": a.get("FolderType"),
        "status": status,
        "date": a.get("IntakeDate"),
        "address": a.get("FolderName"),
        "description": (a.get("Description") or "").strip(),
        "homes": (f"{homes} ({'approved' if approved else 'proposed'}; city's structured field)"
                  if homes else None),
    }


SOURCES = {
    "brampton": {
        "name": "City of Brampton Open Data, Planning & Land Use Development layers",
        "layers": [f"{BRAMPTON}/{n}" for n in (9, 11, 7, 8, 5, 10)],
        "map": _brampton,
    },
    "york": {
        "name": "York Region Open Data, Active Development Applications",
        "layers": [YORK],
        "map": _york,
    },
    "oakville": {
        "name": "Town of Oakville Open Data, Planning and Development Applications",
        "layers": [OAKVILLE],
        "map": _oakville,
    },
}


def get(url, **q):
    q.setdefault("f", "json")
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(q),
                                 headers={"User-Agent": "dev-report-feasibility/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "error" in data:
        raise RuntimeError(f"{url}: {data['error']}")
    return data


def geocode(address):
    r = get(GEOCODER, SingleLine=address, maxLocations=1, outSR=4326,
            countryCode="CAN", outFields="Addr_type")
    if not r.get("candidates") or r["candidates"][0]["score"] < 90:
        sys.exit(f"Could not geocode {address!r} confidently")
    c = r["candidates"][0]
    return c["address"], c["location"]["x"], c["location"]["y"]


def bearing(dx, dy):
    deg = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    return ["north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"][int((deg + 22.5) // 45) % 8]


def to_date(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc).date()
    return date.fromisoformat(str(v)[:10])


def nearby(layer, lon, lat, radius):
    """Every feature within `radius` metres of the point, geometry in UTM."""
    feats, offset = [], 0
    while True:
        r = get(layer + "/query", where="1=1", outFields="*", returnGeometry="true",
                geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", inSR=4326,
                spatialRel="esriSpatialRelIntersects", distance=radius,
                units="esriSRUnit_Meter", outSR=UTM, f="geojson",
                resultOffset=offset, resultRecordCount=1000)
        feats += r.get("features", [])
        if not r.get("properties", {}).get("exceededTransferLimit") and \
                not r.get("exceededTransferLimit"):
            return feats
        offset += 1000


def short_address(text):
    """'7616 Yonge Street, 7610 Yonge Street, ... , Vaughan' (15 parts) ->
    '7616 Yonge Street, 7610 Yonge Street, 16 Arnold Avenue +12 more, Vaughan'."""
    if not text or not text.strip():
        return "address not given"
    sep = "|" if "|" in text else ","
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    tail = []
    if sep == "," and len(parts) > 1 and not any(ch.isdigit() for ch in parts[-1]):
        tail = [parts.pop()]  # municipality name
    if len(parts) > 3:
        parts = parts[:3] + [f"+{len(parts) - 3} more"]
    return ", ".join(parts + tail).replace(", +", " +")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", choices=SOURCES)
    ap.add_argument("address", help="full address incl. city, e.g. '10 Main St, Markham'")
    ap.add_argument("--radius", type=float, default=500, help="metres (default 500)")
    ap.add_argument("--max-age", type=float, default=6,
                    help="skip approved files submitted more than N years ago (default 6); "
                         "files still under review or appeal are always kept")
    args = ap.parse_args()
    src = SOURCES[args.source]

    home, lon, lat = geocode(args.address)
    hx, hy = Transformer.from_crs(4326, UTM, always_xy=True).transform(lon, lat)
    here = Point(hx, hy)
    today = date.today()

    rows, skipped_dead, skipped_old = [], 0, 0
    for layer in src["layers"]:
        for f in nearby(layer, lon, lat, args.radius):
            a = src["map"](f["properties"])
            status = (a["status"] or "").strip()
            if any(w in status.lower() for w in DEAD):
                skipped_dead += 1
                continue
            d = to_date(a["date"])
            pending = any(w in status.lower() for w in
                          ("review", "progress", "appeal", "submitted", "circulation",
                           "scheduled", "public meeting", "received", "open", "comments"))
            if not pending and (d is None or (today - d).days > args.max_age * 365):
                skipped_old += 1
                continue
            geom = shape(f["geometry"]) if f.get("geometry") else None
            if geom is None:
                continue
            a["dist"] = geom.distance(here)  # 0 if the home is on the site
            c = geom.representative_point()
            a["dir"] = "on this site" if a["dist"] == 0 else bearing(c.x - hx, c.y - hy)
            a["date"] = d.isoformat() if d else "unknown"
            a["status"] = status
            rows.append(a)

    # One entry per file; one block per site.
    seen, uniq = set(), []
    for a in sorted(rows, key=lambda r: r["dist"]):
        k = (a["file"], a["type"])
        if k not in seen:
            seen.add(k)
            uniq.append(a)
    sites = {}
    for a in uniq:
        sites.setdefault(short_address(a["address"]), []).append(a)

    print(f"HOME: {home}")
    print(f"RADIUS: {args.radius:.0f} m")
    print(f"CHECKED: {today:%b %-d, %Y}")
    print(f"SOURCE: {src['name']}")
    print(f"OPEN APPLICATIONS FOUND: {len(uniq)} "
          f"(left out: {skipped_dead} closed/withdrawn/registered, "
          f"{skipped_old} approved more than {args.max_age:g} years ago)")
    print()
    for i, (site, apps) in enumerate(sites.items(), 1):
        first = apps[0]
        where = "on this site" if first["dist"] == 0 else f"{first['dist']:.0f} m {first['dir']}"
        print(f"=== SITE {i}: {site} | {where}")
        for a in sorted(apps, key=lambda r: r["date"]):
            print(f"- {a['file'] or '(file number not published)'} | {a['type']} | "
                  f"{a['status']} | submitted {a['date']}")
            if a["homes"]:
                print(f"  homes: {a['homes']}")
            print(f"  {' '.join(a['description'].split()) or '(no description published)'}")
        print()


if __name__ == "__main__":
    main()
