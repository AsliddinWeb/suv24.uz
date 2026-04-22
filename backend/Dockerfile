FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Tashkent

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /app

COPY pyproject.toml README.md* ./
RUN pip install --upgrade pip && \
    pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "python-multipart>=0.0.9" \
                "pydantic>=2.8.0" "pydantic-settings>=2.4.0" "email-validator>=2.2.0" \
                "sqlalchemy>=2.0.35" "alembic>=1.13.2" "asyncpg>=0.29.0" "psycopg[binary]>=3.2.0" \
                "redis>=5.0.8" "slowapi>=0.1.9" \
                "celery>=5.4.0" \
                "argon2-cffi>=23.1.0" "passlib[bcrypt]>=1.7.4" "python-jose[cryptography]>=3.3.0" "pyjwt>=2.9.0" \
                "httpx>=0.27.0" "tenacity>=9.0.0" "python-dateutil>=2.9.0" "orjson>=3.10.0" \
                "sentry-sdk[fastapi]>=2.13.0" "structlog>=24.4.0"

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
