---
name: zahlendreher-serie
description: Baut deutsche TikTok-Storytelling-Serien im Pixar-3D-Stil für den Account @zahlendreher.tv – Figuren mit einer leuchtenden Zahl (Kontostand) auf der Stirn, Rollenstimmen (männlich/weiblich), mehrteilige Handlung mit Cliffhanger am Ende jedes Teils, gerendert im Code mit HyperFrames. Auch für Profilname, Profilbild, Bio und Videobeschreibungen. Verwenden, wenn ein neuer Teil, ein Drehbuch, eine Videobeschreibung oder Profil-Material für @zahlendreher.tv gebraucht wird.
---

# @zahlendreher.tv – Serien-Skill

Vorbild: @schubladendenker (Pixar-Lebensmittel-Figuren, „Alkzahl“ auf der Stirn).
Unser eigenes Format: **Jeder trägt seinen Kontostand auf der Stirn. Manche lügen.**

## 1. Account-Identität

| Feld | Inhalt |
|---|---|
| Profilname | `@zahlendreher.tv` (Anzeigename: **Zahlendreher**) |
| Profilbild | Leo Laugenbrezel, Nahaufnahme, verschmitzter Seitenblick, Stirn-Display zeigt rot **„0 €“**, warmes Bokeh-Abendlicht, Pixar-3D, Kopf mittig (Kreis-Crop!) |
| Bio | `Jeder trägt seinen Kontostand auf der Stirn. 💶` / `Manche lügen. 🤫` / `Neue Teile jeden Tag – folge für Teil 2 👇` |

## 2. Stil-Bibel (aus der Referenzanalyse)

