import logging
from typing import Optional
from database.services.firebase_config import db
from database.services.memory_cache import obter_cache, salvar_cache

logger = logging.getLogger(__name__)
COLECAO_INDICADORES = "indicadores"

def buscar_indicador(
    titulo: str,
    eixo: int,
) -> Optional[dict]:
    """
    Busca um indicador pelo título e eixo.
    """

    try:
        docs = (
            db.collection(COLECAO_INDICADORES)
            .where("titulo", "==", titulo)
            .where("eixo", "==", eixo)
            .limit(1)
            .stream()
        )

        for doc in docs:
            return {
                "id": doc.id,
                **doc.to_dict(),
            }

        return None

    except Exception:
        logger.exception(
            "Erro ao buscar indicador no Firestore."
        )
        return None


def contar_indicadores_por_eixo(
    eixo: int,
) -> int:
    """
    Retorna a quantidade de indicadores de um eixo.
    """

    try:
        docs = (
            db.collection(COLECAO_INDICADORES)
            .where("eixo", "==", eixo)
            .stream()
        )

        return sum(1 for _ in docs)

    except Exception:
        logger.exception(
            "Erro ao contar indicadores no Firestore."
        )
        return 0


def listar_indicadores_por_eixo(
    eixo: Optional[int],
) -> list[dict]:
    """
    Retorna os indicadores de determinado eixo.
    """

    try:
        docs = (
            db.collection(COLECAO_INDICADORES)
            .where("eixo", "==", eixo)
            .stream()
        )

        return [
            {
                "id": doc.id,
                **doc.to_dict(),
            }
            for doc in docs
        ]

    except Exception:
        logger.exception(
            "Erro ao listar indicadores por eixo."
        )
        return []
    
def listar_indicadores() -> list[dict]:
    """Retorna todos os indicadores cadastrados no Firestore."""
    encontrado, valor = obter_cache("indicadores:todos")
    if encontrado:
        return [dict(indicador) for indicador in valor]
    try:
        docs = db.collection(COLECAO_INDICADORES).stream()
        indicadores = [
            {
                "id": doc.id,
                **doc.to_dict(),
            }
            for doc in docs
        ]
        salvar_cache(
            "indicadores:todos",
            tuple(dict(indicador) for indicador in indicadores),
            30,
        )
        return indicadores

    except Exception:
        logger.exception(
            "Erro ao listar todos os indicadores no Firestore."
        )
        return []
