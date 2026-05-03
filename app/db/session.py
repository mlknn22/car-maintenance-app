from app.db.database import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

