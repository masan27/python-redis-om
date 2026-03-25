# Python Redis OM

A high-performance FastAPI service that acts as a query and indexing engine for Redis OM models. Designed as a companion to the [laravel-redis-om](https://github.com/masan27/laravel-redis-om) package.

## Features

- **Dynamic Filtering**: Robust ORM-style query capabilities using Redisearch.
- **Multi-Model Support**: Easily register and query multiple Redis OM models.
- **Generic Key Operations**: Read-only access to any Redis key with automatic type detection (JSON, String, List, Hash).
- **Auto-Prefixing**: Intelligent global key prefixing to ensure consistent multi-tenancy or environment isolation.
- **Production Ready**: Multi-stage Docker builds and structured logging.

## Tech Stack

- **FastAPI**: Modern, high-performance web framework.
- **Redis OM (Python)**: Object Mapping for Redis and Redisearch.
- **Pydantic Settings**: Type-safe environment configuration.
- **Loguru**: Structured and beautiful logging.

## Getting Started

### Prerequisites

- Python 3.12+
- Redis Stack (with ReJSON and RediSearch modules)
- Poetry (recommended)

### Environment Configuration

Create a `.env` file in the root directory:

```env
APP_NAME="Redis OM Service"
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
GLOBAL_KEY_PREFIX=app_project_name
```

### Installation

1. **Local Setup (Poetry)**:
   ```bash
   # Configure poetry to create virtualenv in project directory (.venv)
   poetry config virtualenvs.in-project true --local
   
   # Use specific python version (optional but recommended)
   poetry env use python3.12
   
   # Install dependencies
   poetry install
   
   # Run service
   poetry run uvicorn app.main:app --reload
   ```

2. **Docker Setup**:
   ```bash
   docker-compose up -d
   ```

### Migrations

To create or update Redisearch indexes for your models:

```bash
# Run migrations
python migrate.py

# Force re-index (drops existing indexes)
python migrate.py --force
```

> **IMPORTANT**
> Ensure that the field types defined in your models match the actual data types stored in Redis. If there's a mismatch (e.g., a field is defined as `int` in the model but stored as a `string` in Redis), the indexing engine may fail to detect or index the data correctly.

## API Reference

### 1. ORM-style Query
`POST /query`

Example payload:
```json
{
  "model": "users",
  "filters": [
    {"field": "status", "op": "==", "value": "active"},
    {"field": "name", "op": "like", "value": "john"}
  ],
  "limit": 10,
  "offset": 0,
  "sort_by": "created_at",
  "sort_asc": false
}
```

### 2. Get by Key
`GET /key/{full_key}`

Automatically detects the data type and prepends the `GLOBAL_KEY_PREFIX` if missing.

## Registering New Models

1. Define your model in `app/models/your_model.py` (inherit from `JsonModel`).
2. Register it in `app/models/__init__.py`:
   ```python
   MODEL_REGISTRY = {
       "your_model_name": YourModelClass,
   }
   ```
3. Run `python migrate.py` to create the index.

## Related Projects

- **[laravel-redis-om](https://github.com/masan27/laravel-redis-om)**: Laravel support for this service, enabling direct Redis access with Python search fallback.

## License

Custom Fork-Only License. Please see the [LICENSE](LICENSE) file for more information.
