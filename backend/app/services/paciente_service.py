from sqlalchemy.orm import Session
from app.schemas.paciente_schema import PacienteCreate
from app.models.paciente_models import Paciente
from app import crud
from .http_client import call_ml_service, call_llm_service
from app.core.config import settings
import math
from datetime import date # Importe o 'date'

def _calculate_age(born: date) -> int:
    """Função helper para calcular a idade a partir da data de nascimento."""
    today = date.today()
    # Lógica para calcular a idade
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

async def create_paciente_with_orchestration(
    db: Session, *, paciente_in: PacienteCreate
) -> Paciente:
    
    # 1. Salva no banco
    db_paciente = crud.create_paciente(db, paciente_in=paciente_in)
    
    # 2. Prepara dados para o ML
    ml_input_data = paciente_in.model_dump()
    ml_input_data["idade"] = _calculate_age(paciente_in.data_nascimento)
    del ml_input_data["data_nascimento"] 
    del ml_input_data["nome"]
    del ml_input_data["email"]
    del ml_input_data["endereco"]
    
    # 3. Chama o ML e salva os resultados BRUTOS no banco
    try:
        ml_result = await call_ml_service(ml_input_data)
        is_outlier = ml_result.get("is_outlier", False)
        
        # Salva os resultados do ML no Banco
        db_paciente.is_outlier = is_outlier
        
        if is_outlier:
            # Salva a recomendação BÁSICA no campo do LLM
            db_paciente.acoes_geradas_llm = "Paciente classificado como outlier. Requer atenção especial."
        else:
            db_paciente.acoes_geradas_llm = "Paciente classificado como estável. Manter acompanhamento padrão."
        
        db.commit()
        db.refresh(db_paciente)
        
    except Exception as e:
        print(f"ALERTA: Paciente {db_paciente.id} criado, mas falha na orquestração: {e}")
        # (Não fazemos nada, o 'db_paciente' será retornado
        # e o schema de saída usará os valores padrão)

    # 4. Retorna o objeto do banco (com 'is_outlier' e 'acoes_geradas_llm' preenchidos)
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