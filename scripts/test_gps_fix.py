#!/usr/bin/env python3
"""
Test-Skript: GPS-Extraktion aus ADVERT-Paketen
Vergleicht alte Logik (Flag-abhaengig) mit neuer Logik (Smart-Detection)

Szenarien:
  A: GPS vorhanden + Flag gesetzt     (Idealfall)
  B: GPS vorhanden + Flag NICHT gesetzt (der Bug!)
  C: Kein GPS - bewusste Entscheidung
"""

import struct
import math

# ──────────────────────────────────────────────
# Hilfsfunktion: ADVERT-Payload zusammenbauen
# ──────────────────────────────────────────────

def build_advert_payload(name, lat=None, lon=None, role=2, gps_flag=False):
    """
    Baut eine simulierte ADVERT-Payload zusammen.
    role: 1=Chat, 2=Repeater, 3=Room, 4=Sensor
    """
    payload = bytes(32)                        # Public Key (32 Bytes)
    payload += struct.pack("<I", 1713650000)   # Timestamp (4 Bytes)
    payload += bytes(64)                       # Signatur (64 Bytes)

    # App Flags (1 Byte): Bit 0-3=Rolle, Bit 4=GPS, Bit 7=Name
    flags = role & 0x0F
    if gps_flag:
        flags |= (1 << 4)
    flags |= (1 << 7)                         # Name-Flag immer setzen
    payload += bytes([flags])

    # GPS-Daten (optional: 8 Bytes)
    if lat is not None and lon is not None:
        payload += struct.pack("<f", lat)      # Lat (4 Bytes)
        payload += struct.pack("<f", lon)      # Lon (4 Bytes)

    # Name (variable Laenge)
    payload += name.encode("utf-8")

    return payload


# ──────────────────────────────────────────────
# ALTE Logik: nur wenn GPS-Flag gesetzt
# ──────────────────────────────────────────────

def parse_old(payload):
    """Originaler Observer-Code: Prueft NUR das GPS-Flag."""
    result = {"lat": "", "lon": "", "name": ""}

    if len(payload) <= 100:
        return result

    fb = payload[100]
    has_gps = (fb >> 4) & 0x01                 # Bit 4 pruefen

    if has_gps and len(payload) >= 109:
        try:
            lat = struct.unpack("<f", payload[101:105])[0]
            lon = struct.unpack("<f", payload[105:109])[0]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                result["lat"] = round(lat, 6)
                result["lon"] = round(lon, 6)
        except:
            pass
        name_bytes = payload[109:]             # Name ab 109
    else:
        name_bytes = payload[101:]             # Name ab 101

    result["name"] = name_bytes.decode("utf-8", errors="replace").rstrip('\x00')
    return result


# ──────────────────────────────────────────────
# NEUE Logik: Smart-Detection (Dreifach-Check)
# ──────────────────────────────────────────────

def parse_new(payload):
    """Neue Logik: Versucht GPS zu lesen, validiert mit Dreifach-Check."""
    result = {"lat": "", "lon": "", "name": ""}

    if len(payload) <= 100:
        return result

    gps_found = False

    if len(payload) >= 109:
        try:
            lat_raw = struct.unpack("<f", payload[101:105])[0]
            lon_raw = struct.unpack("<f", payload[105:109])[0]

            # Check 1: Gueltige Koordinaten?
            coords_valid = (
                not math.isnan(lat_raw)
                and not math.isinf(lat_raw)
                and not math.isnan(lon_raw)
                and not math.isinf(lon_raw)
                and -90 <= lat_raw <= 90
                and -180 <= lon_raw <= 180
                and not (abs(lat_raw) < 0.01 and abs(lon_raw) < 0.01)
            )

            # Check 2: Binaere Bytes (nicht ASCII-Text)?
            gps_bytes = payload[101:109]
            has_binary = any(b < 0x20 or b > 0x7E for b in gps_bytes)

            if coords_valid and has_binary:
                result["lat"] = round(lat_raw, 6)
                result["lon"] = round(lon_raw, 6)
                gps_found = True
        except:
            pass

    # Name: Position haengt davon ab, ob GPS gefunden wurde
    if gps_found:
        name_bytes = payload[109:]
    else:
        name_bytes = payload[101:]

    result["name"] = name_bytes.decode("utf-8", errors="replace").rstrip('\x00')
    return result


# ══════════════════════════════════════════════
# TESTLAEUFE
# ══════════════════════════════════════════════

print("=" * 70)
print("  GPS-Extraktions-Test: ALTE vs. NEUE Logik")
print("=" * 70)

tests = [
    {
        "label": "A: GPS + Flag gesetzt (Idealfall)",
        "payload": build_advert_payload(
            name="Bantiger", lat=46.977, lon=7.528,
            role=2, gps_flag=True
        )
    },
    {
        "label": "B: GPS vorhanden, Flag NICHT gesetzt (der Bug!)",
        "payload": build_advert_payload(
            name="Bantiger", lat=46.977, lon=7.528,
            role=2, gps_flag=False
        )
    },
    {
        "label": "C: Kein GPS - bewusste Entscheidung",
        "payload": build_advert_payload(
            name="HB9BG Belp", lat=None, lon=None,
            role=2, gps_flag=False
        )
    },
]

for test in tests:
    payload = test["payload"]
    old = parse_old(payload)
    new = parse_new(payload)

    print(f"\n{'-' * 70}")
    print(f"  Szenario {test['label']}")
    print(f"  Payload-Laenge: {len(payload)} Bytes")
    print(f"  App Flags Byte: 0x{payload[100]:02X} (binaer: {payload[100]:08b})")
    print(f"{'-' * 70}")
    print(f"  {'':22s} {'ALTE Logik':>15s}  {'NEUE Logik':>15s}")
    print(f"  {'Name:':22s} {str(old['name']):>15s}  {str(new['name']):>15s}")
    print(f"  {'Latitude:':22s} {str(old['lat']):>15s}  {str(new['lat']):>15s}")
    print(f"  {'Longitude:':22s} {str(old['lon']):>15s}  {str(new['lon']):>15s}")

    # Bewertung
    if old['lat'] == new['lat'] and old['lon'] == new['lon'] and old['lat'] != "":
        print(f"  -> Beide finden GPS - korrekt!")
    elif new['lat'] != "" and old['lat'] == "":
        print(f"  -> BUG! Alte Logik verpasst GPS! Neue Logik findet es!")
    elif new['lat'] == "" and old['lat'] == "":
        print(f"  -> Korrekt: Kein GPS vorhanden")

print(f"\n{'=' * 70}")
print("  Test abgeschlossen!")
print("=" * 70)
