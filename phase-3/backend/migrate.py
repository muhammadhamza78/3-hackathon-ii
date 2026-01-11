# """
# Standalone Migration Script
# Run database migrations without importing app modules.
# """

# import sys
# import os
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     print("❌ Error: DATABASE_URL not found in environment")
#     sys.exit(1)

# # Create engine
# engine = create_engine(DATABASE_URL)

# print("Running database migration: Add profile and soft delete fields\n")

# with engine.connect() as conn:
#     # Add columns to users table
#     try:
#         conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(255)"))
#         conn.commit()
#         print("✓ Added 'name' column to users table")
#     except Exception as e:
#         if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
#             print("⚠ Column 'name' already exists in users table")
#         else:
#             print(f"⚠ Error adding 'name' column: {e}")

#     try:
#         conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500)"))
#         conn.commit()
#         print("✓ Added 'profile_picture' column to users table")
#     except Exception as e:
#         if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
#             print("⚠ Column 'profile_picture' already exists in users table")
#         else:
#             print(f"⚠ Error adding 'profile_picture' column: {e}")

#     # Add column to tasks table
#     try:
#         conn.execute(text("ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP"))
#         conn.commit()
#         print("✓ Added 'deleted_at' column to tasks table")
#     except Exception as e:
#         if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
#             print("⚠ Column 'deleted_at' already exists in tasks table")
#         else:
#             print(f"⚠ Error adding 'deleted_at' column: {e}")

# print("\n✅ Migration completed!")






# """
# Standalone Migration Script
# Run database migrations safely without importing app modules.
# """

# import sys
# import os
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv

# # --------------------------
# # Load environment variables
# # --------------------------
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     print("❌ Error: DATABASE_URL not found in environment")
#     sys.exit(1)

# # --------------------------
# # Create SQLAlchemy engine
# # --------------------------
# engine = create_engine(DATABASE_URL)
# print("🔧 Running database migration: Add profile and soft delete fields\n")

# # --------------------------
# # Migration statements
# # --------------------------
# migrations = [
#     {
#         "table": "users",
#         "sql": "ALTER TABLE users ADD COLUMN name VARCHAR(255)",
#         "description": "'name' column"
#     },
#     {
#         "table": "users",
#         "sql": "ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500)",
#         "description": "'profile_picture' column"
#     },
#     {
#         "table": "tasks",
#         "sql": "ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP",
#         "description": "'deleted_at' column"
#     }
# ]

# # --------------------------
# # Apply migrations
# # --------------------------
# with engine.connect() as conn:
#     for migration in migrations:
#         try:
#             conn.execute(text(migration["sql"]))
#             conn.commit()
#             print(f"✓ Added {migration['description']} to {migration['table']} table")
#         except Exception as e:
#             # Handle "already exists" gracefully
#             if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
#                 print(f"⚠ {migration['description']} already exists in {migration['table']} table")
#             else:
#                 print(f"⚠ Error adding {migration['description']}: {e}")

# print("\n✅ Migration completed successfully!")





"""
Standalone Migration Script
Run database migrations safely without importing app modules.
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in environment")
    sys.exit(1)

# --------------------------
# Create SQLAlchemy engine
# --------------------------
engine = create_engine(DATABASE_URL, future=True)
inspector = inspect(engine)

print("🔧 Running database migration: Add profile and soft delete fields\n")

# --------------------------
# Helper: check column exists
# --------------------------
def column_exists(table_name: str, column_name: str) -> bool:
    columns = inspector.get_columns(table_name)
    return any(col["name"] == column_name for col in columns)

# --------------------------
# Apply migrations safely
# --------------------------
with engine.begin() as conn:
    # USERS TABLE
    if not column_exists("users", "name"):
        conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(255)"))
        print("✓ Added 'name' column to users table")
    else:
        print("⚠ 'name' column already exists in users table")

    if not column_exists("users", "profile_picture"):
        conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500)"))
        print("✓ Added 'profile_picture' column to users table")
    else:
        print("⚠ 'profile_picture' column already exists in users table")

    # TASKS TABLE
    if not column_exists("tasks", "deleted_at"):
        conn.execute(text("ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP"))
        print("✓ Added 'deleted_at' column to tasks table")
    else:
        print("⚠ 'deleted_at' column already exists in tasks table")

print("\n✅ Migration completed successfully!")
