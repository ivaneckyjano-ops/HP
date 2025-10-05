Droplet token infra

Tento adresár obsahuje pomocné skripty a dokumentáciu pre token daemon a token proxy.

- `token_daemon.py` (v Testovanie/) - proces, ktorý pravidelne kontroluje a obnovuje tokeny
- `token_proxy.py` - jednoduchý lokálny HTTP server, ktorý poskytuje `access_token` ostatným službám

Použi Docker alebo systemd na nasadenie podľa `deploy.md`.
