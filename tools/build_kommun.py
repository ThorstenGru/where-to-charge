"""Builds data/kommun.json: municipality borders (lat/lon, simplified) + price area(s) + reduced energy tax flag. See docs/KOMMUN.md.

Inputs (download them first, they are not stored in the repo):
  1. SCB municipality borders, CC0: https://www.scb.se/hitta-statistik/regional-statistik-och-kartor/regionala-indelningar/digitala-granser/
     (shape_svenska_*.zip, inside it Kommun_Sweref99TM.zip; unzip so that Kommun_Sweref99TM.shp is readable)
  2. Boio El municipality table, CC BY 4.0 (credit "Kalla: Boio El, https://boio.se/el"): https://boio.se/el/api/v1/kommuner (save as boio.json)
Usage: python tools/build_kommun.py path/to/Kommun_Sweref99TM.shp path/to/boio.json   (needs: pip install pyshp). Writes data/kommun.json.
"""
import json
import math
import sys

import shapefile

SHP, BOIO = sys.argv[1], sys.argv[2]
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
    out.append({"c": code, "n": b["name"], "a": b["areas"], "t": 1 if b["energyTax"].get("reduced") else 0, "p": rings})

doc = {"v": 1, "updated": json.load(open(BOIO, encoding="utf-8"))["period"], "n": len(out),
       "attribution": ["Borders: SCB (CC0)", "Price areas and energy tax zone: Boio El, https://boio.se/el (CC BY 4.0)"],
       "note": "Rings are [lat, lon, lat, lon, ...], simplified (about 120 m). 't' = 1: reduced energy tax (46 northern municipalities). 'a' lists the price area(s): 17 municipalities have two.",
       "k": out}
import os
os.makedirs("data", exist_ok=True)
open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
print(len(out), "municipalities,", os.path.getsize(OUT), "bytes")
