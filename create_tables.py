"""
Script para criar as tabelas no banco de dados PostgreSQL
Execute este arquivo para inicializar o banco de dados
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models import Base


async def create_tables():
    """Cria todas as tabelas definidas nos modelos SQLAlchemy"""
    print("Conectando ao banco de dados...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_size=10,
        max_overflow=20
    )
    
    try:
        print("Criando tabelas no banco de dados...")
        async with engine.begin() as conn:
            # Cria todas as tabelas definidas nos modelos
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise
    finally:
        await engine.dispose()
        print("Conexão com o banco de dados fechada.")


async def drop_tables():
    """Remove todas as tabelas do banco de dados (use com cuidado!)"""
    print("⚠️  ATENÇÃO: Esta operação irá remover todas as tabelas!")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_size=10,
        max_overflow=20
    )
    
    try:
        print("Removendo tabelas do banco de dados...")
        async with engine.begin() as conn:
            # Remove todas as tabelas
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tabelas removidas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao remover tabelas: {e}")
        raise
    finally:
        await engine.dispose()
        print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        # python create_tables.py drop
        asyncio.run(drop_tables())
    else:
        # python create_tables.py
        asyncio.run(create_tables())