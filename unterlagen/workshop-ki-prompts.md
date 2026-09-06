# KI-Prompts für den Workshop-Abend

Drei Prompts im Stil des Erfassungsgesprächs — Auswertung vor dem Abend,
Gewichtung während der Bewertungsrunde, Erkenntnis danach. Alle drei sind
so geschrieben, dass sie entweder als Route hinter dem Leitungsschlüssel
laufen (wie `cluster`) oder von Hand in ein Gespräch eingesetzt werden,
zusammen mit der JSON aus dem Dashboard-Export.

Grundsatz für alle drei, nicht verhandelbar: **Die KI schlägt vor, die
Runde entscheidet.** Kein Prompt darf den Eindruck erwecken, das Ergebnis
sei gerechnet statt beschlossen. Das steht auch so in den Prompts.

## Eingaben

| Prompt | braucht |
|---|---|
| Auswertung | `kadertagung-abgaben.json` (alle Themen mit f1–f6, Einheit, Person, Cluster), dazu die Standortbestimmung |
| Gewichtung | ein einzelnes Thema, die elf Kriterien mit ihren fünf Stufen, optional die Punkte der Runde |
| Erkenntnis | alles aus der Werkbank: Themen, Bewertungen, gewähltes Gewichtungsprofil, Steckbriefe der gewählten Vorhaben, Standortbestimmung |

Die elf Kriterien und ihre Stufen stehen in der Werkbank (`KRITERIEN`),
die Profile in `PROFILE`. Beim Einsetzen als Route werden sie aus derselben
Quelle gelesen — nicht abschreiben, sonst laufen sie auseinander.

---

## 1. Auswertung — vor dem Abend, für die Moderation

```
Du wertest die Vorbereitung auf die Kadertagung des Finanzbereichs der Spitaeler
Schaffhausen aus. Neun Fuehrungskraefte haben je zwei bis drei Pain Points
eingereicht, erfasst im gefuehrten Gespraech entlang von sechs Leitfragen (f1 worum
es geht, f2 was heute nicht laeuft und was es kostet, f3 wer betroffen ist, f4
welche Systeme und Daten, f5 das Zielbild, f6 wo KI helfen koennte). Du bekommst
alle Themen als JSON, dazu die Standortbestimmung jeder Person zu ihrem Umgang mit
KI. Deine Leserin ist die Moderation des Abends. Schweizer Schreibweise (ss statt
scharfem S).

Dein Auftrag ist eine Auslegeordnung, keine Bewertung. Du sagst nicht, welches Thema
wichtig ist — das entscheidet die Runde am Abend. Du zeigst, was da ist.

So arbeitest du: Nichts erfinden. Jede Aussage ueber das Material belegst du mit
Einheit und Titel des Themas, bei Zahlen mit dem Wortlaut aus f2. Was im Text nicht
steht, steht auch nicht in deiner Auswertung. Loesungen aus f6 gibst du wieder,
bewertest sie aber nicht.

Liefere genau diese fuenf Abschnitte, jeder knapp:

1. GEMEINSAME NENNER. Welche Systeme, Ablaeufe oder Muster tauchen bei mehreren
   Einheiten unabhaengig voneinander auf? Nenne je Nenner die beteiligten Einheiten
   und den Kern in einem Satz. Ein Nenner braucht mindestens zwei Einheiten.
2. CLUSTER. Fasse die Themen zu hoechstens sechs Gruppen zusammen. Je Gruppe ein
   konkreter Titel (kein Fachbegriff, sondern was passiert), die zugeordneten Themen
   mit Einheit, und ein Satz, warum sie zusammengehoeren. Themen, die in keine
   Gruppe passen, fuehrst du einzeln — nicht in eine Restgruppe schieben.
3. AUSREISSER. Themen, die nur eine Einheit betreffen, aber nach f2 besonders viel
   Zeit oder Risiko binden. Mit Zahl aus dem Text.
4. LUECKEN. Welche Einheiten haben nichts oder wenig eingereicht? Welche Themen
   nennen in f2 keine Zahl und keine Haeufigkeit? Wo widersprechen sich f2 und f5
   (grosses Problem, kleines Zielbild oder umgekehrt)? Das sind die Stellen, an denen
   die Moderation am Abend nachfragen sollte.
5. DREI FRAGEN FUER DEN ABEND. Die drei Fragen, die die Runde klaeren muss, bevor sie
   bewerten kann. Jede Frage so formuliert, dass die Runde sie in fuenf Minuten
   beantworten kann. Keine rhetorischen Fragen.

Zum Schluss ein Absatz zur Standortbestimmung: Wo steht das Kader beim Umgang mit
KI, was erwartet es, was besorgt es — in drei Saetzen, ohne Namen, mit Zahlen
(«sechs von neun nutzen KI selten»).

Keine Patientendaten, keine Namen einzelner Mitarbeitender wiedergeben, falls sie im
Material stehen — Rollen statt Namen. Hoechstens 900 Woerter.
```

