# Was wir von PeakPrivacy wissen müssen — abgeleitet aus den Themen

Stand 6. September 2026, 14 Themen von fünf Einheiten. Wird nach der Frist
und nach dem Workshop nachgeführt.

Ziel der Kadertagung ist nicht die Bewertung an sich, sondern die Antwort
auf eine Frage: **Was davon lässt sich mit PeakPrivacy umsetzen?** Dafür
muss man die Themen nicht nach Wichtigkeit sortieren, sondern nach der
Art der Lösung, die sie brauchen. Das macht dieses Dokument.

## Was in den Themen tatsächlich steckt

Die 14 Themen zerfallen in fünf Lösungsarten. Sie stellen an einen
Anbieter sehr unterschiedliche Anforderungen.

### A. Dokumente lesen und Daten herausziehen

Ein Dokument kommt an — per Mail, als PDF, als Scan — und jemand tippt
den Inhalt in ein System ab.

| Thema | Einheit | Was gelesen werden muss |
|---|---|---|
| 20–30 Auftragsbestätigungen pro Tag | Einkauf | Mail mit Anhang: Preis, Menge, Artikel |
| Lieferscheine an Bestellung anbinden | Einkauf | Gescannter Lieferschein: Positionen, Mengen |
| Serviceberichte ins Gerätebuch | Medizintechnik | PDF oder Scan: Gerät, Datum, Arbeiten |
| Tarifverträge im ERP nachführen | ERP | Vertrag: Taxpunktwerte, Pauschalen, Differenz zum Vorjahr |

**Vier Themen, drei Einheiten, alle mit Zahlen.** Das ist der grösste
gemeinsame Nenner und die klarste Anforderung: *strukturierte Daten aus
unstrukturierten Dokumenten holen.* Wer das kann, deckt fast ein Drittel
der Themen ab.

### B. Herausgezogene Daten gegen ein System abgleichen

Der zweite Schritt nach A: Stimmt die Bestätigung mit der Bestellung
überein? Weicht der Tarif vom Vorjahr ab? Dafür muss die Lösung **lesend
ins ERP** und die Abweichung markieren — und im Idealfall bei Übereinstimmung
innerhalb einer Toleranz **selbst buchen** (Raphael nennt das ausdrücklich).

Betrifft dieselben vier Themen wie A, plus die Kanban-Kontrolle (Einkauf:
Verbrauchsdaten aus zwei Systemen zusammenführen).

### C. Meldungen entgegennehmen und ins Ticketsystem leiten

Jemand meldet einen Mangel, eine Störung, ein Anliegen. Heute versandet es
oder landet im falschen Kanal.

| Thema | Einheit | Ziel |
|---|---|---|
| Meldetool für Störungen an Geräten | Medizintechnik | Chatbot nimmt Meldung auf, fragt nach, leitet weiter |
| Mängelmeldung und -verfolgung | Immobilien und Betrieb | Foto plus Kurznachricht vom Handy, direkt in die Dispo |
| Zu viele IT-Schnittstellen | Medizintechnik | Eine Anfrage, automatisch an fünf Bereiche verteilt |
| Auftragserfassung in Matrix 42 | Immobilien und Betrieb | Tickets finden, Stand auf Anfrage beantworten |

**Vier Themen, zwei Einheiten. Alle hängen an Matrix 42.** Ohne Anbindung
an Matrix 42 ist keines davon lösbar — egal, wie gut die KI ist.

### D. Termine und Abläufe auslösen

| Thema | Einheit |
|---|---|
| Wartungstermine aus dem Gerätebuch, Vorschläge an alle Beteiligten | Medizintechnik |
| Kontaktdaten neuer Lernender in sechs Reports | ERP |

Das ist weniger KI als Prozessautomatisierung. Auslöser aus einem System,
Aktion in einem anderen. Fällt es aus dem Angebot, ist das kein Verlust —
aber man sollte es wissen.

### E. Fragen an die eigenen Daten stellen

| Thema | Einheit |
|---|---|
| Lifecycle und Investitionen Medizintechnik: Auffälligkeiten im Dialog | Medizintechnik |
| Investitionsprozess: Anträge, Budgets, Prognosen zusammenführen | Controlling |

Das ist am nächsten an dem, was PeakPrivacy unter «Projektwissen» zeigt —
Fragen stellen, Antwort mit Quelle. Aber beide Themen brauchen zuerst
**strukturierte Daten aus mehreren Systemen** (Gerätebuch, Fibu,
Anlagenspiegel, Excel, Access). Sevil schreibt selbst: «Auf dem Markt gibt
es ein solches System noch nicht.» Ihr Thema ist zuerst ein
Integrationsthema.

## Welche Systeme im Spiel sind

Aus f4 aller Themen, gezählt:

