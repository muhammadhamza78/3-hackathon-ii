from sqlmodel import Session, create_engine, SQLModel
from typing import Generator
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine_args = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

# Apply pooling ONLY for non-SQLite databases
if not DATABASE_URL.startswith("sqlite"):
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 0,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    })

engine = create_engine(DATABASE_URL, **engine_args)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    from app.models.user import User
    from app.models.task import Task

    SQLModel.metadata.create_all(engine)

