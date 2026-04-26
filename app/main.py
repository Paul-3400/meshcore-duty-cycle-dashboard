"""
MeshCore Duty Cycle Dashboard – Flask App
Webserver mit API und Kartenansicht.
"""

from flask import Flask, render_template, jsonify
from app.config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from app.data_loader import get_node_positions, get_activity, get_routes

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)


@app.route("/")
def index():
    """Startseite mit Leaflet-Karte."""
    return render_template("index.html")


@app.route("/api/nodes")
def api_nodes():
    """API: Liefert Node-Positionen als JSON."""
    nodes = get_node_positions()
    return jsonify({
        "count": len(nodes),
        "nodes": nodes
    })


@app.route("/api/activity")
def api_activity():
    """API: Liefert Aktivitaetsdaten mit Zeit- und Typfilter."""
    from flask import request
    hours = int(request.args.get('hours', 24))
    packet_type = request.args.get('type', 'ALL')
    data = get_activity(hours=hours, packet_type=packet_type)
    return jsonify({
        "count": len(data),
        "hours": hours,
        "type": packet_type,
        "activity": data
    })


@app.route("/api/routes")
def api_routes():
    """API: Liefert Routen zwischen Nodes als JSON."""
    from flask import request
    hours = int(request.args.get("hours", 24))
    packet_type = request.args.get("type", "ALL")
    routes = get_routes(hours=hours, packet_type=packet_type)
    return jsonify({
        "count": len(routes),
        "hours": hours,
        "type": packet_type,
        "routes": routes
    })


def main():
    """Startet den Flask-Server."""
    print("=" * 50)
    print("  MeshCore Duty Cycle Dashboard")
    print(f"  http://{FLASK_HOST}:{FLASK_PORT}")
    print("=" * 50)
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )


if __name__ == "__main__":
    main()
