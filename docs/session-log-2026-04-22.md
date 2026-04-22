# 📓 Session Log – 22. April 2026

## Was haben wir heute gemacht?

### 1. GitHub-Repository erstellt
- Name: `meshcore-duty-cycle-dashboard`
- URL: https://github.com/Paul-3400/meshcore-duty-cycle-dashboard
- Public, MIT-Lizenz, Python .gitignore

### 2. Repo auf den Mac geklont
- Git installiert (Xcode-Lizenz akzeptiert)
- Projekt-Ordner: `~/Projects/meshcore-duty-cycle-dashboard`
- Gelernt: `git clone`, `git add`, `git commit`, `git push`
- Personal Access Token (PAT) für GitHub erstellt

### 3. Ordnerstruktur angelegt
app/ → Python Backend (Flask)
templates/ → HTML-Seiten
static/ → CSS, JS, Bilder
css/
js/
img/
scripts/ → Hilfsskripte (z.B. CSV holen)
docs/ → Dokumentation
data/ → CSV-Daten (lokal, nicht auf GitHub)


### 4. Raspi 4B vorbereitet
- OS: Debian 13 (Trixie)
- Python 3.13.5, pip 25.1.1, Git 2.47.3 – alles aktuell!
- Repo geklont nach `~/Projects/meshcore-duty-cycle-dashboard`
- Virtuelle Umgebung erstellt: `python3 -m venv venv`
- Flask 3.1.3 und Pandas 2.2.3 installiert

### 5. CSV-Daten analysiert
- Testdatei: `duty_cycle_2026-04-21.csv` (via USB-Stick)
- 22'503 Datensätze, 25 Spalten, Trennzeichen: Semikolon
- 572 eindeutige Knoten im Netz!
- Pakettypen: RESPONSE (4967), TXT_MSG (4310), REQ (3607), ADVERT (2883), ...
- **Erkenntnis:** lat/lon sind in den ADVERTs leer (GPS-Flag nicht gesetzt)
- **Lösung:** Eigene Standort-Datei `nodes.csv` mit bekannten Koordinaten

### 6. Standort-Datei nodes.csv geplant
- Wird in Numbers auf dem Mac erstellt
- Spalten: node_name, lat, lon, description
- Koordinaten via map.geo.admin.ch
- Start mit eigenen 3 Knoten + 10-15 bekannte

## Offene Aufgaben (nächste Session)
- [ ] nodes.csv in Numbers erstellen und mit Koordinaten füllen
- [ ] nodes.csv auf den Raspi bringen
- [ ] Python Data-Loader schreiben (Schritt 4)
- [ ] Flask-Webserver aufsetzen (Schritt 5)
- [ ] Leaflet.js Karte mit Knotenpositionen (Schritt 6)

## Architektur-Überblick
Raspi Zero W (Observer) → USB/WLAN → Raspi 4B (Flask+Pandas) → Browser (Leaflet-Karte)


## Gelernte Befehle
| Befehl | Bedeutung |
|--------|-----------|
| sudo | Super User DO – Adminrechte |
| mkdir -p | Ordner anlegen |
| cd | In Ordner wechseln |
| git clone | Repo kopieren |
| git add . | Alle Änderungen einpacken |
| git commit -m | Schnappschuss mit Beschreibung |
| git push | An GitHub senden |
| touch | Leere Datei erstellen |
| head -3 | Erste 3 Zeilen anzeigen |
| wc -l | Zeilen zählen |
| grep -c | Treffer zählen |
| lsblk | Speichergeräte anzeigen |
| sudo mount/umount | USB-Stick ein-/auskoppeln |
| source venv/bin/activate | Virtuelle Python-Umgebung starten |
