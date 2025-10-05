# Droplet: conare

Prehľad a inštrukcie pre nasadenie služieb na droplet "conare".

## Prehľad
- Účel: Token infra pre Saxo (refresher + HTTP proxy) a voliteľne web UI
- Prostredia: sim (demo) / live
- Hlavné komponenty:
  - token-daemon: pravidelné obnovovanie tokenov
  - token-proxy: HTTP endpoint na vydanie aktuálneho access tokenu
  - webapp (voliteľné): jednoduché UI

## Štruktúra
```
droplets/
└─ conare/
   └─ var02/
      └─ token_proxy.py   # jednoduchý HTTP proxy server
```

Pozn.: Dockerfile a docker-compose sa nachádzajú v `pc/PC/OpenAIGPT/SaxoAPI/Testovanie/` (zdieľané pre všetky droplets). Token proxy skript je lokálny v `droplets/conare/var02/`.

## Porty
- token-proxy demo: 8080 (mapované na hosta podľa compose)
- token-proxy live: 8081 (mapované na hosta podľa compose)
- webapp (voliteľné): 5000
- Ďalšie proxy inštancie (reader/0dte/trader): 8181, 8182, 8183

## Tajomstvá (secrets)
- Pre live role použi `.env` súbory v štýle:
  - `SAXO_ENV=live`
  - `SAXO_CLIENT_ID=...`
  - `SAXO_CLIENT_SECRET=...`
  - `REDIRECT_URI=http://127.0.0.1:8765/callback/<role>`
- Príklady nájdeš v: `pc/PC/OpenAIGPT/SaxoAPI/Testovanie/secrets/live/`
- Necommituj reálne hodnoty do git; súbory maj súkromné (600) na serveri.

## Rýchly štart (odporúčané)
Použi hlavný docker-compose v `pc/PC/OpenAIGPT/SaxoAPI/Testovanie/`:

1) Príprava `.env` (ak používaš demo):
```
cd pc/PC/OpenAIGPT/SaxoAPI/Testovanie
cp .env.example .env
# uprav .env ak treba a nastav práva
chmod 600 .env
```

2) Spustenie demá:
```
docker compose up -d --build token-proxy-demo saxo-token-daemon-demo
```

3) Test proxy:
```
curl http://localhost:8080/token
```

4) Vypnutie:
```
docker compose down
```

## Alternatíva: spustenie len token-proxy (bez webappu)
V `pc/PC/OpenAIGPT/SaxoAPI/Testovanie/docker-compose.yml` už existujú služby `token-proxy-*` s príkazom:
```
command: ["python3", "/app/droplets/conare/var02/token_proxy.py"]
```
Môžeš spustiť konkrétnu službu napr. reader:
```
docker compose up -d --build token-proxy-live-reader
```
Nezabudni nastaviť `TOKENS_FILE` a mount `./data:/data`, kde daemoni ukladajú tokeny.

## Poznámky
- Odporúčam spúšťať proxy len na vnútornú sieť alebo cez reverzný proxy s TLS a autentifikáciou.
- Pri nasadení na server (droplet) skontroluj firewall pravidlá pre použité porty.
