FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    GATEPATH_SECURE_COOKIES=true \
    GATEPATH_DATABASE_PATH=/var/data/gatepath.db

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system gatepath \
    && useradd --system --gid gatepath --home-dir /nonexistent --shell /usr/sbin/nologin gatepath \
    && mkdir -p /var/data \
    && chown -R gatepath:gatepath /var/data

COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY backend/app ./backend/app
COPY frontend ./frontend
COPY .env.example ./.env.example
COPY scripts/docker-entrypoint.sh /usr/local/bin/gatepath-entrypoint
RUN chmod 0755 /usr/local/bin/gatepath-entrypoint \
    && chown -R root:root /app

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/gatepath-entrypoint"]
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
