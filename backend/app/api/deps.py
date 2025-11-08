from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from app.core import security
from app.db.session import get_db
from app import crud
from app.models.user_models import User

# Esta linha diz ao FastAPI para procurar um header "Authorization"
# e extrair o token dele.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependência para obter o usuário logado a partir do token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decodifica o token
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub") # "sub" é o email que salvamos no token
    if email is None:
        raise credentials_exception
    
    # 2. Busca o usuário no banco
    user = crud.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user