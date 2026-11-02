import flet as ft
from typing import Callable

from components.core.router.rotas_cts import ROTA_RELATORIOS, ROTA_RELATORIOS_DADOS
from components.widgets.menu.menu_item import criar_item_menu


def criar_menu_relatorios(
    page: ft.Page,
    dark_mode: bool,
    cor_texto: str,
    mudar_tela: Callable[[str], None],
) -> list[ft.Control]:
    """Cria o link direto para a única tela de relatórios."""
    rota_atual = getattr(page, "route", "") or ""
    return [
        criar_item_menu(
            ft.Icons.PIE_CHART_OUTLINE,
            "Relatórios",
            ROTA_RELATORIOS_DADOS,
            dark_mode,
            cor_texto,
            mudar_tela,
            ativo=rota_atual in (ROTA_RELATORIOS, ROTA_RELATORIOS_DADOS),
        )
    ]
