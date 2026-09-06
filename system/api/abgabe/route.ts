// Nimmt die Abgabe einer Teilnehmerin entgegen: KI-Standortbestimmung,
// Pain Points und Menuewahl. Es zaehlt der letzte Stand; jede Fassung wird
// zusaetzlich im Verlauf aufbewahrt. Gespeichert werden nur die Angaben
// selbst plus Name/Einheit aus dem Token — keine IP, kein User-Agent.

import { kaderConfig, personZuToken, kaderDb, pinPruefen, fristVorbei, abgabeNormalisieren, fortschritt, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

export async function POST(request: Request) {
  const roh = await request.text()
  if (roh.length > 200_000) return antwort({ ok: false, grund: 'zu_gross' })

  let body: { token?: string; pin?: string } & Record<string, unknown>
  try {
    body = JSON.parse(roh)
  } catch {
    return antwort({ ok: false, grund: 'kein_json' })
  }

  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || (treffer.person.rolle !== 'teilnahme' && treffer.person.rolle !== 'test')) return abgelehnt()
  if (fristVorbei(config)) return antwort({ ok: false, grund: 'frist' })

  const db = await kaderDb()
  if (!db) return abgelehnt()
  const pinStand = await pinPruefen(db, treffer.token, treffer.person.pin, body.pin)
  if (pinStand === 'limit') return antwort({ ok: false, grund: 'pin_limit' })
  if (pinStand === 'falsch') return antwort({ ok: false, grund: 'pin' })

  const abgabe = abgabeNormalisieren(body)
  const gesendet = new Date().toISOString()
  const json = JSON.stringify({ name: treffer.person.name, einheit: treffer.person.einheit, ...abgabe })

  await db.batch([
    db
      .prepare(
        'INSERT INTO abgaben (token, json, gesendet) VALUES (?, ?, ?) ' +
          'ON CONFLICT(token) DO UPDATE SET json = excluded.json, gesendet = excluded.gesendet'
      )
      .bind(treffer.token, json, gesendet),
    db.prepare('INSERT INTO verlauf (token, json, gesendet) VALUES (?, ?, ?)').bind(treffer.token, json, gesendet),
  ])

  return antwort({ ok: true, gesendet, zaehler: await fortschritt(db, config) })
}
