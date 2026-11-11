# Handover: "Where to charge today?" (Santa Fe PHEV, Sweden SE4)

Live: https://thorstengru.github.io/where-to-charge/ · Repo: ThorstenGru/where-to-charge

## Goal
A phone web page that decides every day: **charge on the road, charge at home, or do not charge (HEV mode, petrol)**.

## Status
- One self-contained file: `index.html` (HTML, CSS, JS inline, no build). Deployed with GitHub Pages from `main`.
- Works: inputs (petrol, home electricity, season, battery level, parking time, charging power), "Here I am" button (geolocation) listing the 5 nearest Type 2 AC chargers and the 5 nearest petrol 95 prices, recommendation, comparison table, `localStorage` persistence (key `wo-laden-heute-v1`, kept unchanged so saved values survive).
- Live data from eurofuelprices.com (CORS open): `ev_se.json` (charger locations, from Open Charge Map and NOBIL), `ac_tariffs.json` (hand-kept operator list prices; only Mer, E.ON Drive and Recharge have a figure), `se.json` (petrol prices), `elpris.json` (SE4 monthly spot averages).
- Tested with a simulated location in a desktop browser. Not tested on a real phone.

## Vehicle and assumptions
- Hyundai Santa Fe PHEV 1.6 T-GDi, model year 2025 (MX5 generation), battery 13.8 kWh gross.
- Electric range WLTP: 54 km (Hyundai Sweden, MX5). Older sources say 58 km.
- AC charging only, about 3.6 kW (sources disagree: 3.3 / 3.6 / 3.7 kW; Hyundai quotes 6.5 h on a household socket). No DC fast charging assumed.
- Usable energy from the socket per full charge: about 10.4 kWh (= 54 km x 0.192 kWh/km), `USABLE_KWH` in the code.

| Season | Electric | Petrol (battery empty) | Electric range (assumption) |
|---|---|---|---|
| Summer | 19 kWh/100 km | 7.0 l/100 km | about 50 km |
| Winter (-5...+5 C) | 25 kWh/100 km | 8.3 l/100 km | about 30 km |

Petrol sources: Motor1 test (7.0 mixed, 8.3 motorway), m3.se cold test (0.8-0.85 l/mil), Spritmonitor long term (7.33). **Winter electric figures and ranges are own estimates.**

## Calculation (in the code: `calc()`)
```
l_per_kWh      = petrol_l_100 / el_kWh_100       // litres saved per charged kWh
value_per_kWh  = l_per_kWh * petrol_price        // SEK
gain_per_kWh   = value_per_kWh - electricity_price
break_even_petrol_price = electricity_price / l_per_kWh   // SEK/l
free_kWh       = USABLE_KWH * (1 - battery%/100)
remote_kWh     = min(free_kWh, parking_h * min(car_kW, charger_kW))
```
Decision: the best gain per kWh wins. Below 0.30 SEK/kWh, or with an almost full battery (<0.5 kWh free), the advice is "drive in HEV mode / do not charge". If a road charger wins, the rest is suggested at home. Home is always one of the compared options.

## Prices (as of 2026-11-10)
- Petrol 95: 15.80 SEK/l. From 1 Dec 2026 the temporary CO2 tax cut ends (+3 SEK/l incl. VAT), so about 18.80.
- **Home electricity (Skelleftea Kraft + E.ON Nat, bidding area SE4):** variable contract billed on the **monthly average of the spot price**, not hourly. The time of charging does not change the cost.
  - Formula, derived from the October 2026 invoices: `home = (monthly spot excl. VAT + 0.11497 variable + 0.2584 grid transfer + 0.36 energy tax) x 1.25`. The fixed markup (0.06) and the discount (0.06) cancel until 2027-05-31.
  - October check: spot 1.5667 -> 2.875 SEK/kWh (invoice basis 2.88).
  - Fixed costs (grid subscription 668 kr/month) do not change the price per kWh and are not part of the calculation.
  - The page offers the formula result from the current month's spot average as a button. November is a partial month, so the value moves until the month ends.
- Public chargers: list prices from `ac_tariffs.json` (ad hoc, without subscription, incl. VAT). All other chargers need a price entered by hand.

## Known gaps and risks
1. No route calculation. "Nearest" means straight-line distance.
2. Winter range (30 km) and winter consumption (25 kWh/100 km) are not documented. Calibrate with real driving data.
3. Charging power 3.6 kW unconfirmed. Check whether 22 kW chargers really charge the car faster (probably not).
4. Charger prices are list prices or crowd data and age quickly. Parking fees, idle fees and detours are not in the model.
5. The home price for November is an estimate until the November invoice arrives.
6. Petrol prices come from a crowd source and ANWB. Many have no timestamp (shown as "date unknown").
7. Only chargers up to 22 kW are listed, and many have no operator name, so no price.

## Done since first handover
- Trip mode: enter round-trip km. Electric km = (battery now + charge on site) x 100 / kWh per 100 km. Charge on site = best ticked charger, parking hours x min(car kW, charger kW), capped at one full battery (assumes the charge happens mid-trip). Shows fully electric yes/no, otherwise petrol km, litres and SEK.
- PWA basics: `manifest.json`, icons (192, 512, apple-touch), standalone display. No service worker, because the page needs live data anyway.

- UI rework (2026-11-10): petrol from the chosen nearby pump (no price forecast); home price per month (last bill, current month, 3 estimated months) as pure energy price incl. VAT without fixed fees; explanations for season, battery level and charging power; parking time slider 0.5-12 h; one chosen charger (radio) sets price and power (min of car limit and charger kW); detailed per-option comparison (kWh, cost, petrol saved, result, break-even petrol price).
- Month estimates (audited 2026-11-10): typical level of the month in 2023-25 (own mean from `monthly`, not the feed's `seasonal`, which includes 2026) raised by f = mean ratio of the last 3 months to typical; the excess fades by 30 % per month. Range = back to typical .. excess persists. The current partial month is estimated as known days + typical-plus-faded-excess for the rest. A rule of thumb, NOT a market forecast (no futures source).

- Charger prices: NOBIL was tested on 2026-11-06 (see EuroFuelPrices docs/NOBIL_TEST_2026-11-06.md): it has NO price fields, and its terms forbid exposing the API to end users. So prices stay: operator list price (Mer, E.ON Drive, Recharge) or entered by hand. A price entered for one charger is remembered per operator and offered for that operator's other chargers ("your last price for <operator>"). Chargers without an operator name cannot share a price.

## Ideas for next steps
- Annual calculation by mileage, split summer/winter.
- Automatic season preset by date.
- Real routing instead of straight-line distances.

## Constraints
- One file, no external dependencies except the optional font (Google Fonts, with system fallback).
- Mobile first, light/dark via `prefers-color-scheme`, safe-area insets respected.
- UI language: English. Decimal point in the display; input accepts comma and point.
- User preference: short, clear recommendation with numbers. No filler.
