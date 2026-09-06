#!/usr/bin/env python3
"""Schneidet die ElevenLabs-Aufnahme in die 13 Segmente, legt sie an die
tatsaechlichen Szenenanfaenge der Bildaufnahme und mischt beides zum Video.

Der Ton wird NICHT gedehnt oder gestaucht — jedes Segment beginnt genau dort,
wo seine Szene im Bild beginnt. Laeuft eine Bildszene laenger als ihr Ton,
steht das Bild am Ende still; das ist gewollt und besser als Versatz.
"""
import json, pathlib, subprocess, sys, shutil

HIER = pathlib.Path(__file__).parent
MP3  = pathlib.Path(sys.argv[1])
AUF  = json.loads((HIER/'aufnahme.json').read_text())
VORLAUF = 2.0          # muss mit schnitt.py uebereinstimmen
BAU  = HIER/'bau'
if BAU.exists(): shutil.rmtree(BAU)
BAU.mkdir()

def lauf(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(' '.join(str(c) for c in cmd)); print(r.stderr[-1500:]); sys.exit(1)
    return r

# ---------- 1. Bildspur aus den Einzelbildern mit echten Standzeiten ----------
bilder = AUF['bilder']
gesamt = AUF['gesamt']
zeilen = []
for i, b in enumerate(bilder):
    bis = bilder[i+1]['t']/1000 if i+1 < len(bilder) else gesamt
    dauer = max(bis - b['t']/1000, 0.02)
    zeilen.append(f"file '{HIER/'frames'/b['datei']}'")
    zeilen.append(f"duration {dauer:.4f}")
zeilen.append(f"file '{HIER/'frames'/bilder[-1]['datei']}'")   # letztes Bild noch einmal
(BAU/'bilder.txt').write_text('\n'.join(zeilen)+'\n')

print(f"Bildspur: {len(bilder)} Bilder, {gesamt:.2f}s")
lauf(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(BAU/'bilder.txt'),
      '-vf','fps=25,format=yuv420p','-c:v','libx264','-preset','medium','-crf','20',
      str(BAU/'bild.mp4')])

# ---------- 2. Tonspur: je Segment an seinen Szenenanfang ----------
szenen = AUF['szenen']
teile, filt = [], []
for i, s in enumerate(szenen):
    von, bis = s['ton_von'], s['ton_bis']
    # Rand wie bisher: vorne etwas frueher, hinten etwas spaeter
    a = max(von-0.15, 0); b = bis+0.25
    ziel = BAU/f"seg{i:02d}.wav"
    lauf(['ffmpeg','-v','error','-y','-ss',f"{a:.3f}",'-to',f"{b:.3f}",'-i',str(MP3),
          '-ac','1','-ar','48000',str(ziel)])
    teile.append(ziel)
    # Der Vorlauf steckt in Szene 1; alle uebrigen Segmente sitzen exakt auf
    # ihrem Szenenanfang, die Pausen dazwischen kommen aus der Szenendauer.
    verzug = int((s['start'] + (VORLAUF if i == 0 else 0))*1000)
    filt.append(f"[{i}:a]adelay={verzug}|{verzug}[a{i}]")

ein = []
for t in teile: ein += ['-i', str(t)]
mix = ';'.join(filt) + ';' + ''.join(f"[a{i}]" for i in range(len(teile))) + \
      f"amix=inputs={len(teile)}:normalize=0:dropout_transition=0[m];" \
      f"[m]apad,atrim=0:{gesamt:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[out]"
lauf(['ffmpeg','-v','error','-y'] + ein + ['-filter_complex',mix,'-map','[out]',
      '-ac','1','-ar','48000',str(BAU/'ton.wav')])
print(f"Tonspur: {len(teile)} Segmente gemischt")

# ---------- 3. Zusammenlegen ----------
ZIEL = HIER/'lernvideo-teilnahme.mp4'
lauf(['ffmpeg','-v','error','-y','-i',str(BAU/'bild.mp4'),'-i',str(BAU/'ton.wav'),
      '-c:v','copy','-c:a','aac','-b:a','128k','-shortest',str(ZIEL)])
print(f"fertig: {ZIEL}  ({ZIEL.stat().st_size/1e6:.2f} MB)")
