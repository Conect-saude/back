from pydantic import BaseModel, EmailStr

# --- Schema Base ---
# Campos comuns a todos os schemas de usuário
class UserBase(BaseModel):
    email: EmailStr
    # Adicione outros campos se desejar (ex: nome_completo: str)


# --- Schema de Criação ---
# O que esperamos receber no endpoint /register
class UserCreate(UserBase):
    password: str


# --- Schema de Resposta (Leitura) ---
# O que vamos retornar ao frontend (NUNCA inclua o password)
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        # Permite que o Pydantic leia dados de um objeto SQLAlchemy
        from_attributes = True

class UserLogin(BaseModel):
    """
    Schema para o corpo (body) da requisição de login.
    Corresponde ao JSON {email, password} do api.ts
    """
    email: EmailStr
    password: str