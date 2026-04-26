"""
MeshCore Duty Cycle Dashboard – Data Loader
Liest CSV-Dateien ein und bereitet Daten fuer die Karte auf.
"""

import os
import glob
import pandas as pd
from app.config import DATA_DIR, CSV_SEPARATOR


def load_all_csv():
    """
    Liest alle duty_cycle_*.csv Dateien aus dem data-Verzeichnis.
    Gibt einen grossen DataFrame zurueck.
    """
    pattern = os.path.join(DATA_DIR, "duty_cycle_*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"[WARN] Keine CSV-Dateien gefunden in: {DATA_DIR}")
        return pd.DataFrame()

    frames = []
    for f in files:
        try:
            df = pd.read_csv(f, sep=CSV_SEPARATOR, low_memory=False)
            frames.append(df)
            print(f"[OK] {os.path.basename(f)}: {len(df)} Zeilen")
        except Exception as e:
            print(f"[ERR] {os.path.basename(f)}: {e}")

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def get_node_positions():
    """
    Liefert die letzte bekannte Position jedes Nodes.
    Filtert nur ADVERT-Pakete mit gueltigen GPS-Daten.
    Gibt eine Liste von Dicts zurueck (JSON-ready).
    """
    df = load_all_csv()

    if df.empty:
        return []

    # Nur ADVERT-Pakete mit GPS-Koordinaten
    mask = (
        (df["packet_type"] == "ADVERT")
        & (df["lat"].notna())
        & (df["lon"].notna())
        & (df["lat"] != "")
        & (df["lon"] != "")
    )
    adverts = df[mask].copy()

    if adverts.empty:
        print("[WARN] Keine ADVERT-Pakete mit GPS gefunden")
        return []

    # Koordinaten als Zahlen sicherstellen
    adverts["lat"] = pd.to_numeric(adverts["lat"], errors="coerce")
    adverts["lon"] = pd.to_numeric(adverts["lon"], errors="coerce")
    adverts = adverts.dropna(subset=["lat", "lon"])

    # Timestamp sortieren, letzten Eintrag pro Node nehmen
    adverts["timestamp"] = pd.to_datetime(adverts["timestamp"])
    adverts = adverts.sort_values("timestamp")

    # Gruppieren nach node_key (eindeutig pro Node)
    latest = adverts.groupby("node_key").last().reset_index()

    # JSON-freundliches Format
    nodes = []
    for _, row in latest.iterrows():
        nodes.append({
            "node_key":    row.get("node_key", ""),
            "name":        row.get("source_name", "Unbekannt"),
            "hash":        row.get("source_hash", ""),
            "lat":         round(row["lat"], 6),
            "lon":         round(row["lon"], 6),
            "mode":        row.get("node_mode", ""),
            "rssi":        row.get("rssi", ""),
            "snr":         row.get("snr", ""),
            "hops":        row.get("hops", ""),
            "last_seen":   str(row.get("timestamp", "")),
            "dc_pct":      row.get("window_dc_pct", ""),
        })

    print(f"[OK] {len(nodes)} Nodes mit GPS-Position gefunden")
    return nodes

from datetime import datetime, timedelta
from collections import Counter


def build_position_lookup():
    """Telefonbuch: Node-Hash -> letzte bekannte Position."""
    df = load_all_csv()
    gps = df[df['lat'].notna() & df['lon'].notna()]

    lookup = {}
    for _, row in gps.iterrows():
        sh = str(row.get('source_hash', '')).strip()
        if sh and sh != 'nan':
            lookup[sh] = {
                'lat': float(row['lat']),
                'lon': float(row['lon']),
                'name': str(row.get('source_name', 'Unbekannt'))
            }
    return lookup

from datetime import datetime, timedelta
from collections import Counter


def build_position_lookup():
    """Telefonbuch: Node-Hash -> letzte bekannte Position."""
    df = load_all_csv()
    gps = df[df['lat'].notna() & df['lon'].notna()]

    lookup = {}
    for _, row in gps.iterrows():
        sh = str(row.get('source_hash', '')).strip()
        if sh and sh != 'nan':
            lookup[sh] = {
                'lat': float(row['lat']),
                'lon': float(row['lon']),
                'name': str(row.get('source_name', 'Unbekannt'))
            }
    return lookup


def get_activity(hours=24, packet_type=None):
    """Aktivitätsdaten: Wo wurden wie viele Pakete empfangen?"""
    df = load_all_csv()
    lookup = build_position_lookup()

    # Zeitfilter
    now = datetime.now()
    cutoff = now - timedelta(hours=hours)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[df['timestamp'] >= cutoff]

    # Pakettyp-Filter
    if packet_type and packet_type != 'ALL':
        df = df[df['packet_type'] == packet_type]

    # Pakete zaehlen pro Source-Position
    activity = Counter()
    names = {}
    for _, row in df.iterrows():
        sh = str(row.get('source_hash', '')).strip()
        if sh in lookup:
            pos = lookup[sh]
            key = (pos['lat'], pos['lon'])
            activity[key] += 1
            names[key] = pos['name']

    # Ergebnis aufbereiten
    result = []
    max_count = max(activity.values()) if activity else 1
    for (lat, lon), count in activity.items():
        result.append({
            'lat': lat,
            'lon': lon,
            'name': names.get((lat, lon), '?'),
            'count': count,
            'intensity': round(count / max_count, 2)
        })

    return result


def get_routes(hours=24, packet_type=None):
    df = load_all_csv()
    lookup = build_position_lookup()
    if df.empty or not lookup:
        return []
    now = datetime.now()
    cutoff = now - timedelta(hours=hours)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[df['timestamp'] >= cutoff]
    if packet_type and packet_type != 'ALL':
        df = df[df['packet_type'] == packet_type]
    mask = (df['source_collision'] == 1) & (df['dest_collision'] == 1)
    df = df[mask]
    df = df[
        df['source_hash'].astype(str).str.strip().isin(lookup.keys())
        & df['dest_hash'].astype(str).str.strip().isin(lookup.keys())
    ]
    if df.empty:
        return []
    route_counts = Counter()
    route_names = {}
    for _, row in df.iterrows():
        sh = str(row.get('source_hash', '')).strip()
        dh = str(row.get('dest_hash', '')).strip()
        if sh in lookup and dh in lookup:
            if sh == dh:
                continue
            src = lookup[sh]
            dst = lookup[dh]
            key = (src['lat'], src['lon'], dst['lat'], dst['lon'])
            route_counts[key] += 1
            route_names[key] = (src['name'], dst['name'])
    if not route_counts:
        return []
    max_count = max(route_counts.values())
    result = []
    for (slat, slon, dlat, dlon), count in route_counts.items():
        src_name, dst_name = route_names.get((slat, slon, dlat, dlon), ('?', '?'))
        result.append({
            'from_lat': slat, 'from_lon': slon,
            'to_lat': dlat, 'to_lon': dlon,
            'from_name': src_name, 'to_name': dst_name,
            'count': count,
            'intensity': round(count / max_count, 2)
        })
    return result
