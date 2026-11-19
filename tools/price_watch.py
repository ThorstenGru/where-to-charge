"""Weekly check that the charging list prices used in index.html (PUBLIC band) still match the operators' own price pages.

It never changes the page: it only reports. Exit code 1 = something differs or could not be read (the workflow then opens an issue).
One GET per page per week, with an identifying User-Agent. Operators' terms about automated reading were NOT read (docs/RESEARCH_2026-11-18.md 2.4): if an operator objects, remove its entry.
Only pages that can be read as plain text with a stable phrase are checked. Recharge (price loaded by script) and Ionity (several countries mixed, no stable phrase)
must be checked by hand. `python tools/price_watch.py --selftest` tests the parsing offline.
"""
import re
import sys
import urllib.request

UA = "where-to-charge price check (weekly, one request per page; https://github.com/ThorstenGru/where-to-charge)"

# name, url, [(label, regex with one group = the number, expected SEK/kWh incl. VAT)]. Expected values: read 2026-11-18.
CHECKS = [
    ("Circle K", "https://www.circlek.se/laddning/priser", [
        ("own ultra-fast DC 300-400 kW, price via app", r"Pris via app:\s*(\d+[,.]\d+)\s*kr/kWh", 6.69)]),
    ("Allego", "https://www.allego.eu/pricing/", [
        ("first price block (Sweden at the time): regular up to 22 kW, pay as you go", r"Pay as you go.{0,60}?Regular up to 22 kW\s*(\d+[,.]\d+)\s*kr/kWh|Regular up to 22 kW\s*(\d+[,.]\d+)\s*kr/kWh", 6.25),
        ("first price block: ultra-fast up to 400 kW, pay as you go", r"Pay as you go\s*Ultrafast up to 400\s*kW\s*(\d+[,.]\d+)\s*kr/kWh", 6.30)]),
]


def text_of(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&gt;", ">")
    return re.sub(r"\s+", " ", t)


def first_number(pattern, text):
    m = re.search(pattern, text, re.S)
    if not m:
        return None
    g = next((x for x in m.groups() if x), None)
    return float(g.replace(",", ".")) if g else None


def check_text(text, rules):
    """-> list of (label, found, expected, ok)"""
    out = []
    for label, pat, want in rules:
        got = first_number(pat, text)
        out.append((label, got, want, got is not None and abs(got - want) < 0.005))
    return out


def selftest():
    cir = "Ultrasnabbladdare DC 300-400 kW Pris via app: 6,69 kr/kWh Engångsbetalning: 6,69 kr/kWh Priser roaming Mer"
    assert check_text(cir, CHECKS[0][2])[0][1:] == (6.69, 6.69, True)
    assert check_text(cir.replace("6,69", "6,99", 1), CHECKS[0][2])[0][3] is False
    alg = "Pay as you go Ultrafast up to 400kW 6.30 kr/kWh Charge and pay as you go No app Fast up to 50 kW 6.30 kr/kWh Regular up to 22 kW 6.25 kr/kWh"
    r = check_text(alg, CHECKS[1][2])
    assert r[0][1] == 6.25 and r[1][1] == 6.30 and all(x[3] for x in r), r
    assert check_text("nothing here", CHECKS[1][2])[0][1] is None   # unreadable page counts as a failure, not as "unchanged"
    print("price_watch selftest: ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    problems = []
    for name, url, rules in CHECKS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            problems.append(f"{name}: page could not be read ({type(e).__name__})")
            continue
        for label, got, want, ok in check_text(text_of(html), rules):
            line = f"{name} / {label}: expected {want:.2f}, found " + ("nothing" if got is None else f"{got:.2f}")
            print(("ok   " if ok else "DIFF ") + line)
            if not ok:
                problems.append(line)
    if problems:
        print("\n".join(["", "Charging list prices to re-check (then update PUBLIC in index.html and this file):"] + problems))
        sys.exit(1)


if __name__ == "__main__":
    main()
