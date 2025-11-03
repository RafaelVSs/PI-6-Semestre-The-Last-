import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

#Cria uma fábrica de sessões assíncronas
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

#Função de dependência para obter uma sessão
async def get_db_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


async def main():
    print("Conectando ao banco de dados...")
    try:
        async with engine.connect() as connection:
            # Executa uma query simples para verificar a conexão
            result = await connection.execute(text("SELECT 1"))
            if result.scalar_one() == 1:
                print("✅ Conexão com o PostgreSQL bem-sucedida!")
            else:
                print("❌ A conexão funcionou, mas a query de teste falhou.")
    except Exception as e:
        print(f"❌ Falha ao conectar com o banco de dados: {e}")
    finally:
        # Garante que o pool de conexões seja fechado corretamente
        await engine.dispose()
        print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    asyncio.run(main())