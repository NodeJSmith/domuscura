# Domuscura

Self-hosted home maintenance tracker. Tracks recurring maintenance schedules, one-off projects, known issues, assets, and spending.

The name is Latin: *domus* (house) + *cura* (care).

## Quick Start (Docker)

```bash
cp .env.example .env
# Edit .env — at minimum change DJANGO_SECRET_KEY

docker compose up -d
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py seed_data   # optional: load starter schedules
```

Open [http://localhost:8000](http://localhost:8000).

## Quick Start (Local)

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/NodeJSmith/domuscura.git
cd domuscura
make setup   # installs deps, runs migrations, seeds data
make dev     # starts dev server on http://localhost:8000
```

Or without Make:

```bash
uv sync --dev
uv run python manage.py migrate
uv run python manage.py seed_data
uv run python manage.py runserver
```

## What You Get

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | At-a-glance view of overdue, due soon, and never-done schedules |
| Schedules | `/schedules/` | Recurring maintenance tasks with filtering and sorting |
| Projects | `/projects/` | One-time improvements, repairs, upgrades |
| Issues | `/issues/` | Known problems and things to watch |
| Assets | `/assets/` | Equipment registry with warranty tracking |
| Spending | `/spending/` | Cost tracking with monthly and category breakdowns |
| Admin | `/admin/` | Django admin for direct data access |

## Tech Stack

- **Django 5.1** — server-rendered, no SPA complexity
- **PicoCSS** — classless CSS framework for clean defaults
- **HTMX** — partial page updates without writing JavaScript
- **Alpine.js** — lightweight reactivity for modals/toggles
- **SQLite** — zero-config database, perfect for single-household use
- **Gunicorn** — production WSGI server (included)

## Configuration

All settings are controlled via environment variables. See [`.env.example`](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | insecure default | **Change in production** |
| `DJANGO_DEBUG` | `True` | Set `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated hostnames |
| `DJANGO_DB_NAME` | `db.sqlite3` | Path to SQLite database |
| `NTFY_URL` | *(empty)* | ntfy server URL for notifications |
| `NTFY_TOPIC` | `domuscura` | ntfy topic name |

## Development

```bash
make install   # install all dependencies including dev
make test      # run pytest
make check     # run Django system checks
make shell     # open Django shell
```

## Project Structure

```
domuscura/
├── domuscura/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── maintenance/        # Main app
│   ├── models.py       # 7 models: Location, Asset, Schedule, Project, Issue, WorkLog, Notification
│   ├── views/          # View modules: dashboard, schedule, project, issue, asset, spending, work_log
│   ├── forms.py        # ModelForms for all entities
│   ├── templates/      # Django templates (base + per-entity + partials)
│   └── management/     # seed_data command
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml      # Dependencies managed with uv
```

## License

MIT
