#!/usr/bin/env bash
set -euo pipefail

# Simple deploy script to run on the droplet after copying/extracting the release archive.
# Usage: sudo ./deploy.sh [TARGET_DIR]
# Example: sudo ./deploy.sh /opt/saxo

TARGET_DIR=${1:-/opt/saxo}
USER_TO_OWN=${SUDO_USER:-${USER}}

echo "Deploying to ${TARGET_DIR} (owner: ${USER_TO_OWN})"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. You can install it with: sudo apt update && sudo apt install -y docker.io docker-compose-plugin"
  echo "Or run this script with --install-prereqs to attempt auto-install (not recommended without review)."
fi

mkdir -p "${TARGET_DIR}"
echo "Copying files to ${TARGET_DIR}..."
rsync -a --exclude='__pycache__' ../Testovanie/ "${TARGET_DIR}/Testovanie/"
rsync -a ./token_proxy.py "${TARGET_DIR}/"
rsync -a ./deploy.md "${TARGET_DIR}/"
rsync -a ./saxo-token-daemon.service "${TARGET_DIR}/saxo-token-daemon.service" || true

echo "Setting ownership to ${USER_TO_OWN}..."
chown -R "${USER_TO_OWN}:" "${TARGET_DIR}"

echo "Preparing tokens folder /var/lib/saxo ..."
mkdir -p /var/lib/saxo
touch /var/lib/saxo/tokens_min.json
chown "${USER_TO_OWN}:" /var/lib/saxo/tokens_min.json
chmod 600 /var/lib/saxo/tokens_min.json

# If .env exists in the copied Testovanie folder, protect it
if [ -f "${TARGET_DIR}/Testovanie/.env" ]; then
  chmod 600 "${TARGET_DIR}/Testovanie/.env"
  chown root:root "${TARGET_DIR}/Testovanie/.env" || true
  echo "Found .env in Testovanie/ — ensure it contains correct SAXO_CLIENT_ID and SAXO_CLIENT_SECRET"
fi

echo "Starting docker-compose (build + up)"
cd "${TARGET_DIR}/Testovanie"
docker compose up -d --build

echo "Deployment finished. Containers status:"
docker compose ps

echo
echo "If you want to install systemd unit for the daemon, run on the droplet as root:"
echo "  sudo cp ${TARGET_DIR}/saxo-token-daemon.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now saxo-token-daemon.service"

echo "You can follow logs with: docker compose logs -f saxo-token-daemon"
