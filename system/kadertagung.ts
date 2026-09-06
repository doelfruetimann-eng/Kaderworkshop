// Gemeinsame Helfer fuer die Kadertagung-API (/api/kadertagung/*).
// Konfiguration (Frist, KI-Schalter, Token-Tabelle) kommt aus der Tabelle
// konfig in der Datenbank, ersatzweise aus dem Worker-Secret KADER_CONFIG —
// Tokens stehen damit in keinem Repo.
// Die Beitraege liegen in der D1-Datenbank KADER_DB (Region Westeuropa).

import { getCloudflareContext } from '@opennextjs/cloudflare'

// Schlanke Struktur-Typen fuer das D1-Binding — das Projekt zieht keine
// @cloudflare/workers-types, und mehr als das hier braucht die API nicht.
export type KaderStatement = {
  bind(...werte: unknown[]): KaderStatement
  first<T>(): Promise<T | null>
  run(): Promise<unknown>
  all<T>(): Promise<{ results?: T[] }>
}
export type KaderDb = {
  prepare(sql: string): KaderStatement
  batch(anweisungen: KaderStatement[]): Promise<unknown>
}

export type KaderPerson = { name: string; einheit: string; rolle: 'teilnahme' | 'leitung' | 'test'; pin?: string; mail?: string }
export type KaderConfig = { frist?: string; tagung?: string; ki?: boolean; tokens: Record<string, KaderPerson> }

function configLesen(roh: string | undefined | null): KaderConfig | null {
  if (!roh) return null
  try {
    const c = JSON.parse(roh) as KaderConfig
    if (!c || typeof c.tokens !== 'object') return null
    return c
  } catch {
    return null
  }
}

// Woher die Konfiguration zuletzt kam — nur fuer die Diagnose.
export type KonfigQuelle = 'datenbank' | 'secret' | null

export async function kaderConfigMitQuelle(): Promise<{ config: KaderConfig | null; quelle: KonfigQuelle }> {
  // 1. Datenbank. Das ist der verlaessliche Weg: ein Deploy kann sie nicht
  //    loeschen, und sie laesst sich in der D1-Konsole direkt setzen
  //    (siehe KADERTAGUNG.md, Abschnitt "Konfiguration in der Datenbank").
  const db = await kaderDb()
  if (db) {
    try {
      const zeile = await db
        .prepare('SELECT wert FROM konfig WHERE schluessel = ?')
        .bind('kader_config')
        .first<{ wert: string }>()
      const ausDb = configLesen(zeile?.wert)
      if (ausDb) return { config: ausDb, quelle: 'datenbank' }
    } catch {}
  }

  // 2. Worker-Secret KADER_CONFIG (bei `next dev` nur auf dem Cloudflare-Kontext).
  let roh = process.env.KADER_CONFIG
  if (!roh) {
    const { env } = await getCloudflareContext({ async: true })
    roh = (env as { KADER_CONFIG?: string }).KADER_CONFIG
  }
  const ausSecret = configLesen(roh)
  return ausSecret ? { config: ausSecret, quelle: 'secret' } : { config: null, quelle: null }
}

export async function kaderConfig(): Promise<KaderConfig | null> {
  return (await kaderConfigMitQuelle()).config
}

// Konstantzeit-Vergleich, damit Token nicht ueber Antwortzeiten erratbar sind.
function gleich(a: string, b: string): boolean {
  const laenge = Math.max(a.length, b.length)
  let diff = a.length === b.length ? 0 : 1
  for (let i = 0; i < laenge; i++) {
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0)
  }
  return diff === 0
}

// Sucht den Token in der Tabelle — immer ueber alle Eintraege, aus demselben Grund.
export function personZuToken(config: KaderConfig, token: string): { token: string; person: KaderPerson } | null {
  if (!token || token.length < 8 || token.length > 64) return null
  let treffer: { token: string; person: KaderPerson } | null = null
  for (const [t, person] of Object.entries(config.tokens)) {
    if (gleich(t, token)) treffer = { token: t, person }
  }
  return treffer
}

// Heutiges Datum in der Schweiz als JJJJ-MM-TT — fuer den Fristvergleich.
export function heuteZuerich(): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Zurich' }).format(new Date())
}

export function fristVorbei(config: KaderConfig): boolean {
  const frist = (config.frist ?? '').trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(frist)) return false
  return heuteZuerich() > frist
}

export async function kaderDb(): Promise<KaderDb | null> {
  const { env } = await getCloudflareContext({ async: true })
  const db = (env as { KADER_DB?: KaderDb }).KADER_DB
  if (!db) return null
  await db.batch([
    db.prepare(
      'CREATE TABLE IF NOT EXISTS abgaben (token TEXT PRIMARY KEY, json TEXT NOT NULL, gesendet TEXT NOT NULL)'
    ),
    db.prepare(
      'CREATE TABLE IF NOT EXISTS verlauf (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT NOT NULL, json TEXT NOT NULL, gesendet TEXT NOT NULL)'
    ),
    db.prepare(
      'CREATE TABLE IF NOT EXISTS kichat (token TEXT NOT NULL, tag TEXT NOT NULL, anzahl INTEGER NOT NULL, PRIMARY KEY (token, tag))'
    ),
    db.prepare(
      'CREATE TABLE IF NOT EXISTS feedback (token TEXT NOT NULL, typ TEXT NOT NULL, json TEXT NOT NULL, gesendet TEXT NOT NULL, PRIMARY KEY (token, typ))'
    ),
    db.prepare(
      'CREATE TABLE IF NOT EXISTS pinversuche (token TEXT NOT NULL, tag TEXT NOT NULL, anzahl INTEGER NOT NULL, PRIMARY KEY (token, tag))'
    ),
    db.prepare(
      'CREATE TABLE IF NOT EXISTS cluster (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT NOT NULL, roh TEXT NOT NULL, gesendet TEXT NOT NULL)'
    ),
    db.prepare('CREATE TABLE IF NOT EXISTS konfig (schluessel TEXT PRIMARY KEY, wert TEXT NOT NULL)'),
  ])
  return db
}

