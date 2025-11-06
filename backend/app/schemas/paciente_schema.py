from pydantic import BaseModel, computed_field
from typing import Optional, List
from datetime import date, datetime

# =================================================================
# Schema de ENTRADA (Baseado no PacienteFormData do api.ts)
# =================================================================
class PacienteBase(BaseModel):
    # Campos exatamente como no seu api.ts
    email: str
    nome: str
    endereco: Optional[str] = None
    data_nascimento: date # FastAPI converte string "YYYY-MM-DD" para date
    sexo: Optional[str] = None
    escolaridade: Optional[str] = None
    renda_familiar_sm: Optional[str] = None
    atividade_fisica: Optional[str] = None
    consumo_alcool: Optional[str] = None
    tabagismo_atual: bool
    qualidade_dieta: Optional[str] = None
    qualidade_sono: Optional[str] = None
    nivel_estresse: Optional[str] = None
    suporte_social: Optional[str] = None
    historico_familiar_dc: bool
    acesso_servico_saude: Optional[str] = None
    aderencia_medicamento: Optional[str] = None
    consultas_ultimo_ano: int
    imc: float
    pressao_sistolica_mmHg: int
    pressao_diastolica_mmHg: int
    glicemia_jejum_mg_dl: int
    colesterol_total_mg_dl: int
    hdl_mg_dl: int
    triglicerides_mg_dl: int

class PacienteCreate(PacienteBase):
    """ Schema usado para criar um novo paciente via API """
    pass


# =================================================================
# Schema de SAÍDA (Baseado no PacienteOut do api.ts)
# =================================================================
class Paciente(PacienteBase): # (Herda os 22 campos)
    id: int
    created_at: datetime
    
    # --- Campos lidos do DB ---
    # Estes são os campos que o service.py salvou no banco
    is_outlier: Optional[bool] = None # (Ex: False)
    acoes_geradas_llm: Optional[str] = None # (Ex: "Paciente estável...")

    # --- Campos Calculados para o Frontend ---
    # (Valores padrão, se o ML falhar e 'is_outlier' for None)
    probabilidade_diabetes: float = 0.0
    probabilidade_hipertensao: float = 0.0

    @computed_field
    @property
    def risco_diabetes(self) -> str:
        """
        TRADUZ 'is_outlier: bool' para 'risco_diabetes: str'
        que o frontend espera.
        """
        if self.is_outlier is None:
            # Se o ML falhou, o 'N/A' do seu frontend deve ser isso
            return "Não Calculado" 
        return "Crítico" if self.is_outlier else "Estável"

    @computed_field
    @property
    def risco_hipertensao(self) -> str:
        """
        TRADUZ 'is_outlier: bool' para 'risco_hipertensao: str'
        que o frontend espera.
        """
        if self.is_outlier is None:
            return "Não Calculado"
        return "Crítico" if self.is_outlier else "Estável"
        
    @computed_field
    @property
    def recomendacao_geral(self) -> str:
        """
        Passa o campo 'acoes_geradas_llm' do banco para o campo 
        'recomendacao_geral' que o frontend espera.
        """
        return self.acoes_geradas_llm or "Nenhuma recomendação gerada."

    class Config:
        from_attributes = True


# =================================================================
# Schema de SAÍDA para LISTAGEM (Baseado no PacienteListResponse)
# =================================================================
class PacienteListMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int

class PacienteListResponse(BaseModel):
    """ Schema para a resposta paginada de pacientes """
    items: List[Paciente]
    meta: PacienteListMeta