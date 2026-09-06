// Freiwilliges KI-Gespraech ueber die eigenen Pain Points, nach dem Absenden.
// Der Server holt die Abgabe selbst aus der Datenbank und reicht nur den
// Chat-Verlauf an die Claude-API weiter; der ANTHROPIC_API_KEY bleibt hier.
// Abschaltbar ueber ki:false im KADER_CONFIG. Tageslimit pro Token.

import { kaderConfig, personZuToken, kaderDb, pinPruefen, heuteZuerich, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

// Gemeinsamer Tageszaehler mit dem Interview-Modus (Tabelle kichat).
const ZUEGE_PRO_TAG = 80

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    token?: string
    pin?: string
    verlauf?: { rolle?: string; text?: string }[]
  }

  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer) return abgelehnt()
  // Testkonten fuehren das Finalisierungs-Feedback immer per KI —
  // unabhaengig davon, ob das Gespraech fuer die Teilnahme freigeschaltet ist.
  const testlauf = treffer.person.rolle === 'test'
  if (!testlauf && config.ki !== true) return abgelehnt()

  const key = process.env.ANTHROPIC_API_KEY
  if (!key) return abgelehnt()

  const db = await kaderDb()
  if (!db) return abgelehnt()
  const pinStand = await pinPruefen(db, treffer.token, treffer.person.pin, body.pin)
  if (pinStand === 'limit') return antwort({ ok: false, grund: 'pin_limit' })
  if (pinStand === 'falsch') return antwort({ ok: false, grund: 'pin' })

  const zeile = await db
    .prepare('SELECT json FROM abgaben WHERE token = ?')
    .bind(treffer.token)
    .first<{ json: string }>()
  if (!zeile && !testlauf) return antwort({ ok: false, grund: 'keine_abgabe' })

  // Tageslimit: freundlich fuer 10 Personen, hart genug gegen Missbrauch.
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

  let abgabe: { name?: string; painpoints?: Record<string, string>[] } = {}
  try {
    if (zeile) abgabe = JSON.parse(zeile.json)
  } catch {}
  const themen = (abgabe.painpoints ?? [])
    .map(
      (p, i) =>
        `Pain Point ${i + 1}: ${p.titel || 'Ohne Titel'}\n` +
        `Worum es geht: ${p.f1 || '-'}\nWas nicht optimal laeuft: ${p.f2 || '-'}\n` +
        `Betroffene: ${p.f3 || '-'}\nDaten und Systeme: ${p.f4 || '-'}\n` +
        `Zielbild: ${p.f5 || '-'}\nKI-Vermutung: ${p.f6 || '-'}`
    )
    .join('\n\n')

  const systemTest =
    'Du fuehrst ein strukturiertes Feedback-Gespraech zur Finalisierung einer Vorbereitungs-Website fuer die ' +
    'Kadertagung des Finanzbereichs der Spitaeler Schaffhausen. Dein Gegenueber gehoert zum Kernteam (Doelf, ' +
    'Melina, Markus oder Fabienne) und hat die Seite gerade als Testperson durchgespielt: persoenlicher Link mit PIN, ' +
    'KI-Standortbestimmung, gefuehrtes Erfassen von Pain Points mit Nachfragen, Kontrolle mit Menuewahl, ' +
    'Absenden, Danke-Seite mit Programm und Countdown. Per du, Schweizer Schreibweise (ss statt scharfem S). ' +
    'Fuehre nacheinander durch vier Punkte und stelle immer nur eine Frage aufs Mal: (1) Was ist gut und soll ' +
    'so bleiben? (2) Was wuerdest du anpassen — was hat gestoert oder gefehlt? (3) Konkrete ' +
    'Verbesserungsvorschlaege — frage nach, bis sie umsetzbar formuliert sind (welcher Schritt, welcher Text, ' +
    'was stattdessen). (4) Zum Schluss: eine zusaetzliche Idee, die noch niemand eingebracht hat. Wo sinnvoll, ' +
    'schlage selbst eine konkrete Anpassung vor und hole dir ein Ja/Nein dazu. Bleib kurz — zwei bis vier ' +
    'Saetze plus eine Frage. Fasse am Ende alles als kompakte Punkteliste zusammen. Wenn der Verlauf leer ist, ' +
    'begruesse die Person mit Vornamen, erklaere in einem Satz das Vorgehen und starte mit Punkt 1.\n\n' +
    `Die Person heisst ${treffer.person.name}.`

  const system =
    'Du bist ein freundlicher Sparringspartner bei der Vorbereitung einer Kadertagung des Finanzbereichs ' +
    'der Spitaeler Schaffhausen. Dein Gegenueber ist eine Fuehrungskraft, per du, Schweizer Schreibweise ' +
    '(ss statt scharfem S). Die Person hat Pain Points aus ihrem Arbeitsalltag erfasst; hilf ihr, diese zu ' +
    'schaerfen: stelle gezielte Rueckfragen (eine pro Antwort), schlage konkretere Formulierungen und ' +
    'Mengenangaben vor, weise auf fehlende Angaben hin und gib realistische Hinweise, wo KI helfen koennte ' +
    'und wo nicht. Bleib kurz — zwei bis vier Saetze plus hoechstens eine Frage. Keine Patientendaten, ' +
    'Rollen statt Namen. Wenn der Verlauf leer ist, eroeffne das Gespraech selbst: begruesse die Person mit ' +
    'Vornamen und steige mit einer konkreten Beobachtung zu einem ihrer Pain Points ein.\n\n' +
    `Die Person heisst ${abgabe.name ?? 'unbekannt'}. Ihre erfassten Pain Points:\n\n${themen || 'Noch keine Pain Points erfasst.'}`

  const verlauf = Array.isArray(body.verlauf) ? body.verlauf.slice(-40) : []
  const messages = verlauf
    .filter((m) => typeof m.text === 'string' && m.text.trim())
    .map((m) => ({
      role: m.rolle === 'ich' ? 'user' : 'assistant',
      content: String(m.text).slice(0, 4000),
    }))
  if (!messages.length || messages[messages.length - 1].role !== 'user') {
    messages.push({ role: 'user', content: 'Bitte eroeffne das Gespraech.' })
  }

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-opus-5',
        max_tokens: 2000,
        output_config: { effort: 'low' },
        system: testlauf ? systemTest : system,
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
    const gekuerzt = text.slice(0, 6000)
    if (testlauf) {
      // Der ganze Verlauf inkl. neuer Antwort wandert in die feedback-Tabelle,
      // damit das Finalisierungs-Feedback zentral beim Dashboard landet.
      const komplett = verlauf
        .filter((m) => typeof m.text === 'string' && m.text.trim())
        .map((m) => ({ rolle: m.rolle === 'ich' ? 'ich' : 'ki', text: String(m.text).slice(0, 4000) }))
        .concat([{ rolle: 'ki', text: gekuerzt }])
      await db
        .prepare(
          "INSERT INTO feedback (token, typ, json, gesendet) VALUES (?, 'chat', ?, ?) " +
            'ON CONFLICT(token, typ) DO UPDATE SET json = excluded.json, gesendet = excluded.gesendet'
        )
        .bind(
          treffer.token,
          JSON.stringify({ typ: 'chat', name: treffer.person.name, verlauf: komplett }),
          new Date().toISOString()
        )
        .run()
    }
    return antwort({ ok: true, antwort: gekuerzt })
  } catch {
    return antwort({ ok: false, grund: 'ki_fehler' })
  }
}
