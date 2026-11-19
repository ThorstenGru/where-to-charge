# cars.json: where the model values come from (2026-11-19)

The picker "Your model (optional)" lists the models in `cars.json`. Each entry has the values the page needs (`v`: usable kWh from the socket, AC kW, reserve, summer/winter consumption, petrol values of a comparable petrol car), the raw inputs (`raw`), a source text and a confidence label. Everything stays editable in the page, and the consumption log corrects it.

## Sources and rules
- **Kia EV6 (2 entries, added at the owner's request):** Kia Sweden's own product fact sheet (valid from 2025-02-17): battery capacity 84 kWh, on-board charger 10.5 kW 3-phase (not 11), DC max 258 kW, WLTP up to 582 km and 15.9 kWh/100 km (RWD), 546 km and 17.0 kWh/100 km (AWD, 19\" wheels). Confidence **A** for those. Kia gives no net capacity: 0.95 x 84 kWh is an assumption. The WLTP consumption is already measured at the socket, so only the real-world factor is applied.
- **BEV (9 entries):** open-ev-data v1.24.0 (2025-12-30; CDLA-Permissive-2.0, which allows redistribution with the licence text; the dataset cites manufacturer data). Confidence **B**: not re-read against the manufacturers. Models are named by net battery size because the dataset's trim names are not reliable (ID.7 "PRO" is the 86 kWh car). Entries with an impossible combination (AC 11 kW on one phase: Fiat 500e, Renault 5, Peugeot e-208, Hyundai Ioniq 6) were left out.
- **PHEV (1 entry):** VW Tiguan eHybrid: net battery 19.7 kWh, AC up to 11 kW and up to about 120 km WLTP electric range from the Volkswagen press release (confidence **A** for those); the electric consumption is derived from them and the petrol values are the generic profile.
- **Derived values (estimates):** consumption at the socket (summer) = net kWh / WLTP range x 100 x 1.25 (charging losses and real-world driving; the factor is an assumption); winter = summer x 1.29 (the page's presets; evidence range 1.23 to 1.43). Usable from the socket = net kWh x 1.1. Petrol comparison by size class (net < 50 kWh small, < 75 medium, else large), like the generic profiles. The estimates for Tesla are likely optimistic (WLTP range is generous): correct them with the log.
- **DC peak** (BEV, used for the fast-charging model) = the dataset's maximum DC power.

## Not used, on purpose
- **EV Database (ev-database.org) and ADAC:** their terms allow use only with permission, unchanged and with a link, and the API is paid. A research helper read EV Database pages for the top sellers; those values are **not** in `cars.json` (they may be used by a person to cross-check, never copied).
- Models without a licence-clean source are missing, among them the top sellers Volvo EX40/XC40, EX30, Tesla Model Y, Kia EV3, Polestar 4 (the Kia EV6 was added from Kia's own sheet, see above), and the plug-in hybrids Volvo XC60, Skoda Kodiaq, Kia Sportage, VW Passat (net kWh missing or sources disagree; Volvo and Skoda pages blocked automated reads). To add one: read the manufacturer's own page (Swedish market) by hand, put the numbers into `raw`, fill `v` like the others, label confidence A.

## Maintenance
New models appear every year; this list is dated 2026-11-19. Run `python tools/build_cars.py <open-ev-data json>` again or edit the JSON by hand; `tests/calc.test.html` checks version, unique ids, limits, source and confidence.
