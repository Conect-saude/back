from sqlalchemy.orm import Session
from app.models.paciente_models import Paciente
from app.schemas.paciente_schema import PacienteCreate
from typing import List, Optional

def get_by_id(db: Session, *, id: int) -> Optional[Paciente]:
    """Busca um paciente pelo ID."""
    return db.query(Paciente).filter(Paciente.id == id).first()

def create_paciente(db: Session, *, paciente_in: PacienteCreate) -> Paciente:
    """Cria um novo paciente e salva no banco."""
    
    # Converte o schema Pydantic para um dict
    paciente_data = paciente_in.model_dump()
    
    # Cria o objeto do modelo SQLAlchemy
    db_paciente = Paciente(**paciente_data)
    
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

def get_multi(
    db: Session, *, page: int = 1, page_size: int = 10, search: str = ""
) -> (List[Paciente], int):
    """
    Busca pacientes com paginação e busca.
    Retorna uma tupla (lista_de_pacientes, total_de_pacientes).
    """
    query = db.query(Paciente)

    if search:
        # Busca por nome ou email (exemplo)
        query = query.filter(
            (Paciente.nome.ilike(f"%{search}%")) |
            (Paciente.email.ilike(f"%{search}%"))
        )

    total = query.count()
    
    pacientes = (
        query.order_by(Paciente.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    return pacientes, total