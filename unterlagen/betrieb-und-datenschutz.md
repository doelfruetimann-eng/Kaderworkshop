# Betrieb und Datenschutz

## Wo die Daten liegen

Es gibt zwei Welten, und sie funktionieren bewusst unterschiedlich.

**Die Teilnahme-Seite** (`umfrage.win/kadertagung/`) führt durch
Standortbestimmung, Pain-Point-Erfassung und Menüwahl. Bis zum Absenden
bleiben die Eingaben im Browser auf dem eigenen Gerät; beim Absenden werden
sie verschlüsselt (HTTPS) an die Website übertragen und dort in einer
Datenbank gespeichert (Cloudflare D1, Standort-Hint Region Westeuropa).
Ehrlich benannt heisst das: Cloudflare ist ein US-Anbieter, die Daten liegen
in einer EU-Region — **kein Schweizer Server**. Vertretbar ist das, weil die
Inhalte Prozessbeschreibungen ohne besonders schützenswerte Personendaten
sind (Rollen statt Namen), weil der Zugriff über Zugangsschlüssel auf drei
Personen beschränkt ist — Dölf Rütimann, Markus Hausmann-Spiess und Melina
(Chief AI Officer) — und weil die Daten nach der Tagung gelöscht werden
(siehe Löschkonzept unten).

**Die Werkbank** (`index.html`) ist weiterhin eine einzelne HTML-Datei ohne
Server und ohne eigene Datenbank: Alle Eingaben liegen im `localStorage` des
jeweiligen Browsers. Es gibt dort keine Übermittlung, keinen Login, keine
Konten, keinen Netzwerkverkehr im Betrieb.

Konkret heisst das:

| Was | Wo es liegt | Wer es sieht |
|---|---|---|
| Abgaben der Teilnehmenden (Standortbestimmung, Pain Points, Menüwahl) | D1-Datenbank (Cloudflare, Region Westeuropa) | Dölf, Markus, Melina |
| KI-Gespräch über die eigenen Pain Points (freiwillig, nach dem Absenden) | Anthropic-API | nur die Person selbst und der Anbieter gemäss dessen Bedingungen |
| Eingaben in der Werkbank (Bewertungen, Notizen der Leitung) | Browser der Workshop-Leitung | nur die Leitung |
| Teilnehmendenliste, Mailadressen, Frist | Browser der Workshop-Leitung | nur die Leitung |
| Dashboard-Export als JSON | wo die Leitung ihn speichert | wer ihn erhält |
| Protokoll als Markdown | wie oben | wie oben |

Der Austausch läuft neu über die Datenbank: Jede Person sendet über ihren
persönlichen Link ab, das Dashboard zeigt der Leitung den Rücklauf —
Nachbessern geht mit demselben Link bis zur Frist, es zählt der letzte Stand.
Die Brücke in die Werkbank für den Abend ist der **Dashboard-Export als
JSON-Datei**: Die Leitung lädt ihn herunter und liest ihn in die Werkbank ein.

**Für die Werkbank gilt weiterhin:** Wer den Browser wechselt, das Gerät
wechselt oder die Browserdaten löscht, verliert die dortigen Eingaben. Vor
dem Gerätewechsel exportieren. Der private Modus des Browsers löscht beim
Schliessen alles.

## Datenschutzrechtliche Einordnung

**Unkritisch, solange nur Prozesse beschrieben werden.** Pain Points betreffen
Abläufe, Systeme und Rollen — keine Patientendaten und keine Personendossiers.
Das ist der Normalfall und braucht keine besondere Bewilligung.

**Zu beachten sind drei Punkte:**

1. **Personendaten der Teilnehmenden.** Namen, Funktionen und dienstliche
   Mailadressen der neun Führungspersonen sind im Werkzeug hinterlegt, damit
   Einladung und Rücklauf funktionieren. Das sind dienstliche Kontaktdaten aus
   dem internen Verzeichnis, verarbeitet für einen internen Anlass — normal.
   Trotzdem: Die publizierte Seite ist privat und darf nicht öffentlich
   geteilt werden.

2. **Freitextfelder.** Niemand hindert jemanden daran, in ein Beschreibungsfeld
   einen Patientennamen zu schreiben. Deshalb steht in der Anleitung und im
   Werkzeug: **Rollen statt Namen.** Diesen Punkt bitte in der Einladung und
   am Abend ausdrücklich erwähnen.

3. **Spracherkennung.** Das Diktat läuft über den Sprachdienst des Browsers;
   Chrome und Edge übermitteln die Aufnahme dazu an den Hersteller. Das ist
   für ein Spital heikel — deshalb steht überall, wo das Diktat läuft, ein
   ausdrücklicher Hinweis: keine Patientendaten, keine Personendaten, Rollen
   statt Namen. Auf der Teilnahme-Seite funktioniert das Diktat dank HTTPS
   zuverlässig. Wer ganz sichergehen will, lässt es weg; alles funktioniert
   vollständig ohne. Das **Vorlesen** ist unproblematisch: Es erzeugt nur
   Ton und sendet nichts.

**Empfehlung:** Kurz mit Markus Hausmann-Spiess (ICT) abstimmen, bevor die
Einladung rausgeht. Nicht weil etwas kritisch wäre, sondern weil er es
ohnehin wissen sollte — und weil Ziffer 1 des Abends «Leitplanken klären»
heisst. Das Werkzeug ist dafür ein gutes erstes Beispiel.

## Wie die Teilnehmenden auf die Seite kommen

Jede Person erhält per Mail einen persönlichen Link
(`https://umfrage.win/kadertagung/?t=TOKEN`). Kein Login, kein
Konto: Der Link selbst ist der Zugang, Name und Einheit sind hinterlegt.
Unterbrechen und mit demselben Link weitermachen geht jederzeit — bis zur
Frist zählt der letzte Stand.

Technisch braucht das **keinen zusätzlichen Anbieter**: Die Seite läuft auf
der bestehenden Website-Infrastruktur von Dölf (Cloudflare Workers + D1).
Einmalig einzurichten sind ein Konfigurations-Secret und die Datenbank.

**Die Werkbank** ist davon nicht berührt. Sie bleibt bei der Leitung; soll
sie intern weitergegeben werden, gilt weiterhin: `werkbank-verteilfassung.html`
verwenden (ohne Kontaktdaten), als Datei oder über eine interne Ablage — da
die Werkbank komplett im Browser läuft, genügt dafür eine gewöhnliche
Dateiablage.

## Was noch einzurichten ist

- D1-Datenbank anlegen (einmalig, siehe SETUP im Website-Repo)
- Konfigurations-Secret mit den Zugangs-Tokens setzen
- Persönliche Links erzeugen (`werkzeug/tokens.py`) und in die Einladungen übernehmen
- Rückmeldefrist festlegen und eintragen
- Nach der Tagung löschen (siehe Löschkonzept)

## Löschkonzept

Nach der Tagung werden die Datenbanktabellen geleert und die Tokens ungültig
gemacht — die persönlichen Links laufen dann ins Leere. Ebenfalls löschen:
den Dashboard-Export und das Protokoll aus der Ablage der Leitung (Ordner
leeren). Den Termin dafür im README notieren, damit er nicht vergessen geht.
