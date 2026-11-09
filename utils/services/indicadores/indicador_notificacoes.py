import logging
from components.core.auth.auth_state import auth_state
from utils.services.notifications.notificacoes_service import adicionar_notificacao

logger = logging.getLogger(__name__)

def criar_notificacao_indicador(titulo: str, eixo: int) -> None:
    """Cria uma notificação para o usuário autenticado sobre um novo indicador."""
    
    usuario = auth_state.usuario
    usuario_id = None

    if usuario:
        usuario_id = usuario.get("user_id") or usuario.get("localId")

    if usuario_id:
        notificacao_id = adicionar_notificacao(
            tipo="indicador",
            titulo="Novo indicador cadastrado",
            descricao=f"O indicador '{titulo}' foi cadastrado no eixo {eixo}.",
            usuario_id=usuario_id,
        )

        if not notificacao_id:
            logger.warning(
                "O indicador foi salvo, mas não foi possível "
                "criar a notificação."
            )
    else:
        logger.warning(
            "O indicador foi salvo, mas não foi possível "
            "identificar o usuário para criar a notificação."
        )


def criar_notificacao_status_indicador(titulo: str, status: str) -> None:
    """Notifica o usuário autenticado quando o status de um indicador muda."""
    usuario = auth_state.usuario
    usuario_id = (usuario or {}).get("user_id") or (usuario or {}).get("localId")
    if not usuario_id:
        logger.info("Status atualizado sem usuário disponível para notificação.")
        return

    acao = "ativado" if status == "ATIVO" else "desativado"
    try:
        notificacao_id = adicionar_notificacao(
            tipo="indicador",
            titulo="Status do indicador atualizado",
            descricao=f"O indicador '{titulo}' foi {acao}.",
            usuario_id=usuario_id,
        )
        if not notificacao_id:
            logger.warning("Não foi possível criar notificação de status do indicador.")
    except Exception:
        logger.exception("Falha ao notificar alteração do status do indicador.")
