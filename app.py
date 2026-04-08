from flask import Flask, send_from_directory, request, jsonify
from data_handler import (
    sørg_data_fil,
    tilføj_proviant_køb,
    tilføj_betaling,
    tilføj_registrering,
    hent_totaler
)

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("UI", "home.html")

@app.route("/<path:htmlFil>")
def static_files(htmlFil):
    return send_from_directory("UI", htmlFil)

@app.route("/api/fuldfor_proviant_køb", methods=["POST"])
def fuldfor_proviant_køb():
    data = request.get_json()

    varer = data.get("varer", [])
    total = data.get("total", 0)
    betalings_type = data.get("betalings_type", "ukendt")
    status = data.get("status", "gennemført")

    if not varer:
        return jsonify({"message": "Ingen varer modtaget"}), 400

    if total <= 0:
        return jsonify({"message": "Total skal være større end 0"}), 400

    køb = tilføj_proviant_køb(varer, total)
    betaling = tilføj_betaling(betalings_type, total, status)

    return jsonify({
        "message": "Køb og betaling gemt",
        "køb": køb,
        "betaling": betaling
    }), 200

@app.route("/api/registrering", methods=["POST"])
def gem_registrering():
    data = request.get_json()

    registrering = tilføj_registrering(
        navn=data["navn"],
        mobil=data["mobil"],
        ankomst=data["ankomst"],
        afrejse=data["afrejse"],
        antal_personer=data["antal_personer"]
    )

    return jsonify({
        "message": "Registrering gemt",
        "registrering": registrering
    }), 200

@app.route("/api/totaler", methods=["GET"])
def totaler():
    return jsonify(hent_totaler())

if __name__ == "__main__":
    sørg_data_fil()
    import webbrowser
    webbrowser.open("http://localhost:5000")
    app.run(debug=True)