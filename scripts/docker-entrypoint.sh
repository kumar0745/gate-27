#!/bin/sh
set -eu

DB_PATH="${GATEPATH_DATABASE_PATH:-/var/data/gatepath.db}"
case "$DB_PATH" in
  /*) DB_DIR="$(dirname "$DB_PATH")" ;;
  *) DB_DIR="/app/$(dirname "$DB_PATH")" ;;
esac
mkdir -p "$DB_DIR"
chown -R gatepath:gatepath "$DB_DIR"
exec gosu gatepath "$@"
