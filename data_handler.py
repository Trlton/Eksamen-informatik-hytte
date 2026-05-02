import json
import os
import random
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hytte_data.json")

internet_avaliable = False

def sørg_data_fil():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        start_data = {
            "kunder": [],
            "registreringer": [],
            "proviant_køb": [],
            "betalinger": [],
            "venter_på_sending": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(start_data, f, indent=4, ensure_ascii=False)
    else:
        # Sikrer at gamle JSON-filer får de nye felter
        data = læs_data_raw()

        data.setdefault("kunder", [])
        data.setdefault("registreringer", [])
        data.setdefault("proviant_køb", [])
        data.setdefault("betalinger", [])
        data.setdefault("venter_på_sending", [])

        skriv_data(data)

def læs_data_raw():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def læs_data():
    sørg_data_fil()
    return læs_data_raw()

def skriv_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def nyt_ID(liste):
    if not liste:
        return 1
    return max(item["id"] for item in liste)+1

def normaliser_tekst(tekst):
    return str(tekst).strip().lower()


def normaliser_mobil(mobil):
    return str(mobil).replace(" ", "").strip()


def find_eller_opret_kunde(data, navn="", mobil="", email=""):
    navn_normaliseret = normaliser_tekst(navn)
    mobil_normaliseret = normaliser_mobil(mobil)
    email_normaliseret = normaliser_tekst(email)

    for kunde in data["kunder"]:
        kunde_email = normaliser_tekst(kunde.get("email", ""))
        kunde_mobil = normaliser_mobil(kunde.get("mobil", ""))
        kunde_navn = normaliser_tekst(kunde.get("navn", ""))

        if email_normaliseret and kunde_email == email_normaliseret:
            return kunde

        if mobil_normaliseret and kunde_mobil == mobil_normaliseret:
            return kunde

        if navn_normaliseret and kunde_navn == navn_normaliseret:
            return kunde

    ny_kunde = {
        "id": nyt_ID(data["kunder"]),
        "navn": navn,
        "mobil": mobil,
        "email": email,
        "oprettet": datetime.now().isoformat()
    }

    data["kunder"].append(ny_kunde)
    return ny_kunde


def tilføj_til_sendekø(data, type_navn, id):
    data["venter_på_sending"].append({
        "type": type_navn,
        "id": id
    })


def tilføj_registrering(navn, mobil, email, ankomst, afrejse, antal_personer):
    data = læs_data()

    kunde = find_eller_opret_kunde(data, navn, mobil, email)

    ny_registrering = {
        "id": nyt_ID(data["registreringer"]),
        "kunde_id": kunde["id"],
        "ankomst": ankomst,
        "afrejse": afrejse,
        "antal_personer": antal_personer,
        "oprettet": datetime.now().isoformat(),
        "sendt_til_ejer": False
    }

    data["registreringer"].append(ny_registrering)

    tilføj_til_sendekø(data, "registrering", ny_registrering["id"])

    skriv_data(data)
    return ny_registrering


def tilføj_proviant_køb(kunde_data, varer, total):
    data = læs_data()

    kunde = find_eller_opret_kunde(
        data,
        navn=kunde_data.get("navn", ""),
        mobil=kunde_data.get("mobil", ""),
        email=kunde_data.get("email", "")
    )

    nyt_køb = {
        "id": nyt_ID(data["proviant_køb"]),
        "kunde_id": kunde["id"],
        "varer": varer,
        "total": total,
        "oprettet": datetime.now().isoformat(),
        "sendt_til_ejer": False
    }

    data["proviant_køb"].append(nyt_køb)

    tilføj_til_sendekø(data, "proviant_køb", nyt_køb["id"])

    skriv_data(data)
    return nyt_køb


def tilføj_betaling(type_betaling, beløb, status, kunde_id=None):
    data = læs_data()

    ny_betaling = {
        "id": nyt_ID(data["betalinger"]),
        "kunde_id": kunde_id,
        "type": type_betaling,
        "beløb": beløb,
        "status": status,
        "oprettet": datetime.now().isoformat(),
        "sendt_til_ejer": False
    }

    data["betalinger"].append(ny_betaling)

    tilføj_til_sendekø(data, "betaling", ny_betaling["id"])

    skriv_data(data)
    return ny_betaling


def hent_element(data, type_navn, id):
    if type_navn == "registrering":
        liste = data["registreringer"]
    elif type_navn == "proviant_køb":
        liste = data["proviant_køb"]
    elif type_navn == "betaling":
        liste = data["betalinger"]
    else:
        return None

    for item in liste:
        if item["id"] == id:
            return item

    return None


def marker_som_sendt(data, type_navn, id):
    item = hent_element(data, type_navn, id)

    if item:
        item["sendt_til_ejer"] = True


def hent_totaler():
    data = læs_data()

    samlet_proviant = sum(køb["total"] for køb in data["proviant_køb"])
    samlet_betaling = sum(b["beløb"] for b in data["betalinger"])

    return {
        "antal_kunder": len(data["kunder"]),
        "antal_registreringer": len(data["registreringer"]),
        "antal_proviant_køb": len(data["proviant_køb"]),
        "proviant_omsætning": samlet_proviant,
        "samlet_betaling": samlet_betaling,
        "venter_på_sending": len(data["venter_på_sending"])
    }


def simuler_internetstatus():
    global internet_available

    internet_available = random.choice([True, False])

    print("Wifi:", "ONLINE" if internet_available else "OFFLINE")


def send_ventende_data():
    data = læs_data()

    if not internet_available:
        print("Wifi offline - data bliver liggende i kø.")
        return "Offline"

    if not data["venter_på_sending"]:
        print("Ingen ventende data at sende.")
        return "Ingen data"

    for kø_item in data["venter_på_sending"]:
        type_navn = kø_item["type"]
        id = kø_item["id"]

        item = hent_element(data, type_navn, id)

        if item:
            print("Sender til ejer:", type_navn, item)
            marker_som_sendt(data, type_navn, id)

    data["venter_på_sending"] = []

    skriv_data(data)

    print("Alt ventende data er sendt.")
    return "Alt data sendt"