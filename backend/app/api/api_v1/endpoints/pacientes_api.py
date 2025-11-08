from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user_models import User # Necessário para a dependência
from app.schemas import paciente_schema
from app.services import paciente_service
from app.crud import crud_paciente as crud

router = APIRouter()

@router.post(
    "/", 
    response_model=paciente_schema.Paciente,
    status_code=status.HTTP_201_CREATED
)
async def create_paciente_endpoint(
    *,
    db: Session = Depends(get_db),
    paciente_in: paciente_schema.PacienteCreate, # O JSON do frontend
    current_user: User = Depends(get_current_user) # Rota protegida
):
    """
    Cria um novo paciente e dispara o fluxo de orquestração (ML/LLM).
    Corresponde ao 'createPaciente' do api.ts.
    """
    # Note que esta função é 'async' porque ela 'await' (espera)
    # o serviço de orquestração, que faz chamadas de rede (HTTP).
    db_paciente = await paciente_service.create_paciente_with_orchestration(
        db, paciente_in=paciente_in
    )
    return db_paciente


@router.get(
    "/",
    response_model=paciente_schema.PacienteListResponse
)
def list_pacientes_endpoint(
    *,
    db: Session = Depends(get_db),
    # Parâmetros de query baseados no api.ts
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user) # Rota protegida
):
    """
    Lista pacientes com paginação e busca.
    Corresponde ao 'fetchPacientes' do api.ts.
    """
    # O service.py já formata a resposta como o frontend espera
    return paciente_service.get_pacientes_paginados(
        db, page=page, page_size=page_size, search=search
    )


    return paciente


@router.get("/{id}", response_model=paciente_schema.Paciente)
def get_paciente_by_id_endpoint(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user) # Rota protegida
):
    """
    Busca um único paciente pelo ID.
    Corresponde ao 'getPacienteById' do api.ts.
    """
    paciente = crud.get_by_id(db, id=id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado",
        )
    return paciente


@router.put("/{id}", response_model=paciente_schema.Paciente)
async def update_paciente_endpoint(
    *,
    db: Session = Depends(get_db),
    id: int,
    paciente_in: paciente_schema.PacienteCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um paciente e re-executa o fluxo de orquestração (ML/LLM).
    Corresponde ao 'updatePaciente' do api.ts.
    """
    paciente = await paciente_service.update_paciente_with_orchestration(
        db, id=id, paciente_in=paciente_in
    )
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado",
        )
    return paciente


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paciente_endpoint(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Remove um paciente.
    Corresponde ao 'deletePaciente' do api.ts.
    """
    paciente = crud.get_by_id(db, id=id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado",
        )
    crud.remove(db, id=id)