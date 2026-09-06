# Kadertagung Finanzbereich — Pain Points und Erhebungswerkzeug

Spitäler Schaffhausen, Kadertagung vom 14. September 2026.
Privates Repo. Bitte zuerst [DATENSCHUTZ.md](DATENSCHUTZ.md) lesen.

**Für PeakPrivacy:** Was wir aus den Themen an Anforderungen ableiten und
welche zwölf Fragen wir stellen, steht in
[unterlagen/anforderungen-peakprivacy.md](unterlagen/anforderungen-peakprivacy.md).

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
| `system/` | Teilnahmeseite, alle acht Serverrouten, Dashboard, Werkbank, Betriebsanleitung |
| `konzept/` | Ablauf des Abends, Methodik, Übergabeunterlagen, Papierform als PDF |
| `video/` | Das Lernvideo, die Sprechtexte und die Skripte, die es bauen |
| `werkzeug/` | Skripte für Zugänge, Mailversand und die Verteilfassung |

## Das Laufende ansehen

Alles läuft unter **umfrage.win**. Die Adressen:

| Adresse | Was zu sehen ist |
|---|---|
| [umfrage.win/kadertagung/?demo=1](https://umfrage.win/kadertagung/?demo=1) | **Der beste Einstieg.** Die Teilnahmeseite im Vorführbetrieb — ohne Zugangsdaten, mit Beispieldaten, ohne dass etwas gespeichert wird |
| [umfrage.win/kadertagung/](https://umfrage.win/kadertagung/) | Der echte Zugang. Fragt nach persönlichem Link und PIN, ohne beides kommt man nicht weiter |
| [umfrage.win/kadertagung/lernvideo.mp4](https://umfrage.win/kadertagung/lernvideo.mp4) | Zwei Minuten, zeigt den ganzen Ablauf |
| [umfrage.win/kadertagung/dashboard](https://umfrage.win/kadertagung/dashboard) | Rücklauf und Auswertung. Zeigt ohne Leitungsschlüssel nichts an |
| [umfrage.win/kadertagung/werkbank](https://umfrage.win/kadertagung/werkbank) | Das Arbeitsgerät für den Abend: Bewertung, Priorisierung, Portfolio. Startet leer, die Themen werden aus dem Dashboard hineingeladen |

Der Demo-Betrieb ist der schnellste Weg, ein Gefühl für die Erhebung zu
bekommen: Er durchläuft dieselben Schritte wie die echten Teilnehmenden,
inklusive geführtem Gespräch, nur ohne Datenbank dahinter.

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
