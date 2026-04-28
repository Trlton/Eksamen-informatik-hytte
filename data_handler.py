import json
import os
import random
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hytte_data.json")

def sørg_data_fil():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        start_data = {
            "registreringer": [],
            "proviant_køb": [],
            "betalinger": [],
            "venter_på_sending": []
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
    data["venter_på_sending"].append({
        "type": "registrering",
        "data": ny_registrering
    })
    skriv_data(data)
    return ny_registrering

def tilføj_proviant_køb(vare, total):
    data = læs_data()
    nyt_køb = {
        "id": len(data["proviant_køb"]) + 1,
        "køb_info": vare,
        "total": total,
        "oprettet": datetime.now().isoformat()
    }
    data["proviant_køb"].append(nyt_køb)
    data["venter_på_sending"].append({
        "type": "proviant_køb",
        "data": nyt_køb
    })
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
    data["venter_på_sending"].append({
        "type": "betaling",
        "data": ny_betaling
    })
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

internet_avaliable = False

def simuler_internetstatus():
    global internet_avaliable
    internet_avaliable = random.choice([True, False])
    print("Wifi:", "ONLINE" if internet_avaliable else "OFFLINE")

def send_ventende_data():
    data = læs_data()
    if not internet_avaliable:
        print("Wifi offline - sender når forbindelse genoprettes...")
        return
    for item in data["venter_på_sending"]:
        print("sender til ejer:", item)
    data["venter_på_sending"] = []
    skriv_data(data)

    return "Alt data sent"

