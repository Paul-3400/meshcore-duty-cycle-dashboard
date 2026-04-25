"""
MeshCore Duty Cycle Dashboard – Konfiguration
Zentrale Einstellungen für die Flask-App.
"""

import os

# Basisverzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV-Datenverzeichnis
DATA_DIR = os.path.join(BASE_DIR, "data")

# CSV-Trennzeichen
CSV_SEPARATOR = ";"

# Flask-Einstellungen
FLASK_HOST = "0.0.0.0"   # Erreichbar von allen Geräten im Netzwerk
FLASK_PORT = 5000
FLASK_DEBUG = True        # Später auf False setzen!

# Karten-Zentrum (Schweiz)
MAP_CENTER_LAT = 46.8
MAP_CENTER_LON = 8.2
MAP_ZOOM = 8
