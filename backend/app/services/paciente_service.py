from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.paciente_schema import PacienteCreate
from app.models.paciente_models import Paciente
from app import crud
# (Verifique se call_llm_service está importado)
from .http_client import call_ml_service, call_llm_service
from app.core.config import settings
import math
from datetime import date

def _calculate_age(born: date) -> int:
    """Função helper para calcular a idade."""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

async def _run_orchestration(db: Session, paciente_in: PacienteCreate, db_paciente: Paciente) -> Paciente:
    """
    Função helper que executa a orquestração ML/LLM para um paciente.
    """
    # Prepara dados para os microserviços
    ml_input_data = paciente_in.model_dump()
    ml_input_data["idade"] = _calculate_age(paciente_in.data_nascimento)
    del ml_input_data["data_nascimento"] 
    del ml_input_data["nome"]
    del ml_input_data["email"]
    del ml_input_data["endereco"]
    
    try:
        # Chama o Serviço de ML
        ml_result = await call_ml_service(ml_input_data)
        is_outlier = ml_result.get("is_outlier", False)
        
        # Salva o resultado do ML
        db_paciente.is_outlier = is_outlier
        
        if is_outlier:
            print(f"Paciente {db_paciente.id} é outlier. Chamando Agente LLM...")
            
            llm_input_payload = {
                "patient_data": ml_input_data
            }
            
            llm_result = await call_llm_service(llm_input_payload)
            generated_text = llm_result.get("generated_actions")
            db_paciente.acoes_geradas_llm = generated_text
            
        else:
            db_paciente.acoes_geradas_llm = "Paciente classificado como estável. Manter acompanhamento padrão."
            
        db.commit()
        db.refresh(db_paciente)
        
    except Exception as e:
        print(f"ALERTA: Falha na orquestração para paciente {db_paciente.id}: {e}")

    return db_paciente


async def create_paciente_with_orchestration(
    db: Session, *, paciente_in: PacienteCreate
) -> Paciente:
    """
    Orquestra o fluxo completo: Salva, Classifica (ML) e Gera Ações (LLM).
    """
    
    # 1. Salva o paciente no banco
    db_paciente = crud.create_paciente(db, paciente_in=paciente_in)
    
    # 2. Prepara dados para os microserviços
    # (Remove dados que não são features, como nome/email/data)
    ml_input_data = paciente_in.model_dump()
    ml_input_data["idade"] = _calculate_age(paciente_in.data_nascimento)
    del ml_input_data["data_nascimento"] 
    del ml_input_data["nome"]
    del ml_input_data["email"]
    del ml_input_data["endereco"]
    
    # 3. Chama o Serviço de ML (Porta 8001)
    try:
        ml_result = await call_ml_service(ml_input_data)
        is_outlier = ml_result.get("is_outlier", False)
        
        # Salva o resultado do ML no Banco
        db_paciente.is_outlier = is_outlier
        
        # --- ETAPA FINAL (A CORREÇÃO) ---
        if is_outlier:
            print(f"Paciente {db_paciente.id} é outlier. Chamando Agente LLM (Porta 8003)...")
            
            # Prepara o JSON para o serviço LLM (que espera PatientDataForLLM)
            # O 'ml_input_data' já tem o formato { "idade": ..., "sexo": ..., etc }
            llm_input_payload = {
                "patient_data": ml_input_data
            }
            
            # Chama o Serviço LLM (Porta 8003)
            llm_result = await call_llm_service(llm_input_payload)
            
            # Salva a resposta REAL do LLM no banco
            generated_text = llm_result.get("generated_actions")
            db_paciente.acoes_geradas_llm = generated_text
            
        else:
            # Se não for outlier, apenas salvamos a mensagem padrão
            db_paciente.acoes_geradas_llm = "Paciente classificado como estável. Manter acompanhamento padrão."
        # --- FIM DA CORREÇÃO ---
            
        db.commit()
        db.refresh(db_paciente)
        
    except Exception as e:
        print(f"ALERTA: Paciente {db_paciente.id} criado, mas falha na orquestração: {e}")

    return db_paciente


def get_pacientes_paginados(
    db: Session, *, page: int, page_size: int, search: str
):
    """
    Busca pacientes paginados e prepara a resposta 
    exatamente como o frontend (api.ts) espera.
    """
    pacientes, total = crud.get_multi(
        db, page=page, page_size=page_size, search=search
    )
    
    meta = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size)
    }
    
    return {"items": pacientes, "meta": meta}


async def update_paciente_with_orchestration(
    db: Session, *, id: int, paciente_in: PacienteCreate
) -> Optional[Paciente]:
    """
    Atualiza um paciente e re-executa o fluxo de orquestração (ML/LLM).
    """
    db_paciente = crud.get_by_id(db, id=id)
    if not db_paciente:
        return None
        
    # Atualiza os campos do paciente
    for field, value in paciente_in.model_dump().items():
        setattr(db_paciente, field, value)
    
    # Re-executa a orquestração
    return await _run_orchestration(db, paciente_in, db_paciente)