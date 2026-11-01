from typing import Any
from components.core.auth.auth_state import auth_state
from utils.services.notifications.notificacoes_service import (
    listar_notificacoes as listar_notificacoes_db,
    contar_notificacoes_nao_lidas,
    marcar_todas_como_lidas as marcar_todas_como_lidas_db,
    excluir_todas_notificacoes as excluir_todas_notificacoes_db,
)
from .notificacoes_formatadores import (
    obter_icone, 
    formatar_tempo,
)

def _obter_usuario_id() -> str | None:
    """Obtém o ID do usuário atualmente autenticado."""
    usuario = auth_state.usuario

    if not usuario:
        return None

    return usuario.get("user_id") or usuario.get("localId")

def listar_notificacoes() -> list[dict[str, Any]]:
    """Lista as notificações do usuário no formato esperado pela TopBar."""
    usuario_id = _obter_usuario_id()

    if not usuario_id:
        return []

    notificacoes_db = listar_notificacoes_db(usuario_id)
    notificacoes = []

    for notificacao in notificacoes_db:
        notificacoes.append(
            {
                "id": notificacao.get("id"),
                "icone": obter_icone(notificacao.get("tipo", "")),
                "titulo": notificacao.get("titulo", "Notificação"),
                "descricao": notificacao.get("descricao", ""),
                "tempo": formatar_tempo(notificacao.get("data_criacao")),
                "lida": notificacao.get("lida", False),
            }
        )

    return notificacoes

def contar_nao_lidas() -> int:
    """Retorna a quantidade de notificações não lidas do usuário."""
    usuario_id = _obter_usuario_id()

    if not usuario_id:
        return 0

    return contar_notificacoes_nao_lidas(usuario_id)

def marcar_todas_como_lidas() -> None:
    """Marca todas as notificações do usuário como lidas."""
    usuario_id = _obter_usuario_id()

    if not usuario_id:
        return

    marcar_todas_como_lidas_db(usuario_id)


def limpar_notificacoes() -> bool:
    """Exclui as notificações da conta autenticada."""
    usuario_id = _obter_usuario_id()

    if not usuario_id:
        return False

    return excluir_todas_notificacoes_db(usuario_id)