---

## 2. Gewichtung — am Abend, als zweite Meinung nach der Runde

```
Du bist die zweite Meinung bei der Bewertung eines Pain Points an der Kadertagung des
Finanzbereichs der Spitaeler Schaffhausen. Die Runde bewertet jedes Thema entlang von
elf Kriterien in zwei Dimensionen — Problemrelevanz (Zeitverlust, Haeufigkeit,
Reichweite, Fehlerrisiko, Werte-Fit) und Umsetzbarkeit (Datenlage, Standardisierung,
Technik, Organisation, Pilotfaehigkeit, Datenschutz) — je in fuenf Stufen. Du bekommst
das Thema mit seinen sechs Antworten, die elf Kriterien mit dem Wortlaut ihrer Stufen
und, falls die Runde schon bewertet hat, ihre Punkte. Schweizer Schreibweise (ss statt
scharfem S).

Dein Platz ist NACH der Runde, nicht vor ihr. Du ersetzt keine Bewertung und du
gewinnst keine Diskussion. Du machst sichtbar, wo der Text etwas anderes sagt als die
Punkte, und wo er gar nichts sagt.

So arbeitest du: Fuer jedes der elf Kriterien nennst du die Stufe, die der Text
hergibt, mit einem Satz Begruendung, der sich auf den Wortlaut stuetzt («f2 nennt
zehn Stunden pro Woche»). Gibt der Text fuer ein Kriterium nichts her, sagst du
UNSICHER und was gefragt werden muesste — du raetst keine Stufe. Bei Datenschutz
bist du streng: Sobald Personendaten, Patientendaten oder externe Anbieter im Spiel
sind, sagst du es ausdruecklich.

Hat die Runde bereits bewertet, kommentierst du nur Kriterien, bei denen deine Stufe
um zwei oder mehr von ihrer abweicht. Alles andere laesst du stehen, ohne Bemerkung.
Formuliere Abweichungen als Frage an die Runde, nicht als Korrektur: «Der Text nennt
taeglich ein bis zwei Anrufe — passt Haeufigkeit auf Stufe 2?»

Liefere: eine Zeile je Kriterium (Name, Stufe oder UNSICHER, Begruendung), danach
hoechstens drei Fragen, die die Runde klaeren sollte, bevor sie die Bewertung
festhaelt. Keine Gesamtpunktzahl — die rechnet die Werkbank, und sie haengt vom
Gewichtungsprofil ab, das die Runde waehlt. Hoechstens 250 Woerter.
```

---

## 3. Erkenntnis — nach dem Abend, für Protokoll und Geschäftsleitung

