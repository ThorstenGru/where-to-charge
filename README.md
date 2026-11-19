# Where to charge today?

Live: https://thorstengru.github.io/where-to-charge/ · Repo: ThorstenGru/where-to-charge

A phone web page for everyone who drives electrically instead of on petrol. **Primary: plug-in hybrids (PHEV). Secondary: pure electric cars (BEV).** It answers one question every day: where to charge, and is it worth it? For a plug-in hybrid: charge at home, top up on the road, or drive on petrol. For an electric car: where to charge (home or road) and what it saves against a comparable petrol car.

Languages: English, Deutsch, Svenska (switch top right; the browser language is the default, `?lang=de` forces one). The translations were written without a native review: please report mistakes. Coverage today: **Sweden** (petrol prices, electricity price areas SE1-SE4, Type 2 AC chargers).

## Files
- `index.html`: the whole app (HTML, CSS, JS inline, no build; the only library is Leaflet 1.9.4, kept in `vendor/leaflet-1.9.4/` with its licence and an integrity hash; no third-party script host).
- `manifest.json`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`: install as a home-screen app. No service worker (the page needs live data anyway).
- `tests/calc.test.html`: about 100 checks (calculation, car types, recommendation, charger list, price months, hourly prices, log, tomorrow, year, texts in three languages). Open it over http (`python -m http.server`, then `/tests/calc.test.html`, or the same path on the Pages URL). The title says PASS or FAIL.
- `.github/workflows/tests.yml`: runs the test page in headless Chrome on every push and fails when it does not say ALL PASSED (it reports only; Pages deploys from `main` regardless).
- `TESTING.md`: phone test checklist and calibration table.

## What the page does
Page order: recommendation (a "close call" for a plug-in hybrid when the gain is within ±0.45 SEK/kWh of the 0.30 limit), your basis (car kind, price area, optional location; the answer is there with the defaults, no setup), break-even, then one layer down under "Adjust and details": car, time at the charger, chargers on the map, petrol, electricity at home, distance, per year, details, consumption log, car settings.

- **Car type:** six generic profiles (plug-in hybrid and electric car, each small / medium / large; own estimates, marked "typical") and "Hyundai Santa Fe PHEV 2025". Every value (usable battery energy at the socket, AC limit, hybrid hold level or reserve buffer, electric consumption and petrol consumption, summer and winter) can be edited; changes are stored on the device. For a BEV the "petrol" values describe the comparable petrol car and there is no hybrid mode.
- **Electric car without home charging:** a checkbox (electric cars only) switches the answer to "Charge on the road" with dated list-price bands for public AC and DC (checked 2026-11-18, `PUBLIC` in index.html; the page warns after 60 days) and what 100 km cost against a petrol car. Electric cars also get a cost-per-100-km table. No price per station, ever.
- **Recommendation:** PHEV: charge at home, "top up on the road only below X SEK/kWh", or drive in hybrid mode. BEV: where to charge, plus a hint when a petrol car would be cheaper.
- **Chargers:** the 150 nearest Type 2 AC chargers (up to 22 kW) on a map (Leaflet, OpenStreetMap) and in a list for keyboard users. For the chosen charger: name, operator, power, number of points, fixed cable, card/membership, notice, pay at the location, parking fee, free according to the source, last verification year, links to navigate and to search the price. **No charger prices** (see below).
- **Your model (optional):** `cars.json` lists 11 electric cars (9 from open-ev-data, confidence B; 2 Kia EV6 from Kia Sweden's own fact sheet, confidence A) and 1 plug-in hybrid (VW press release, confidence A); a model sets battery, AC power and an estimated consumption, everything stays editable. How the values were made and what was left out on purpose: docs/CARS.md. The list is short on purpose: only licence-clean, sourced values.
- **Time at the charger:** km on electricity by time and power: household sockets at 6, 8, 10, 12, 16 A (x 230 V) and stations. The car's own limit is the maximum power everywhere. Home has its own time and charger (socket current or wallbox).
- **Electricity at home:** price area SE1-SE4 and contract: monthly average (month chips with this and the next months), hourly spot (the average of the cheapest hours in the next 24 h, enough hours for the energy to charge), or a fixed price. Fees on top of the spot price are editable.
- **Distance:** tomorrow's distance (how much to charge, how long, what it costs) and a round trip with a charging stop.
- **Per year:** estimated saving for N full charges a week, half a year with summer and half with winter values.
- **Consumption log:** enter kWh at the socket and electric km after a charge; the page shows the real kWh per 100 km per season and can use it as the car's value.
- **Temperature (opt-in):** use the outside temperature at your position instead of the season. It sends the rounded position (0.1 degree) to open-meteo.com.

## Data and privacy
No accounts, no cookies, no tracking of individuals. Anonymous counters (what is used, never who): on the live site only, once per browser session, a fixed list of names (opened, car type, which recommendation, location used), no identifier and no referrer, off with Do Not Track / Global Privacy Control; they go to the EuroFuelPrices worker (`/api/poll`, table `events`, no IP stored). (the page has a privacy and disclaimer section and a button that deletes all saved data). Settings and the log stay on the device (localStorage; only values that differ from the defaults are stored, car values one by one; a manual season choice and typed prices expire after 7 days; a damaged save is kept under `wo-laden-heute-v1-bad`). Requests go to: eurofuelprices.com (petrol prices, charger file, spot prices; no personal data), cdnjs (Leaflet, integrity-checked), tile.openstreetmap.org (map tiles; they see your IP and the map area), and api.open-meteo.com only when you switch on the temperature option. The position itself is never sent anywhere except as stated. Content-Security-Policy in the page lists these hosts.

## Calculation (`calc(st, ch)` in `index.html`, tested)
```
l_per_kWh      = petrol_l_100 / el_kWh_100            // litres saved per charged kWh
value_per_kWh  = l_per_kWh * petrol_price             // SEK
gain_per_kWh   = value_per_kWh - electricity_price
break_even_petrol_price      = electricity_price / l_per_kWh   // SEK/l
break_even_electricity_price = value_per_kWh                    // SEK/kWh
free_kWh       = usable * (100 - max(battery%, hold%)) / (100 - hold%)
charged_kWh    = min(free_kWh, time_parked * min(car_kW, charger_kW))
road_limit     = value_per_kWh - MIN_GAIN        // highest road price worth paying
```
Consumption is the summer value, the winter value, or in between by outside temperature (20 C and warmer: summer, 0 C: winter, colder rises up to -10 C). PHEV decision: home gain below `MIN_GAIN` (0.30 SEK/kWh) or an almost full battery (< 0.5 kWh free): hybrid mode; otherwise charge at home and top up on the road only below min(home price, road limit). A BEV always charges: the road is worth it below the home price.

## Prices
- **Petrol** is a daily price, loaded automatically: only user-reported prices (bensinpriser.nu; ANWB's Swedish "95" slot is ignored), dated in the last 3 days (all if fewer than 20), prices outside max(0.8 SEK, 5 %) of the first median dropped, then the median of the brand medians (brands with 3+ prices) so one chain cannot decide. Cached 6 hours. "Use my location" replaces it with a nearby pump. The petrol tax steps (+3.00 SEK/l incl. VAT on 2026-12-01, +0.125 on 2027-01-01; table `TAXSTEPS`, source in docs/RESEARCH_2026-11-18.md) are added to prices stamped before the step, marked as an estimate, and announced 11 days ahead. No forecast.
- **Hand-typed prices** (petrol, home price, fees) expire after 7 days and the live data applies again; the page says so.
- **Home electricity:** price = (spot + fees) x 1.25. The fee default (0.73337 SEK/kWh excl. VAT) is one household's October 2026 bills (variable costs + grid transfer + energy tax): the page warns after 2026-12-31 while it is untouched, and users should enter their own. Monthly estimates are a rule of thumb, not a market forecast: the mean of the last 3 complete months times the square root of (typical level of the target month / typical level of those 3 months); typical = same month of the last three full years, never 2022. Band on the all-in price: ±20 % (±30 % Nov-Mar); the current month is the mean of the known days (±12 % / ±6 %). A banner warns when the last 3 months were more than 1.5x typical (as in winter 2026), because the estimates are then unreliable and probably too low. Backtest and sources: docs/RESEARCH_2026-11-18.md 2.2.
- **Chargers have no price in the page.** No free per-station price feed exists for Sweden (researched 2026-11-12): NOBIL (the data behind Trafikverket's national access point trafficdata.se) has no price fields, and its terms forbid exposing the API to end users; Chargeprice and similar are commercial; 94 % of the Type 2 chargers up to 22 kW had no operator name in the old data. Instead the page shows what a road charge delivers and the highest price worth paying; you compare it with the price in the charger's app.

## Hyundai Santa Fe PHEV 2025 (preset)
13.8 kWh gross, about 10.4 kWh usable from the socket (54 km WLTP), AC limit 3.6 kW and hybrid level 15 % (confirmed by the owner, 2026-11-14), 230 V single phase at home. Winter consumption 25 kWh/100 km and 8.3 l/100 km are estimates. Published evidence (researched 2026-11-14): EV Database via elektrischeauto.nl (2021 model, 11 kWh usable, indicative): real range 36 km winter (-10 C, heating on) / 46 km summer; consumption 30.6 / 23.9 kWh/100 km; [hh-autos.com](https://hh-autos.com/hyundai-santa-fe-phev-im-winter-test-warum-die-e-reichweite-auf-32-km-einbricht/) winter test of the 2026 model: 32-38 km at about 0 C; m3.se: 8.0-8.5 l/100 km with an empty battery on a long drive. The basis (socket or battery) of the EV Database numbers is not stated, so the comparison is rough. Higher consumption lowers the petrol value per kWh and can flip the recommendation to hybrid mode: measure with the consumption log.

## Known gaps
1. Sweden only. Other countries need their own petrol, spot and charger data.
2. Fast chargers (CCS, CHAdeMO, Tesla, MCS; file `ev_dc_se.json` from the EuroFuelPrices pipeline, about 2,300 Swedish stations) are shown for electric cars only. Their kW is the charger's rated power, a ceiling; the page assumes about two thirds of the car's fast-charging peak on average (10 to 80 %), a rough estimate. Plug-in hybrids see Type 2 AC only. Not modelled: charging only to 80 %, cold batteries, shared hub power.
3. "Nearest" means straight-line distance, no routing.
4. No live availability or fault status of chargers (the data source for that has its own terms, not checked).
5. The typical car values are estimates; the page has not been tested on a real phone.

## Ideas
- More countries (Norway has chargers already).
- Routing and charging stops along a route.
- Live status of chargers.
