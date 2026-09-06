// Kurz-Feedback zur Vorbereitung selbst («Wie war das fuer dich?»):
// eine Stufe 1-4 plus optionaler Text, jederzeit aenderbar (Upsert).
// Getrennt von den Abgaben, damit Nachbessern das Feedback nicht ueberschreibt.

import { kaderConfig, personZuToken, kaderDb, pinPruefen, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    token?: string
    pin?: string
    stufe?: number
    text?: string
  }

  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || (treffer.person.rolle !== 'teilnahme' && treffer.person.rolle !== 'test')) return abgelehnt()

  const db = await kaderDb()
  if (!db) return abgelehnt()
  const pinStand = await pinPruefen(db, treffer.token, treffer.person.pin, body.pin)
  if (pinStand === 'limit') return antwort({ ok: false, grund: 'pin_limit' })
  if (pinStand === 'falsch') return antwort({ ok: false, grund: 'pin' })

  const stufe = Number(body.stufe)
  if (!Number.isInteger(stufe) || stufe < 1 || stufe > 4) return antwort({ ok: false, grund: 'stufe' })
  const text = typeof body.text === 'string' ? body.text.slice(0, 2000) : ''

  const gesendet = new Date().toISOString()
  const json = JSON.stringify({ typ: 'kurz', name: treffer.person.name, einheit: treffer.person.einheit, stufe, text })
  await db
    .prepare(
      "INSERT INTO feedback (token, typ, json, gesendet) VALUES (?, 'kurz', ?, ?) " +
        'ON CONFLICT(token, typ) DO UPDATE SET json = excluded.json, gesendet = excluded.gesendet'
    )
    .bind(treffer.token, json, gesendet)
    .run()

  return antwort({ ok: true })
}
