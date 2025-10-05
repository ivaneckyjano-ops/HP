# Droplet README template

Krátky popis dropletu (názov, účel, kontakty):
- Názov: ...
- Účel: ...
- Prostredie: sim/live
- Kontakty: ...

## Služby
- token-daemon: refresher Saxo tokenov
- token-proxy: HTTP endpoint /token
- webapp: UI (ak je súčasťou)

## Cesty a súbory
- docker-compose.yml
- Dockerfile (ak je vlastný)
- secrets/ (ak je potrebné)

## Nasadenie
```
# build & run
docker compose up -d --build
# logy
docker compose logs -f
```

## Poznámky
- Firewall a porty: ...
- TLS/reverzný proxy: ...
- Monitoring: ...
