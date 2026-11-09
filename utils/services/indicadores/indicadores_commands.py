import logging
from database.services.firebase_config import db
from database.services.memory_cache import invalidar_cache
from utils.services.indicadores.indicadores_queries import buscar_indicador
from .indicador_notificacoes import (
    criar_notificacao_indicador,
    criar_notificacao_status_indicador,
)

logger = logging.getLogger(__name__)
COLECAO_INDICADORES = "indicadores"


def _invalidar_cache_indicadores() -> None:
    invalidar_cache("indicadores:")
    invalidar_cache("respostas_tabela:")
    invalidar_cache("mapa_eixos:")
    invalidar_cache("dashboard:")
    invalidar_cache("resultados:")
    invalidar_cache("resumo_eixos:")

def adicionar_indicador(titulo: str, eixo: int, descricao: str) -> bool:
    """Cria um novo indicador no Firestore."""
    try:
        titulo = titulo.strip()
        descricao = descricao.strip()

        if not titulo or eixo is None:
            return False

        # Evita duplicidade de título dentro do mesmo eixo.
        if buscar_indicador(titulo, eixo):
            logger.warning("Indicador já existente: '%s' (eixo %s)", titulo, eixo)
            return False

        novo_item = {
            "titulo": titulo,
            "eixo": eixo,
            "descricao": descricao,
            "status": "ATIVO",
            "criterios": {
                "1": "",
                "2": "",
                "3": "",
                "4": "",
                "5": "",
            },
        }

        db.collection(COLECAO_INDICADORES).add(novo_item)
        _invalidar_cache_indicadores()
        logger.info("Indicador '%s' adicionado ao eixo %s.", titulo, eixo)

        # Delega a criação da notificação para o serviço especializado
        criar_notificacao_indicador(titulo, eixo)

        return True

    except Exception:
        logger.exception("Erro ao adicionar indicador ao Firestore.")
        return False


def excluir_indicador(indicador_id: str) -> bool:
    """Exclui permanentemente um indicador do Firestore utilizando diretamente o ID do documento."""
    try:
        if not indicador_id:
            logger.warning("Tentativa de exclusão sem ID de indicador.")
            return False

        doc_ref = db.collection(COLECAO_INDICADORES).document(indicador_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning("Indicador não encontrado para exclusão: %s", indicador_id)
            return False

        doc_ref.delete()
        _invalidar_cache_indicadores()
        logger.info("Indicador '%s' excluído com sucesso.", indicador_id)
        return True

    except Exception:
        logger.exception("Erro ao excluir indicador do Firestore.")
        return False


def atualizar_indicador(indicador_id: str, novo_titulo: str, nova_descricao: str) -> bool:
    """Atualiza título e descrição de um indicador utilizando diretamente o ID do documento."""
    try:
        if not indicador_id:
            logger.warning("Tentativa de edição sem ID de indicador.")
            return False

        novo_titulo = novo_titulo.strip()
        nova_descricao = nova_descricao.strip()

        if not novo_titulo:
            return False

        doc_ref = db.collection(COLECAO_INDICADORES).document(indicador_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning("Indicador não encontrado para edição: %s", indicador_id)
            return False

        dados_atuais = doc.to_dict() or {}
        eixo = dados_atuais.get("eixo")

        existente = buscar_indicador(novo_titulo, eixo)

        if existente and existente["id"] != indicador_id:
            logger.warning(
                "Já existe outro indicador com o título '%s' no eixo %s.",
                novo_titulo, eixo
            )
            return False

        doc_ref.update({
            "titulo": novo_titulo,
            "descricao": nova_descricao,
        })
        _invalidar_cache_indicadores()

        logger.info("Indicador '%s' atualizado.", indicador_id)
        return True

    except Exception:
        logger.exception("Erro ao atualizar indicador no Firestore.")
        return False


def atualizar_status_indicador(indicador_id: str, novo_status: str) -> bool:
    """Atualiza o status de um indicador no Firestore."""
    try:
        status = str(novo_status or "").strip().upper()
        if not indicador_id or status not in {"ATIVO", "INATIVO"}:
            logger.warning("ID ou status inválido ao atualizar indicador.")
            return False

        doc_ref = db.collection(COLECAO_INDICADORES).document(indicador_id)
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning("Indicador não encontrado para atualização de status: %s", indicador_id)
            return False

        dados_indicador = doc.to_dict() or {}
        doc_ref.update({"status": status})
        _invalidar_cache_indicadores()
        criar_notificacao_status_indicador(
            str(dados_indicador.get("titulo") or "Indicador"),
            status,
        )
        logger.info("Status do indicador '%s' alterado para %s.", indicador_id, status)
        return True
    except Exception:
        logger.exception("Erro ao atualizar status do indicador no Firestore.")
        return False


def atualizar_criterios_indicador(indicador_id: str, novos_criterios: dict) -> bool:
    """Atualiza os cinco critérios de avaliação do indicador utilizando diretamente o ID do documento."""
    try:
        if not indicador_id:
            logger.warning("Tentativa de atualizar critérios sem ID de indicador.")
            return False

        if not isinstance(novos_criterios, dict):
            logger.warning("Critérios inválidos para o indicador '%s'.", indicador_id)
            return False

        doc_ref = db.collection(COLECAO_INDICADORES).document(indicador_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning(
                "Indicador não encontrado para atualização dos critérios: %s", 
                indicador_id
            )
            return False

        criterios = {
            "1": str(novos_criterios.get("1", "")).strip(),
            "2": str(novos_criterios.get("2", "")).strip(),
            "3": str(novos_criterios.get("3", "")).strip(),
            "4": str(novos_criterios.get("4", "")).strip(),
            "5": str(novos_criterios.get("5", "")).strip(),
        }

        doc_ref.update({"criterios": criterios})
        _invalidar_cache_indicadores()
        logger.info("Critérios do indicador '%s' atualizados.", indicador_id)
        return True

    except Exception:
        logger.exception("Erro ao atualizar critérios no Firestore.")
        return False
