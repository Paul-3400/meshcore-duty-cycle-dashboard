#!/bin/bash
# Holt CSV-Dateien vom Observer (Pi Zero) zum Dashboard (Pi 4B)
# Quelle: RpPi2W-002 (10.0.1.156)
# Ziel:   lokaler data/-Ordner

SRC="paul-rppi@10.0.1.156:/home/paul-rppi/meshcore-duty-cycle-observer/logs/"
DST="/home/paul-rppi/Projects/meshcore-duty-cycle-dashboard/data/"

echo "$(date): Starte CSV-Sync von Pi Zero..."
rsync -avz --include='duty_cycle_*.csv' --exclude='*' "$SRC" "$DST"
echo "$(date): Sync fertig."
