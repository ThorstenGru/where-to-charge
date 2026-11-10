# Handover: „Wo laden heute?“ (Santa Fe PHEV, Schweden SE4)

## Ziel
Eine Handy-Webseite, die jeden Tag entscheidet: **remote laden, zuhause laden oder nicht laden (HEV-Modus, Benzin)**. Auslöser im Chat war die Frage „Wo laden heute?“.

## Stand
- Eine einzige, selbstenthaltene Datei: `wo-laden-heute.html` (HTML, CSS, JS inline, kein Build).
- Veröffentlicht als Claude-Artifact: https://claude.ai/artifact/R2Rqc4S9qraL2mrFXGXK2n (Änderungen dort nur über Claude.ai, nicht aus Claude Code).
- Funktioniert: Eingaben (Benzin, Heimstrom, Jahreszeit, Akku-Stand, Standzeit, Ladeleistung), 7 Säulen mit Haken und editierbarem Preis, Empfehlung, Vergleichstabelle, Speicherung per `localStorage` (Schlüssel `wo-laden-heute-v1`).
- Nicht getestet auf einem echten Gerät.

## Fahrzeug und Annahmen
- Hyundai Santa Fe PHEV 1.6 T-GDi, VIN-Modelljahr 2025 (MX5-Generation), Batterie 13,8 kWh brutto.
- Elektrische Reichweite WLTP: 54 km (Hyundai Schweden, MX5). Ältere Quellen nennen 58 km.
- Laden nur AC, ca. 3,6 kW (Quellen uneinig: 3,3 / 3,6 / 3,7 kW; Hyundai nennt 6,5 h am Haushaltsstecker). Kein DC-Schnellladen angenommen.
- Nutzbare Energie aus der Steckdose pro Vollladung: ca. 10,4 kWh (= 54 km × 0,192 kWh/km), im Code `USABLE_KWH`.

| Jahreszeit | Elektrisch | Benzin (Akku leer) | Elektrische Reichweite (Annahme) |
|---|---|---|---|
| Sommer | 19 kWh/100 km | 7,0 l/100 km | ca. 50 km |
| Winter (−5…+5 °C) | 25 kWh/100 km | 8,3 l/100 km | ca. 30 km |

Quellen für Benzin: Motor1-Test (7,0 gemischt, 8,3 Autobahn), m3.se-Kältetest (0,8–0,85 l/mil), Spritmonitor-Langzeit (7,33). **Elektrische Winterwerte und Reichweiten sind eigene Schätzungen.**

## Rechenmodell (im Code: `calc()`)
```
l_pro_kWh   = benzin_l_100 / el_kWh_100          // gesparte Liter pro geladener kWh
wert_pro_kWh = l_pro_kWh * benzinpreis            // SEK
gewinn_pro_kWh = wert_pro_kWh - strompreis
break_even_benzinpreis = strompreis / l_pro_kWh   // SEK/l
frei_kWh = USABLE_KWH * (1 - akku%/100)
remote_kWh = min(frei_kWh, standzeit_h * kW)
```
Entscheidungslogik: bester Gewinn pro kWh gewinnt. Unter 0,30 SEK/kWh oder bei fast vollem Akku (<0,5 kWh frei) lautet die Empfehlung „HEV fahren / nicht laden“. Bei Remote-Sieg wird der Rest zuhause vorgeschlagen.

## Preise (Stand 10.11.2026)
- Benzin 95: 15,80 SEK/l. Ab 1. Dez. 2026 endet die Teilsenkung der CO₂-Steuer (+3 SEK/l inkl. Moms), also ca. 18,80.
- **Heimstrom (Skellefteå Kraft + E.ON Nät, Elområde SE4):** Rörligt avtal, abgerechnet mit dem **Monatsmittel des Spotpreises**, nicht stündlich. Der Zeitpunkt des Ladens ändert die Kosten also nicht.
  - Oktober: Mittelspot 1,5667 SEK/kWh, rörliga kostnader 0,11497, Påslag 0,06 (rabattiert bis 2027-05-31), Nät-Överföring 0,2584, Energieskatt 0,36, Moms 25 % → **2,88 SEK/kWh**.
  - November (Schätzung, Spotsnitt ca. 2,94 SEK exkl. Moms bis 5. Nov.): **ca. 4,59 SEK/kWh**.
  - Fixe Kosten (Elnätsabonnemang 668 kr/Monat) sind nicht Teil der Rechnung.
- Öffentliche Säulen (ChargeFinder-Screenshots, „zuletzt registrierte Preise“, Standardwerte im Code):
  Lidl Eslöv 3,50 · InCharge Teckomatorp 3,50 · Karlsrobad Eslöv (Milepost-App) 4,25 · MAX Handelsvägen 4,50 · Aimo Helsingborg 4,50 · ChargeNode Löddeköpinge/Helsingborg 4,76 · InCharge Coop Landskrona 5,00.

## Bekannte Lücken und Risiken
1. Entfernung Billeberga → Karlsrobad (Eslöv) nur geschätzt (~30 km pro Richtung). Es gibt keine Streckenrechnung in der Seite.
2. Winterreichweite (30 km) und Winterverbrauch (25 kWh/100 km) sind nicht belegt. Mit realen Fahrdaten kalibrieren.
3. Ladeleistung 3,6 kW unbestätigt. Prüfen, ob die 22-kW-Säulen das Auto wirklich schneller laden (vermutlich nein).
4. Säulenpreise sind Crowd-Daten und veralten. Parkgebühren, Blockiergebühren und Umwege fehlen im Modell.
5. Heimstrompreis November ist eine Schätzung. Nach der Novemberrechnung korrigieren.
6. Die Seite kennt keinen Benzinpreis-Verlauf und keine Live-Daten (kein Netzwerkzugriff möglich, daher alles manuell).

## Vorschläge für nächste Schritte
- Strecken-Modus: Hin- und Rückfahrt (km eingeben), Berechnung „komplett elektrisch möglich?“ inklusive Laden vor Ort (Winter ca. 44 km, Sommer ca. 69 km Rundfahrt bei 1 h Laden).
- Jahreskalkulation nach Fahrleistung, getrennt Sommer/Winter.
- Heimstrompreis als Formel aus Spotsnitt + Aufschlägen statt Direkteingabe.
- Automatische Voreinstellung der Jahreszeit nach Datum.
- PWA-Basics (Manifest, Homescreen-Icon), falls die Seite selbst gehostet wird.

## Randbedingungen
- Eine Datei, keine externen Abhängigkeiten außer der optionalen Schriftart (Google Fonts, mit System-Fallback).
- Mobile first, Hell/Dunkel per `prefers-color-scheme`, Safe-Area-Insets beachtet.
- Sprache der Oberfläche: Deutsch. Dezimalkomma in der Anzeige, Eingabe akzeptiert Komma und Punkt.
- Nutzerwunsch: kurze, klare Empfehlung mit Zahlen. Keine Füllsätze.
