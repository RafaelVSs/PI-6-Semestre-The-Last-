from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

# Criar engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

# Criar sessão assíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
