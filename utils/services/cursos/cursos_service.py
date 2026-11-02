import logging
from database.services.firebase_config import db
from database.services.institutions.institutions_service import (
    listar_documentos_da_instituicao,
    obter_instituicao_id_atual,
)

logger = logging.getLogger(__name__)

'''
ATENÇÃO ARQUITETURAL: 
    Esta constante aponta para a coleção "cursos" do Firestore, mas espera um formato de documento diferente (nome/modalidade/ativo) do outro arquivo de cursos do sistema. 
        Recomenda-se unificar as assinaturas antes de ir para produção.
'''
COLECAO_CURSOS = "cursos"

def listar_cursos() -> list[dict]:
    """Busca todos os cursos cadastrados na coleção 'cursos' do Firestore."""
    
    try:
        docs = listar_documentos_da_instituicao(COLECAO_CURSOS)
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    except Exception:
        logger.exception("Erro ao buscar cursos.")
        return []

def criar_curso(nome: str, modalidade: str) -> None:
    """Cadastra um novo curso no Firestore."""
    
    try:
        novo_curso = {
            "nome": nome,
            "modalidade": modalidade,
            "ativo": True,  # Soft delete: Permite ocultar o curso futuramente sem perder o histórico do banco.
            "instituicao_id": obter_instituicao_id_atual(),
        }
        db.collection(COLECAO_CURSOS).add(novo_curso)

    except Exception:
        logger.exception("Erro ao criar curso '%s'.", nome)
