# HP Repository

Tento repozitár obsahuje veci pre PC a rôzne droplets (servery).

## Štruktúra

- `pc/` - Veci pre lokálne PC (napr. OpenAIGPT SaxoAPI)
- `droplets/` - Priečinok pre rôzne droplets
  - `droplet1/` - Prvý droplet (napr. var02 proxy)
  - `droplet2/` - Druhý droplet (prázdny, pre budúce použitie)
- `webapp/` - Web aplikácia
- `scripts/` - Pomocné skripty
- `deploy_release/` - Deploy a release veci

## Ako pridať nový droplet

1. Vytvor nový priečinok v `droplets/`, napr. `droplet3/`
2. Skopíruj potrebné súbory (docker-compose.yml, Dockerfile, atď.)
3. Aktualizuj README.md v priečinku

## Deploy

Pozri `deploy_release/deploy.md` pre návod na nasadenie.
