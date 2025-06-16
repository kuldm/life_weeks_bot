# 1. Берём базовый образ Python 3.13-slim
FROM python:3.13-slim

# Чтобы логи сразу шли в stdout без буферизации
# ENV PYTHONUNBUFFERED=1

# Чтобы apt не спрашивал о подтверждении лицензий для ttf-mscorefonts-installer
ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем системные зависимости (включая шрифты)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        fonts-dejavu-core \
        postgresql-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Копируем файлы с описанием зависимостей, чтобы слой кешировался
COPY pyproject.toml uv.lock /app/

# 3. Устанавливаем UV (он разберёт зависимости из pyproject.toml)
RUN pip install --upgrade pip \
 && pip install uv

# 4. Запускаем UV, чтобы он поставил всё из pyproject.toml/uv.lock
RUN uv sync

# 5. Теперь копируем весь код бота (main.py, settings.py и т.д.)
COPY . /app

# 8. Копируем скрипт миграции и делаем его исполняемым
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# 9. Скрипт-мигратор запускается первым, затем передаёт управление UV
ENTRYPOINT ["/app/entrypoint.sh"]

# 6. Команда по умолчанию: запускаем через UV в режиме модуля.
# Это гарантирует корректный PYTHONPATH и позволяет импортировать пакет app.
CMD ["uv", "run", "-m", "app.main"]

