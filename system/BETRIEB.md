# Kadertagung Finanzbereich — umfrage.win/kadertagung/

Die Vorbereitung der Kadertagung Finanzbereich (Spitäler Schaffhausen) läuft
auf einer eigenen, dedizierten Domain **`umfrage.win`** — direkt bei
Cloudflare gekauft, komplett unabhängig von der übrigen Website (die läuft
separat bei Vercel unter `dölfrütimann.ch` und ist davon nicht betroffen).
Die neun Einheitsleitungen bekommen je einen
persönlichen Link plus eine 4-stellige PIN (beides in derselben
Einladungsmail — die PIN steht nie in einer URL und schützt so vor
weitergegebenen Links, Browserverlauf und Logs), beantworten eine kurze
KI-Standortbestimmung, erfassen zwei bis drei Pain Points und schicken ab.
Die Beiträge landen in einer D1-Datenbank; ein Dashboard zeigt der Leitung
den Rücklauf, das Stimmungsbild und den Erinnerungs-Knopf für alle Offenen.

Die Unterlagen selbst (Werkbank für den Abend, Papierform, Doku) liegen im
Repo `doelfruetimann-eng/CAS-KI` — hier lebt nur der Web-Teil.

## Die Teile

| Pfad | Wofür |
|---|---|
| `web/public/kadertagung/index.html` | Geführte Teilnahme-Seite (`?t=TOKEN`) |
| `web/public/kadertagung/dashboard.html` | Dashboard für die Leitung (Zugangsschlüssel) |
| `web/src/app/api/kadertagung/wer` | Token → Name/Einheit (+ eigene Abgabe per POST) |
| `web/src/app/api/kadertagung/abgabe` | Abgabe speichern (letzter Stand zählt, Verlauf bleibt) |
| `web/src/app/api/kadertagung/stand` | Rücklauf + alle Abgaben, nur mit Leitungs-Schlüssel |
| `web/src/app/api/kadertagung/ki` | Freiwilliges KI-Gespräch (Claude, Schlüssel bleibt serverseitig) |
| `web/src/app/api/kadertagung/interview` | «Im Gespräch erfassen» + «Mit KI schärfen» (Opus 5; Frage-, Auszug- und Feinschliff-Modus, 80 Züge/Tag gemeinsam mit dem KI-Gespräch) |
| `web/src/app/api/kadertagung/feedback` | Kurz-Feedback zur Vorbereitung (Stufe + Text) |
| `web/src/lib/kadertagung.ts` | Gemeinsame Helfer (Config, D1, Validierung) |

## Einmalige Einrichtung

`umfrage.win` wurde direkt bei Cloudflare gekauft — sie läuft darum von
Anfang an auf Cloudflare-Nameservern, kein Delegations-Umweg nötig. Einzige
Reihenfolge-Regel: Die Custom Domain (Schritt 4) lässt sich erst eintragen,
**nachdem** der Worker durch den ersten Deploy (Schritt 3) überhaupt
existiert.

1. **Datenbank anlegen** (einmalig, im Ordner `web/`):

   ```
   npx wrangler d1 create kadertagung --location weur
   ```

   Die zurückgegebene `database_id` in `web/wrangler.jsonc` beim Binding
   `KADER_DB` eintragen. **Mit dem Platzhalter schlägt der Deploy fehl** —
   erst eintragen, dann mergen.

2. **Zugänge erzeugen** — im CAS-KI-Repo:

   ```
   python3 werkzeug/tokens.py --basis https://umfrage.win/kadertagung/ --frist JJJJ-MM-TT --tagung JJJJ-MM-TT
   ```

   `--tagung` ist das Datum der Kadertagung selbst — damit zeigt die
   Teilnahme-Seite einen Countdown («Noch X Tage bis zur Kadertagung»).
   Ohne Angabe bleibt der Countdown einfach weg.

   Das Skript ist idempotent (bestehende Links und PINs bleiben gültig) und
   schreibt `werkzeug/kader-config.json` (Secret-Wert) und
   `werkzeug/tokenliste.md` (Links + PINs pro Person, dazu vier Testzugänge
   für die Finalisierung). Beide sind gitignored.

3. **Deployen**: Merge auf `main` deployt automatisch — dabei entsteht der
   Worker `doelfruetimann` im Cloudflare-Konto überhaupt erst.

4. **Secret setzen**: Jetzt existiert der Worker. Im Cloudflare-Dashboard
   bei `doelfruetimann` unter Einstellungen → Variablen und Geheimnisse ein
   Secret **`KADER_CONFIG`** anlegen und den Inhalt von `kader-config.json`
   einfügen. (Das bestehende `ANTHROPIC_API_KEY` versorgt auch das
   KI-Gespräch — freischalten über `--ki` beim Token-Skript und Secret neu
   setzen.)

   > **Immer den Typ «Geheimnis» wählen — nie «Text» und nie «JSON».**
   > Klartext-Variablen werden bei jedem Deploy aus der Repo-Konfiguration
   > überschrieben, und weil `web/wrangler.jsonc` bewusst keinen
   > `vars`-Block hat, heisst das: sie sind nach dem nächsten Deploy weg.
   > Verschlüsselte Geheimnisse überleben Deploys. Am 18.08.2026 sind so
   > `KADER_CONFIG` und `SITE_PASSWORD` verschwunden, während der als
   > Geheimnis gesetzte `ANTHROPIC_API_KEY` blieb — daran war es zu sehen.
   > Nach jedem Eintrag **«Bereitstellen»** klicken, sonst wird nichts
   > gespeichert.
   >
   > Gegenprobe von aussen, ohne Anmeldung:
   > `curl -s https://umfrage.win/api/kadertagung/status`
   > meldet für jeden Baustein Ja/Nein (nie Werte). Alles auf `true` und
   > `rollen` mit 9 Teilnahme, 3 Leitung, 4 Test — dann steht es.