- **Format:** 1080×1920, 30 fps, 55–75 s pro Teil, keine Untertitel (wie Vorbild), kein Intro, kein Logo.
- **Look:** Pixar/Disney-3D, warmes Golden-Hour- oder Abendlicht, Großstadt-Bokeh, glänzende Materialien, große ausdrucksstarke Augen.
- **Schnitt:** neues Bild alle **1,8–2,6 s** (≈ 25–32 Einstellungen). Wechsel Nahaufnahme ↔ Halbtotale ↔ Totale. Jedes Bild bekommt eine langsame Kamerafahrt (Push-in 4–8 % oder seitlicher Drift), harter Schnitt, keine Überblendungen.
- **Die Zahl:** LED-Display auf der Stirn, **im Code** gerendert (nie vom Bildmodell – Bildmodelle schreiben Zahlen falsch). Rot = wenig Geld (< 1.000 €), Grün = viel Geld. Format deutsch: `2.400.000 €`. Wechsel als Zähl-Animation (Rollen der Ziffern, 0,6–1,2 s) mit kurzem Flackern.
- **Sprache:** Umgangsdeutsch, kurze Sätze, Jugendsprache dosiert („Digger“, „Alter“, „ernsthaft jetzt?“). Gedanken einer Figur als Flüstern („Soll ich's ihr sagen?“).
- **Ton:** fast nur Dialog. Leise Musik (≈ −30 LUFS) und Geräusche auf sichtbaren Aktionen (Klick am Display, Gläserklirren, Restaurant-Atmo).

## 3. Erzählregeln (jeder Teil)

1. **Hook im ersten Satz** – die Prämisse in einem Atemzug, Gesicht + Zahl im ersten Frame (Frame 0 = Thumbnail).
2. **Eskalation** – die Lüge wird größer, jemand kommt ihr fast auf die Schliche.
3. **Twist-Spiegel** – die Gegenseite hat ebenfalls ein Geheimnis (wie im Vorbild: beide lügen).
4. **Offenes Ende** – der letzte Satz ist eine Frage, ein „Was?!“ oder eine Enthüllung **ohne Auflösung**. Letzte Einstellung: Nahaufnahme einer geschockten Reaktion oder der Zahl. Nie auflösen, was der nächste Teil erzählen soll.
5. Teil N beginnt genau mit der Szene, in der Teil N−1 aufgehört hat.

## 4. Figuren & Stimmen

Stimmen über Gemini-TTS (`GEMINI_API_KEY`), deutsche Texte, Regieanweisung im `style`, nie im gesprochenen Text. **Männliche Figur → männliche Stimme, weibliche Figur → weibliche Stimme.**

| Figur | Aussehen (Prompt-Kern) | Echte Zahl | Gemini-Stimme | Fallback (Piper, lokal) |
|---|---|---|---|---|
| **Leo Laugenbrezel** (Held) | Mann mit glänzendem Laugenbrezel-Kopf, Salzkörner, schwarzes Hemd, Uhr | 2.400.000 € (zeigt 0 €) | `Puck` – locker, verschmitzt | `de-thorsten-low` |
| **Mia** | junge Frau, Disney-Stil, braune Haare im Messy Bun, weiße Strickjacke, Jeans | zeigt 312 € (Geheimnis!) | `Leda` – jung, warm | `de-eva_k-x-low` |
| **Chantal** | blonde Frau, roter Minirock, Designer-Tasche, arrogant | 48 € (spielt reich) | `Zephyr` – hell, zickig | `de-kerstin-low` |
| **Henri Baguette** (Butler) | Baguette-Kopf, Frack, weiße Handschuhe, Handtuch über dem Arm | 1.250 € | `Charon` – ruhig, vornehm | `de-thorsten-low` (tiefer) |
| **Karl Kartoffel** (Kellner) | Kartoffel-Kopf, Weste, Fliege, Notizblock | 3 € | `Algenib` – rau, gutmütig | `de-thorsten-low` |

Neue Figur: zuerst hier eintragen (Lebensmittel-Kopf für Männer/Nebenfiguren, Disney-Frauen wie im Vorbild).

## 5. Bilder (Pixar-Stil)

Jede Einstellung = ein Bild, erzeugt mit dem neuesten Gemini-Bildmodell (`GET https://generativelanguage.googleapis.com/v1beta/models` → Modell mit Bildausgabe wählen). Für Figurenkonstanz die vorherigen Bilder derselben Figur als Referenzbild mitschicken.

Prompt-Vorlage:
```
Pixar-style 3D animated film still, vertical 9:16. <Figur-Beschreibung aus Tabelle>.
On the forehead a small black rectangular LED display panel, screen BLANK and dark (no digits).
<Aktion/Emotion>. <Ort>, warm cinematic evening light, city skyline bokeh, shallow depth of field.
<Einstellung: close-up / medium shot / wide shot>. No text, no letters, no watermark.
```

Nach dem Erzeugen: jedes Bild ansehen und Position, Größe und Drehung des Displays in die Shotliste eintragen (`display: {x, y, w, rot}` in px auf 1080×1920). Darauf setzt HyperFrames die Zahl.

## 6. Bauen mit HyperFrames

Vorher den HyperFrames-Skill lesen (`npx hyperframes skills update`, dann `/hyperframes`).

1. `npx hyperframes init folgen/teil-NN` – Hochformat 1080×1920.
2. `assets/shots/sNN.png` (Bilder), `assets/voice/*.wav` (Stimmen), Musik nach `assets/music/`.
3. Stimmen: `audio_request.json` mit `provider: "gemini"`, eine `line` pro Satz, `voice` je Figur, `lang: "de"`. Ausführen mit dem `audio.mjs` aus `/media-use` (`--only tts`). Die Dauer jeder Zeile bestimmt den Schnitt.
4. `index.html`: eine Sub-Composition pro Einstellung (Bild + Kamerafahrt + Stirn-Display), dazu die `<audio>`-Spuren der Sätze nacheinander (Lücke 0,15–0,3 s, bei Streit überlappend).
5. Stirn-Display als wiederverwendbare Komponente: schwarzer Rahmen, LED-Ziffern (Monospace, Glow per `text-shadow`), Farbe nach Betrag, Zähl-Animation über die GSAP-Timeline (kein `Math.random`, kein Timer).
6. `npx hyperframes check --json` → `npx hyperframes snapshot --review` → Vorschau → `npx hyperframes render`.

## 7. Videobeschreibung (pro Teil)

```
Teil <N> | <Spannungssatz mit der offenen Frage> 😳 Wie geht's weiter? 👇
#zahlendreher #storytime #serie #kivideo #pixar #fyp #fürdich #deutsch #teil<N>
```
Regeln: ≤ 150 Zeichen vor den Hashtags, die Frage des Cliffhangers anteasern, nie spoilern.

## 8. Folgen

Drehbücher liegen unter `episodes/teil-NN.md` (Shotliste mit Sprecher, Text, Stimmung, Bild-Prompt). Vor einem neuen Teil das vorherige Drehbuch lesen, damit Anschluss und Zahlen stimmen.
