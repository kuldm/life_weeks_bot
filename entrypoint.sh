#!/usr/bin/env sh
set -e

echo "Waiting for Postgres at $DB_HOST:$DB_PORT…"
# Ждём готовности БД
export PGPASSWORD="$DB_PASS"
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
  echo -n "."
  sleep 10
done
unset PGPASSWORD
echo "\nPostgres is up — running migrations"

# Запускаем alembic напрямую (не через uv)
uv run alembic upgrade head

# Пускаем в ход CMD (uv run app/main.py)
exec "$@"
