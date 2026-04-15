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

#skriv kode-forklaring af json-kode/gemmer senere
@app.route("/api/proviant/betal", methods=["POST"])
def gem_proviant_betaling():
    data = request.get_json()

    varer = data.get("varer", [])
    total = data.get("total", 0)
    kunde = data.get("kunde", {})
    betaling = data.get("betaling", {})

    if not varer:
        return jsonify({"message": "Ingen varer modtaget"}), 400

    if total <= 0:
        return jsonify({"message": "Total skal være større end 0"}), 400

    køb_data = {
        "kunde": kunde,
        "varer": varer
    }

    gemt_køb = tilføj_proviant_køb(køb_data, total)
    gemt_betaling = tilføj_betaling(
        betaling.get("type", "kort"),
        total,
        betaling.get("status", "gennemført")
    )

    return jsonify({
        "message": "køb gemt",
        "køb": gemt_køb,
        "betaling": gemt_betaling
    }), 200


if __name__ == "__main__":
    sørg_data_fil()
    import webbrowser

    webbrowser.open("http://localhost:5000")
    app.run(debug=True)

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