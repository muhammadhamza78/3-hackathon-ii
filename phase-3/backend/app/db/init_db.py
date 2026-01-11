from sqlmodel import SQLModel
from app.db.session import engine
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation

def init_db():
    print("📦 Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tables ready!")

if __name__ == "__main__":
    init_db()
