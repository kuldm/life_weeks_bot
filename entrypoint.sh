#!/bin/sh
set -e

echo "Waiting for Postgres at $DB_HOST:$DB_PORT…"
# Ждём готовности БД
until pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; do
  echo -n "."
  sleep 1
done
echo "\nPostgres is up — running migrations"

# Запускаем alembic напрямую (не через uv)
uv run alembic upgrade head

# Пускаем в ход CMD (uv run -m app.main)
exec "$@"
