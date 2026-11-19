# Entscheidungen 2026-11-18/19 (Owner)

Basis: [RESEARCH_2026-11-18.md](RESEARCH_2026-11-18.md). Nummern verweisen auf dessen Abschnitt 7 (1-16) und 9 (S1-S11).

## Entschieden
| Thema | Entscheidung |
|---|---|
| Benzinzahl (1) | Marken-Median, nur Crowd-95, ANWB-95 ausgeschlossen, Plausibilitätsband, Abgleich EU-Bulletin |
| Steuerstufe (3) | Ab ca. 20. Nov ankündigen; ab 2026-12-01 00:00 +3,00 SEK/l (inkl. Moms) addieren, in den ersten 3 Tagen als "Schätzung" gekennzeichnet; 2027-01-01 +0,125 |
| Erststart (5) | Zwei Fragen (Autotyp, Wohnort), sofort Antwort mit Standardwerten |
| Knapp-Urteil (4) | Ja, "knapp" statt klarem Urteil nahe der Schwelle (ca. ±0,45 SEK/kWh) |
| Gebühren (2) | Automatisch (Gebiet, Steuerzone, Netz-Default aus Wohnort), Rechnungszahlen nur hinter "Anpassen" oder wenn das Urteil kippen könnte |
| Prognose (7) | Variante A: SD3, Band ±20 % (Winter breiter), Regime-Banner (letzter Monat > 1,5x typisch), laufender Monat = Mittel der bekannten Tage, rollierendes HIST ohne 2022 |
| Euronext (6) | Nur Link, keine Daten, keine Anfrage |
| Zähler (8) | Anonymer Zähler am Cloudflare-Worker, ohne IP und Freitext; README/Datenschutztext von "keine Analytics" auf "anonyme Zähler" ändern; nie automatisch auf Preise anwenden |
| Kontakt (8) | Alias über eurofuelprices.com (und Facebook-Seite als zweiter Weg); kein Name, keine Privatadresse. Alias muss der Owner in Cloudflare E-Mail-Routing anlegen |
| Höchstkostenschutz (14) | Separate Zeile, nicht eingerechnet |
| Reihenfolge (14) | Elektroautos mit DC zuerst, dann Dänemark |
| Monetarisierung (16) | Nie |
| Einstellungen (S1) | Still automatisch speichern, nur die zwölf Fehler reparieren (Option A); kein "Merken"-Schalter, kein Export-Code. Schema trotzdem mit Versionsfeld |
| Getippte Preise (S2) | Nach 7 Tagen zurück auf Live-Daten, mit sichtbarem Hinweis "Dein Preis vom ..." |
| NOBIL-Zählprobe (11) | Freigegeben (einmalig, nur Zählwerte) |
| iPhone-Test (10) | Owner testet; Testseite wird gebaut (Safari-Tab gegen Home-Screen, 3 Tage) |

## Noch nicht entschieden (Standard = Empfehlung des Dokuments, falls nichts anderes gesagt wird)
9 Lizenzen (RegSO, Boio, bensinpriser.nu): nur CC0/CC BY-Quellen nutzen. 12 PHEV-Definitionen: Santa-Fe-Wert bleibt, Hold 15 %. 13 Karte: nächste 30 bis 50. 15 Selbstheilung: weiter manuell mit ntfy. Saison (S3): nur auto, kurzer Override. Herkunft (S4), QR/Profile (S9), Same-Origin-Aufgabe (S11): offen.