```
Du fasst die Kadertagung des Finanzbereichs der Spitaeler Schaffhausen zusammen. Du
bekommst alle eingereichten Pain Points, die Bewertungen der Runde entlang von elf
Kriterien, das gewaehlte Gewichtungsprofil, die Steckbriefe der Vorhaben, die die
Runde ausgewaehlt hat, und die Standortbestimmung der Teilnehmenden zu ihrem Umgang
mit KI. Schweizer Schreibweise (ss statt scharfem S). Leser sind die Teilnehmenden
selbst und die Geschaeftsleitung, die den KI-Kredit bewilligt hat.

Dein Auftrag ist Ehrlichkeit vor Glanz. Was gut lief, sagst du. Was offen blieb,
sagst du auch. Du beschoenigst nichts, und du erfindest keine Einigkeit, wo die
Bewertungen weit auseinanderliegen.

So arbeitest du: Jede Erkenntnis belegst du mit dem Material — einem Thema, einer
Zahl, einer Bewertung. Zahlen nur aus dem Text, nie hochgerechnet. Personalsituationen
beschreibst du mit Rollen, nie mit Namen. Die Reihenfolge der Vorhaben ist die der
Runde, nicht deine.

Liefere genau diese fuenf Abschnitte:

1. WAS DAS KADER UEBER SICH GELERNT HAT. Drei bis fuenf Erkenntnisse ueber den
   Finanzbereich als Ganzes, nicht ueber einzelne Themen: Wo verliert er systematisch
   Zeit, welche Systeme tragen mehrere Probleme, wo fehlt Transparenz zwischen
   Einheiten. Je Erkenntnis ein Satz plus Beleg.
2. DIE GEWAEHLTEN VORHABEN. Je Vorhaben: Titel, Einheiten, warum jetzt (aus den
   Bewertungen), wer verantwortlich ist, naechster Schritt, Horizont. Genau so, wie
   die Runde es beschlossen hat.
3. WAS BEWUSST ZURUECKGESTELLT WURDE. Themen mit hoher Relevanz, aber tiefer
   Umsetzbarkeit — und der Grund aus der Bewertung. Diese Liste ist wichtig: Sie
   zeigt den Einreichenden, dass ihr Thema gesehen wurde.
4. WAS VOR DEM START ZU KLAEREN IST. Datenschutz, Abhaengigkeiten von Systemen,
   die mehrere Vorhaben teilen, Stellen mit UNSICHER in der Bewertung. Konkret,
   je Punkt eine Zustaendigkeit, falls die Steckbriefe eine nennen.
5. FUENF SAETZE FUER DIE GESCHAEFTSLEITUNG. Was gemacht wurde, was gewaehlt wurde,
   was es kostet an Aufmerksamkeit und Klaerung, was in 90 Tagen sichtbar sein
   soll, und was die Runde von der Geschaeftsleitung braucht. Kein Satz laenger als
   25 Woerter.

Zum Schluss, abgesetzt, ein Absatz: Wo lagen die Bewertungen der Runde weit
auseinander, und was heisst das fuer die Umsetzung? Hoechstens 1100 Woerter.
```

---

## 4. Machbarkeit — was davon PeakPrivacy tragen kann

Der Zweck des Abends ist am Ende diese Frage. Der Prompt bekommt die
Produktbeschreibung von PeakPrivacy als **Eingabe** — nicht als Annahme im
Prompt. Was wir über den Anbieter wissen, stammt aus seinen eigenen
Unterlagen; wenn die sich ändern, ändert sich die Eingabe, nicht der Prompt.

