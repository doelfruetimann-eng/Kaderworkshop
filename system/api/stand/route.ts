// Ruecklauf fuer die Leitung (Doelf, Markus, Melina): wer hat abgegeben, wie
// viele Pain Points, welche Menuewahl — plus alle Abgaben im Volltext, das
// Kurz-Feedback und die Testlauf-Gespraeche fuer das Dashboard. Nur per POST
// mit einem Leitungs-Token (so landet der Schluessel weder im Browserverlauf
// noch in Server-Logs). Tokens werden nie zurueckgegeben.

import { kaderConfig, personZuToken, kaderDb, antwort, abgelehnt, type Abgabe } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { token?: string }
  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || treffer.person.rolle !== 'leitung') return abgelehnt()

  const db = await kaderDb()
  if (!db) return abgelehnt()

  const zeilen = await db
    .prepare('SELECT token, json, gesendet FROM abgaben')
    .all<{ token: string; json: string; gesendet: string }>()
  const proToken = new Map<string, { abgabe: Abgabe & { name: string; einheit: string }; gesendet: string }>()
  for (const z of zeilen.results ?? []) {
    try {
      proToken.set(z.token, { abgabe: JSON.parse(z.json), gesendet: z.gesendet })
    } catch {}
  }

  const fb = await db
    .prepare('SELECT token, typ, json, gesendet FROM feedback')
    .all<{ token: string; typ: string; json: string; gesendet: string }>()
  const kurzProToken = new Map<string, { stufe?: number; text?: string; gesendet: string }>()
  const chatProToken = new Map<string, { verlauf?: { rolle: string; text: string }[]; gesendet: string }>()
  for (const z of fb.results ?? []) {
    try {
      const inhalt = JSON.parse(z.json)
      if (z.typ === 'kurz') kurzProToken.set(z.token, { ...inhalt, gesendet: z.gesendet })
      if (z.typ === 'chat') chatProToken.set(z.token, { ...inhalt, gesendet: z.gesendet })
    } catch {}
  }

  // Erwartet werden alle Teilnahme-Tokens; Leitung und Testkonten zaehlen nicht dazu.
  const personen = Object.entries(config.tokens)
    .filter(([, p]) => p.rolle === 'teilnahme')
    .map(([t, p]) => {
      const eintrag = proToken.get(t)
      return {
        name: p.name,
        einheit: p.einheit,
        mail: p.mail ?? '',
        abgegeben: eintrag?.gesendet ?? null,
        anzahl: eintrag?.abgabe.painpoints?.length ?? 0,
        menue: eintrag?.abgabe.menue ?? '',
      }
    })

  // Kurz-Feedback («Wie war die Vorbereitung?») von Teilnahme UND Testlauf.
  const stimmung = Object.entries(config.tokens)
    .filter(([t, p]) => (p.rolle === 'teilnahme' || p.rolle === 'test') && kurzProToken.has(t))
    .map(([t, p]) => {
      const k = kurzProToken.get(t)!
      return { name: p.name, einheit: p.einheit, test: p.rolle === 'test', stufe: k.stufe ?? 0, text: k.text ?? '', gesendet: k.gesendet }
    })

  // Testlauf: eigene Abgaben und die KI-gefuehrten Feedback-Gespraeche.
  const tests = Object.entries(config.tokens)
    .filter(([, p]) => p.rolle === 'test')
    .map(([t, p]) => {
      const eintrag = proToken.get(t)
      const chat = chatProToken.get(t)
      return {
        name: p.name,
        einheit: p.einheit,
        abgegeben: eintrag?.gesendet ?? null,
        // Die erfassten Themen, damit sich die Kette Dashboard → Werkbank im
        // Testlauf einmal durchspielen laesst. Sie bleiben aus `abgaben`
        // heraus und zaehlen darum nirgends in Ruecklauf oder Auswertung.
        painpoints: eintrag?.abgabe?.painpoints ?? [],
        verlauf: chat?.verlauf ?? [],
        chatZeit: chat?.gesendet ?? null,
      }
    })

  // Nur echte Teilnahme-Abgaben — Testlaeufe gehoeren nicht in Auswertung und Export.
  const testTokens = new Set(
    Object.entries(config.tokens)
      .filter(([, p]) => p.rolle === 'test')
      .map(([t]) => t)
  )
  const abgaben = Array.from(proToken.entries())
    .filter(([t]) => !testTokens.has(t))
    .map(([, e]) => ({ ...e.abgabe, gesendet: e.gesendet }))

  // Juengster KI-Cluster-Vorschlag (falls je berechnet).
  const clusterZeile = await db
    .prepare('SELECT json, gesendet FROM cluster ORDER BY id DESC LIMIT 1')
    .first<{ json: string; gesendet: string }>()
  let cluster: unknown = null
  if (clusterZeile) {
    try {
      cluster = { daten: JSON.parse(clusterZeile.json), gesendet: clusterZeile.gesendet }
    } catch {}
  }

  return antwort({ ok: true, frist: config.frist ?? '', tagung: config.tagung ?? '', personen, abgaben, stimmung, tests, cluster })
}
