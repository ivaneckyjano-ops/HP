Token proxy

Použitie:

1. Uistite sa, že `TOKENS_FILE` existuje a je čitateľný pre užívateľa, ktorý spúšťa proxy.
2. Spusti proxy:

```bash
TOKENS_FILE=/var/lib/saxo/tokens_min.json PROXY_HOST=127.0.0.1 PROXY_PORT=8080 python3 token_proxy.py
```

3. Lokálne služby môžu zavolať `GET http://127.0.0.1:8080/token` a dostať JSON s `access_token` a `expires_at`.

Bezpečnosť:
- Proxy by mala byť dostupná iba lokálne (127.0.0.1) alebo cez unix socket.
- Nastav prístupové práva tak, aby len lokálne služby mali prístup.
