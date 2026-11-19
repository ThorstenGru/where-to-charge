"""Builds data/kommun.json: municipality borders (lat/lon, simplified) + price area(s) + reduced energy tax flag. See docs/KOMMUN.md.

Inputs (download them first, they are not stored in the repo):
  1. SCB municipality borders, CC0: https://www.scb.se/hitta-statistik/regional-statistik-och-kartor/regionala-indelningar/digitala-granser/
     (shape_svenska_*.zip, inside it Kommun_Sweref99TM.zip; unzip so that Kommun_Sweref99TM.shp is readable)
  2. Boio El municipality table, CC BY 4.0 (credit "Kalla: Boio El, https://boio.se/el"): https://boio.se/el/api/v1/kommuner (save as boio.json)
  3. Optional, for the grid fee: Ei's table of grid fees for households (Excel, open data), https://www.ei.se/om-oss/statistik-och-oppna-data/natavgifter---elnat
     (Hushallskunder-elnatsforetagens-elnatsavgifter.xlsx). Column "Villa 20A, 20 000 kWh/ar", code NT4030 "Rorlig 1, ore/kWh exkl. moms", year 2026.
Usage: python tools/build_kommun.py path/to/Kommun_Sweref99TM.shp path/to/boio.json [path/to/ei.xlsx]   (needs: pip install pyshp openpyxl). Writes data/kommun.json.
"""
import json
import math
import sys

import shapefile

SHP, BOIO = sys.argv[1], sys.argv[2]
EI = sys.argv[3] if len(sys.argv) > 3 else None
OUT = "data/kommun.json"
TOL_M = 120.0      # Douglas-Peucker tolerance in metres: keeps the file small, the border error is below the tolerance
DEC = 3            # coordinates rounded to 0.001 degree (about 110 m north-south)

# SWEREF 99 TM (EPSG:3006) -> WGS84, Transverse Mercator inverse (Krueger series), GRS80
A, F, K0, LON0, FE = 6378137.0, 1 / 298.257222101, 0.9996, math.radians(15.0), 500000.0
n = F / (2 - F)
a_hat = A / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
d1 = n / 2 - 2 * n ** 2 / 3 + 37 * n ** 3 / 96 - n ** 4 / 360
d2 = n ** 2 / 48 + n ** 3 / 15 - 437 * n ** 4 / 1440
d3 = 17 * n ** 3 / 480 - 37 * n ** 4 / 840
d4 = 4397 * n ** 4 / 161280
e2 = F * (2 - F)
A_ = e2 + e2 ** 2 + e2 ** 3 + e2 ** 4
B_ = -(7 * e2 ** 2 + 17 * e2 ** 3 + 30 * e2 ** 4) / 6
C_ = (224 * e2 ** 3 + 889 * e2 ** 4) / 120
D_ = -(4279 * e2 ** 4) / 1260


def to_wgs84(x, y):
    xi, eta = y / (K0 * a_hat), (x - FE) / (K0 * a_hat)
    xi_p = xi - d1 * math.sin(2 * xi) * math.cosh(2 * eta) - d2 * math.sin(4 * xi) * math.cosh(4 * eta) - d3 * math.sin(6 * xi) * math.cosh(6 * eta) - d4 * math.sin(8 * xi) * math.cosh(8 * eta)
    eta_p = eta - d1 * math.cos(2 * xi) * math.sinh(2 * eta) - d2 * math.cos(4 * xi) * math.sinh(4 * eta) - d3 * math.cos(6 * xi) * math.sinh(6 * eta) - d4 * math.cos(8 * xi) * math.sinh(8 * eta)
    phi_s = math.asin(math.sin(xi_p) / math.cosh(eta_p))
    dlon = math.atan(math.sinh(eta_p) / math.cos(xi_p))
    s = math.sin(phi_s)
    phi = phi_s + s * math.cos(phi_s) * (A_ + B_ * s ** 2 + C_ * s ** 4 + D_ * s ** 6)
    return math.degrees(phi), math.degrees(LON0 + dlon)


