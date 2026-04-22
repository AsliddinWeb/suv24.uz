# Alembic

Database migration management.

```bash
# Generate migration (autogenerate from models)
alembic revision --autogenerate -m "add something"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Current version
alembic current
```

Migration fayllari `versions/` papkasida saqlanadi.
