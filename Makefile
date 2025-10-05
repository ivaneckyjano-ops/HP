# Makefile pre rýchly beh a správu služieb
# Požiadavka: Docker + Docker Compose

DIR := pc/PC/OpenAIGPT/SaxoAPI/Testovanie
COMPOSE := docker compose -f $(DIR)/docker-compose.yml
DATA_DIR := $(DIR)/data

.PHONY: help prepare-data config ps build up-demo logs-demo down up-webapp logs-webapp up-live-reader up-live-0dte up-live-trader logs-live-reader logs-live-0dte logs-live-trader preview-webapp preview-demo clean

help:
	@echo "Dostupné ciele:"
	@echo "  make config            - validácia docker-compose"
	@echo "  make ps                - stav služieb"
	@echo "  make up-demo           - spusti demo (daemon + proxy)"
	@echo "  make logs-demo         - logy demá"
	@echo "  make up-webapp         - spusti webapp + potrebné proxy"
	@echo "  make logs-webapp       - logy webapp"
	@echo "  make up-live-reader    - spusti live reader (daemon + proxy)"
	@echo "  make up-live-0dte      - spusti live 0dte (daemon + proxy)"
	@echo "  make up-live-trader    - spusti live trader (daemon + proxy)"
	@echo "  make down              - zastav všetko v compose"
	@echo "  make preview-demo      - otvor náhľad na demo proxy (http://localhost:8080/token)"
	@echo "  make preview-webapp    - otvor náhľad na webapp (http://localhost:5000)"
	@echo "  make clean             - stop + odstráni sieť/containers"

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
	$(COMPOSE) up -d --build webapp token-proxy-demo token-proxy-live

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