// Anonymer Fortschritt fuer die Teilnehmenden: wie viele Einheiten haben
// abgegeben, wie viele Themen liegen vor — ohne jeden Inhalt.
export async function fortschritt(db: KaderDb, config: KaderConfig): Promise<{ einheiten: number; themen: number; total: number }> {
  const zeilen = await db.prepare('SELECT token, json FROM abgaben').all<{ token: string; json: string }>()
  let einheiten = 0
  let themen = 0
  for (const z of zeilen.results ?? []) {
    const person = config.tokens[z.token]
    if (!person || person.rolle !== 'teilnahme') continue
    try {
      const a = JSON.parse(z.json) as { painpoints?: unknown[] }
      const n = Array.isArray(a.painpoints) ? a.painpoints.length : 0
      if (n > 0) {
        einheiten += 1
        themen += n
      }
    } catch {}
  }
  const total = Object.values(config.tokens).filter((p) => p.rolle === 'teilnahme').length
  return { einheiten, themen, total }
}

const PIN_VERSUCHE_PRO_TAG = 15

// Prueft die PIN zum Token. Personen ohne PIN im Config brauchen keine.
// Fehlversuche werden pro Tag gezaehlt — vier Ziffern waeren sonst ratbar.
export async function pinPruefen(
  db: KaderDb,
  token: string,
  personPin: string | undefined,
  pin: unknown
): Promise<'ok' | 'falsch' | 'limit'> {
  if (!personPin) return 'ok'
  const tag = heuteZuerich()
  const stand = await db
    .prepare('SELECT anzahl FROM pinversuche WHERE token = ? AND tag = ?')
    .bind(token, tag)
    .first<{ anzahl: number }>()
  if ((stand?.anzahl ?? 0) >= PIN_VERSUCHE_PRO_TAG) return 'limit'
  if (typeof pin === 'string' && gleich(personPin, pin)) return 'ok'
  await db
    .prepare(
      'INSERT INTO pinversuche (token, tag, anzahl) VALUES (?, ?, 1) ' +
        'ON CONFLICT(token, tag) DO UPDATE SET anzahl = anzahl + 1'
    )
    .bind(token, tag)
    .run()
  return 'falsch'
}

export type Abgabe = {
  standort: {
    haeufigkeit: string
    erfahrungen: string[]
    erfahrungAnderes: string
    werkzeuge: string[]
    erwartung: string
    sorgen: string
  }
  painpoints: { titel: string; f1: string; f2: string; f3: string; f4: string; f5: string; f6: string; impuls: string }[]
  menue: string
}

const MENUES = new Set(['cordonbleu', 'wienerschnitzel', 'zuercher', 'vegetarisch', 'vegan', 'keins', ''])

function kurz(wert: unknown, max: number): string {
  return typeof wert === 'string' ? wert.slice(0, max) : ''
}
function liste(wert: unknown, max: number): string[] {
  if (!Array.isArray(wert)) return []
  return wert.filter((e): e is string => typeof e === 'string').map((e) => e.slice(0, 200)).slice(0, max)
}

// Strikte Whitelist: nur bekannte Felder, begrenzte Laengen — alles andere faellt weg.
export function abgabeNormalisieren(roh: unknown): Abgabe {
  const b = (roh ?? {}) as Record<string, unknown>
  const standort = (b.standort ?? {}) as Record<string, unknown>
  const painpoints = Array.isArray(b.painpoints) ? b.painpoints.slice(0, 5) : []
  return {
    standort: {
      haeufigkeit: kurz(standort.haeufigkeit, 60),
      erfahrungen: liste(standort.erfahrungen, 12),
      erfahrungAnderes: kurz(standort.erfahrungAnderes, 300),
      werkzeuge: liste(standort.werkzeuge, 12),
      erwartung: kurz(standort.erwartung, 4000),
      sorgen: kurz(standort.sorgen, 4000),
    },
    painpoints: painpoints.map((p) => {
      const pp = (p ?? {}) as Record<string, unknown>
      return {
        titel: kurz(pp.titel, 300),
        f1: kurz(pp.f1, 4000),
        f2: kurz(pp.f2, 4000),
        f3: kurz(pp.f3, 4000),
        f4: kurz(pp.f4, 4000),
        f5: kurz(pp.f5, 4000),
        f6: kurz(pp.f6, 4000),
        impuls: kurz(pp.impuls, 400),
      }
    }),
    menue: MENUES.has(kurz(b.menue, 20)) ? (b.menue as string) : '',
  }
}

export function antwort(daten: Record<string, unknown>, status = 200) {
  return Response.json(daten, { status })
}

// Bewusst informationsarm: ungueltiger Token, fehlende Konfiguration und
// fehlende Datenbank sehen von aussen gleich aus.
export function abgelehnt() {
  return antwort({ ok: false })
}
