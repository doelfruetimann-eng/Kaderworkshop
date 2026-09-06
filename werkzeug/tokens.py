#!/usr/bin/env python3
"""Erzeugt die persönlichen Zugänge für die Kadertagung Finanzbereich.

Schreibt drei Dateien (alle gitignored — Tokens und PINs gehören in kein Repo):

  werkzeug/tokens.json       Merkdatei: bestehende Tokens/PINs bleiben bei jedem
                             Lauf erhalten, damit verschickte Links gültig bleiben.
  werkzeug/kader-config.json Der Wert für das Cloudflare-Secret KADER_CONFIG
                             (siehe KADERTAGUNG.md im Website-Repo).
  werkzeug/tokenliste.md     Für die Leitung: pro Person Link + PIN — zum
                             Eintragen in die Ansicht «Teilnehmende» der Werkbank.

Neben den 9 Teilnahme- und 3 Leitungszugängen entstehen vier Testzugänge
(Dölf/Melina/Markus/Fabienne (Test), Rolle «test») für die Finalisierung:
gleiche Seite, eigenes KI-Feedback-Gespräch, zählt nirgends in den Rücklauf.
Unbenutzte Testzugänge erscheinen nirgends — verteil nur, was du brauchst.

Scharfschalten nach dem Testlauf: `--ohne-test` erzeugt das Config OHNE die
Testzugänge → Secret neu setzen, Tabellen leeren (KADERTAGUNG.md), verschicken.

Aufrufe:
  python3 werkzeug/tokens.py
  python3 werkzeug/tokens.py --basis https://umfrage.win/kadertagung/
  python3 werkzeug/tokens.py --frist 2026-09-04 --tagung 2026-09-17 --ki
  python3 werkzeug/tokens.py --ohne-test          # fürs Scharfschalten
  python3 werkzeug/tokens.py --neu "Fabienne Grant"   # rotiert Token + PIN einer Person
"""
import argparse
import json
import secrets
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent

# Einheitsnamen wortgleich zur Konstante EINHEITEN in index.html — sie sind
# der Zuordnungs- und Dedup-Schlüssel beim Import in die Werkbank.
# Mailadressen aus docs/verteiler-und-einladung.md (für den
# Erinnerungs-Knopf im Dashboard).
TEILNAHME = [
    ("Fabienne Grant",        "Rechnungswesen, Ertragsmanagement, Patientenadministration", "vorname.name@spitaeler-sh.ch"),
    ("Sevil Erdogan",         "Controlling / Reporting",                                    "vorname.name@spitaeler-sh.ch"),
    ("Daniela Graf",          "Medizinische Codierung",                                     "vorname.name@spitaeler-sh.ch"),
    ("Yannick Steiner",       "Querschnittsfunktionen und ERP",                             "vorname.name@spitaeler-sh.ch"),
    ("Raphael Kuhn",          "Einkauf / Logistik",                                         "vorname.name@spitaeler-sh.ch"),
    ("Dölf Rütimann",         "Immobilien und Betrieb",                                     "Doelf.Ruetimann@spitaeler-sh.ch"),
    ("Markus Hausmann-Spiess","Informatik",                                                 "vorname.name@spitaeler-sh.ch"),
    ("Brian Sailer",          "Medizintechnik",                                             "vorname.name@spitaeler-sh.ch"),
    ("Jürg Rahm",             "Finanzen & Support",                                         "vorname.name@spitaeler-sh.ch"),
]
LEITUNG = ["Dölf Rütimann", "Markus Hausmann-Spiess", "Melina", "Fabienne Grant"]
TEST = ["Dölf (Test)", "Melina (Test)", "Markus (Test)", "Fabienne (Test)"]

# Ohne Verwechsler (kein 0/O, 1/l/i): Links werden auch mal abgetippt.
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def token(laenge):
    return "".join(secrets.choice(ALPHABET) for _ in range(laenge))


