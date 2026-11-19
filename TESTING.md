# Phone test checklist

Automated calculation tests: open `/tests/calc.test.html` over http (for example on the Pages URL). The tab title must say PASS.

Page: https://thorstengru.github.io/where-to-charge/

## 1. Install and start (5 min)
- [ ] Open the page in Safari (iPhone) or Chrome (Android). It loads without errors and shows a recommendation.
- [ ] Add to Home Screen. The green lightning-bolt icon appears and the app opens full screen.
- [ ] Rotate / scroll: no horizontal scrolling, nothing cut off, dark mode readable.

## 2. Automatic data and languages (5 min)
- [ ] Petrol shows "daily price, loaded automatically" with a recent date and a plausible price (check against a pump you know).
- [ ] Home electricity: the month chips show last month, this month (estimated) and three estimates. Switch the price area (SE1-SE4) and the contract (monthly, hourly, fixed): the text and price follow.
- [ ] Switch the language EN, DE, SV: every text changes, nothing is cut off, decimals use a comma in DE and SV. Report translation mistakes.
- [ ] Switch the car type to the electric car: there is no hybrid mode, the petrol card says it is the comparison car.
- [ ] Airplane mode: the page still opens and warns about missing data instead of breaking.

## 3. Use my location (5 min)
- [ ] Tap "Use my location", allow access. Five petrol stations appear and the map shows chargers around you.
- [ ] The nearest petrol station and charger are really near you (compare with a maps app).
- [ ] Pick a petrol station: the petrol price above changes to it.
- [ ] Tap a charger on the map (or choose it in the list): details appear and the recommendation names the highest road price worth paying. Compare it with the price in the charger's app. "Navigate" opens the route, "Find the price" a web search.
- [ ] Switch on the outside temperature (opt-in): the season note shows the temperature.

## 3b. New since 2026-11-19 (10 min)
- [ ] First open: the answer is at the top with no setup. Under it "Your basis": plug-in hybrid / electric car, price area SE1-SE4, the basis line, "Use my location". Everything else sits under "Adjust and details" (closed). Nothing cut off at the right edge (the EN DE SV switch).
- [ ] A "Close call" verdict (amber, dashed) appears when the home gain is near 0.30 SEK/kWh: does it read clearly?
- [ ] Open "Adjust and details": the map draws completely (no grey area) after opening.
- [ ] Electric car: tick "I cannot charge at home or at work": the answer becomes "Charge on the road" with list prices and a cost per 100 km table; untick: back to normal.
- [ ] Electric car + "Use my location": violet dots = fast chargers (CCS/CHAdeMO), also in the list ("Fast DC ... kW"). Pick one: the power note says "about X kW on average". Is the charger really there? Is the kW plausible?
- [ ] "Your model (optional)": pick one: battery, AC power and consumption change; Santa Fe stays as a car type in the list.
- [ ] Petrol price: after 1 December it should show the +3.00 SEK/l step (note "Estimate ..." for 3 days); from about 20 November a notice announces it.
- [ ] Type a petrol price: after 7 days it falls back to the live price with a notice.
- [ ] Safari: close the tab and reopen it the next day: are your settings still there (also after installing to the Home Screen: that is a separate store, set them again)?
- [ ] Open "Privacy and disclaimer": text readable in your language; "Delete all my saved settings and log" works.

## 3c. Added 2026-11-19 (10 min)
- [ ] "Use my location": below the price areas a line says which municipality you are in, the price area and the energy tax. Is the municipality right? If you live near a border or the coast, is it still right? In a municipality with two price areas the line asks you to choose.
- [ ] After that the price area chip and the fee field changed by themselves (only if you had not typed fees). Close and reopen the page: the area stays.
- [ ] "Your model (optional)": pick a Kia EV6 or EV3 (electric car): battery, AC 10.5 kW and consumption change; the note under the picker names Kia's fact sheet. Do the values look like your experience? Tell me which ones are off.
- [ ] Electric car, "Adjust and details", time table: the two "Fast DC" columns show an average kW; do the km after 0.5 and 1 h look realistic for your car?
- [ ] Footer: "Källa: Boio El" and the SCB link are there; "Privacy and disclaimer" mentions the municipality lookup.
- [ ] Weekly price check: nothing to do. If a GitHub issue "Charging list prices changed" appears, read it and update the price band (PUBLIC in index.html and tools/price_watch.py).

## 4. Calibrate the assumptions (over 2-3 weeks)
Write down the real values and change the defaults in `index.html` (or on the page) if they differ.

| Assumption | Now | Real value | How to measure |
|---|---|---|---|
| Electric range, full charge, summer | 55 km | | Trip meter on a full charge, mild weather |
| Electric range, full charge, winter | 42 km | | Same, at -5 to +5 C |
| Winter consumption | 25 kWh/100 km (estimated; see README for published figures and their basis) | | kWh from the socket (wall meter or charger) / km driven |
| Petrol in hybrid mode, winter | 8.3 l/100 km | | Board computer or fill-up |

## 5. Use it for a few weeks
- [ ] Log each charge in "Measure your real consumption" (kWh at the socket, electric km since the last charge). After 20+ km per season, use the result as the car's value.
- [ ] Note the monthly price estimate the page shows shortly before the bill arrives (it changes every day), then compare it with the real price per kWh to judge the forecast rule.

## Report back
Note anything that looks wrong (screenshot + what you expected) and send it to Claude.
