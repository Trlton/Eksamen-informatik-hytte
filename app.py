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
    hent_totaler, send_ventende_data
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

    gemt_køb = tilføj_proviant_køb(køb_data, varer, total)
    gemt_betaling = tilføj_betaling(
        type_betaling=betaling.get("type", "kort"),
        beløb=total,
        status=betaling.get("status", "gennemført"),
        kunde_id=gemt_køb["kunde_id"]
    )

    return jsonify({
        "message": "Køb gemt lokalt og sat i kø til sending",
        "køb": gemt_køb,
        "betaling": gemt_betaling
    }), 200

@app.route("/api/registrering", methods=["POST"])
def gem_registrering():
    data = request.get_json()

    registrering = tilføj_registrering(
        navn=data.get("navn", ""),
        email=data.get("email", ""),
        mobil=data.get("mobil", ""),
        ankomst=data.get("ankomst"),
        afrejse=data.get("afrejse"),
        antal_personer=data.get("antal_personer")
    )

    return jsonify({
        "message": "Registrering gemt lokalt, og sat i kø til sendelse",
        "registrering": registrering
    }), 200

@app.route("/api/totaler", methods=["GET"])
def totaler():
    return jsonify(hent_totaler())

def sync_loop():
    while True:
        wait_time = random.randint(20,60)
        time.sleep(wait_time)

        data_handler.simuler_internetstatus()
        data_handler.send_ventende_data()

if __name__ == "__main__":
    sørg_data_fil()
    threading.Thread(target=sync_loop, daemon=True).start()

    import webbrowser
    webbrowser.open("http://localhost:5000")
    app.run(debug=True, use_reloader=False)
