from .crud_user import get_by_email, create_user

# --- ADICIONE ESTAS LINHAS ---
# Elas expõem as funções do crud_paciente para o resto do app
from .crud_paciente import create_paciente, get_by_id, get_multi
# -----------------------------