# Where to charge today? (Santa Fe PHEV, Sweden SE4)

Live: https://thorstengru.github.io/where-to-charge/ · Repo: ThorstenGru/where-to-charge

A phone web page that decides every day: **charge on the road (and top up at home), charge at home, or do not charge (drive in hybrid mode on petrol)**.

## Files
- `index.html`: the whole app (HTML, CSS, JS inline, no build, no external fonts). Deployed with GitHub Pages from `main`.
- `manifest.json`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`: install as a home-screen app. No service worker (the page needs live data anyway).
- `tests/calc.test.html`: tests for the calculation. Open it over http (`python -m http.server`, then `/tests/calc.test.html`, or the same path on the Pages URL). The title says PASS or FAIL.
- `TESTING.md`: phone test and calibration checklist.

## How the page works
Page order: recommendation, break-even, then six input steps (car, location, petrol, road charger, home price, trip), then details and settings.

Live data from eurofuelprices.com (open CORS), no personal data is sent:
- `se.json`: petrol prices. The page uses the median of prices dated in the last 3 days (all prices if fewer than 20 are dated), cached 6 hours. "Find my location" lists the 5 nearest pumps and preselects the cheapest dated one.
- `ev_se.json`: charger positions (Open Charge Map, NOBIL), version 1 only. Nearest 5 Type 2 chargers up to 22 kW. A charger's id is its rounded position, so saved prices survive data rebuilds.
- `ac_tariffs.json`: hand-kept operator list prices (only Mer, E.ON Drive and Recharge have a figure).
- `elpris.json`: SE4 monthly spot averages (excl. VAT).

Settings are stored on the device only when they differ from the defaults. Values that come from data (pump price, home price from spot, charger choice) are stored only when typed by hand. The first price you enter for an operator becomes that operator's default for all its chargers without an own price. Later prices typed on a charger apply to that charger only; the button "use ... as default" changes the operator default. Order: own price, free, operator default, list price.

## Calculation (`calc(st, ch)` in `index.html`, tested)
```
l_per_kWh      = petrol_l_100 / el_kWh_100            // litres saved per charged kWh
value_per_kWh  = l_per_kWh * petrol_price             // SEK
gain_per_kWh   = value_per_kWh - electricity_price
break_even_petrol_price      = electricity_price / l_per_kWh   // SEK/l
break_even_electricity_price = value_per_kWh                    // SEK/kWh
free_kWh       = 10.4 * (100 - max(battery%, hold%)) / (100 - hold%)
road_kWh       = min(free_kWh, parking_h * min(car_kW, charger_kW))
```
Decision: the best gain per kWh wins. Below 0.30 SEK/kWh, or with an almost full battery (< 0.5 kWh free), the advice is hybrid mode. If a road charger wins and more than 0.5 kWh remain, the rest is suggested at home. Trip mode: electric km = (battery now + charge on site, capped at one full battery) x 100 / kWh per 100 km.

## Vehicle and assumptions
- Hyundai Santa Fe PHEV 1.6 T-GDi, model year 2025, battery 13.8 kWh gross. WLTP electric range 54 km (older sources: 58 km).
- Usable energy from the socket per full charge: about 10.4 kWh (= 54 km x 0.192 kWh/km), counted between the hybrid hold level (default 15 %, `HOLD_DEFAULT`, not yet read from the car) and 100 %.
- AC only, about 3.6 kW (sources: 3.3 / 3.6 / 3.7 kW). The charger's power only limits it downwards.

| Season | Electric | Petrol in hybrid mode | Range on a full charge |
|---|---|---|---|
| Summer | 19 kWh/100 km | 7.0 l/100 km | about 55 km |
| Winter (-5...+5 C) | 25 kWh/100 km | 8.3 l/100 km | about 42 km |

Petrol sources: Motor1 test (7.0 mixed, 8.3 motorway), m3.se cold test, Spritmonitor long term (7.33). **Winter electric figures are own estimates**, calibrate them (see `TESTING.md`).

## Prices
- **Petrol** is a daily price, loaded automatically. No forecast. A planned tax change on 1 Dec 2026 is not modelled.
- **Home electricity** is a monthly price (variable contract, billed on the monthly average of the spot price, so the time of charging does not matter). Formula derived from the October 2026 bills: `home = (monthly spot excl. VAT + 0.11497 variable + 0.2584 grid transfer + 0.36 energy tax) x 1.25`. October check: spot 1.5667 -> 2.875 SEK/kWh (bill basis 2.88). Fixed monthly fees are not part of the price per kWh.
  - The last bill month is "calculated from your bill" (`BILL` in the code). The current month is an estimate for the whole month (known days + typical rest). The next 3 months are estimates.
  - Estimates are a rule of thumb, not a market forecast: typical level of the month in 2023-25, raised by the factor (capped at 5) by which the last 3 months exceeded typical, with that excess fading 30 % per month. Range: back to typical .. excess persists.
  - `HOME_ADD` is valid until `HOME_ADD_VALID_TO` (2026-12-31); after that the page warns that fees may be outdated. Update `HOME_ADD` and `BILL` from the next bill.
- **Chargers:** NOBIL was tested on 2026-11-06 (EuroFuelPrices `docs/NOBIL_TEST_2026-11-06.md`): it has no price fields, and its terms forbid exposing the API to end users. So prices are operator list prices or entered by hand. Chargers without an operator name cannot share a price.

## Known gaps
1. "Nearest" means straight-line distance, no routing.
2. Winter range/consumption, AC power and the hybrid hold level are not measured yet.
3. Petrol and charger prices are crowd data or list prices and age quickly. Parking and idle fees and detours are not in the model.
4. The page has not been tested on a real phone.

## Ideas
- Annual calculation by mileage, split summer/winter.
- Automatic season preset by date.
- Real routing instead of straight-line distances.

## Constraints
- One file, no build, no third-party requests except eurofuelprices.com (Content-Security-Policy in the page).
- Mobile first, light/dark via `prefers-color-scheme`, safe-area insets respected.
- UI language: English. Decimal point in the display; input accepts comma and point.
- Short, clear recommendation with numbers. No filler.
