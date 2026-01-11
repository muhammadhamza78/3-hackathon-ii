"""Quick database test and migration script."""

import sys
from sqlmodel import SQLModel, Session, create_engine, text
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database...")
print(f"URL: {DATABASE_URL[:30]}..." if DATABASE_URL else "ERROR: No DATABASE_URL")

if not DATABASE_URL:
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Test connection
try:
    with Session(engine) as session:
        session.execute(text("SELECT 1"))
    print("SUCCESS: Database connection working!\n")
except Exception as e:
    print(f"ERROR: Database connection failed: {e}")
    sys.exit(1)

# Import models AFTER confirming connection
try:
    from app.models.user import User
    from app.models.task import Task
    print("SUCCESS: Models imported\n")
except Exception as e:
    print(f"ERROR: Failed to import models: {e}")
    sys.exit(1)

# Create/update tables
print("Running SQLModel.metadata.create_all()...")
try:
    SQLModel.metadata.create_all(engine)
    print("SUCCESS: Tables created/updated!\n")
except Exception as e:
    print(f"ERROR: Failed to create/update tables: {e}")
    sys.exit(1)

# Verify columns exist
print("Verifying schema...")
with Session(engine) as session:
    # Check users table
    result = session.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """))
    user_columns = [row[0] for row in result]
    print(f"users table columns: {', '.join(user_columns)}")

    if 'name' in user_columns and 'profile_picture' in user_columns:
        print("   SUCCESS: Profile columns present")
    else:
        missing = []
        if 'name' not in user_columns:
            missing.append('name')
        if 'profile_picture' not in user_columns:
            missing.append('profile_picture')
        print(f"   WARNING: Missing columns: {', '.join(missing)}")

    # Check tasks table
    result = session.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        ORDER BY ordinal_position
    """))
    task_columns = [row[0] for row in result]
    print(f"tasks table columns: {', '.join(task_columns)}")

    if 'deleted_at' in task_columns:
        print("   SUCCESS: Soft delete column present")
    else:
        print("   WARNING: Missing column: deleted_at")

print("\nDatabase ready!")
