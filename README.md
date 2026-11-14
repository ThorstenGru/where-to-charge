# Where to charge today? (Santa Fe PHEV, Sweden SE4)

Live: https://thorstengru.github.io/where-to-charge/ · Repo: ThorstenGru/where-to-charge

A phone web page that decides every day: **charge on the road (and top up at home), charge at home, or do not charge (drive in hybrid mode on petrol)**.

## Files
- `index.html`: the whole app (HTML, CSS, JS inline, no build; the only libraries are Leaflet from cdnjs with an integrity hash). Deployed with GitHub Pages from `main`.
- `manifest.json`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`: install as a home-screen app. No service worker (the page needs live data anyway).
- `tests/calc.test.html`: tests for the calculation. Open it over http (`python -m http.server`, then `/tests/calc.test.html`, or the same path on the Pages URL). The title says PASS or FAIL.
- `TESTING.md`: phone test and calibration checklist.

## How the page works
Page order: location (it sets petrol price and chargers, so it comes first; it runs by itself when the permission is already granted), recommendation, break-even, then what you can adjust (car, chargers on the map, petrol, home electricity, trip), then details and settings. The season follows the date (October to March = winter) until you pick one.

Live data from eurofuelprices.com (open CORS), no personal data is sent:
- `se.json`: petrol prices. The page uses the median of prices dated in the last 3 days (all prices if fewer than 20 are dated), cached 6 hours. "Use my location" lists the 5 nearest pumps and preselects the cheapest dated one.
- `ev_se.json`: charger positions (Open Charge Map, NOBIL), version 1 only. All entries are Type 2 AC. The 150 nearest chargers up to 22 kW are shown on a map (Leaflet, OpenStreetMap tiles); tapping one selects it. For the selected charger the page shows name, operator, power, connector type (Type 2 AC), number of points, and the flags of the data file: fixed cable, card or membership needed, notice required, pay at the location, parking fee, free according to the source, and the year of the last verification (marked old after 2 years). Cost notes and prices are not used: **no charger prices**. A credit line names the sources (Open Charge Map contributors, NOBIL by Enova, both CC BY 4.0) and the file date.
- `elpris.json`: SE4 monthly spot averages (excl. VAT).

Settings are stored on the device only when they differ from the defaults. Values that come from data (pump price, home price from spot) are stored only when typed by hand. The chosen charger is never stored.

## Calculation (`calc(st, ch)` in `index.html`, tested)
```
l_per_kWh      = petrol_l_100 / el_kWh_100            // litres saved per charged kWh
value_per_kWh  = l_per_kWh * petrol_price             // SEK
gain_per_kWh   = value_per_kWh - electricity_price
break_even_petrol_price      = electricity_price / l_per_kWh   // SEK/l
break_even_electricity_price = value_per_kWh                    // SEK/kWh
free_kWh       = 10.4 * (100 - max(battery%, hold%)) / (100 - hold%)
road_kWh       = min(free_kWh, parking_h * min(car_kW, charger_kW))
road_limit     = value_per_kWh - MIN_GAIN        // highest road price worth paying
```
Decision: the road price is unknown by design, so only home is rated against petrol. Home gain below `MIN_GAIN` (0.30 SEK/kWh), or an almost full battery (< 0.5 kWh free): hybrid mode. Otherwise: charge at home; with a charger chosen the page adds "top up there only if its app shows less than X" with X = min(home price, road_limit). In hybrid mode it names the road limit. Trip mode: electric km = (battery now + charge on site, capped at one full battery) x 100 / kWh per 100 km.

## Time at the charger
Home and road are limited the same way: time parked x power, never more than the room in the battery. Home has its own time (default 10 h, 1-24 h) and charger: a household socket at 6, 8, 10, 12 or 16 A (amps x 230 V, single phase: 1.38 to 3.68 kW) or a wallbox. At stations and on a wallbox the car's limit (default 3.6 kW) is the maximum power, so 16 A (3.68 kW) and every station give the same result. The card "Time at the charger" shows km on electricity by time (0.5-12 h plus your two times) for each socket current and for stations, plus the time for a full charge.

## Vehicle and assumptions
- Hyundai Santa Fe PHEV 1.6 T-GDi, model year 2025, battery 13.8 kWh gross. WLTP electric range 54 km (older sources: 58 km).
- Usable energy from the socket per full charge: about 10.4 kWh (= 54 km x 0.192 kWh/km), counted between the hybrid hold level (15 %, `HOLD_DEFAULT`: the level at which the car switches to hybrid mode, confirmed by the owner 2026-11-14) and 100 %.
- AC only, 3.6 kW car limit and 230 V single-phase mains (both confirmed by the owner, 2026-11-14; published sources vary: 3.3 / 3.6 / 3.7 kW). A charger's power only limits it downwards.

| Season | Electric | Petrol in hybrid mode | Range on a full charge |
|---|---|---|---|
| Summer | 19 kWh/100 km | 7.0 l/100 km | about 55 km |
| Winter (-5...+5 C) | 25 kWh/100 km | 8.3 l/100 km | about 42 km |

Petrol sources: Motor1 test (7.0 mixed, 8.3 motorway), m3.se cold test, Spritmonitor long term (7.33). **Winter electric figures are own estimates**, calibrate them (see `TESTING.md`).

### Winter consumption: published evidence (researched 2026-11-14; the page keeps 25 kWh/100 km and 8.3 l/100 km as "estimated")
- EV Database figures, via [elektrischeauto.nl](https://www.elektrischeauto.nl/?p=49683) (2021 model, 11 kWh usable, "indicative, partly estimated", no data date): real range 36 km in winter (-10 C, heating on) and 46 km in summer (23 C, AC off); consumption 30.6 kWh/100 km winter (city 25.6, highway 36.7) and 23.9 kWh/100 km summer (city 18.3, highway 29.7); WLTP 19 kWh/100 km.
- Winter test of the 2026 model with the 13.8 kWh battery, [hh-autos.com](https://hh-autos.com/hyundai-santa-fe-phev-im-winter-test-warum-die-e-reichweite-auf-32-km-einbricht/): electric range 32 to 38 km at about 0 C (WLTP 54 km); no consumption figures given.
- Petrol with an empty battery in the cold: [m3.se](https://www.m3.se/article/1828285/hyundai-santa-fe-phev.html) measured 0.8-0.85 l/mil (8.0-8.5 l/100 km), which fits the 8.3 used here.
- Not usable for per-km consumption: Spritmonitor logs (for example 13.74 kWh/100 km) average over all km including petrol km.
- Reading: both seasons look optimistic against these sources (summer 19 = WLTP versus 23.9 real; winter 25 versus 30.6 at -10 C and about 27-32 implied at 0 C). Higher consumption lowers the petrol value per kWh and can flip the recommendation to hybrid mode. Values are unchanged until the owner decides; measure the real figure (see `TESTING.md`).

## Prices
- **Petrol** is a daily price, loaded automatically. No forecast. A planned tax change on 1 Dec 2026 is not modelled.
- **Home electricity** is a monthly price (variable contract, billed on the monthly average of the spot price, so the time of charging does not matter). Formula derived from the October 2026 bills: `home = (monthly spot excl. VAT + 0.11497 variable + 0.2584 grid transfer + 0.36 energy tax) x 1.25`. October check: spot 1.5667 -> 2.875 SEK/kWh (bill basis 2.88). Fixed monthly fees are not part of the price per kWh.
  - The last bill month is "calculated from your bill" (`BILL` in the code). The current month is an estimate for the whole month (known days + typical rest). The next 3 months are estimates.
  - Estimates are a rule of thumb, not a market forecast: typical level of the month in 2023-25, raised by the factor (capped at 5) by which the last 3 months exceeded typical, with that excess fading 30 % per month. Range: back to typical .. excess persists.
  - `HOME_ADD` is valid until `HOME_ADD_VALID_TO` (2026-12-31); after that the page warns that fees may be outdated. Update `HOME_ADD` and `BILL` from the next bill.
- **Chargers have no price in the page.** No free per-station price feed exists for Sweden (researched 2026-11-12): NOBIL (the data behind Trafikverket's national access point trafficdata.se) has no price fields, and its terms forbid exposing the API to end users (EuroFuelPrices `docs/NOBIL_TEST_2026-11-06.md`); Chargeprice and similar are commercial; 94 % of the Type 2 chargers up to 22 kW have no operator name. Instead the page shows what a road charge can deliver (kWh, km, petrol saved) and the highest price worth paying; you compare it with the price in the charger's app. Break-even tiles and a small table (app price 3-7 SEK/kWh, and petrol -3/0/+3 SEK/l) show where the decision flips.

## Input checks
Stored settings are validated on start (a bad value falls back to the default, so the page cannot break). Petrol and home price are clamped at 0 and the page warns above plausible limits (petrol outside 8-30 SEK/l, home above 15 SEK/kWh). Pumps farther than 50 km are not listed, and a nearest charger farther than 30 km is flagged.

## Known gaps
1. "Nearest" means straight-line distance, no routing.
2. Winter range/consumption is not measured yet.
3. Petrol prices are crowd data and age quickly. The road price must be read from the charger's app. Parking and idle fees and detours are not in the model.
4. The page has not been tested on a real phone.

## Ideas
- Annual calculation by mileage, split summer/winter.
- Automatic season preset by date.
- Real routing instead of straight-line distances.

## Constraints
- One file, no build. Requests go only to eurofuelprices.com (data), cdnjs (Leaflet, integrity-checked) and tile.openstreetmap.org (map tiles; they see your IP and the map area). Content-Security-Policy in the page.
- Mobile first, light/dark via `prefers-color-scheme`, safe-area insets respected.
- UI language: English. Decimal point in the display; input accepts comma and point.
- Short, clear recommendation with numbers. No filler.
