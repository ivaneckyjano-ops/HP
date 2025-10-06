#!/usr/bin/env python3
"""Testovanie 0DTE stratégie pre QQQ.

Tento skript:
- Stiahne historické dáta pre QQQ (posledných 30 dní).
- Implementuje jednoduchú 0DTE stratégiu: každý deň, ak je cena QQQ > 200-dňový MA, buy 0DTE call (simulácia).
- Simuluje P&L na základe denných zmien.
- Vypíše výsledky.

Poznámka: Toto je simulácia, nie reálny trading. Pre reálne testovanie použite demo účet.

Použitie:
- Nastav SAXO_CLIENT_ID a tokeny (tokens_demo.json alebo tokens_live.json).
- Spusti: python test_0dte_qqq.py
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta
import statistics

# --- Configure ---
CLIENT_ID = os.getenv("SAXO_CLIENT_ID", "TU_DAJ_SVOJ_APPKEY")
TOKENS_FILE = "tokens_demo.json"  # alebo tokens_live.json
ENV = "sim"  # alebo "live"

if ENV == "live":
    BASE_URL = "https://gateway.saxobank.com/openapi"
else:
    BASE_URL = "https://gateway.saxobank.com/sim/openapi"

# Načítať tokeny
def load_tokens():
    try:
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        raise SystemExit(f"Chyba: nenašiel som {TOKENS_FILE}. Spusti auto_oauth.py najprv.")

def get_access_token():
    tokens = load_tokens()
    exp = tokens.get("expires_at", 0)
    if exp < time.time():
        raise SystemExit("Token expiroval. Obnov ho cez auto_oauth.py.")
    return tokens["access_token"]

# Stiahnuť historické dáta pre QQQ
def get_qqq_data(access_token, days=7):  # zmenené na 7 dní
    # Najprv nájsť UIC pre QQQ
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    search_url = f"{BASE_URL}/ref/v1/instruments"
    params = {"Keywords": "QQQ", "AssetType": "Stock", "$top": 1}
    r = requests.get(search_url, headers=headers, params=params)
    if r.status_code != 200:
        raise SystemExit(f"Chyba pri hľadaní QQQ: {r.status_code} {r.text}")
    data = r.json()
    if not data.get("Data"):
        raise SystemExit("QQQ nenájdené.")
    uic = data["Data"][0]["Identifier"]

    # Stiahnuť chart dáta
    chart_url = f"{BASE_URL}/chart/v1/charts"
    params = {
        "AssetType": "Stock",
        "Uic": uic,
        "Horizon": 1,  # 1 deň
        "Count": days,
        "Mode": "UpTo",
    }
    r = requests.get(chart_url, headers=headers, params=params)
    if r.status_code != 200:
        raise SystemExit(f"Chyba pri sťahovaní dát: {r.status_code} {r.text}")
    chart_data = r.json()
    return chart_data

# Jednoduchá 0DTE stratégia: buy call každý deň ak cena > 200-dňový MA (ale máme len 30 dní, tak použijeme 10-dňový)
def simulate_strategy(data):
    prices = [d["Close"] for d in data["Data"] if d.get("Close")]
    if len(prices) < 10:
        raise SystemExit("Nedostatok dát pre MA.")

    ma_period = 10
    pnl = 0
    trades = []

    for i in range(ma_period, len(prices)):
        ma = statistics.mean(prices[i-ma_period:i])
        current_price = prices[i]
        if current_price > ma:
            # Simulácia: buy 0DTE call, predpokladáme delta ~0.5, takže P&L = (zmena ceny) * 0.5 * 100 (pre 1 kontrakt)
            # Zjednodušenie: P&L = (prices[i+1] - prices[i]) * 50 ak je ďalší deň, inak 0
            if i + 1 < len(prices):
                change = prices[i+1] - prices[i]
                trade_pnl = change * 50  # aproximácia
                pnl += trade_pnl
                trades.append({
                    "date": data["Data"][i]["Time"],
                    "action": "buy_call",
                    "price": current_price,
                    "pnl": trade_pnl
                })

    return pnl, trades

def main():
    if not CLIENT_ID or CLIENT_ID == "TU_DAJ_SVOJ_APPKEY":
        raise SystemExit("Nastav SAXO_CLIENT_ID.")

    access_token = get_access_token()
    print("Sťahujem dáta pre QQQ...")
    data = get_qqq_data(access_token, days=30)
    print(f"Stiahnutých {len(data.get('Data', []))} dátových bodov.")

    print("Simulujem stratégiu...")
    total_pnl, trades = simulate_strategy(data)
    print(f"Celkové P&L: {total_pnl:.2f} USD")
    print(f"Počet obchodov: {len(trades)}")
    for t in trades[:5]:  # ukáž prvých 5
        print(f"- {t['date']}: {t['action']} @ {t['price']:.2f}, P&L: {t['pnl']:.2f}")

if __name__ == "__main__":
    main()