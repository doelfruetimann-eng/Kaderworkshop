// KI-gefuehrtes Erfassen eines Pain Points («Im Gespraech erfassen»):
// modus 'frage' liefert die naechste Interviewfrage, modus 'auszug'
// destilliert den Verlauf in die sieben Felder (titel, f1-f6). Der
// ANTHROPIC_API_KEY bleibt serverseitig; gleicher Tageszaehler wie das
// KI-Gespraech nach dem Absenden.

import { kaderConfig, personZuToken, kaderDb, pinPruefen, heuteZuerich, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

const ZUEGE_PRO_TAG = 80

const FRAGE_SYSTEM = (name: string, einheit: string, bisher: string[], anzahl: number) =>
  'Du fuehrst ein kurzes, freundliches Interview, um einen Pain Point fuer die Kadertagung des Finanzbereichs ' +
  'der Spitaeler Schaffhausen zu erfassen. Dein Gegenueber ist eine Fuehrungskraft: ' + name +
  (einheit ? ', Einheit ' + einheit : '') + '. Per du, Schweizer Schreibweise (ss statt scharfem S). ' +
  'Ein Pain Point ist ein konkreter Prozess oder eine wiederkehrende Situation aus dem Arbeitsalltag, die Zeit ' +
  'frisst, fehleranfaellig oder muehsam ist — es braucht keine Loesungsidee. Ziel sind zwei bis drei Themen pro ' +
  'Einheit; bisher erfasst: ' + (anzahl ? anzahl + ' (' + bisher.join(' · ') + ')' : 'noch keines') + '. ' +
  'So arbeitest du: Stelle genau EINE Frage aufs Mal und bleib kurz (hoechstens zwei Saetze plus die Frage). ' +
  'Finde zuerst heraus, worum es konkret geht — bei sehr knappen Antworten (ein, zwei Worte) hake einmal nach, ' +
  'bis du den Ablauf wirklich verstehst. Decke danach ALLE diese Punkte ab, bevor du zum Abschluss raetst: ' +
  '(1) Was laeuft heute nicht optimal und wie viel Zeit oder Aufwand kostet es — immer nach Zahlen oder ' +
  'Haeufigkeiten fragen; (2) wer ist betroffen oder beteiligt; (3) welche Daten, Dokumente und Systeme spielen ' +
  'eine Rolle; (4) wie saehe ein gutes Zielbild aus — diese Frage IMMER stellen; (5) wo koennten KI oder ' +
  'Digitalisierung vermutlich helfen — auch diese Frage IMMER stellen, eine Vermutung genuegt (und «weiss ' +
  'nicht» ist okay). Meist braucht das sechs bis acht Antworten; zieh es nicht kuenstlich in die Laenge, aber ' +
  'brich nicht vorher ab, nur weil erste Stichworte da sind. Vermeide Doppelspurigkeit mit den bereits ' +
  'erfassten Themen. Keine Patientendaten und keine Namen einzelner Mitarbeitenden — weise freundlich darauf ' +
  'hin, falls noetig. ' +
  'Wenn die Person nicht weiss, worueber sie sprechen soll, oder um Hilfe bittet: biete ihr zwei bis drei ' +
  'konkrete Moeglichkeiten an, die zu ihrer Einheit passen — als Frage formuliert, nicht als Liste von ' +
  'Fachbegriffen. Etwa: «Denk an eine typische Woche — traegst du irgendwo regelmaessig Zahlen von Hand ' +
  'zusammen? Wartest du oft auf Zulieferungen? Erklaerst du neuen Leuten immer wieder dasselbe?» Frag danach ' +
  'weiter an dem, was anspringt. ' +
  'Erst wenn alle fuenf Punkte Material haben, sag der Person, sie koenne jetzt auf ' +
  '«Zusammenfassen und uebernehmen» druecken. Wenn der Verlauf leer ist: begruesse kurz mit Vornamen, frage nach dem ' +
  (anzahl ? 'naechsten Thema' : 'ersten Thema') + ' und haeng einen kurzen Halbsatz an, dass du auch Vorschlaege ' +
  'machst, falls gerade nichts einfaellt.'

const SCHAERF_SYSTEM =
  'Du verbesserst die Verstaendlichkeit eines Pain-Point-Entwurfs fuer die Kadertagung Finanzbereich der ' +
  'Spitaeler Schaffhausen. Du bekommst sieben Felder (titel, f1-f6). Formuliere sie klarer und konkreter, OHNE ' +
  'Fakten zu erfinden oder wegzulassen: gleiche Ich-Perspektive, Schweizer Schreibweise (ss statt scharfem S), ' +
  'kurze klare Saetze; Zahlen, Haeufigkeiten und Systemnamen unveraendert uebernehmen. Leere Felder bleiben ' +
  'leer. Falls fuer die Weiterarbeit am Workshop wichtige Angaben fehlen (Zeitaufwand in Zahlen, betroffene ' +
  'Rollen, Systemnamen, Zielbild), formuliere zusaetzlich hoechstens zwei kurze, konkrete Nachfragen. Antworte ' +
  'AUSSCHLIESSLICH mit einem JSON-Objekt: {"titel": "...", "f1": "...", "f2": "...", "f3": "...", "f4": "...", ' +
  '"f5": "...", "f6": "...", "fragen": ["..."]} — "fragen" ist ein leeres Array, wenn nichts Wichtiges fehlt. ' +
  'Kein Text ausserhalb des JSON.'

const AUSZUG_SYSTEM =
  'Extrahiere aus dem Interview die Angaben fuer einen Pain Point der Kadertagung Finanzbereich. Antworte ' +
  'AUSSCHLIESSLICH mit einem JSON-Objekt mit genau diesen Schluesseln: "titel" (praegnant, hoechstens 80 ' +
  'Zeichen), "f1" (Worum geht es konkret?), "f2" (Was laeuft heute nicht optimal? Mengenangaben uebernehmen, ' +
  'falls genannt), "f3" (Wer ist betroffen oder beteiligt?), "f4" (Welche Daten, Dokumente oder Systeme ' +
  'spielen eine Rolle?), "f5" (Was waere ein gutes Zielbild?), "f6" (Wo koennte KI oder Digitalisierung ' +
  'unterstuetzen?). Schreibe aus der Ich-Perspektive der interviewten Person, ein bis drei Saetze pro Feld, ' +
  'Schweizer Schreibweise (ss statt scharfem S), nur tatsaechlich Gesagtes — nichts dazuerfinden. Fuer Felder ' +
  'ohne Material: leerer String. Kein Text ausserhalb des JSON.'

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    token?: string
    pin?: string
    modus?: string
    verlauf?: { rolle?: string; text?: string }[]
  }

  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || (treffer.person.rolle !== 'teilnahme' && treffer.person.rolle !== 'test')) return abgelehnt()

  const key = process.env.ANTHROPIC_API_KEY
  if (!key) return abgelehnt()

  const db = await kaderDb()
  if (!db) return abgelehnt()
  const pinStand = await pinPruefen(db, treffer.token, treffer.person.pin, body.pin)
  if (pinStand === 'limit') return antwort({ ok: false, grund: 'pin_limit' })
  if (pinStand === 'falsch') return antwort({ ok: false, grund: 'pin' })

  const tag = heuteZuerich()
  const stand = await db
    .prepare('SELECT anzahl FROM kichat WHERE token = ? AND tag = ?')
    .bind(treffer.token, tag)
    .first<{ anzahl: number }>()
  if ((stand?.anzahl ?? 0) >= ZUEGE_PRO_TAG) return antwort({ ok: false, grund: 'limit' })
  await db
    .prepare(
      'INSERT INTO kichat (token, tag, anzahl) VALUES (?, ?, 1) ' +
        'ON CONFLICT(token, tag) DO UPDATE SET anzahl = anzahl + 1'
    )
    .bind(treffer.token, tag)
    .run()

  // Bisherige Titel aus der eigenen Abgabe — damit die KI nicht doppelt fragt.
  const zeile = await db
    .prepare('SELECT json FROM abgaben WHERE token = ?')
    .bind(treffer.token)
    .first<{ json: string }>()
  let bisher: string[] = []
  try {
    if (zeile) {
      const a = JSON.parse(zeile.json) as { painpoints?: { titel?: string }[] }
      bisher = (a.painpoints ?? []).map((p) => p.titel || '').filter(Boolean).slice(0, 5)
    }
  } catch {}

  const auszug = body.modus === 'auszug'
  const schaerfen = body.modus === 'schaerfen'
  let messages: { role: string; content: string }[]
  if (schaerfen) {
    const f = (body as { felder?: Record<string, unknown> }).felder ?? {}
    const kurzE = (w: unknown, max: number) => (typeof w === 'string' ? w.slice(0, max) : '')
    const entwurf = {
      titel: kurzE(f.titel, 300), f1: kurzE(f.f1, 4000), f2: kurzE(f.f2, 4000), f3: kurzE(f.f3, 4000),
      f4: kurzE(f.f4, 4000), f5: kurzE(f.f5, 4000), f6: kurzE(f.f6, 4000),
    }
    messages = [{ role: 'user', content: 'Der Entwurf als JSON:\n' + JSON.stringify(entwurf) }]
  } else {
    const verlauf = Array.isArray(body.verlauf) ? body.verlauf.slice(-60) : []
    messages = verlauf
      .filter((m) => typeof m.text === 'string' && m.text.trim())
      .map((m) => ({
        role: m.rolle === 'ich' ? 'user' : 'assistant',
        content: String(m.text).slice(0, 4000),
      }))
    if (auszug) {
      messages.push({ role: 'user', content: 'Bitte erstelle jetzt das JSON mit den sieben Feldern.' })
    } else if (!messages.length || messages[messages.length - 1].role !== 'user') {
      messages.push({ role: 'user', content: 'Bitte eroeffne das Gespraech.' })
    }
  }

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-opus-5',
        max_tokens: 2000,
        output_config: { effort: 'low' },
        system: schaerfen
          ? SCHAERF_SYSTEM
          : auszug
            ? AUSZUG_SYSTEM
            : FRAGE_SYSTEM(treffer.person.name, treffer.person.einheit, bisher, bisher.length),
        messages,
      }),
    })
    if (!res.ok) return antwort({ ok: false, grund: 'ki_fehler' })
    const data = (await res.json()) as { content?: { type?: string; text?: string }[]; stop_reason?: string }
    if (data.stop_reason === 'refusal') return antwort({ ok: false, grund: 'ki_fehler' })
    const text = (data.content ?? [])
      .filter((b) => b.type === 'text')
      .map((b) => b.text ?? '')
      .join('')
      .trim()
    if (!text) return antwort({ ok: false, grund: 'ki_fehler' })

    if (!auszug && !schaerfen) return antwort({ ok: true, antwort: text.slice(0, 6000) })

    // Auszug: JSON herausloesen (auch wenn das Modell es in Zaeune packt).
    const roh = text.replace(/^```(?:json)?/m, '').replace(/```\s*$/m, '').trim()
    const von = roh.indexOf('{')
    const bis = roh.lastIndexOf('}')
    if (von < 0 || bis <= von) return antwort({ ok: false, grund: 'auszug' })
    let felder: Record<string, unknown>
    try {
      felder = JSON.parse(roh.slice(von, bis + 1))
    } catch {
      return antwort({ ok: false, grund: 'auszug' })
    }
    const kurz = (w: unknown, max: number) => (typeof w === 'string' ? w.slice(0, max) : '')
    const fragen = schaerfen && Array.isArray(felder.fragen)
      ? (felder.fragen as unknown[]).filter((f): f is string => typeof f === 'string').map((f) => f.slice(0, 300)).slice(0, 2)
      : []
    return antwort({
      ok: true,
      felder: {
        titel: kurz(felder.titel, 300),
        f1: kurz(felder.f1, 4000),
        f2: kurz(felder.f2, 4000),
        f3: kurz(felder.f3, 4000),
        f4: kurz(felder.f4, 4000),
        f5: kurz(felder.f5, 4000),
        f6: kurz(felder.f6, 4000),
      },
      fragen,
    })
  } catch {
    return antwort({ ok: false, grund: 'ki_fehler' })
  }
}