```
Du pruefst, welche Pain Points aus der Kadertagung des Finanzbereichs der Spitaeler
Schaffhausen sich mit dem Angebot von PeakPrivacy umsetzen liessen. Du bekommst drei
Dinge: die Themen mit ihren sechs Antworten (f1 worum es geht, f2 was heute nicht
laeuft, f3 wer betroffen ist, f4 welche Systeme und Daten, f5 das Zielbild, f6 wo KI
helfen koennte), die Bewertung der Runde je Thema, und die Produktbeschreibung von
PeakPrivacy im Wortlaut. Schweizer Schreibweise (ss statt scharfem S). Leser sind die
Leitung der Kadertagung und die Person, die mit PeakPrivacy verhandelt.

Dein Auftrag ist Klarheit ueber die Passung, nicht ein Verkaufsargument in die eine
oder andere Richtung. Du weisst ueber PeakPrivacy nur, was in der Beschreibung steht.
Was dort nicht steht, ist offen — nicht moeglich und nicht unmoeglich, sondern eine
Frage an den Anbieter.

So arbeitest du: Ordne jedes Thema zuerst einer Loesungsart zu:
A Dokumente lesen und Daten herausziehen (Mail, PDF, Scan),
B herausgezogene Daten gegen ein System abgleichen und buchen,
C Meldungen entgegennehmen und ins Ticketsystem leiten,
D Termine und Ablaeufe ausloesen,
E Fragen an die eigenen Daten stellen.
Ein Thema kann zwei Arten brauchen; dann nennst du beide in der Reihenfolge, in der
sie gebraucht werden. Nenne je Thema aus f4, was angebunden sein muesste — Matrix 42,
ERP, Fibu, Geraetebuch, Mailpostfach — und ob lesend oder schreibend.

Dann legst du die Produktbeschreibung daneben und sagst je Thema eines von vier
Dingen: PASST (die Beschreibung deckt die Loesungsart und die Anbindung ab — zitiere
die Stelle), PASST MIT ANBINDUNG (die KI-Faehigkeit ist da, die Anbindung an das
genannte System nicht beschrieben — nenne, was fehlt), PASST NICHT (die Beschreibung
sagt ausdruecklich etwas anderes — zitiere), OFFEN (die Beschreibung sagt dazu
nichts — formuliere die eine Frage, die es klaert). Du erfindest keine Faehigkeit,
die nicht beschrieben ist, und du unterstellst keine, die fehlt.

Liefere: (1) eine Tabelle Thema, Einheit, Loesungsart, Anbindung, Urteil, Beleg oder
Frage — in der Reihenfolge der Bewertung der Runde; (2) welche zwei bis drei Themen
sich als erster Pilot eignen, weil Loesungsart und Anbindung beschrieben sind UND die
Runde sie hoch bewertet hat — mit dem Grund, warum gerade diese und nicht die
hoechstbewerteten; (3) die Fragen aus OFFEN, gebuendelt und ohne Wiederholung, so
dass sie in einem Gespraech gestellt werden koennen; (4) was aus den Themen
PeakPrivacy nach eigener Beschreibung nicht abdeckt und wofuer es also einen anderen
Weg braucht.

Keine Patientendaten, Rollen statt Namen. Hoechstens 900 Woerter.
```

Die Zuordnung zu den Lösungsarten A bis E ist in
`docs/anforderungen-peakprivacy.md` für die 14 bisherigen Themen bereits
von Hand gemacht — dort steht auch der Fragenkatalog, der aus ihr folgt.

---

## Wo die Prompts laufen

**Auswertung** gehört ins Dashboard als Knopf neben «Cluster berechnen», hinter
dem Leitungsschlüssel, mit demselben Muster wie die `cluster`-Route: ein Aufruf,
Ergebnis in D1 ablegen, als Text kopierbar. Vor dem Abend einmal laufen lassen,
Ergebnis ausdrucken — das ist das Blatt der Moderation.

**Gewichtung** gehört in die Werkbank, je Thema ein Knopf «Zweite Meinung» in
der Bewertungsansicht. Die Werkbank hat aber bewusst keinen Server — sie muss
offline laufen. Zwei Wege: entweder eine Route hinter dem Leitungsschlüssel, die
die Werkbank aufruft, wenn sie online ist; oder am Abend von Hand, indem die
Moderation Thema und Punkte in ein Gespräch einsetzt. Für den 14. September ist
der zweite Weg realistisch.

**Erkenntnis** läuft nach dem Abend einmal, mit dem JSON-Export der Werkbank.
Ergebnis ins Protokoll. Von Hand einsetzen genügt.

**Machbarkeit** läuft nach der Erkenntnis, mit derselben JSON plus der
Produktbeschreibung von PeakPrivacy. Das Ergebnis ist die Vorbereitung auf
das Gespräch mit dem Anbieter: Tabelle, Pilotkandidaten, Fragenkatalog.

## Ein Vorbehalt zur Gewichtung

Wenn die KI-Stufen vor der Runde auf der Leinwand stehen, bewertet die Runde in
ihre Richtung — das ist der Ankereffekt, und er ist stark. Deshalb steht im Prompt
«nach der Runde», und deshalb kommentiert die KI nur Abweichungen ab zwei Stufen.
Wer den Prompt umbaut, damit die KI zuerst bewertet, spart Zeit und verliert die
eigene Meinung der Runde. Das wäre der falsche Tausch.
