# Lernvideo vertonen — Anleitung für ElevenLabs

Gilt für `docs/lernvideo-teilnahme.mp4`, das Lernvideo zur Teilnahme-Seite.
Du erzeugst **eine einzige MP3** mit allen dreizehn Sprechtexten und den
Pausen dazwischen und lädst sie im Chat hoch. Claude schneidet an den Pausen,
nimmt die Bildspur passend neu auf, mischt und legt das Video in beide Repos.

Der Sprechtext steht in `docs/lernvideo-teilnahme-sprechtexte-elevenlabs.txt`
— diese Datei ist zum direkten Kopieren gedacht und enthält nichts als den
Text und die Trennmarken.

## Einstellungen

Diese Werte stammen aus der Aufnahme vom 19. August 2026, die sauber
funktioniert hat (Dateiname `…_pvc_sp100_s90_sb91_m2.mp3`):

| Regler | Wert | Warum |
|---|---|---|
| Modell | **Eleven Multilingual v2** | spricht Deutsch nativ; englische Modelle verunstalten die Umlaute |
| Stimme | **Carla Blum** | ruhig und sachlich, passt zur Schulung |
| Speed | **1.00** | nicht heruntersetzen — siehe unten |
| Stability | **90** | hält die Stimme über dreizehn Segmente gleichmässig |
| Similarity | **91** | nah am Original |
| Style | niedrig (0–20) | für eine Schulung bewusst zurückhaltend |
| Speaker boost | ein | etwas mehr Präsenz |
| Format | MP3, ab 128 kbit/s | |

**Zur Geschwindigkeit.** Die erste Fassung wirkte gehetzt. Ursache war nicht
die Stimme, sondern der Zusammenbau: Die Szenen waren genau so lang gemacht
wie ihr Sprechtext, wodurch die zwölf Pausen von je rund 1,7 Sekunden
verschwanden — zusammen etwa zwanzig Sekunden Luft. Das ist behoben;
`schnitt.py` leitet die Szenendauer jetzt als Sprechdauer plus folgende Pause
ab. Gemessen war die Aufnahme selbst nur 4 Prozent schneller als die
Vorgängerin. Speed also bei 1.00 lassen und erst heruntersetzen, wenn das
fertige Video immer noch zu schnell wirkt.

## Drei Regeln für den Text

**Eine `<break time="2.0s" />` ganz an den Anfang, vor den ersten Satz.**
Ohne sie schneidet ElevenLabs gelegentlich die ersten Wörter ab — bei uns ist
mehrfach «Ich helfe dir» verschwunden. Die Pause selbst kommt nicht ins Video:
Der Schnitt erkennt eine führende Stille und verwirft sie, der Vorlauf vor dem
ersten Wort entsteht ohnehin beim Mischen.

**Die `<break time="1.4s" />`-Marken zwischen den Segmenten sind Pflicht.** An ihnen wird
geschnitten. Nicht entfernen, nicht kürzen, keine zusätzlichen einfügen — der
Schnitt bricht ab, wenn er nicht genau zwölf lange Pausen findet.

**Keine Abkürzungen buchstabieren lassen.** «K-I» mit Bindestrich wurde als
Silbe gelesen und war unverständlich. Ausgeschrieben — «künstlicher
Intelligenz» — kann nichts schiefgehen.

## Ablauf

1. Text aus `lernvideo-teilnahme-sprechtexte-elevenlabs.txt` **in einem Stück**
   ins Feld kopieren
2. Einstellungen wie oben, erzeugen, als MP3 herunterladen
3. MP3 im Chat hochladen

Danach läuft automatisch: `schnitt.py` (Segmentgrenzen aus der Aufnahme,
Abbruch bei falscher Anzahl) → `rec.mjs` (Bildspur passend zur neuen Länge)
→ `mische.py` (Ton auf die Szenen legen, Pegel angleichen).

## Kosten

Rund 1700 Zeichen — das liegt im kostenlosen Kontingent von ElevenLabs.

## Wenn du lieber selbst sprichst

Geht genauso: die dreizehn Abschnitte am Stück einsprechen, dazwischen rund
zwei Sekunden Pause lassen, als MP3 oder WAV schicken. Eine ruhige Umgebung
und etwa zwanzig Zentimeter Abstand zum Mikrofon genügen — eine echte Stimme
aus dem Haus wirkt in einer internen Schulung ohnehin stärker als jede
synthetische.
