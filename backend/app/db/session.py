from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Vamos criar este arquivo depois

# URL de conexão com o banco (ex: "postgresql://user:pass@host/db_name")
# Ou "sqlite:///./test.db" para um teste rápido com SQLite
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # O argumento connect_args é necessário apenas para SQLite
    # , connect_args={"check_same_thread": False} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()