FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /app/data && chown -R app:app /app/data
USER app

EXPOSE 8000

# Default: run gunicorn
CMD ["uv", "run", "gunicorn", "domuscura.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120"]