### Konfiguration in der Datenbank

Frist, Tagungsdatum, KI-Schalter und die Token-Tabelle stehen in der Tabelle
`konfig` der D1-Datenbank (Schlüssel `kader_config`), nicht mehr im
Worker-Secret. Der Grund: Klartext-Variablen im Dashboard überleben keinen
Deploy, und das Feld nahm zuletzt gar keine Werte mehr an. Die Datenbank ist
deploy-fest und über die D1-Konsole direkt zu setzen.

Ändern: `werkzeug/tokens.py` laufen lassen, dann aus
`werkzeug/kader-config.json` einen INSERT bauen und in der D1-Konsole
ausführen (Cloudflare → Speicher und Datenbanken → D1 → `kadertagung` →
Konsole):

    CREATE TABLE IF NOT EXISTS konfig (schluessel TEXT PRIMARY KEY, wert TEXT NOT NULL);
    INSERT INTO konfig (schluessel, wert) VALUES ('kader_config', '…')
      ON CONFLICT(schluessel) DO UPDATE SET wert = excluded.wert;

> **Das JSON muss reines ASCII sein** — in Python `json.dumps(…,
> ensure_ascii=True)`. Aus `ö` wird dann `\u00f6`, und die Seite macht beim
> Lesen wieder ein ö daraus. Mit echten Umlauten im Befehl geht das Kopieren
> durch Terminal, Editor und Browser schief: Am 18.08.2026 stand danach
> «D├Âlf» statt «Dölf» in der Datenbank und auf der Seite. Die Datei selbst
> und der Content-Type waren dabei in Ordnung — der Fehler steckte allein
> im eingefügten Wert.

### Eine Adresse für die Kadertagung

Alles zur Tagung läuft unter **`umfrage.win`**:

- **umfrage.win/kadertagung/** — die Teilnahme-Seite. Zugang über den
  persönlichen Token in der URL plus die 4-stellige PIN.
- **umfrage.win/kadertagung/dashboard** — der Rücklauf für Dölf, Markus und
  Melina. Zugang über den 24-Zeichen-Leitungsschlüssel, der per POST geprüft
  wird. Die Seite selbst lädt ohne Schlüssel, zeigt dann aber keine Daten.

Von der übrigen Website gibt diese Domain nichts her: Reiseplaner,
Startseite, `/login` und alle fremden API-Routen werden auf die
Teilnahme-Seite umgeleitet (`web/src/middleware.ts`). Umgekehrt greift auf
allen anderen Domains das Seiten-Passwort — und fehlt `SITE_PASSWORD`, wird
zugesperrt (503), nie aufgemacht.

Statische Dateien liefert Cloudflare normalerweise aus, bevor der Worker
läuft — sie gingen damit am Passwort-Gate vorbei. Betroffene Pfade stehen
darum in `web/wrangler.jsonc` unter `assets.run_worker_first`
(derzeit `/schweden2026/*`).

5. **Custom Domain verbinden**: Im Worker `doelfruetimann` → Einstellungen
   → Domänen und Routen → **Benutzerdefinierte Domain hinzufügen** →
   `umfrage.win` eintragen. Cloudflare stellt automatisch das Zertifikat
   aus (kann ein paar Minuten dauern).

6. **Fünf-Minuten-Check**: eigenen Test-Link öffnen (PIN aus der
   tokenliste), Probe-Abgabe schicken, KI-Feedback-Gespräch anspielen, im
   Dashboard prüfen.

## Vom Testlauf zum Ernstbetrieb

Die vier Testzugänge (Rolle «test») existieren nur im Secret und in der
Datenbank — im Code muss nichts zurückgebaut werden. Wenn alle
Rückmeldungen da sind:

1. `python3 werkzeug/tokens.py --ohne-test` — erzeugt das Config ohne
   Testzugänge (Teilnahme-Links und PINs bleiben unverändert gültig).
2. Secret `KADER_CONFIG` mit dem neuen Inhalt überschreiben — die
   Test-Links sind sofort tot, die Testlauf-Sektion im Dashboard
   verschwindet.
3. Tabellen einmal leeren (Befehl unten), damit keine Testdaten im
   Rücklauf liegen.
4. Einladungen verschicken.

## Datenschutz, kurz

Beiträge gehen beim Absenden per HTTPS an diese Website und liegen in
Cloudflare D1 (Region Westeuropa). Zugriff haben nur die drei
Leitungs-Schlüssel. Gespeichert werden die Angaben selbst plus Name und
Einheit — keine IP-Adressen, keine User-Agents. Nach der Tagung: Tabellen
leeren (`npx wrangler d1 execute kadertagung --remote --command "DELETE FROM abgaben; DELETE FROM verlauf; DELETE FROM kichat; DELETE FROM feedback; DELETE FROM pinversuche; DELETE FROM cluster"` —
oder dieselben DELETE-Befehle in der D1-Konsole im Cloudflare-Dashboard)
und das Secret `KADER_CONFIG` entfernen oder leeren.

<!-- Deploy-Marke: 17.08.2026, neue Version fuer Secrets KADER_CONFIG,
     SITE_PASSWORD und ANTHROPIC_API_KEY. -->
