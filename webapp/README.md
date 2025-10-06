Saxo Live - jednoduchý prototyp web UI

Spustenie lokálne:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Spustenie v Dockeri:

```bash
docker build -t saxolive-web .
docker run -p 5000:5000 saxolive-web
```

Tento prototyp je minimalistický a slúži na rýchlu vizualizáciu layoutu. Pridaj API integrácie a autentifikáciu pre reálne nasadenie.

Navigácia a stránky:
- Dashboard: rýchly prehľad, ukážkové boty, systémové metriky a náhľad token služieb.
- Boti: tabuľka botov (mock dáta).
- Denník: história obchodov (mock dáta).
- Stratégie: prehľad otvorených stratégií (mock dáta).
- Príležitosti: zoznam signálov (mock dáta).
- Droplet: monitoring servera, systémové zdroje + stav bežiacich služieb (proxy a daemony).
- Reporty, Nastavenia: placeholdery; v Nastaveniach je voliteľný reštart služieb.

Premenné prostredia:
- PROXY_DEMO_URL (default http://localhost:8080/token) – endpoint token-proxy DEMO.
- PROXY_LIVE_URL (default http://localhost:8081/token) – endpoint token-proxy LIVE.
- ENABLE_SERVICE_CONTROL=1 – povolí POST /api/restart/<service> z Nastavení.
- COMPOSE_FILE – voliteľná cesta na docker-compose.yml ak sa používa iná ako default.

Poznámky:
- Stav služieb sa vyhodnocuje cez token-proxy endpointy. OK = endpoint je dostupný a token má >60s TTL.
- Reštart služieb vyžaduje, aby webapp bežal v prostredí s prístupom k Dockeru.

Tipy na náhľad/porty:
- Ak v náhľade vidíš hlášku „Pripájanie k presmerovanému portu…“, skús stránku obnoviť (Ctrl/Cmd+R) alebo otvor port 5000 v externom prehliadači (panel Porty → 5000 → Open in Browser).
- Alternatívne priamo navštív http://localhost:5000 vo svojom prehliadači.
- Pre token proxy môžeš overiť JSON na http://localhost:8080/token (DEMO) alebo http://localhost:8081/token (LIVE).
