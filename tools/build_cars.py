"""Builds cars.json from open-ev-data. See docs/CARS.md.

First download open-ev-data-v1.24.0.json from https://github.com/open-ev-data/open-ev-data-dataset/releases (CDLA-Permissive-2.0).
Usage: python tools/build_cars.py path/to/open-ev-data-v1.24.0.json   (writes cars.json in the current folder; run it in the folder of index.html)
"""
import json
import sys

OEV = sys.argv[1]
OUT = "cars.json"
vehicles = json.load(open(OEV, encoding="utf-8"))["vehicles"]

# (make slug, model slug, year, net kWh to match, display name). Names carry the NET battery size: trim names in the dataset are inconsistent.
PICK = [("volkswagen", "id_3", 2025, 58.0, "VW ID.3 (58 kWh)"), ("volkswagen", "id_3", 2025, 77.0, "VW ID.3 (77 kWh)"),
        ("volkswagen", "id_7", 2025, 86.0, "VW ID.7 (86 kWh)"),
        ("cupra", "born", 2025, 58.0, "Cupra Born (58 kWh)"), ("cupra", "born", 2025, 77.0, "Cupra Born (77 kWh)"),
        ("mg", "mg4", 2025, 61.0, "MG4 (61 kWh)"),
        ("bmw", "i4", 2025, 81.3, "BMW i4 eDrive40 (81 kWh)"),
        ("tesla", "model_3", 2025, 57.0, "Tesla Model 3 RWD (57 kWh)"), ("tesla", "model_3", 2025, 75.0, "Tesla Model 3 Long Range (75 kWh)")]

REAL = 1.25      # real-world and charging-loss factor on the WLTP battery consumption (estimate)
WINTER = 1.29    # winter / summer ratio of the app's presets (evidence range 1.23 to 1.43)


def petrol(net):
    return (5.5, 6.5) if net < 50 else (6.5, 7.5) if net < 75 else (8.0, 9.5)   # comparable petrol car by size class: the app's generic profiles


cars = []
for mk, md, yr, net, name in PICK:
    hit = [v for v in vehicles if v["make"]["slug"] == mk and v["model"]["slug"].startswith(md) and v["year"] == yr and v.get("vehicle_type") == "passenger_car"
           and abs((v["battery"].get("pack_capacity_kwh_net") or 0) - net) < 0.01]
    assert hit, name
    v = hit[0]
    ac = v["charging"]["ac"]["max_power_kw"]
    dc = v["charging"]["dc"]["max_power_kw"]
    rng = [r["range_km"] for r in v["range"]["rated"] if r["cycle"] == "wltp"][0]
    assert 7 <= ac <= 22 and 50 <= dc <= 350 and 250 <= rng <= 800, name
    elS = round(net / rng * 100 * REAL, 1)
    lS, lW = petrol(net)
    cars.append({"id": mk + "_" + md + "_" + str(int(net)), "type": "bev", "name": name, "dc": dc, "conf": "B",
                 "src": "open-ev-data v1.24.0 (CDLA-Permissive-2.0, cites manufacturer data)",
                 "raw": {"net_kwh": net, "ac_kw": ac, "dc_kw": dc, "wltp_km": rng, "year": yr, "entry": v["unique_code"]},
                 "v": {"usable": round(net * 1.1, 1), "kw": ac, "hold": 10, "elS": elS, "elW": round(elS * WINTER, 1), "lS": lS, "lW": lW}})

# Plug-in hybrid: only what a primary source states. VW press release: net 19.7 kWh, AC up to 11 kW, up to about 120 km electric (WLTP, best variant).
net, rng = 19.7, 120.0
elS = round(net / rng * 100 * REAL, 1)
cars.append({"id": "vw_tiguan_ehybrid", "type": "phev", "name": "VW Tiguan eHybrid (19.7 kWh)", "dc": None, "conf": "A",
             "src": "Volkswagen press release (battery, AC power, range); consumption derived; petrol values are the generic profile",
             "raw": {"net_kwh": net, "ac_kw": 11, "wltp_ev_range_km": rng,
                     "url": "https://www.volkswagen-newsroom.com/en/press-releases/now-available-to-order-long-range-plug-in-hybrid-drives-for-the-tiguan-from-48655-euro-18182"},
             "v": {"usable": round(net * 1.1, 1), "kw": 11, "hold": 10, "elS": elS, "elW": round(elS * WINTER, 1), "lS": 6.5, "lW": 7.5}})

