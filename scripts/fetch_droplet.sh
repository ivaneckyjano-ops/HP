#!/usr/bin/env bash
set -euo pipefail
# fetch_droplet.sh
# Usage: ./fetch_droplet.sh <user@host> <remote_path> [local_snapshot_dir] [--branch BRANCH]
# Example: ./fetch_droplet.sh deploy@1.2.3.4 /home/deploy /workspaces/narbon-jan-HP/droplet_snapshot --branch droplet-sync

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <user@host> <remote_path> [local_snapshot_dir] [--branch BRANCH]"
  exit 2
fi

REMOTE_HOST="$1"
REMOTE_PATH="$2"
LOCAL_DIR="${3:-./droplet_snapshot}"
BRANCH=""

shift 2
while [ "$#" -gt 0 ]; do
  case "$1" in
    --branch)
      shift
      BRANCH="$1"
      ;;
    *)
      ;;
  esac
  shift || true
done

mkdir -p "$LOCAL_DIR"
echo "Fetching from ${REMOTE_HOST}:${REMOTE_PATH} -> ${LOCAL_DIR}"

# Use rsync over ssh. Accept new host keys interactively but don't disable checks.
rsync -avz --delete -e "ssh -o StrictHostKeyChecking=accept-new" "${REMOTE_HOST}:${REMOTE_PATH}/" "${LOCAL_DIR}/"

echo "Snapshot fetched into ${LOCAL_DIR}"

if [ -n "$BRANCH" ]; then
  # Create a temp branch, add snapshot, commit and push
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Not a git repo (run this from the repository root to commit snapshot). Skipping git commit." >&2
    exit 0
  fi

  TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
  SNAP_BRANCH="${BRANCH}-${TIMESTAMP}"
  git checkout -b "$SNAP_BRANCH"
  git add --all "$LOCAL_DIR"
  git commit -m "droplet snapshot ${TIMESTAMP} from ${REMOTE_HOST}:${REMOTE_PATH}"
  echo "Created branch $SNAP_BRANCH. Push it to origin with: git push -u origin $SNAP_BRANCH"
fi

echo "Done."
