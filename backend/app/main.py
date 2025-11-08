from fastapi import FastAPI
# 1. Importe o 'api_router' principal (de app/api/api_v1/api.py)
from app.api.api_v1.api import api_router 
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware

# --- Criação das Tabelas ---
Base.metadata.create_all(bind=engine)
# ---------------------------

app = FastAPI(
    title="Conecta+Saúde - Backend Principal",
    description="API para gerenciamento de pacientes e orquestração de serviços de ML/LLM.",
    version="1.0.0"
)

# 2. Defina as origens permitidas (CONFIRME A PORTA DO SEU FRONTEND)
origins = [
    "http://localhost:3000", 
    "http://localhost",
]

# 3. Adicione o middleware ao 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Inclua o 'api_router' principal com o prefixo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def health_check():
    """Verifica se a API está online."""
    return {"status": "ok", "service": "Backend Principal"}