def pin4():
    return "".join(secrets.choice("0123456789") for _ in range(4))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--basis", default="https://umfrage.win/kadertagung/",
                   help="Basis-URL der Teilnahme-Seite")
    p.add_argument("--frist", default="", help="Rückmeldefrist als JJJJ-MM-TT (einschliesslich)")
    p.add_argument("--tagung", default="", help="Datum der Kadertagung als JJJJ-MM-TT (für den Countdown auf der Teilnahme-Seite)")
    p.add_argument("--ki", action="store_true", help="KI-Gespräch nach dem Absenden freischalten")
    p.add_argument("--ohne-test", action="store_true",
                   help="Config ohne Testzugänge erzeugen (Scharfschalten nach dem Testlauf)")
    p.add_argument("--neu", metavar="NAME", help="Token und PIN dieser Person neu erzeugen (alte Links werden ungültig)")
    a = p.parse_args()

    if not a.basis.isascii():
        sys.exit("FEHLER: Die Basis-URL enthält Nicht-ASCII-Zeichen (Umlautdomain?). "
                 "Bitte die ASCII- oder Punycode-Form verwenden — Mailprogramme "
                 "zerlegen Umlaut-Links unzuverlässig.")
    basis = a.basis if a.basis.endswith("/") else a.basis + "/"

    merk_pfad = HIER / "tokens.json"
    merk = {"teilnahme": {}, "leitung": {}, "test": {}, "pins": {}, "frist": "", "tagung": "", "ki": False}
    if merk_pfad.exists():
        merk.update(json.loads(merk_pfad.read_text(encoding="utf-8")))
    merk.setdefault("test", {})
    merk.setdefault("pins", {})

    if a.frist:
        merk["frist"] = a.frist
    if a.tagung:
        merk["tagung"] = a.tagung
    if a.ki:
        merk["ki"] = True

    # Bestehende Tokens/PINs bleiben; nur fehlende (oder per --neu rotierte) kommen dazu.
    if a.neu:
        merk["teilnahme"].pop(a.neu, None)
        merk["leitung"].pop(a.neu, None)
        merk["test"].pop(a.neu, None)
        merk["pins"].pop(a.neu, None)
    for name, _, _ in TEILNAHME:
        merk["teilnahme"].setdefault(name, token(12))
        merk["pins"].setdefault(name, pin4())
    for name in LEITUNG:
        merk["leitung"].setdefault(name, token(24))
    for name in TEST:
        merk["test"].setdefault(name, token(12))
        merk["pins"].setdefault(name, pin4())
    merk_pfad.write_text(json.dumps(merk, ensure_ascii=False, indent=2), encoding="utf-8")

    einheiten = {name: einheit for name, einheit, _ in TEILNAHME}
    mails = {name: mail for name, _, mail in TEILNAHME}
    tokens = {}
    for name, t in merk["teilnahme"].items():
        tokens[t] = {"name": name, "einheit": einheiten.get(name, ""), "rolle": "teilnahme",
                     "pin": merk["pins"][name], "mail": mails.get(name, "")}
    for name, t in merk["leitung"].items():
        tokens[t] = {"name": name, "einheit": "", "rolle": "leitung"}
    if not a.ohne_test:
        for name, t in merk["test"].items():
            tokens[t] = {"name": name, "einheit": "Testlauf", "rolle": "test", "pin": merk["pins"][name]}
    config = {"frist": merk["frist"], "tagung": merk.get("tagung", ""), "ki": merk["ki"], "tokens": tokens}
    (HIER / "kader-config.json").write_text(
        json.dumps(config, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    zeilen = [
        "# Persönliche Zugänge — NICHT ins Repo, NICHT weiterleiten",
        "",
        f"Basis: {basis}  ·  Frist: {merk['frist'] or '(noch offen)'}  ·  Tagung: "
        + (merk.get("tagung") or "(noch offen)") + "  ·  KI-Gespräch: "
        + ("an" if merk["ki"] else "aus")
        + ("  ·  OHNE Testzugänge (scharf)" if a.ohne_test else ""),
        "",
        "Link und PIN gehören in DIESELBE Einladungsmail (PIN unten). Die PIN",
        "steht nie in einer URL — sie schützt, falls nur der Link weitergegeben",
        "wird (Browserverlauf, Logs); gegen Weiterleiten der ganzen Mail nicht.",
        "",
        "## Teilnahme-Links (in der Werkbank unter «Teilnehmende» eintragen)",
        "",
        "| Person | Einheit | Persönlicher Link | PIN |",
        "|---|---|---|---|",
    ]
    for name, _, _ in TEILNAHME:
        url = f"{basis}?t={merk['teilnahme'][name]}"
        assert url.isascii()
        zeilen.append(f"| {name} | {einheiten[name]} | {url} | `{merk['pins'][name]}` |")
    zeilen += [
        "",
        "## Testzugänge für die Finalisierung (nach Bedarf verteilen)",
        "",
        "Gleiche Seite, eigenes KI-Feedback-Gespräch am Schluss; zählt nirgends",
        "in den Rücklauf. Nach dem Testlauf: `tokens.py --ohne-test`, Secret neu",
        "setzen, Tabellen leeren — dann sind diese Links tot.",
        "",
        "| Person | Link | PIN |",
        "|---|---|---|",
    ]
    for name in TEST:
        url = f"{basis}?t={merk['test'][name]}"
        assert url.isascii()
        zeilen.append(f"| {name} | {url} | `{merk['pins'][name]}` |")
    zeilen += [
        "",
        "## Zugangsschlüssel Leitung (fürs Dashboard — persönlich übergeben, nie mailen)",
        "",
        "| Person | Schlüssel |",
        "|---|---|",
    ]
    for name in LEITUNG:
        zeilen.append(f"| {name} | `{merk['leitung'][name]}` |")
    zeilen += [
        "",
        "Danach: Inhalt von `kader-config.json` als Cloudflare-Secret `KADER_CONFIG`",
        "setzen (Anleitung: KADERTAGUNG.md im Website-Repo) und einmal neu deployen.",
        "",
    ]
    (HIER / "tokenliste.md").write_text("\n".join(zeilen), encoding="utf-8")

    print(f"ok — {len(tokens)} Zugänge ({len(merk['teilnahme'])} Teilnahme, {len(merk['leitung'])} Leitung"
          + (f", {len(merk['test'])} Test" if not a.ohne_test else ", Testzugänge WEGGELASSEN") + ")")
    print(f"Secret:     {HIER / 'kader-config.json'}")
    print(f"Linkliste:  {HIER / 'tokenliste.md'}")


if __name__ == "__main__":
    main()
