FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

ENV ENV=docker
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Делаем entrypoint.sh исполняемым (если он есть)
RUN chmod +x entrypoint.sh 2>/dev/null || true

# Открываем порт
EXPOSE 8000

# Лучше явно указать команду
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]