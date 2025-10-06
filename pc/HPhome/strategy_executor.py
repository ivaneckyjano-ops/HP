#!/usr/bin/env python3
"""Strategy Executor Daemon.

Načítava stratégie z strategies/, kontroluje watchlist, vyhodnocuje podmienky,
a otvára/zatvára pozície v demo prostredí cez Saxo API.

Použitie:
- python strategy_executor.py
- Beží ako daemon, kontroluje každých 5 min počas obchodného času.
"""
import os
import yaml
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import math

# --- Configure ---
CLIENT_ID = os.getenv("SAXO_CLIENT_ID", "TU_DAJ_SVOJ_APPKEY")
CLIENT_SECRET = os.getenv("SAXO_CLIENT_SECRET", "")
TOKENS_FILE = os.getenv("TOKENS_FILE", "tokens_live_trader.json")
ENV = os.getenv("SAXO_ENV", "live")
PROXY_URL = os.getenv("PROXY_URL", "http://localhost:8183/token")
STORE_URL = os.getenv("STORE_URL", "http://localhost:8090")

if ENV == "sim":
    BASE_URL = "https://gateway.saxobank.com/sim/openapi"
else:
    BASE_URL = "https://gateway.saxobank.com/openapi"

ET = timezone(timedelta(hours=-4))

STRATEGIES_DIR = Path("strategies")
WATCHLIST_FILE = Path("watchlist/watchlist.yaml")
POSITIONS_FILE = "open_positions.json"  # sledovanie otvorených pozícií
TRADES_FILE = "trades_log.json"  # log všetkých transakcií

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def load_strategies():
    strategies = {}
    for file in STRATEGIES_DIR.glob("*.yaml"):
        strat = load_yaml(file)
        if strat.get("aktívne", False):
            strategies[strat["kód"]] = strat
    return strategies

def load_watchlist():
    return load_yaml(WATCHLIST_FILE)