| Quelle | Themen | Einheiten |
|---|---|---|
| E-Mail als Eingangskanal | 6 | Einkauf, Betrieb, Medizintechnik, ERP |
| Excel | 5 | Controlling, Einkauf, Betrieb, Medizintechnik, ERP |
| PDF und Scans | 4 | Einkauf, Medizintechnik, ERP |
| Gerätebuch | 4 | Medizintechnik |
| Matrix 42 | 3 | Controlling, Betrieb (und indirekt Medizintechnik) |
| Externe: Lieferanten, Dienstleister | 3 | Einkauf, Medizintechnik |
| ERP, Fibu, Anlagenspiegel, Access | je 1 | Controlling, ERP |

**E-Mail ist der häufigste Eingang.** Wer Mails nicht lesen und Anhänge
nicht verarbeiten kann, deckt das häufigste Muster nicht ab.

## Was das Kader selbst verlangt

Aus f6 fällt eine Bedingung auf, die nicht von uns kommt, sondern von den
Einreichenden: Dölf schreibt «intern entwickeln und lokal betreiben, damit
die Daten das Haus nicht verlassen». Das ist genau das, womit PeakPrivacy
wirbt («dedizierte Schweizer Umgebung oder lokale KI-Station im eigenen
Netz»). Diese Bedingung gehört an den Anfang des Gesprächs, nicht ans Ende.

## Die Fragen an PeakPrivacy

Geordnet nach dem, was die Themen brauchen — nicht nach dem, was die
Website verspricht.

**Zu A, Dokumente lesen**

1. Könnt ihr aus einer eingehenden Mail mit PDF-Anhang strukturierte Felder
   ziehen — Artikelnummer, Menge, Preis, Datum — und als Datensatz
   ausgeben? Zeigt es an einer echten Auftragsbestätigung.
2. Wie geht ihr mit gescannten Papieren um, schief eingelesen, mit
   Stempeln, teils handschriftlich ergänzt? Lieferscheine sind selten sauber.
3. Wie hoch ist die Trefferquote bei solchen Feldern, und was passiert bei
   Unsicherheit — Rückfrage an einen Menschen, oder stille Annahme?

**Zu B, Abgleich mit dem ERP**

4. Welche ERP-Systeme habt ihr angebunden — lesend und schreibend? Unser
   Spital braucht beides: lesen für den Abgleich, schreiben für die Buchung
   bei Übereinstimmung.
5. Kann eine Regel «bei Abweichung unter x Prozent selbst buchen, sonst
   vorlegen» bei euch abgebildet werden, mit Protokoll, wer was freigegeben
   hat?

**Zu C, Matrix 42**

6. Habt ihr Matrix 42 je angebunden? Vier unserer Themen hängen daran.
   Wenn nein: Wie bindet ihr ein Ticketsystem an, das ihr nicht kennt, und
   wer trägt das Risiko, dass es nicht klappt?
7. Kann ein Chatbot bei euch eine Meldung aufnehmen, fehlende Angaben
   nachfragen, ein Foto entgegennehmen und daraus ein Ticket im richtigen
   Kanal erzeugen?

**Zum Betrieb**

8. «Lokale KI-Station im eigenen Netz»: Was ist das konkret — Hardware, wer
   wartet sie, was passiert bei einem Ausfall, wie kommen Modell-Updates
   hinein, ohne dass Daten hinausgehen?
9. Rollen und Rechte: Kann eine Person aus dem Einkauf nur Einkaufsdaten
   sehen, jemand aus dem Controlling alles? Wie wird das gepflegt — bei uns
   oder bei euch?
10. Auditierbarkeit: Zeigt uns ein Protokoll. Wer hat wann was gefragt,
    welche Quelle wurde genutzt, wer hat freigegeben.

**Zum Vorgehen**

11. Wenn wir mit einem einzigen Thema anfangen — den Auftragsbestätigungen
    im Einkauf, 20 bis 30 pro Tag, klarer Nutzen, sauberer Umfang — wie
    sieht ein 90-Tage-Pilot aus, was kostet er, und was müsst ihr von uns
    haben?
12. Was aus unseren 14 Themen könnt ihr **nicht**? Die ehrliche Antwort
    hier sagt mehr als jede Referenz.

## Was am Abend zu entscheiden ist

Die Bewertung in der Werkbank liefert die Rangliste nach Relevanz und
Umsetzbarkeit. Für das Gespräch mit PeakPrivacy braucht es dazu eine
einzige zusätzliche Frage je Thema oben in der Rangliste:

> **Welche Lösungsart ist das — A bis E — und was muss dafür angebunden
> sein?**

Damit ist am Ende des Abends klar, welche zwei, drei Themen ihr PeakPrivacy
vorlegt, und ihr könnt Frage 11 mit konkreten Namen stellen.
