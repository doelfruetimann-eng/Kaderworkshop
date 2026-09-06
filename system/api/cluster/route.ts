// KI-Clustering der eingegangenen Pain Points fuer die Moderation:
// EIN Claude-Aufruf ueber alle Nicht-Test-Abgaben, Ergebnis als Vorschlag
// (nicht als Entscheid) in der cluster-Tabelle. Nur mit Leitungs-Token.
// Teilnehmende sehen davon nichts — deckt sich mit dem Entscheid, Beitraege
// vor dem Abend nicht gegenseitig sichtbar zu machen.

import { kaderConfig, personZuToken, kaderDb, antwort, abgelehnt } from '@/lib/kadertagung'

export const dynamic = 'force-dynamic'

const SYSTEM =
  'Du bist ein erfahrener Moderator fuer einen KI-Workshop im Finanzbereich eines Schweizer Spitals. ' +
  'Gruppiere die folgenden Pain Points in inhaltlich sinnvolle Cluster. Regeln: Hoechstens sechs Cluster ' +
  'plus eine Restgruppe; ein Cluster braucht mindestens zwei Themen. Cluster-Titel konkret und ' +
  'handlungsorientiert (nicht «Kommunikation» oder «Prozesse»), Schweizer Schreibweise (ss statt scharfem S). ' +
  'Erkenne echte Querschnittsthemen ueber Einheiten hinweg. Erfinde keine Inhalte — nutze nur, was in den ' +
  'Texten steht. Antworte AUSSCHLIESSLICH mit gueltigem JSON nach diesem Schema: ' +
  '{"clusters":[{"titel":"...","zusammenfassung":"1-2 Saetze zum gemeinsamen Problem","quer":true,' +
  '"ids":["pp1","pp4"]}],"rest":["pp7"]} — "quer" heisst: betrifft mehrere Einheiten. Kein Text ausserhalb des JSON.'

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { token?: string }
  const config = await kaderConfig()
  if (!config) return abgelehnt()
  const treffer = personZuToken(config, body.token ?? '')
  if (!treffer || treffer.person.rolle !== 'leitung') return abgelehnt()

  const key = process.env.ANTHROPIC_API_KEY
  if (!key) return antwort({ ok: false, grund: 'kein_ki' })

  const db = await kaderDb()
  if (!db) return abgelehnt()

  // Alle echten Abgaben einsammeln und die Themen durchnummerieren.
  const zeilen = await db.prepare('SELECT token, json FROM abgaben').all<{ token: string; json: string }>()
  type Thema = { id: string; einheit: string; person: string; titel: string; f1: string; f2: string; f4: string }
  const themen: Thema[] = []
  for (const z of zeilen.results ?? []) {
    const person = config.tokens[z.token]
    if (!person || person.rolle !== 'teilnahme') continue
    try {
      const a = JSON.parse(z.json) as { painpoints?: Record<string, string>[] }
      for (const p of a.painpoints ?? []) {
        themen.push({
          id: 'pp' + (themen.length + 1),
          einheit: person.einheit,
          person: person.name,
          titel: (p.titel || 'Ohne Titel').slice(0, 300),
          f1: (p.f1 || '').slice(0, 1200),
          f2: (p.f2 || '').slice(0, 1200),
          f4: (p.f4 || '').slice(0, 600),
        })
      }
    } catch {}
  }
  if (themen.length < 3) return antwort({ ok: false, grund: 'zu_wenig', anzahl: themen.length })

  const liste = themen
    .map(
      (t) =>
        `${t.id}\nEinheit: ${t.einheit}\nTitel: ${t.titel}\nWorum es geht: ${t.f1 || '-'}\n` +
        `Was nicht optimal laeuft: ${t.f2 || '-'}\nDaten und Systeme: ${t.f4 || '-'}`
    )
    .join('\n\n')

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-opus-5',
        max_tokens: 3000,
        output_config: { effort: 'low' },
        system: SYSTEM,
        messages: [{ role: 'user', content: 'Die Pain Points:\n\n' + liste }],
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
    const von = text.indexOf('{')
    const bis = text.lastIndexOf('}')
    if (von < 0 || bis <= von) return antwort({ ok: false, grund: 'auszug' })
    let roh: { clusters?: { titel?: string; zusammenfassung?: string; quer?: boolean; ids?: string[] }[]; rest?: string[] }
    try {
      roh = JSON.parse(text.slice(von, bis + 1))
    } catch {
      return antwort({ ok: false, grund: 'auszug' })
    }

    // Validieren und aufloesen: jede ID muss existieren, sonst gilt der Lauf nicht.
    const proId = new Map(themen.map((t) => [t.id, t]))
    const aufloesen = (ids: unknown) => {
      const liste: { titel: string; einheit: string; person: string }[] = []
      for (const id of Array.isArray(ids) ? ids : []) {
        const t = proId.get(String(id))
        if (!t) throw new Error('unbekannte ID')
        liste.push({ titel: t.titel, einheit: t.einheit, person: t.person })
      }
      return liste
    }
    let ergebnis
    try {
      ergebnis = {
        clusters: (roh.clusters ?? []).slice(0, 8).map((c) => ({
          titel: String(c.titel ?? '').slice(0, 120) || 'Ohne Titel',
          zusammenfassung: String(c.zusammenfassung ?? '').slice(0, 600),
          quer: c.quer === true,
          themen: aufloesen(c.ids),
        })),
        rest: aufloesen(roh.rest),
        anzahl: themen.length,
      }
    } catch {
      return antwort({ ok: false, grund: 'auszug' })
    }

    const gesendet = new Date().toISOString()
    await db
      .prepare('INSERT INTO cluster (json, roh, gesendet) VALUES (?, ?, ?)')
      .bind(JSON.stringify(ergebnis), text.slice(0, 60000), gesendet)
      .run()
    return antwort({ ok: true, cluster: ergebnis, gesendet })
  } catch {
    return antwort({ ok: false, grund: 'ki_fehler' })
  }
}
