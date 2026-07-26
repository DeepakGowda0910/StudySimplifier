from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def _add_missing_columns(conn):
    """SQLite create_all() never alters existing tables — patch in new columns for older DBs."""
    result = await conn.execute(text("PRAGMA table_info(users)"))
    existing_cols = {row[1] for row in result.fetchall()}
    migrations = {
        "role": "ALTER TABLE users ADD COLUMN role VARCHAR(30) DEFAULT 'studysmart_user'",
        "school_id": "ALTER TABLE users ADD COLUMN school_id INTEGER",
        "full_name": "ALTER TABLE users ADD COLUMN full_name VARCHAR(200)",
    }
    for col, ddl in migrations.items():
        if col not in existing_cols:
            await conn.execute(text(ddl))

async def init_db():
    from models import user, flashcard, achievement, notes, planner, quiz
    from models import school, curriculum, content_chunk
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _add_missing_columns(conn)