def dp(pts, tol):
    """Douglas-Peucker on a closed ring in metres (list of (x, y)); returns the kept indices."""
    keep = {0, len(pts) - 1}
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-9
        best, bi = -1.0, None
        for k in range(i + 1, j):
            d = abs(dy * pts[k][0] - dx * pts[k][1] + x2 * y1 - y2 * x1) / L
            if d > best:
                best, bi = d, k
        if bi is not None and best > tol:
            keep.add(bi)
            stack += [(i, bi), (bi, j)]
    return sorted(keep)


boio = {k["code"]: k for k in json.load(open(BOIO, encoding="utf-8"))["kommuner"]}

# Variable grid fee (oere/kWh excl. VAT) per grid operator, Ei 2026, Villa 20 A, 20 000 kWh a year (electric heating: the typical home with a car charger)
fee = {}
if EI:
    import openpyxl
    rows = list(openpyxl.load_workbook(EI, data_only=True, read_only=True).worksheets[0].iter_rows(values_only=True))
    col, grp = None, None
    for i in range(len(rows[0])):
        grp = rows[0][i] or grp
        if rows[1][i] == "NT4030" and rows[3][i] == 2026 and str(grp).startswith("Villa 20A, 20"):
            col = i
    assert col is not None, "column NT4030 / 2026 not found"
    for r in rows[4:]:
        if r[0] and str(r[0]).startswith("REL") and r[col] not in (None, ""):
            fee[r[0]] = float(r[col])


def grid_of(b):
    """Main grid operator of the municipality (largest population share) and its variable fee; None when that operator has no value (then the default stays)."""
    nets = sorted(b["grid"]["networks"], key=lambda n: -n["populationSharePct"])
    if not nets or nets[0]["rel"] not in fee:
        return None, None
    v = fee[nets[0]["rel"]]
    return (round(v, 1), nets[0]["company"]) if v >= 1.0 else (None, None)   # under 1 oere/kWh = a power tariff (the cost is in the fixed/power fees): unknown, not free

r = shapefile.Reader(SHP, encoding="latin-1")
out = []
for sr in r.shapeRecords():
    code, name = sr.record[0], sr.record[1]
    b = boio[code]
    sh = sr.shape
    parts = list(sh.parts) + [len(sh.points)]
    rings = []
    for pi in range(len(sh.parts)):
        pts = sh.points[parts[pi]:parts[pi + 1]]
        if len(pts) < 4:
            continue
        # a closed ring has a zero-length first-to-last chord: split it at the point farthest from the start and simplify the two halves
        m = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
        keep = sorted(set(dp(pts[:m + 1], TOL_M)) | {m + i for i in dp(pts[m:], TOL_M)})
        flat = []
        for k in keep:
            la, lo = to_wgs84(*pts[k])
            flat += [round(la, DEC), round(lo, DEC)]
        if len(flat) >= 8:       # at least 4 points
            rings.append(flat)
    g, gc = grid_of(b)
    out.append({"c": code, "n": b["name"], "a": b["areas"], "t": 1 if b["energyTax"].get("reduced") else 0, "g": g, "gc": gc, "p": rings})

doc = {"v": 1, "updated": json.load(open(BOIO, encoding="utf-8"))["period"], "n": len(out),
       "attribution": ["Borders: SCB (CC0)", "Price areas and energy tax zone: Boio El, https://boio.se/el (CC BY 4.0)"],
       "note": "Rings are [lat, lon, lat, lon, ...], simplified (about 120 m). 't' = 1: reduced energy tax (46 northern municipalities). 'a' lists the price area(s): 17 municipalities have two. 'g' = variable grid fee of the main grid operator in oere/kWh excl. VAT (Ei 2026, Villa 20 A / 20 000 kWh), 'gc' its name; null = unknown.",
       "attribution_grid": "Grid fees: Energimarknadsinspektionen (Ei), open data; operator per municipality: Boio El (CC BY 4.0)",
       "k": out}
import os
os.makedirs("data", exist_ok=True)
open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
print(len(out), "municipalities,", os.path.getsize(OUT), "bytes,", sum(1 for k in out if k["g"] is not None), "with a grid fee")
