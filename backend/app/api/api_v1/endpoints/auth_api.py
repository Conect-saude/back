from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Usaremos para o form, mas o login é JSON
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import crud
from app.schemas import user_schema, token_schema
from app.core import security

router = APIRouter()

@router.post(
    "/register", 
    response_model=user_schema.User, 
    status_code=status.HTTP_201_CREATED
)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: user_schema.UserCreate
):
    """
    Registra um novo usuário (profissional de saúde).
    """
    user = crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um usuário com este email já existe.",
        )
    
    user = crud.create_user(db, user_in=user_in)
    return user


@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(
    *,
    db: Session = Depends(get_db),
    login_data: user_schema.UserLogin # Recebe o JSON {email, password}
):
    """
    Autentica um usuário e retorna um token de acesso.
    Corresponde ao api.ts
    """
    # 1. Busca o usuário pelo email
    user = crud.get_by_email(db, email=login_data.email)

    # 2. Verifica se o usuário existe E se a senha está correta
    if not user or not security.verify_password(
        login_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Cria o token JWT
    access_token = security.create_access_token(
        data={"sub": user.email} # "sub" (subject) é o email do usuário
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# NOTA: Os endpoints /forgot-password e /reset-password do seu api.ts
# podem ser adicionados aqui seguindo um padrão similar.