# Kia EV6: Kia Sweden's product fact sheet (valid from 2025-02-17), https://www.kia.com/content/dam/kwcms/kme/se/sv/assets/campaigns/kia-sweden-ev6-specification.pdf
# Stated by Kia: battery capacity 84 kWh (no net figure), on-board charger 10.5 kW 3-phase, DC max 258 kW, WLTP up to 582 km (RWD, 15.9 kWh/100 km) and
# 546 km (AWD, 17.0 kWh/100 km with 19" wheels). Net kWh is NOT stated: 0.95 x 84 is an assumption. WLTP consumption is already measured at the socket,
# so only the real-world factor applies (REAL / 1.1).
for key, name, wltp_km, wltp_kwh in (("rwd", "Kia EV6 Long Range RWD (84 kWh)", 582, 15.9), ("awd", "Kia EV6 Long Range AWD (84 kWh)", 546, 17.0)):
    net = round(84 * 0.95, 1)
    elS = round(wltp_kwh * REAL / 1.1, 1)
    lS, lW = petrol(net)
    cars.append({"id": "kia_ev6_lr_" + key, "type": "bev", "name": name, "dc": 258, "conf": "A",
                 "src": "Kia Sweden product fact sheet (battery 84 kWh, AC 10.5 kW, DC 258 kW, WLTP range and consumption); net kWh assumed 0.95 x 84",
                 "raw": {"gross_kwh": 84, "net_kwh_assumed": net, "ac_kw": 10.5, "dc_kw": 258, "wltp_km": wltp_km, "wltp_kwh_100": wltp_kwh,
                         "url": "https://www.kia.com/content/dam/kwcms/kme/se/sv/assets/campaigns/kia-sweden-ev6-specification.pdf"},
                 "v": {"usable": round(net * 1.1, 1), "kw": 10.5, "hold": 10, "elS": elS, "elW": round(elS * WINTER, 1), "lS": lS, "lW": lW}})

# Kia EV3: Kia Sweden's product fact sheet (valid from 2026-09-16), https://www.kia.com/api/bin/docDownload?program=brochure&locale=se&path=%2Fcontent%2Fdam%2Fkwcms%2Fkme%2Fse%2Fsv%2Fassets%2Fcontents%2Futility%2Fspecifications%2Fev3%2FFaktablad-Kia-EV3.pdf
# Stated: battery capacity 58.3 / 81.4 kWh (no net figure: 0.95 x is an assumption), on-board charger 10.5 kW 3-phase, DC max 101 / 128 kW,
# WLTP FWD up to 436 km (58.3 kWh, 17") 14.9 kWh/100 km and up to 605 km (81.4 kWh, 17") 14.9 kWh/100 km. Consumption is the socket figure (only REAL / 1.1 applies).
EV3_URL = "https://www.kia.com/api/bin/docDownload?program=brochure&locale=se&path=%2Fcontent%2Fdam%2Fkwcms%2Fkme%2Fse%2Fsv%2Fassets%2Fcontents%2Futility%2Fspecifications%2Fev3%2FFaktablad-Kia-EV3.pdf"
for key, gross, dc, wltp_km, wltp_kwh in (("std", 58.3, 101, 436, 14.9), ("lr", 81.4, 128, 605, 14.9)):
    net = round(gross * 0.95, 1)
    elS = round(wltp_kwh * REAL / 1.1, 1)
    lS, lW = petrol(net)
    cars.append({"id": "kia_ev3_" + key, "type": "bev", "name": "Kia EV3 FWD (" + str(gross).rstrip("0").rstrip(".") + " kWh)", "dc": dc, "conf": "A",
                 "src": "Kia Sweden product fact sheet (capacity, AC 10.5 kW, DC, WLTP range and consumption, FWD 17\" wheels); net kWh assumed 0.95 x capacity",
                 "raw": {"gross_kwh": gross, "net_kwh_assumed": net, "ac_kw": 10.5, "dc_kw": dc, "wltp_km": wltp_km, "wltp_kwh_100": wltp_kwh, "url": EV3_URL},
                 "v": {"usable": round(net * 1.1, 1), "kw": 10.5, "hold": 10, "elS": elS, "elW": round(elS * WINTER, 1), "lS": lS, "lW": lW}})

doc = {"v": 1, "updated": "2026-11-19", "note": "Estimates, not measurements. Values are derived as described in docs/CARS.md; correct them with the consumption log.", "cars": cars}
open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
print(len(cars), "models written to", OUT)
