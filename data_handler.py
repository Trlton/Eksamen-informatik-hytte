import json
import os
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hytte_data.json")

def sørg_data_fil():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        start_data = {
            "registreringer": [],
            "proviant_køb": [],
            "betalinger": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(start_data, f, indent=4, ensure_ascii=False)

def læs_data():
    sørg_data_fil()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def skriv_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def tilføj_registrering(navn, mobil, ankomst, afrejse, antal_personer):
    data = læs_data()
    ny_registrering = {
        "id": len(data["registreringer"]) + 1,
        "navn": navn,
        "mobil": mobil,
        "ankomst": ankomst,
        "afrejse": afrejse,
        "antal_personer": antal_personer,
        "oprettet": datetime.now().isoformat()
    }
    data["registreringer"].append(ny_registrering)
    skriv_data(data)
    return ny_registrering

def tilføj_proviant_køb(varer, total):
    data = læs_data()
    nyt_køb = {
        "id": len(data["proviant_køb"]) + 1,
        "varer": varer,
        "total": total,
        "oprettet": datetime.now().isoformat()
    }
    data["proviant_køb"].append(nyt_køb)
    skriv_data(data)
    return nyt_køb

def tilføj_betaling(type_betaling, beløb, status):
    data = læs_data()
    ny_betaling = {
        "id": len(data["betalinger"]) + 1,
        "type": type_betaling,
        "beløb": beløb,
        "status": status,
        "oprettet": datetime.now().isoformat()
    }
    data["betalinger"].append(ny_betaling)
    skriv_data(data)
    return ny_betaling

def hent_totaler():
    data = læs_data()

    samlet_proviant = sum(køb["total"] for køb in data["proviant_køb"])
    samlet_betaling = sum(b["beløb"] for b in data["betalinger"])

    return {
        "antal_registreringer": len(data["registreringer"]),
        "antal_proviant_køb": len(data["proviant_køb"]),
        "proviant_omsætning": samlet_proviant,
        "samlet_betaling": samlet_betaling
    }