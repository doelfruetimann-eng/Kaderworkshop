# Kadertagung Finanzbereich — Pain Points und Erhebungswerkzeug

Spitäler Schaffhausen, Kadertagung vom 14. September 2026.
Privates Repo. Bitte zuerst [DATENSCHUTZ.md](DATENSCHUTZ.md) lesen.

## Worum es geht

Das Spital hat einen Kredit für die Einführung von KI bewilligt. Statt
über Technik zu reden, sammeln wir vorher die echten Probleme: Neun
Leitungspersonen aus dem Finanz- und Supportbereich nennen je zwei bis drei
Stellen aus ihrem Alltag, an denen die Arbeit regelmässig hakt — etwas, das
Zeit frisst, immer wiederkommt, oft schiefgeht oder das niemand gerne macht.
Eine Lösungsidee wird ausdrücklich nicht verlangt.

Am Abend der Tagung werden diese Themen nebeneinandergelegt, geclustert,
bewertet und priorisiert.

## Stand

- **6 von 9 Personen** haben abgegeben
- **17 Themen** aus **6 von 9 Organisationseinheiten**
- Frist: 7. September 2026 · Tagung: 14. September 2026

## Was hier liegt

| Ordner | Inhalt |
|---|---|
| `daten/` | Die Themen im Volltext, die Standortbestimmung, die Rohdaten als JSON |
| `system/` | Die Teilnahmeseite, die Serverrouten und das Dashboard |
| `werkzeug/` | Skripte für Zugänge, Mailversand und die Verteilfassung |

## Wie erhoben wird

Die Teilnehmenden öffnen einen persönlichen Link, geben eine vierstellige
PIN ein und werden durch fünf Schritte geführt. Die Themen erzählen sie
einem KI-Gespräch, das entlang von sechs Leitfragen nachfragt und am Schluss
den Text glättet. Diktieren ist möglich; auf dem Handy funktioniert es
besser als am Rechner.

Technisch: eine statische Seite auf Cloudflare Workers, Daten in einer
D1-Datenbank in Westeuropa, KI-Aufrufe an Claude Opus 5 bei Anthropic.

## Warum dieses Repo besteht

Damit ein Anbieter sehen kann, worum es tatsächlich geht: welche Art von
Aufgaben im Haus anfallen, in welcher Sprache und Tiefe sie beschrieben
sind, und wie das Material aussieht, das eine Lösung später verarbeiten
müsste.
