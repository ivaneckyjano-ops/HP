## Prehľad
Tento balíček obsahuje jednoduchý token proxy server pre Saxo tokeny.

### Súbor
- `token_proxy.py` — HTTP server:
	- GET /token → { access_token, expires_at }
	- Číta `TOKENS_FILE` (JSON) — rovnaký súbor používa token daemon.

### Spustenie lokálne (Python)
```
export TOKENS_FILE=./data/tokens_demo.json
export PROXY_HOST=0.0.0.0
export PROXY_PORT=8080
python3 token_proxy.py
```

### Spustenie cez Docker Compose
Použi služby `token-proxy-*` v `pc/PC/OpenAIGPT/SaxoAPI/Testovanie/docker-compose.yml`.

### Bezpečnosť
- Proxy neposkytuje autentifikáciu — nenasadzuj priamo na internet bez ochrany.
- Odporúčané: reverzný proxy (nginx), mTLS, alebo IP whitelisting.
Droplet token infra

Tento adresár obsahuje pomocné skripty a dokumentáciu pre token daemon a token proxy.

- `token_daemon.py` (v Testovanie/) - proces, ktorý pravidelne kontroluje a obnovuje tokeny
- `token_proxy.py` - jednoduchý lokálny HTTP server, ktorý poskytuje `access_token` ostatným službám

Použi Docker alebo systemd na nasadenie podľa `deploy.md`.
