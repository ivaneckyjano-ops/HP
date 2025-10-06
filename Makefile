# Makefile pre rýchly beh a správu služieb
# Požiadavka: Docker + Docker Compose

DIR := pc/PC/OpenAIGPT/SaxoAPI/Testovanie
COMPOSE := docker compose -f $(DIR)/docker-compose.yml
DATA_DIR := $(DIR)/data


.PHONY: help prepare-data config ps build up-demo logs-demo down up-webapp logs-webapp up-live-reader up-live-0dte up-live-trader logs-live-reader logs-live-0dte logs-live-trader preview-webapp preview-demo clean init-live-reader auth-url-live-reader reader-status reader-status-json reader-accounts reader-orders up-positions-store ingest-positions logs-positions-store start ingest-now \
	demo web stop live-reader live-0dte live-trader logs-reader logs-0dte logs-trader

help:
	@echo "Dostupné ciele:"
	@echo "  make config            - validácia docker-compose"
	@echo "  make ps                - stav služieb"
	@echo "  make up-demo           - spusti demo (daemon + proxy)"
	@echo "  make logs-demo         - logy demá"
	@echo "  make up-webapp         - spusti webapp + demo + live-reader (read-only)"
	@echo "  make logs-webapp       - logy webapp"
	@echo "  make up-live-reader    - spusti live reader (daemon + proxy)"
	@echo "  make up-live-0dte      - spusti live 0dte (daemon + proxy)"
	@echo "  make up-live-trader    - spusti live trader (daemon + proxy)"
	@echo "  make init-live-reader  - inicializuj prvotné live-reader tokeny (interaktívny OAuth)"
	@echo "  make auth-url-live-reader - iba vytlačí autorizačnú URL (klikni ju v prehliadači)"
	@echo "  make auto-oauth-live-reader - automatizovaný OAuth pre live-reader (otvorí browser, počká na dokončenie)"
	@echo "  make auto-oauth-demo - automatizovaný OAuth pre demo (otvorí browser, počká na dokončenie)"
	@echo "  make reader-status      - prečíta pozície cez live-reader token (len čítanie)"
	@echo "  make reader-status-json - uloží raw JSON pozícií do pc/.../Testovanie/data/positions_live_reader.json"
	@echo "  make reader-accounts    - vypíše prehľad účtov cez live-reader token"
	@echo "  make reader-orders      - vypíše otvorené objednávky cez live-reader token"
	@echo "  make up-positions-store - spustí store (SQLite+Flask) na :8090"
	@echo "  make ingest-positions   - načíta pozície a odošle do store (threshold update)"
	@echo "  make logs-positions-store - logy store"
	@echo "  make start             - spustí celý read-only stack (live-reader + store + webapp)"
	@echo "  make ingest-now        - skratka pre ingest-positions"
	@echo "  make down              - zastav všetko v compose"
	@echo "  make preview-demo      - otvor náhľad na demo proxy (http://localhost:8080/token)"
	@echo "  make preview-webapp    - otvor náhľad na webapp (http://localhost:5000)"
	@echo "  make clean             - stop + odstráni sieť/containers"
	@echo "\nAlias skratky:"
	@echo "  make demo | web | stop | live-reader | live-0dte | live-trader | logs-reader | logs-0dte | logs-trader"

prepare-data:
	@mkdir -p $(DATA_DIR)

config:
	$(COMPOSE) config

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build

up-demo: prepare-data
	$(COMPOSE) up -d --build token-proxy-demo saxo-token-daemon-demo

logs-demo:
	$(COMPOSE) logs -f token-proxy-demo saxo-token-daemon-demo

up-webapp: prepare-data
	$(COMPOSE) up -d --build token-proxy-demo token-proxy-live-reader webapp

logs-webapp:
	$(COMPOSE) logs -f webapp

up-live-reader: prepare-data
	$(COMPOSE) up -d --build saxo-token-daemon-live-reader token-proxy-live-reader

