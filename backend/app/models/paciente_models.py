from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Float, 
    ForeignKey, DateTime, Text
)
from sqlalchemy.sql import func
from app.db.base import Base
# from sqlalchemy.orm import relationship # Se precisar vincular Paciente ao User

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados do formulário (baseado no seu PacienteFormData)
    # Precisamos mapear os 22 campos aqui
    
    # Identificação
    email = Column(String, index=True, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    
    # Demográficos
    sexo = Column(String, nullable=True)
    escolaridade = Column(String, nullable=True)
    renda_familiar_sm = Column(String, nullable=True)
    endereco = Column(String, nullable=True)

    # Hábitos de Vida
    atividade_fisica = Column(String, nullable=True)
    consumo_alcool = Column(String, nullable=True)
    tabagismo_atual = Column(Boolean, nullable=True)
    qualidade_dieta = Column(String, nullable=True)
    qualidade_sono = Column(String, nullable=True)

    # Psicossocial
    nivel_estresse = Column(String, nullable=True)
    suporte_social = Column(String, nullable=True)
    
    # Histórico e Acesso
    historico_familiar_dc = Column(Boolean, nullable=True)
    acesso_servico_saude = Column(String, nullable=True)
    aderencia_medicamento = Column(String, nullable=True)
    consultas_ultimo_ano = Column(Integer, nullable=True)

    # Medições Clínicas
    imc = Column(Float, nullable=True)
    pressao_sistolica_mmHg = Column(Integer, nullable=True)
    pressao_diastolica_mmHg = Column(Integer, nullable=True)
    glicemia_jejum_mg_dl = Column(Integer, nullable=True)
    colesterol_total_mg_dl = Column(Integer, nullable=True)
    hdl_mg_dl = Column(Integer, nullable=True)
    triglicerides_mg_dl = Column(Integer, nullable=True)

    # --- Campos de Resultado (pós-processamento) ---
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Resultados do ML (Classificação)
    is_outlier = Column(Boolean, default=False)
    
    # Resultados do LLM (Ações)
    acoes_geradas_llm = Column(Text, nullable=True) # Campo para guardar o texto do LLM
    
    # (Opcional) Chave estrangeira para o profissional que cadastrou
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="pacientes")