def load_positions():
    try:
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_positions(positions):
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def load_trades():
    try:
        with open(TRADES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_trades(trades):
    with open(TRADES_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def get_access_token():
    """Získa access token cez proxy."""
    try:
        r = requests.get(PROXY_URL, timeout=5)
        if r.status_code == 200:
            token_data = r.json()
            exp = token_data.get("expires_at", 0)
            if exp < time.time():
                raise ValueError("Token expired")
            return token_data["access_token"]
        else:
            raise ValueError(f"Proxy returned {r.status_code}")
    except Exception as e:
        raise SystemExit(f"Token problem: {e}")

def get_instrument_uic(symbol, asset_type="Stock"):
    headers = {"Authorization": f"Bearer {get_access_token()}", "Accept": "application/json"}
    params = {"Keywords": symbol, "AssetType": asset_type, "$top": 1}
    r = requests.get(f"{BASE_URL}/ref/v1/instruments", headers=headers, params=params, timeout=10)
    if r.status_code == 200 and r.json().get("Data"):
        return r.json()["Data"][0]["Identifier"]
    return None

def get_price(uic, asset_type="Stock"):
    headers = {"Authorization": f"Bearer {get_access_token()}", "Accept": "application/json"}
    params = {"Uic": uic, "AssetType": asset_type}
    r = requests.get(f"{BASE_URL}/trade/v2/info/prices", headers=headers, params=params, timeout=10)
    if r.status_code == 200:
        quote = r.json().get("Quote", {})
        return {"bid": quote.get("Bid"), "ask": quote.get("Ask"), "mid": quote.get("Mid")}
    return None

def get_options_chain(uic, expiry_date=None):
    """Získa options chain pre daný UIC a expiry."""
    headers = {"Authorization": f"Bearer {get_access_token()}", "Accept": "application/json"}
    params = {"Uic": uic, "OptionRootId": uic}
    if expiry_date:
        params["ExpiryDate"] = expiry_date
    r = requests.get(f"{BASE_URL}/ref/v1/instruments", headers=headers, params=params, timeout=10)
    if r.status_code == 200:
        return r.json().get("Data", [])
    return []

def find_strike_by_delta(chain, target_delta, option_type, max_strikes=10):
    """Nájde strike najbližšie k target_delta."""
    candidates = [opt for opt in chain if opt.get("PutCall") == option_type and abs(opt.get("Delta", 0) - target_delta) < 0.5]
    candidates.sort(key=lambda x: abs(x.get("Delta", 0) - target_delta))
    return candidates[:max_strikes]

def calculate_dte(expiry_date):
    """Vypočíta DTE (days to expiry)."""
    expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    return (expiry - now).days

def is_market_open():
    now = datetime.now(ET)
    if now.weekday() >= 5:
        return False
    current_time = now.hour * 60 + now.minute
    return 9*60 <= current_time <= 16*60 + 30

def check_opening_conditions(strategy, symbol, uic):
    """Skontroluje podmienky pre otvorenie stratégie."""
    opening_rule = next((r for r in strategy["postupné_pravidlá"] if r["názov"] == "otvorenie"), None)
    if not opening_rule:
        return False

    # Získaj aktuálnu cenu podkladu
    price = get_price(uic)
    if not price or not price.get("mid"):
        return False
    spot = price["mid"]

    # Získaj options chain pre DTE=0
    today = datetime.now(ET).date().isoformat()
    chain = get_options_chain(uic, today)
    if not chain:
        return False

    # Skontroluj DTE
    dte_range = opening_rule["spúšťač"]["DTE"]
    dte = calculate_dte(today)
    if not (dte_range[0] <= dte <= dte_range[1]):
        return False

    # Placeholder pre IVR
    ivr_range = opening_rule["spúšťač"]["IVR"]
    # Predpokladáme IVR v rozsahu

    # Časové okno
    now = datetime.now(ET)
    time_window = opening_rule["spúšťač"]["časové_okno_ET"]
    start_h, start_m = map(int, time_window.split("-")[0].split(":"))
    end_h, end_m = map(int, time_window.split("-")[1].split(":"))
    start_min = start_h * 60 + start_m
    end_min = end_h * 60 + end_m
    current_min = now.hour * 60 + now.minute
    if not (start_min <= current_min <= end_min):
        return False

    strategy_type = strategy.get("typ", "železný_kondor")

    if strategy_type == "železný_kondor":
        # Logika pre Iron Condor
        target_call_delta = opening_rule["spúšťač"]["greeks"]["cieľová_delta_krátkych"]["call"]
        target_put_delta = opening_rule["spúšťač"]["greeks"]["cieľová_delta_krátkych"]["put"]

        short_call_strikes = find_strike_by_delta(chain, target_call_delta, "Call")
        short_put_strikes = find_strike_by_delta(chain, target_put_delta, "Put")

        if not short_call_strikes or not short_put_strikes:
            return False

        short_call = short_call_strikes[0]
        short_put = short_put_strikes[0]

        wing_width = opening_rule["cieľ"]["wing_width_strikes"]
        short_call_strike = short_call["StrikePrice"]
        short_put_strike = short_put["StrikePrice"]

        long_call_strike = short_call_strike + wing_width * (spot * 0.01)
        long_put_strike = short_put_strike - wing_width * (spot * 0.01)

        tomorrow = (datetime.now(ET).date() + timedelta(days=1)).isoformat()
        chain_tomorrow = get_options_chain(uic, tomorrow)
        long_call = next((opt for opt in chain_tomorrow if opt["StrikePrice"] == long_call_strike and opt["PutCall"] == "Call"), None)
        long_put = next((opt for opt in chain_tomorrow if opt["StrikePrice"] == long_put_strike and opt["PutCall"] == "Put"), None)

        if not long_call or not long_put:
            return False

        credit = (short_call.get("Ask", 0) + short_put.get("Ask", 0)) - (long_call.get("Bid", 0) + long_put.get("Bid", 0))
        min_credit = opening_rule["ekonomika"]["min_kredit"]
        if credit < min_credit:
            return False

        return {
            "short_call": short_call,
            "short_put": short_put,
            "long_call": long_call,
            "long_put": long_put,
            "credit": credit
        }

    elif strategy_type == "diagonálny_kreditný_spread":
        # Logika pre kreditný spread (PUT alebo CALL)
        side = opening_rule.get("strana", "PUT")
        target_delta = opening_rule["spúšťač"]["greeks"]["cieľová_abs_delta_krátkej"]

        if side == "PUT":
            short_strikes = find_strike_by_delta(chain, -target_delta, "Put")  # negative delta for puts
            option_type = "Put"
        else:
            short_strikes = find_strike_by_delta(chain, target_delta, "Call")
            option_type = "Call"

        if not short_strikes:
            return False

        short_option = short_strikes[0]
        short_strike = short_option["StrikePrice"]

        # Dlhá noha: o 1 strike ďalej OTM
        if side == "PUT":
            long_strike = short_strike - (spot * 0.01)  # 1% lower for put spread
        else:
            long_strike = short_strike + (spot * 0.01)  # 1% higher for call spread

        tomorrow = (datetime.now(ET).date() + timedelta(days=1)).isoformat()
        chain_tomorrow = get_options_chain(uic, tomorrow)
        long_option = next((opt for opt in chain_tomorrow if abs(opt["StrikePrice"] - long_strike) < 0.01 and opt["PutCall"] == option_type), None)

        if not long_option:
            return False

        credit = short_option.get("Ask", 0) - long_option.get("Bid", 0)
        min_credit = opening_rule["ekonomika"]["min_kredit"]
        if credit < min_credit:
            return False

        return {
            "short_option": short_option,
            "long_option": long_option,
            "credit": credit,
            "side": side
        }

    return False

def execute_roll_strategy(strategy, position, new_legs, trades_log):
    """Roll pozície podľa stratégie."""
    strategy_code = strategy["kód"]
    timestamp = datetime.now().isoformat()

    # Placeholder: log roll nákladov
    roll_cost = {
        "timestamp": timestamp,
        "strategy": strategy_code,
        "action": "roll",
        "type": strategy.get("typ", ""),
        "total_cost": 5.0,  # placeholder commission
        "reason": "breach_management"
    }
    trades_log.append(roll_cost)
    print(f"Rolling position for {strategy_code}")

def execute_close_strategy(strategy, position, trades_log):
    """Zatvoriť pozíciu."""
    strategy_code = strategy["kód"]
    timestamp = datetime.now().isoformat()

    # Placeholder: vypočítaj realized P&L
    realized_pnl = 0.5  # placeholder

    close_trade = {
        "timestamp": timestamp,
        "strategy": strategy_code,
        "action": "close",
        "type": strategy.get("typ", ""),
        "realized_pnl": realized_pnl,
        "commission": 1.0,
        "reason": "expiration_or_target"
    }
    trades_log.append(close_trade)
def execute_roll_strategy(strategy, position, new_legs, trades_log):
    """Roll pozície podľa stratégie."""
    strategy_code = strategy["kód"]
    timestamp = datetime.now().isoformat()

    # Placeholder: log roll nákladov
    roll_cost = {
        "timestamp": timestamp,
        "strategy": strategy_code,
        "action": "roll",
        "type": strategy.get("typ", ""),
        "total_cost": 5.0,  # placeholder commission
        "reason": "breach_management"
    }
    trades_log.append(roll_cost)
    print(f"Rolling position for {strategy_code}")

def execute_close_strategy(strategy, position, trades_log):
    """Zatvoriť pozíciu."""
    strategy_code = strategy["kód"]
    timestamp = datetime.now().isoformat()

    # Placeholder: vypočítaj realized P&L
    realized_pnl = 0.5  # placeholder

    close_trade = {
        "timestamp": timestamp,
        "strategy": strategy_code,
        "action": "close",
        "type": strategy.get("typ", ""),
        "realized_pnl": realized_pnl,
        "commission": 1.0,
        "reason": "expiration_or_target"
    }
    trades_log.append(close_trade)
    print(f"Closing position for {strategy_code}, P&L: ${realized_pnl}")

def execute_open_strategy(strategy, symbol, legs, trades_log):
    """Otvoriť stratégiu cez API."""
    strategy_type = strategy.get("typ", "železný_kondor")
    strategy_code = strategy["kód"]
    timestamp = datetime.now().isoformat()

    if strategy_type == "železný_kondor":
        # Iron Condor: 4 nohy
        orders = []
        total_commission = 0
        total_premium = 0

        for leg_name, leg in legs.items():
            if leg_name == "credit":
                continue
            buy_sell = "Sell" if "short" in leg_name else "Buy"
            quantity = 1  # predpokladáme 1 zmluvu

            # Simulované ceny a komisie
            if buy_sell == "Sell":
                price = leg.get("Bid", 0)  # predaj na bid
            else:
                price = leg.get("Ask", 0)  # nákup na ask

            commission = 0.5  # USD per contract
            total_commission += commission
            total_premium += price * quantity * 100  # premium v USD

            order = {
                "Uic": leg["Identifier"],
                "AssetType": "StockOption",
                "Amount": quantity,
                "BuySell": buy_sell,
                "OrderType": "Market",
                "OrderDuration": {"DurationType": "Day"}
            }
            print(f"Placing order: {order}")
            orders.append({"order_id": "fake", "status": "filled"})

            # Log transakcie
            trade = {
                "timestamp": timestamp,
                "strategy": strategy_code,
                "action": "open",
                "type": "iron_condor",
                "leg": leg_name,
                "symbol": leg.get("Symbol", ""),
                "strike": leg.get("StrikePrice", 0),
                "expiry": leg.get("ExpiryDate", ""),
                "option_type": leg.get("PutCall", ""),
                "buy_sell": buy_sell,
                "quantity": quantity,
                "price": price,
                "commission": commission,
                "total_cost": price * quantity * 100 + commission
            }
            trades_log.append(trade)

        # Log celkové náklady otvorenia
        opening_cost = {
            "timestamp": timestamp,
            "strategy": strategy_code,
            "action": "open_summary",
            "type": "iron_condor",
            "total_premium": total_premium,
            "total_commission": total_commission,
            "net_credit": legs.get("credit", 0),
            "net_cost": total_commission  # premium je kredit
        }
        trades_log.append(opening_cost)

        return orders

    elif strategy_type == "diagonálny_kreditný_spread":
        # Kreditný spread: 2 nohy
        orders = []
        total_commission = 0
        total_premium = 0

        for leg_name, leg in legs.items():
            if leg_name in ["credit", "side"]:
                continue
            buy_sell = "Sell" if "short" in leg_name else "Buy"
            quantity = 1

            if buy_sell == "Sell":
                price = leg.get("Bid", 0)
            else:
                price = leg.get("Ask", 0)

            commission = 0.5
            total_commission += commission
            if buy_sell == "Sell":
                total_premium += price * quantity * 100

            order = {
                "Uic": leg["Identifier"],
                "AssetType": "StockOption",
                "Amount": quantity,
                "BuySell": buy_sell,
                "OrderType": "Market",
                "OrderDuration": {"DurationType": "Day"}
            }
            print(f"Placing order: {order}")
            orders.append({"order_id": "fake", "status": "filled"})

            # Log transakcie
            trade = {
                "timestamp": timestamp,
                "strategy": strategy_code,
                "action": "open",
                "type": "credit_spread",
                "side": legs.get("side", ""),
                "leg": leg_name,
                "symbol": leg.get("Symbol", ""),
                "strike": leg.get("StrikePrice", 0),
                "expiry": leg.get("ExpiryDate", ""),
                "option_type": leg.get("PutCall", ""),
                "buy_sell": buy_sell,
                "quantity": quantity,
                "price": price,
                "commission": commission,
                "total_cost": price * quantity * 100 + commission
            }
            trades_log.append(trade)

        # Log celkové náklady otvorenia
        opening_cost = {
            "timestamp": timestamp,
            "strategy": strategy_code,
            "action": "open_summary",
            "type": "credit_spread",
            "total_premium": total_premium,
            "total_commission": total_commission,
            "net_credit": legs.get("credit", 0),
            "net_cost": total_commission
        }
        trades_log.append(opening_cost)

        return orders

    return []

def check_management_conditions(strategy, positions):
    """Skontroluje podmienky pre manažment."""
    # Placeholder: skontroluj breach
    return False

def check_expiry_conditions(strategy, positions):
    """Skontroluje podmienky pre expiráciu/zatvorenie."""
    expiry_rule = next((r for r in strategy["postupné_pravidlá"] if "expirácia" in r["názov"]), None)
    if not expiry_rule:
        return False

    minutes_to_close = expiry_rule["spúšťač"]["minutes_to_close_leq"]
    now = datetime.now(ET)
    close_time = now.replace(hour=16, minute=30, second=0, microsecond=0)
    minutes_left = (close_time - now).total_seconds() / 60
    if minutes_left <= minutes_to_close:
        return True
    return False

def main():
    if not CLIENT_ID or CLIENT_ID == "TU_DAJ_SVOJ_APPKEY":
        raise SystemExit("Nastav SAXO_CLIENT_ID.")

    strategies = load_strategies()
    watchlist = load_watchlist()
    positions = load_positions()
    trades_log = load_trades()

    print(f"Načítané stratégie: {list(strategies.keys())}")
    print(f"Watchlist: {len(watchlist['instruments'])} instrumentov")

    while True:
        if is_market_open():
            print(f"Kontrolujem o {datetime.now(ET).strftime('%H:%M ET')}")
            # Načítaj ceny pre watchlist
            prices = {}
            for inst in watchlist["instruments"]:
                uic = inst.get("uic") or get_instrument_uic(inst["symbol"])
                if uic:
                    prices[inst["symbol"]] = get_price(uic)
                    inst["uic"] = uic  # ulož UIC

            # Vyhodnoť stratégie
            for code, strat in strategies.items():
                symbol = strat["rozsah"]["podklady"][0]  # predpokladáme QQQ
                uic = next((inst["uic"] for inst in watchlist["instruments"] if inst["symbol"] == symbol), None)
                if not uic:
                    continue

                # Skontroluj otvorenie
                opening_data = check_opening_conditions(strat, symbol, uic)
                if opening_data:
                    print(f"Podmienky pre otvorenie splnené pre stratégiu {code}")
                    orders = execute_open_strategy(strat, symbol, opening_data, trades_log)
                    positions[f"{code}_{datetime.now().isoformat()}"] = {
                        "strategy": code,
                        "legs": opening_data,
                        "orders": orders,
                        "opened_at": datetime.now().isoformat()
                    }

                # Skontroluj manažment
                if check_management_conditions(strat, positions):
                    print(f"Manažment potrebný pre stratégiu {code}")
                    # Implement roll logic

                # Skontroluj expiráciu
                if check_expiry_conditions(strat, positions):
                    print(f"Expirácia/zatvorenie pre stratégiu {code}")
                    # Implement close logic

            save_positions(positions)
            # Ulož trades log
            save_trades(trades_log)
            # Ulož watchlist s UIC
            with open(WATCHLIST_FILE, 'w') as f:
                yaml.dump(watchlist, f)
        else:
            print("Burza zatvorená")

        time.sleep(300)  # každých 5 min

if __name__ == "__main__":
    main()