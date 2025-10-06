#!/usr/bin/env python3
"""Daemon na sťahovanie dát pre QQQ počas obchodného času.

Tento skript beží na droplet-e a sťahuje aktuálne dáta pre QQQ každých 30 min počas obchodného času NASDAQ (9:00 - 16:30 ET).

- Spustí sa 30 min pred otvorením (9:00 ET).
- Sťahuje dáta každých 30 min až do 16:30 ET.
- Ukladá do JSON súboru (napr. qqq_data_week.json).

Použitie na droplet-e:
- Nastav env SAXO_CLIENT_ID a tokeny (tokens_demo.json).
- Spusti: python data_collector_qqq.py
- Beží ako daemon, zastav Ctrl+C.

Pre systemd: možno pridať do deploy_release/.
"""
import os
import json
import time
import requests
from datetime import datetime, timezone, timedelta

# --- Configure ---
CLIENT_ID = os.getenv("SAXO_CLIENT_ID", "TU_DAJ_SVOJ_APPKEY")
TOKENS_FILE = "tokens_demo.json"
ENV = "sim"
OUTPUT_FILE = "qqq_data_week.json"

if ENV == "live":
    BASE_URL = "https://gateway.saxobank.com/openapi"
else:
    BASE_URL = "https://gateway.saxobank.com/sim/openapi"

# Eastern Time
ET = timezone(timedelta(hours=-4))  # ET je UTC-4 (letný čas), ale pre presnosť možno použiť pytz, ale jednoducho

def load_tokens():
    try:
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        raise SystemExit(f"Chyba: nenašiel som {TOKENS_FILE}.")

def get_access_token():
    tokens = load_tokens()
    exp = tokens.get("expires_at", 0)
    if exp < time.time():
        raise SystemExit("Token expiroval. Obnov ho.")
    return tokens["access_token"]

def get_qqq_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    # Najprv UIC pre QQQ
    search_url = f"{BASE_URL}/ref/v1/instruments"
    params = {"Keywords": "QQQ", "AssetType": "Stock", "$top": 1}
    r = requests.get(search_url, headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        print(f"Chyba pri hľadaní QQQ: {r.status_code}")
        return None, None
    data = r.json()
    if not data.get("Data"):
        print("QQQ nenájdené.")
        return None, None
    uic = data["Data"][0]["Identifier"]

    # Aktuálna cena
    price_url = f"{BASE_URL}/trade/v2/info/prices"
    params = {"Uic": uic, "AssetType": "Stock"}
    r = requests.get(price_url, headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        print(f"Chyba pri cene: {r.status_code}")
        return None, None
    price_data = r.json()
    quote = price_data.get("Quote", {})
    price_info = {
        "time": datetime.now(ET).isoformat(),
        "price": quote.get("Mid"),
        "bid": quote.get("Bid"),
        "ask": quote.get("Ask"),
    }
    return price_info, uic

def get_qqq_options_chain(access_token, qqq_uic, current_price):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    today = datetime.now(ET).date().isoformat()
    
    # Vyhľadať options: UnderlyingUic=qqq_uic, ExpiryDate=today, AssetType=StockOption
    search_url = f"{BASE_URL}/ref/v1/instruments"
    params = {
        "AssetType": "StockOption",
        "UnderlyingUic": qqq_uic,
        "ExpiryDate": today,
        "$top": 1000  # veľa, filtrovať neskôr
    }
    r = requests.get(search_url, headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        print(f"Chyba pri options: {r.status_code}")
        return []
    
    options = r.json().get("Data", [])
    # Filtrovať ±8 úrovní od current_price
    strikes = sorted(set(o.get("Strike", 0) for o in options))
    if not strikes:
        return []
    
    # Nájsť najbližšie strike k current_price
    closest_idx = min(range(len(strikes)), key=lambda i: abs(strikes[i] - current_price))
    start_idx = max(0, closest_idx - 8)
    end_idx = min(len(strikes), closest_idx + 9)  # +9 pre inclusive
    relevant_strikes = set(strikes[start_idx:end_idx])
    
    filtered_options = [o for o in options if o.get("Strike") in relevant_strikes]
    
    # Pre každú option získať cenu
    options_data = []
    for opt in filtered_options:
        uic = opt["Identifier"]
        price_url = f"{BASE_URL}/trade/v2/info/prices"
        params = {"Uic": uic, "AssetType": "StockOption"}
        r = requests.get(price_url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            price_data = r.json()
            quote = price_data.get("Quote", {})
            options_data.append({
                "uic": uic,
                "symbol": opt.get("DisplayAndFormat", {}).get("Symbol", ""),
                "strike": opt["Strike"],
                "put_call": opt.get("PutCall", ""),
                "bid": quote.get("Bid"),
                "ask": quote.get("Ask"),
                "mid": quote.get("Mid"),
            })
    
    return options_data

def is_market_open():
    now = datetime.now(ET)
    weekday = now.weekday()  # 0=Mon, 6=Sun
    if weekday >= 5:  # weekend
        return False
    hour = now.hour
    minute = now.minute
    current_time = hour * 60 + minute
    open_time = 9 * 60  # 9:00
    close_time = 16 * 60 + 30  # 16:30
    return open_time <= current_time <= close_time

def load_existing_data():
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_data(data):
    global OUTPUT_FILE
    today = datetime.now(ET).date().isoformat().replace("-", "")
    new_file = f"qqq_data_{today}.json"
    if OUTPUT_FILE != new_file:
        # Nový deň, archivuj starý
        if os.path.exists(OUTPUT_FILE):
            os.rename(OUTPUT_FILE, new_file)
        OUTPUT_FILE = new_file
        data = []  # začni nový deň
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    if not CLIENT_ID or CLIENT_ID == "TU_DAJ_SVOJ_APPKEY":
        raise SystemExit("Nastav SAXO_CLIENT_ID.")

    access_token = get_access_token()
    # Nastav OUTPUT_FILE na dnešný deň
    today = datetime.now(ET).date().isoformat().replace("-", "")
    global OUTPUT_FILE
    OUTPUT_FILE = f"qqq_data_{today}.json"
    data = load_existing_data()

    print("Spúšťam data collector pre QQQ...")
    while True:
        if is_market_open():
            print(f"Sťahujem dáta o {datetime.now(ET).strftime('%H:%M ET')}")
            price_info, qqq_uic = get_qqq_data(access_token)
            if price_info and qqq_uic:
                current_price = price_info["price"]
                options_chain = get_qqq_options_chain(access_token, qqq_uic, current_price)
                entry = {
                    "time": price_info["time"],
                    "qqq": price_info,
                    "options": options_chain
                }
                data.append(entry)
                save_data(data)
                print(f"Uložené: QQQ {current_price}, {len(options_chain)} options")
            else:
                print("Nepodarilo stiahnuť dáta.")
        else:
            print(f"Burza zatvorená, čakám... ({datetime.now(ET).strftime('%H:%M ET')})")

        time.sleep(1800)  # 30 min

if __name__ == "__main__":
    main()