# Phone test checklist

Automated calculation tests: open `/tests/calc.test.html` over http (for example on the Pages URL). The tab title must say PASS.

Page: https://thorstengru.github.io/where-to-charge/

## 1. Install and start (5 min)
- [ ] Open the page in Safari (iPhone) or Chrome (Android). It loads without errors and shows a recommendation.
- [ ] Add to Home Screen. The green lightning-bolt icon appears and the app opens full screen.
- [ ] Rotate / scroll: no horizontal scrolling, nothing cut off, dark mode readable.

## 2. Automatic data (2 min)
- [ ] Petrol shows "daily price, loaded automatically" with a recent date and a plausible price (check against a pump you know).
- [ ] Home electricity shows month chips: October "calculated from your bill" = 2.88, November estimated.
- [ ] Airplane mode: the page still opens and warns about missing data instead of breaking.

## 3. Use my location (5 min)
- [ ] Tap "Use my location", allow access. Five petrol stations appear and the map shows chargers around you.
- [ ] The nearest petrol station and charger are really near you (compare with a maps app).
- [ ] Pick a petrol station: the petrol price above changes to it.
- [ ] Tap a charger on the map: details (operator, power, Type 2 AC) appear and the recommendation names the highest road price worth paying. Compare it with the price in the charger's app.

## 4. Calibrate the assumptions (over 2-3 weeks)
Write down the real values and change the defaults in `index.html` (or on the page) if they differ.

| Assumption | Now | Real value | How to measure |
|---|---|---|---|
| Electric range, full charge, summer | 55 km | | Trip meter on a full charge, mild weather |
| Electric range, full charge, winter | 42 km | | Same, at -5 to +5 C |
| Winter consumption | 25 kWh/100 km | | kWh from the socket (wall meter or charger) / km driven |
| Petrol in hybrid mode, winter | 8.3 l/100 km | | Board computer or fill-up |

## 5. After the November bill
- [ ] Compare the real November price per kWh with the estimate (4.06, range 2.97 to 5.00). Note the real value to judge the forecast rule.
- [ ] Add the new monthly spot average to `BILL` in `index.html` if you want the bill month shown as "calculated from your bill".

## Report back
Note anything that looks wrong (screenshot + what you expected) and send it to Claude.
