# HP Repository

Tento repozitár obsahuje veci pre PC a rôzne droplets (servery), vrátane **automatizovaného obchodného systému pre Saxo OpenAPI**.

## Štruktúra

- `pc/` - Veci pre lokálne PC (napr. OpenAIGPT SaxoAPI)
  - `HPhome/` - **Automatizovaný obchodný systém**
- `droplets/` - Priečinok pre rôzne droplets
  - `droplet1/` - Prvý droplet (napr. var02 proxy)
  - `droplet2/` - Druhý droplet (prázdny, pre budúce použitie)
- `webapp/` - Web aplikácia
- `scripts/` - Pomocné skripty
- `deploy_release/` - Deploy a release veci

```
HP/
├─ pc/
│  ├─ HPhome/                           # 🧠 HLAVNÝ OBCHODNÝ SYSTÉM
│  │  ├─ strategies/                    # YAML stratégie
│  │  ├─ watchlist/                     # Watchlist podkladových aktív
│  │  ├─ data_collector_qqq.py          # Intradenný zber dát QQQ
│  │  ├─ strategy_executor.py           # 🚀 HLAVNÝ DAEMON
│  │  ├─ evaluate_strategies.py         # 📊 VYHODNOTENIE STRATÉGIÍ
│  │  ├─ auto_oauth.py                  # OAuth pre PC
│  │  └─ test_0dte_qqq.py               # Test hist. dát
├─ droplets/
│  ├─ conare/
│  │  └─ var02/
│  └─ droplet2/
├─ webapp/
├─ scripts/
└─ deploy_release/
```

## 🧠 Automatizovaný obchodný systém

### Prehľad
Systém automaticky obchoduje 0DTE (same-day expiry) stratégie na QQQ cez Saxo OpenAPI v demo/live prostredí.

### Podporované stratégie (6 stratégií)
1. **ICQQQ-0DTE-P**: Iron Condor konzervatívny, nechať expirovať
2. **ICQQQ-0DTE-C**: Iron Condor konzervatívny, zatvoriť pred expiráciou
3. **ICQQQ-0DTE-M**: Iron Condor mierny
4. **ICQQQ-0DTE-A**: Iron Condor agresívny
5. **CSQQQ-0DTE-PUT-A**: Kreditný PUT spread
6. **CSQQQ-0DTE-CALL-A**: Kreditný CALL spread

### Klúčové komponenty

#### 📁 Watchlist (`watchlist/watchlist.yaml`)
- Obsahuje **podkladové aktíva** (nie jednotlivé opcie!)
- Príklad: `QQQ` - systém automaticky vyhľadá options chain
- **Nie je potrebné zapisovať každú opciu** - systém sám vyberá strikes podľa stratégií

#### 🧠 Strategy Executor (`strategy_executor.py`)
- **Daemon** bežiaci každých 5 min počas obchodného času ET
- Vyhodnocuje podmienky pre všetky stratégie
- Automaticky otvára/zatvára/rolluje pozície
- **Loguje všetky transakcie** do `trades_log.json`

#### 📊 Evaluate Strategies (`evaluate_strategies.py`)
- **Detailné P&L vyhodnotenie** vrátane všetkých nákladov:
  - Komisie pri otvorení/zatvorení
  - Náklady na rollovanie
  - Slippage a iné poplatky
- **Win rate, ROI, úspešnosť stratégií**
- Export do `strategy_evaluation.json`

#### 📈 Data Collector (`data_collector_qqq.py`)
- Zber intradenných dát QQQ + options chain (±8 strikes)
- Denné exporty do JSON pre spätné testovanie

### Workflow systému

1. **Každých 5 min** počas ET obchodného času:
   - Načíta aktuálne ceny podkladových aktív z watchlist
   - Pre každú stratégiu skontroluje podmienky (DTE, IVR, časové okno)
   - Ak sú splnené → automaticky otvorí pozíciu

2. **Manažment pozícií**:
   - Sleduje breach (podklad dotkne krátkej strike)
   - Automatický roll na DTE+1 s vycentrovaním delty
   - Zatvorenie pri dosiahnutí P&L cieľov alebo pred expiráciou

3. **Vyhodnotenie**:
   - `python evaluate_strategies.py` pre detailný report
   - Zahŕňa všetky náklady: komisie, rolls, slippage

### Spustenie

```bash
cd pc/HPhome

# Spustenie daemon
SAXO_CLIENT_ID=your_app_key python strategy_executor.py

# Vyhodnotenie výsledkov
python evaluate_strategies.py
```

### Súbory dát
- `trades_log.json` - Log všetkých transakcií s nákladmi
- `open_positions.json` - Aktuálne otvorené pozície
- `strategy_evaluation.json` - Export vyhodnotenia

### Bezpečnosť
- OAuth PKCE pre token management
- Demo prostredie pred live tradingom
- Risk limity v stratégiách (max strata, max util)

## Ako pridať nový droplet

1. Vytvor nový priečinok v `droplets/`, napr. `droplet3/`
2. Skopíruj potrebné súbory (docker-compose.yml, Dockerfile, atď.)
3. Aktualizuj README.md v priečinku

## Deploy

Pozri `deploy_release/deploy.md` pre návod na nasadenie.
