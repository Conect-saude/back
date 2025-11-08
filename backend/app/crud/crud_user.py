from sqlalchemy.orm import Session
from app.models.user_models import User
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash

def get_by_email(db: Session, *, email: str) -> User | None:
    """Busca um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    """Cria um novo usuário e salva no banco."""
    
    # Converte o schema Pydantic para um dict
    user_data = user_in.model_dump()
    
    # Pega a senha em texto plano e a substitui pelo hash
    plain_password = user_data.pop("password")
    hashed_password = get_password_hash(plain_password)
    
    # Cria o objeto do modelo SQLAlchemy
    db_user = User(**user_data, hashed_password=hashed_password, is_active=True)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user