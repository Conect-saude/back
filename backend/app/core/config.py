from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Banco de Dados
    DATABASE_URL: str

    # Segurança JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Microserviços
    ML_SERVICE_URL: str
    LLM_SERVICE_URL: str

    class Config:
        env_file = ".env"

# Instância única que será importada por outros arquivos
settings = Settings()