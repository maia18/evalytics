import asyncio
import logging
import flet as ft
from components.layout.topbar.core.notifications.notifications import (
    contar_nao_lidas,
    listar_notificacoes,
)

logger = logging.getLogger(__name__)

async def _tarefa_monitorar_notificacoes(page: ft.Page):
    """Executa o loop contínuo de checagem de notificações em background."""
    while True:
        try:
            topbar_atual = getattr(page, "_topbar_notificacoes", None)

            if topbar_atual is not None:
                # Atualiza o contador de notificações
                quantidade = await asyncio.to_thread(contar_nao_lidas)
                page._notificacoes_nao_lidas_cache = quantidade
                topbar_atual.atualizar_notificacoes(quantidade)

                # Atualiza a lista do painel se ele estiver aberto
                painel = getattr(topbar_atual, "painel_notificacoes", None)
                atualizar_lista = getattr(topbar_atual, "atualizar_lista_notificacoes", None)

                if painel is not None and painel.visible and atualizar_lista is not None:
                    novas_notificacoes = await asyncio.to_thread(listar_notificacoes)
                    page._notificacoes_cache = novas_notificacoes
                    atualizar_lista(novas_notificacoes)

                page.update()

        except asyncio.CancelledError:
            break
        except Exception as erro:
            logger.exception("Erro ao atualizar notificações: %s", erro)

        await asyncio.sleep(5)

def iniciar_monitor_notificacoes(page: ft.Page, topbar_instance) -> None:
    """
    Registra a instância atual da topbar e inicia a tarefa de monitoramento apenas se ainda não estiver rodando na página.
    """
    page._topbar_notificacoes = topbar_instance

    if not getattr(page, "_monitor_notificacoes_iniciado", False):
        page._monitor_notificacoes_iniciado = True
        page.run_task(_tarefa_monitorar_notificacoes, page)
