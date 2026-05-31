# Week 15: Deployment & Production

## 🎯 Learning Objectives

- Containerize Django with Docker
- Set up production configuration
- Deploy with Docker Compose
- Configure CI/CD with GitHub Actions
- Implement security best practices

The CI/CD pipeline you'll set up — every push runs through GitHub Actions before any artifact reaches production:

```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
flowchart LR
    Code[git push]

    subgraph ci["GitHub Actions"]
        direction LR
        Lint["ruff check"]
        Test["pytest --cov"]
        Build["docker build"]
        Lint --> Test --> Build
    end

    Deploy[deploy to host]

    Code --> ci --> Deploy
```

## 📚 Required Reading

| Resource                                                                                         | Section     | Time   |
| ------------------------------------------------------------------------------------------------ | ----------- | ------ |
| [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/) | Full page   | 30 min |
| [Docker Tutorial](https://docs.docker.com/get-started/)                                          | Parts 1-4   | 60 min |
| [12-Factor App](https://12factor.net/)                                                           | All factors | 30 min |

---

## Docker Setup

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgres://postgres:postgres@db:5432/taskmaster
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=taskmaster
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

  celery:
    build: .
    command: uv run celery -A config worker -l info
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/taskmaster
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: uv run celery -A config beat -l info
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/taskmaster
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### `nginx.conf` — referenced above, write it now

The compose file mounts `./nginx.conf` into the nginx container. Create it at the project root:

```nginx
# nginx.conf
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;

        # If WhiteNoise serves static files, nginx doesn't need to. But media
        # uploads still flow through here.
        location /media/ {
            alias /app/media/;
        }

        # Optional: serve static directly from nginx for max throughput.
        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
}
```

For HTTPS production, terminate TLS in a load balancer (ALB, GCP LB, Cloudflare) and keep this nginx as a plain HTTP backend, or extend with `listen 443 ssl;` + cert paths.

### Settings split — refactor before adding `production.py`

We've been editing one monolithic `config/settings.py` since Week 03. The production-ready layout splits it by environment so each context inherits a shared base:

```
config/
├── __init__.py
└── settings/
    ├── __init__.py        # empty marker
    ├── base.py            # everything common (INSTALLED_APPS, MIDDLEWARE, etc.)
    ├── dev.py             # imports base, flips DEBUG=True, adds debug_toolbar
    └── production.py      # imports base, hardens for prod
```

**Step 1 — convert the single file into the split:**

```bash
cd config
mkdir settings
git mv settings.py settings/base.py   # preserves history
touch settings/__init__.py
```

**Step 2 — strip dev-only knobs out of `base.py`** (anything `DEBUG`-gated, anything with secrets, anything env-specific). Move them into `dev.py` and `production.py` respectively.

**Step 3 — create `dev.py`:**

```python
# config/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Optional: Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware', *MIDDLEWARE]
INTERNAL_IPS = ['127.0.0.1']
```

**Step 4 — tell Django which file to use.** Set `DJANGO_SETTINGS_MODULE` in your environment (or `manage.py`):

```python
# manage.py — make the default explicit
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
```

Production then sets `DJANGO_SETTINGS_MODULE=config.settings.production` via env var (Dockerfile, systemd unit, Procfile — wherever).

**Step 5 — now write `production.py`:**

```python
# config/settings/production.py
from decouple import config, Csv   # explicit import — was missing in earlier draft
from .base import *
import dj_database_url

DEBUG = False

SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True              # opt into the browser preload list (once stable)
SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER deliberately omitted — the X-XSS-Protection header
# it sets was retired by Chrome/Edge years ago and Mozilla recommends against
# enabling it. Modern XSS defense is a Content Security Policy header instead.
X_FRAME_OPTIONS = 'DENY'

# Static files — WhiteNoise serves them in production.
# 1) Install: uv add whitenoise
# 2) Wire the middleware (do this in base.py, not here, so dev gets it too):
#       MIDDLEWARE = [
#           'django.middleware.security.SecurityMiddleware',
#           'whitenoise.middleware.WhiteNoiseMiddleware',   # ← add directly after security
#           ...rest...
#       ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Modern Django (4.2+) — use the STORAGES dict, not STATICFILES_STORAGE.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run linting
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest --cov
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
          SECRET_KEY: test-secret-key

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          echo "Deploy to your hosting provider here"
```

---

## Deployment Commands

```bash
# Build and run
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web uv run python manage.py migrate

# Create superuser
docker-compose exec web uv run python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Stop all
docker-compose down
```

---

## 📋 Submission Checklist

- [ ] Dockerfile working
- [ ] docker-compose.yml with all services
- [ ] Production settings configured
- [ ] GitHub Actions CI/CD pipeline
- [ ] Security checklist passed
- [ ] Documentation updated

---

**Next**: [Week 16: Capstone Project →](../week-16-capstone/readme.md)
