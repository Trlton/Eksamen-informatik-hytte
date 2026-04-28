from flask import Flask, send_from_directory, request, jsonify
import time
import random
import threading

import data_handler
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

def sync_loop():
    while True:
        wait_time = random.randint(20,60)
        time.sleep(wait_time)
        data_handler.simuler_internetstatus()
        data_handler.send_ventende_data()

if __name__ == "__main__":
    threading.Thread(target=sync_loop, daemon=True).start()
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
    app.run(debug=True, use_reloader=False)
