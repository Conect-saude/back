import httpx
from fastapi import HTTPException, status
from app.core.config import settings

# Usamos um AsyncClient para chamadas de API assíncronas
# Isso evita que nosso servidor trave enquanto espera a resposta do ML/LLM
client = httpx.AsyncClient()

async def call_ml_service(data: dict) -> dict:
    """
    Chama o microserviço de classificação de ML.
    (Esta é a função que estava faltando)
    """
    url = settings.ML_SERVICE_URL # "http://localhost:8001/classify"
    
    try:
        response = await client.post(url, json=data)
        response.raise_for_status() # Lança exceção se for 4xx ou 5xx
        return response.json()
    
    except httpx.HTTPStatusError as e:
        # O serviço de ML retornou um erro (ex: 422 Unprocessable Entity)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro ao classificar paciente (ML): {e.response.json()}"
        )
    except httpx.RequestError as e:
        # Erro de conexão (serviço ML está offline)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de classificação (ML) está offline: {e}"
        )

async def call_llm_service(data: dict) -> dict:
    """
    Chama o microserviço do Agente LLM.
    """
    url = settings.LLM_SERVICE_URL # "http://localhost:8003/generate-actions"
    
    try:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json() # Esperamos algo como {"acoes_geradas": "..."}
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de geração de ações (LLM) está offline: {e}"
        )