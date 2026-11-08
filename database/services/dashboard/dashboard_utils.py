import logging
from database.services.institutions.institutions_service import obter_instituicao_id_atual
from database.services.memory_cache import obter_cache, salvar_cache
from utils.services.indicadores.indicadores_repository import listar_indicadores

logger = logging.getLogger(__name__)

def obter_mapa_eixos() -> dict[str, int]:
    """Cria um mapa relacionando o ID do indicador ao seu eixo."""
    chave_cache = f"mapa_eixos:{obter_instituicao_id_atual()}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return dict(valor)
    try:
        indicadores = listar_indicadores()
        mapa = {
            indicador["id"]: int(indicador.get("eixo", 1))
            for indicador in indicadores
            if indicador.get("id")
        }
        salvar_cache(chave_cache, mapa, 15.0)
        return mapa

    except Exception:
        logger.exception("Erro ao montar mapa de eixos.")
        return {}

def normalizar_nota(valor) -> float | None:
    """
    Converte uma resposta armazenada no Firestore para float.
        Retorna None quando a resposta não representa uma nota válida.
    """
    try:
        nota = float(valor)
    except (TypeError, ValueError):
        return None

    if not 1.0 <= nota <= 5.0:
        return None

    return nota
