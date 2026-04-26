# 📖 Bedienungsanleitung – MeshCore Duty Cycle Dashboard

> Täglicher Betrieb, Überwachung und Auswertung des Dashboard-Systems.
> Ergänzung zur [README.md](README.md) (Installation & Konfiguration).

---

## Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Dashboard starten](#dashboard-starten)
3. [Die Karte verstehen](#die-karte-verstehen)
4. [Filter verwenden](#filter-verwenden)
5. [Routen anzeigen](#routen-anzeigen)
6. [CSV-Daten synchronisieren](#csv-daten-synchronisieren)
7. [API direkt abfragen](#api-direkt-abfragen)
8. [Häufige Probleme](#häufige-probleme)
9. [Nützliche Befehle](#nützliche-befehle)

## Überblick

Das Dashboard zeigt die Aktivität des MeshCore LoRa-Mesh-Netzwerks auf einer interaktiven Karte. Es liest die CSV-Dateien des Observers und visualisiert:

- **Node-Positionen** – Wo stehen die Mesh-Nodes? (aus ADVERT-Paketen)
- **Aktivität** – Welche Nodes waren aktiv? (Kreise: grösser = mehr Pakete)
- **Routen** – Welche Nodes kommunizieren miteinander? (blaue Linien)

Stell dir das Dashboard wie eine **Wetterkarte** vor: Statt Wolken und Regen siehst du Funk-Nodes und Datenpakete. 📡🗺️

---

## Dashboard starten

### Voraussetzung

CSV-Dateien müssen im `data/`-Ordner liegen. Der automatische Sync (cron) erledigt das normalerweise.

### Starten

    cd ~/Projects/meshcore-duty-cycle-dashboard
    source venv/bin/activate
    python3 -m app.main

### Im Browser öffnen

Auf einem beliebigen Gerät im selben Netzwerk:

    http://10.0.1.152:5000

### Stoppen

Im Terminal: `Ctrl+C` 

---

## Die Karte verstehen

### Node-Kreise

Jeder Kreis auf der Karte ist ein Mesh-Node mit bekannter GPS-Position.

| Eigenschaft | Bedeutung |
|-------------|-----------|
| Position | GPS-Koordinaten aus ADVERT-Paketen |
| Grösse | Mehr Pakete = grösserer Kreis |
| Farbe | Rot (Standard) |
| Tooltip | Name, Hash, Paketzahl – erscheint beim Drüberfahren mit der Maus |

**Wichtig:** Nur Nodes mit **eindeutigem Hash** (keine Kollision) und gültigen GPS-Koordinaten werden angezeigt.

### Routen-Linien

Blaue Linien zwischen zwei Nodes bedeuten: Diese Nodes haben miteinander kommuniziert.

| Eigenschaft | Bedeutung |
|-------------|-----------|
| Dicke | Mehr Pakete = dickere Linie |
| Transparenz | Mehr Pakete = kräftigere Farbe |
| Tooltip | Absender, Empfänger, Paketzahl |

---

## Filter verwenden

Oben auf der Karte findest du zwei Reihen von Buttons:

### Zeitfilter

| Button | Zeigt Pakete der letzten... |
|--------|----------------------------|
| 4h | 4 Stunden |
| 8h | 8 Stunden |
| 12h | 12 Stunden |
| 24h | 24 Stunden (Standard) |

### Pakettyp-Filter

| Button | Was wird angezeigt |
|--------|-------------------|
| ALL | Alle Pakettypen |
| ADVERT | Node-Anmeldungen (Name, GPS, Modus) |
| RESPONSE | Antworten auf Anfragen |
| GRP_TXT | Gruppennachrichten (verschlüsselt) |
| PATH | Routing-Informationen mit Hops |
| TRACE | Netzwerk-Diagnose |

**Tipp:** Kombination möglich! Z.B. "8h + RESPONSE" zeigt nur Antwort-Pakete der letzten 8 Stunden.

---

## Routen anzeigen

Rechts neben den Pakettyp-Buttons findest du den **Routen-Toggle**:

| Button | Wirkung |
|--------|---------|
| Ein | Blaue Linien zwischen Nodes sichtbar |
| Aus | Nur Node-Kreise, keine Linien |

Die Routen reagieren auf die aktiven Filter. Wenn du z.B. "8h + RESPONSE" einstellst, werden nur Routen aus RESPONSE-Paketen der letzten 8 Stunden angezeigt.

### Was ist eine Route?

Eine Route entsteht, wenn ein Paket einen **Absender** (source) und **Empfänger** (destination) hat, die beide eine bekannte GPS-Position besitzen. Der Observer zeichnet auf, wer mit wem kommuniziert hat.

---

## CSV-Daten synchronisieren

Das Dashboard liest CSV-Dateien aus dem `data/`-Ordner. Diese werden automatisch vom Observer (Pi Zero) geholt.

### Automatischer Sync

Ein Cron-Job auf dem Pi 4B holt alle 15 Minuten neue Daten:

    # Cron-Job anzeigen
    crontab -l

### Manueller Sync

    ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.sh

### Sync-Log prüfen

    tail -20 ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.log

### Pfade

| Was | Wo |
|-----|-----|
| CSV-Quelle (Pi Zero) | `/home/paul-rppi/meshcore-duty-cycle-observer/logs/` |
| CSV-Ziel (Pi 4B) | `/home/paul-rppi/Projects/meshcore-duty-cycle-dashboard/data/` |

### Welche Dateien sind da?

    ls -la ~/Projects/meshcore-duty-cycle-dashboard/data/

Jede Datei deckt einen Tag ab: `duty_cycle_2026-04-26.csv`

---

## API direkt abfragen

Das Dashboard bietet eine REST-API. Du kannst die Daten auch ohne Browser abrufen – z.B. mit `curl` im Terminal:

### Alle Node-Positionen

    curl http://localhost:5000/api/positions

### Aktivität der letzten 8 Stunden (nur RESPONSE)

    curl "http://localhost:5000/api/activity?hours=8&type=RESPONSE"

### Routen der letzten 24 Stunden

    curl "http://localhost:5000/api/routes?hours=24"

### Ausgabe im Browser

Du kannst die URLs auch direkt im Browser öffnen – du bekommst dann die Roh-Daten als JSON. Nützlich um schnell die Anzahl Nodes oder Routen zu prüfen:

    http://10.0.1.152:5000/api/positions
    http://10.0.1.152:5000/api/activity?hours=24
    http://10.0.1.152:5000/api/routes?hours=24

---

## Häufige Probleme

### Karte zeigt keine Nodes

1. **Sind CSV-Dateien vorhanden?**

        ls ~/Projects/meshcore-duty-cycle-dashboard/data/

2. **Sind die Daten aktuell genug für den Zeitfilter?**

    Bei "4h"-Filter werden nur Pakete der letzten 4 Stunden angezeigt. Wenn die neusten Daten älter sind, erscheint nichts.

3. **Manuell Daten holen:**

        ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.sh

### Routen werden nicht angezeigt

- Ist der **Toggle-Button auf "Ein"**?
- Haben die Nodes **GPS-Koordinaten**? (Nur ADVERT-Pakete liefern GPS)
- Sind **beide** Nodes (Absender + Empfänger) mit eindeutigem Hash?

### Browser zeigt alte Daten

Hard-Refresh im Browser:
- **Mac:** `Cmd+Shift+R`
- **Windows:** `Ctrl+Shift+R`

### Flask startet nicht

    # Port schon belegt?
    lsof -i :5000

    # Anderer Flask-Prozess läuft noch?
    pkill -f "python3 -m app.main"

### Sync funktioniert nicht

    # SSH-Verbindung testen
    ssh paul-rppi@10.0.1.156 "echo OK"

    # Sync-Log prüfen
    tail -20 ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.log

---

## Nützliche Befehle

### Dashboard

    # Starten
    cd ~/Projects/meshcore-duty-cycle-dashboard
    source venv/bin/activate
    python3 -m app.main

    # Stoppen
    Ctrl+C

### CSV-Dateien

    # Alle CSV-Dateien anzeigen
    ls -la ~/Projects/meshcore-duty-cycle-dashboard/data/

    # Heutige Pakete zählen
    wc -l ~/Projects/meshcore-duty-cycle-dashboard/data/duty_cycle_$(date +%Y-%m-%d).csv

    # Pakete nach Typ zählen
    cut -d';' -f4 ~/Projects/meshcore-duty-cycle-dashboard/data/duty_cycle_$(date +%Y-%m-%d).csv | sort | uniq -c | sort -rn

### Sync

    # Manuell Daten holen
    ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.sh

    # Cron-Job prüfen
    crontab -l

    # Sync-Log anschauen
    tail -20 ~/Projects/meshcore-duty-cycle-dashboard/fetch_csv.log

---

## Weiterführende Dokumentation

| Dokument | Beschreibung |
|----------|-------------|
| [README.md](README.md) | Installation, Konfiguration, Architektur |
| [Observer-Repo](https://github.com/Paul-3400/meshcore-duty-cycle-observer) | Der Datenlieferant für dieses Dashboard |
| [MeshCore Docs](https://docs.meshcore.io/) | Offizielle MeshCore-Dokumentation |

---

*Erstellt am 26.04.2026 – Paul's ElektroTech-Lab 🏠 | Brain Gym Edition 🧠💪*
