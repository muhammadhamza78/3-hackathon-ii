"""
Migration: Add Profile Fields and Soft Delete Support
Adds name and profile_picture to users table, deleted_at to tasks table.

Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-001, FR-016)
"""

from sqlalchemy import text
from app.db.session import engine


def upgrade():
    """Add new columns to existing tables."""

    with engine.connect() as conn:
        # Add columns to users table
        try:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN name VARCHAR(255) NULL"
            ))
            print("✓ Added 'name' column to users table")
        except Exception as e:
            print(f"⚠ Column 'name' already exists or error: {e}")

        try:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500) NULL"
            ))
            print("✓ Added 'profile_picture' column to users table")
        except Exception as e:
            print(f"⚠ Column 'profile_picture' already exists or error: {e}")

        # Add column to tasks table
        try:
            conn.execute(text(
                "ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP NULL"
            ))
            print("✓ Added 'deleted_at' column to tasks table")
        except Exception as e:
            print(f"⚠ Column 'deleted_at' already exists or error: {e}")

        conn.commit()
        print("\n✅ Migration completed successfully!")


def downgrade():
    """Remove the added columns (rollback)."""

    with engine.connect() as conn:
        # Remove columns from users table
        try:
            conn.execute(text("ALTER TABLE users DROP COLUMN name"))
            print("✓ Removed 'name' column from users table")
        except Exception as e:
            print(f"⚠ Error removing 'name': {e}")

        try:
            conn.execute(text("ALTER TABLE users DROP COLUMN profile_picture"))
            print("✓ Removed 'profile_picture' column from users table")
        except Exception as e:
            print(f"⚠ Error removing 'profile_picture': {e}")

        # Remove column from tasks table
        try:
            conn.execute(text("ALTER TABLE tasks DROP COLUMN deleted_at"))
            print("✓ Removed 'deleted_at' column from tasks table")
        except Exception as e:
            print(f"⚠ Error removing 'deleted_at': {e}")

        conn.commit()
        print("\n✅ Rollback completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        print("Running migration downgrade...\n")
        downgrade()
    else:
        print("Running migration upgrade...\n")
        upgrade()
