# data/kommun.json: municipality at your position (2026-11-19)

"Use my location" looks up the Swedish municipality on the device and sets the electricity price area and the energy-tax zone. The position never leaves the phone for this; only the 4-digit municipality number is stored (`komm`, plus `taxRed`).

## Data
- **Borders:** SCB, municipality boundaries (shape_svenska_260225.zip), licence CC0. SCB says they are simplified for thematic maps. They are simplified again (Douglas-Peucker 120 m, coordinates rounded to 0.001 degree): 146 KB, 40 KB gzipped, 290 municipalities. Points near a border or on a coast can land in the neighbour or in no municipality (then nothing is changed). Earlier measurement on the SCB file alone: 1.36 % of charger and petrol-station positions in a wrong municipality; this simplified file was only spot-checked (8 cities) and not measured again.
- **Price areas and tax zone:** Boio El (https://boio.se/el, period 2026-11, CC BY 4.0, credit "Källa: Boio El" with link; in the page footer). One person's data set without a service level: it is a build-time source, never loaded by the page. 273 municipalities have one price area, 17 have two (the page then keeps the user's choice if it is one of them and asks to choose the one on the bill). 46 northern municipalities have the reduced energy tax (26.4 instead of 36.0 oere/kWh excl. VAT).
- **Fees:** the default fee (0.73337 SEK/kWh excl. VAT, one household's October 2026 bills) includes the normal energy tax. In a reduced-tax municipality the default is lowered by 0.096. Grid fee per municipality is NOT done (Boio's own field is empty for many municipalities; the per-operator Ei table needs a municipality-to-operator map). A fee the user typed is never changed.

## Rebuild
`python tools/build_kommun.py <Kommun_Sweref99TM.shp> <boio.json>` (needs `pip install pyshp`; inputs described in the script). Do it when the tax or zones change (annually, or on a zone reform: Svenska kraftnät's report is due 2027-01-29) and before the energy tax changes on 1 January.

## Not done / not verified
- The 17 two-area municipalities are listed by Boio (derived); no official geodata of the price areas exists at municipality level.
- Accuracy of the simplified borders was not measured on many points.
- The grid fee, and the supplier mark-up, stay manual or at the default.
