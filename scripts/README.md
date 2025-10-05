# Droplet snapshot helpers

`fetch_droplet.sh` - jednoduchý skript používajúci `rsync` a `ssh` na stiahnutie adresára z dropletu do lokálneho repozitára. Možnosť vytvoriť novú git vetvu so snapshotom.

Bezpečnosť:

- Skript predpokladá, že máte SSH prístup k dropletu. Neposkytujte heslá v skriptoch.
- Overte obsah snapshotu pred commitom — môže obsahovať citlivé súbory (certifikáty, `.env`, atď.). Upravte `.gitignore` ak nechcete ukladať citlivé údaje.

Použitie:

```bash
./fetch_droplet.sh deploy@1.2.3.4 /home/deploy /path/to/local/snapshot --branch droplet-sync
```
