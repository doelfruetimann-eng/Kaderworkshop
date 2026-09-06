// Diagnose fuer die Einrichtung: meldet NUR Ja/Nein, ob die Secrets und die
// Datenbank im laufenden Worker ankommen — nie Werte, nie Tokens. Nur per POST
// mit einem Leitungs-Token: die Auskunft "kennt ihr diesen Token?" und der
// Anthropic-Ping (kostet Geld) duerfen nicht offen im Netz stehen.

import { kaderConfig, kaderConfigMitQuelle, personZuToken, kaderDb, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

// Offene Kurzauskunft: NUR Zaehlwerte — wie viele Zugaenge je Rolle im
// eingespielten Config stehen und ob die Datenbank haengt. Keine Namen, keine
// Tokens, kein Token-Orakel, kein KI-Aufruf. Das reicht, um zu sehen, ob das
// Secret vollstaendig angekommen ist.
export async function GET() {
  const { config, quelle } = await kaderConfigMitQuelle()
  const rollen: Record<string, number> = {}
  for (const person of Object.values(config?.tokens ?? {})) {
    const r = person.rolle ?? 'teilnahme'
    rollen[r] = (rollen[r] ?? 0) + 1
  }
  return Response.json({
    konfigQuelle: quelle,
    kaderConfigGesetzt: Boolean(process.env.KADER_CONFIG),
    kaderConfigLesbar: Boolean(config),
    tokensImConfig: config ? Object.keys(config.tokens).length : 0,
    rollen,
    sitePasswordGesetzt: Boolean(process.env.SITE_PASSWORD),
    anthropicKeyGesetzt: Boolean(process.env.ANTHROPIC_API_KEY),
    datenbankVerbunden: Boolean(await kaderDb()),
  })
}

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    token?: string
    probe?: string
    ki?: boolean
  }
  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || treffer.person.rolle !== 'leitung') return abgelehnt()

  // Form des Schluessels pruefen, ohne ihn preiszugeben: Laenge, Praefix-Typ,
  // versehentliche Leerzeichen oder Anfuehrungszeichen (haeufigste Kopierfehler).
  const k = process.env.ANTHROPIC_API_KEY ?? ''
  const schluesselForm = k
    ? {
        laenge: k.length,
        beginntMitSkAnt: k.startsWith('sk-ant-'),
        randLeerzeichen: k !== k.trim(),
        anfuehrungszeichen: /^["']|["']$/.test(k),
        zeilenumbruch: /[\r\n]/.test(k),
      }
    : null

  // Mini-Aufruf an die Anthropic-API: nur Statuscode und Fehlertyp, nie Schluessel.
  let anthropicPing: unknown = null
  if (body.ki && k) {
    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': k,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-opus-5',
          max_tokens: 16,
          output_config: { effort: 'low' },
          messages: [{ role: 'user', content: 'Sag nur: ok' }],
        }),
      })
      anthropicPing = { status: res.status, auszug: (await res.text()).slice(0, 300) }
    } catch (err) {
      anthropicPing = { fehler: String(err).slice(0, 300) }
    }
  }

  const db = await kaderDb()

  return Response.json({
    anthropicPing,
    probeBekannt: body.probe ? Boolean(personZuToken(config, body.probe)) : null,
    kaderConfigLesbar: true,
    tokensImConfig: Object.keys(config.tokens).length,
    sitePasswordGesetzt: Boolean(process.env.SITE_PASSWORD),
    anthropicKeyGesetzt: Boolean(k),
    schluesselForm,
    datenbankVerbunden: Boolean(db),
  })
}
