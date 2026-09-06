// Loest einen persoenlichen Token zu Name und Einheit auf. GET (der Token
// steht zwangslaeufig in der URL) verraet nur noch, OB eine PIN noetig ist —
// Identitaet und Inhalte gibt es erst per POST mit {token, pin}; mit
// {daten:true} kommt zusaetzlich die eigene Abgabe (Zweitgeraet-Fall).

import { kaderConfig, personZuToken, kaderDb, pinPruefen, fortschritt, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

async function identitaet(token: string, pin: unknown, mitDaten: boolean) {
  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, token)
  if (!treffer) return abgelehnt()

  const db = await kaderDb()
  if (!db) return abgelehnt()
  const pinStand = await pinPruefen(db, treffer.token, treffer.person.pin, pin)
  if (pinStand === 'limit') return antwort({ ok: false, grund: 'pin_limit' })
  if (pinStand === 'falsch') return antwort({ ok: false, grund: 'pin' })

  let abgegeben: string | null = null
  let abgabe: unknown = null
  const zeile = await db
    .prepare('SELECT json, gesendet FROM abgaben WHERE token = ?')
    .bind(treffer.token)
    .first<{ json: string; gesendet: string }>()
  if (zeile) {
    abgegeben = zeile.gesendet
    if (mitDaten) {
      try {
        abgabe = JSON.parse(zeile.json)
      } catch {}
    }
  }

  const basis: Record<string, unknown> = {
    ok: true,
    name: treffer.person.name,
    einheit: treffer.person.einheit,
    mail: treffer.person.mail ?? '',
    rolle: treffer.person.rolle,
    frist: config.frist ?? '',
    tagung: config.tagung ?? '',
    ki: config.ki === true,
    interview: !!process.env.ANTHROPIC_API_KEY,
    abgegeben,
    zaehler: await fortschritt(db, config),
  }
  if (mitDaten && abgabe) basis.abgabe = abgabe
  return antwort(basis)
}

export async function GET(request: Request) {
  const token = new URL(request.url).searchParams.get('t') ?? ''
  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, token)
  if (!treffer) return abgelehnt()
  if (treffer.person.pin) return antwort({ ok: true, pinNoetig: true })
  return identitaet(token, undefined, false)
}

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { token?: string; pin?: string; daten?: boolean }
  return identitaet(body.token ?? '', body.pin, body.daten === true)
}
