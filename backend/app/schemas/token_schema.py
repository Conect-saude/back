from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Schema para a resposta de login bem-sucedido.
    Envia o token de acesso para o frontend.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema dos dados que são codificados dentro do token JWT.
    """
    email: Optional[str] = None