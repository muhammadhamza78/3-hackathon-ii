# Database Migrations

This directory contains database migration scripts for schema changes.

## Running Migrations

### Upgrade (Apply Migration)

```bash
cd backend
python -m app.migrations.001_add_profile_and_soft_delete
```

### Downgrade (Rollback Migration)

```bash
cd backend
python -m app.migrations.001_add_profile_and_soft_delete downgrade
```

## Migration List

1. **001_add_profile_and_soft_delete.py**
   - Adds `name` and `profile_picture` columns to `users` table
   - Adds `deleted_at` column to `tasks` table for soft delete support
   - Spec: specs/002-dashboard-ux-enhancements/spec.md

## Notes

- Migrations are idempotent - running them multiple times is safe
- For new installations, use `init_db()` which creates tables with all fields
- For existing databases, run migrations to add new columns
- Always backup your database before running migrations in production
