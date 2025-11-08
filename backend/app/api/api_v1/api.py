from fastapi import APIRouter
# --- CORREÇÃO AQUI ---
# O caminho deve ser 'app.api.api_v1.endpoints'
from app.api.api_v1.endpoints import auth_api
from app.api.api_v1.endpoints import pacientes_api

api_router = APIRouter()

# Inclui o roteador de autenticação
api_router.include_router(
    auth_api.router, 
    prefix="/auth", # O prefixo será /api/v1/auth
    tags=["Autenticação"]
)

# Inclui o roteador de pacientes
api_router.include_router(
    pacientes_api.router, 
    prefix="/pacientes", # Caminho: /api/v1/pacientes
    tags=["Pacientes"])