up-live-0dte: prepare-data
	$(COMPOSE) up -d --build saxo-token-daemon-live-0dte token-proxy-live-0dte

up-live-trader: prepare-data
	$(COMPOSE) up -d --build saxo-token-daemon-live-trader token-proxy-live-trader

logs-live-reader:
	$(COMPOSE) logs -f saxo-token-daemon-live-reader token-proxy-live-reader

logs-live-0dte:
	$(COMPOSE) logs -f saxo-token-daemon-live-0dte token-proxy-live-0dte

logs-live-trader:
	$(COMPOSE) logs -f saxo-token-daemon-live-trader token-proxy-live-trader

# Inicializácia prvotných tokenov pre LIVE READER (interaktívne OAuth)
# Použije env zo secrets/live/reader.env a uloží do ./data/tokens_live_reader.json
init-live-reader:
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/test_oauth_min.py --manual --tokens-file /data/tokens_live_reader.json

# Vytlačí iba autorizačnú URL pre LIVE READER (hodí sa, keď sa prehliadač neotvorí sám)
auth-url-live-reader:
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/test_oauth_min.py --manual --print-url-only --tokens-file /data/tokens_live_reader.json

# Automatizovaný OAuth pre LIVE READER (otvorí browser, spustí server, počká na dokončenie)
auto-oauth-live-reader:
	$(COMPOSE) run --rm -p 8765:8765 saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/auto_oauth_live_reader.py

# Automatizovaný OAuth pre DEMO (otvorí browser, spustí server, počká na dokončenie)
auto-oauth-demo:
	$(COMPOSE) run --rm -p 8765:8765 saxo-token-daemon-demo \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/auto_oauth_demo.py

# Spustí čítačku pozícií v rámci compose siete (token-proxy-live-reader:8080)
reader-status:
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/live_read_status.py --proxy http://token-proxy-live-reader:8080/token

reader-status-json:
	$(COMPOSE) run --rm -v $(DIR)/data:/data saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/live_read_status.py --proxy http://token-proxy-live-reader:8080/token --json-out /data/positions_live_reader.json

reader-accounts:
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/live_read_status.py --proxy http://token-proxy-live-reader:8080/token --no-positions --accounts

reader-orders:
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/live_read_status.py --proxy http://token-proxy-live-reader:8080/token --no-positions --orders

up-positions-store: prepare-data
	$(COMPOSE) up -d --build positions-store

# Ingest current positions snapshot into the store
ingest-positions:
	$(COMPOSE) build saxo-token-daemon-live-reader positions-store
	$(COMPOSE) run --rm saxo-token-daemon-live-reader \
		python3 /app/pc/PC/OpenAIGPT/SaxoAPI/Testovanie/live_read_status.py --proxy http://token-proxy-live-reader:8080/token --post-to-store http://positions-store:8090/ingest

logs-positions-store:
	$(COMPOSE) logs -f positions-store

# Komfortné skratky
start: prepare-data
	$(COMPOSE) up -d --build saxo-token-daemon-live-reader token-proxy-live-reader positions-store positions-ingestor webapp

ingest-now: ingest-positions

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down

# Náhľady (Preview) – v Codespaces/VS Code sa porty forwardujú automaticky
preview-webapp:
	@echo "Otvára sa webapp: http://localhost:5000"
	@echo "(Ak sa neotvorí automaticky, klikni na Porty -> 5000 -> Open in Browser/Preview)"

preview-demo:
	@echo "Otvára sa demo proxy token endpoint: http://localhost:8080/token"
	@echo "(Ak sa neotvorí automaticky, klikni na Porty -> 8080 -> Open in Browser/Preview)"

# Alias skratky
demo: up-demo
web: up-webapp
stop: down
live-reader: up-live-reader
live-0dte: up-live-0dte
live-trader: up-live-trader
logs-reader: logs-live-reader
logs-0dte: logs-live-0dte
logs-trader: logs-live-trader
