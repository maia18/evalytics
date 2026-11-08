import flet as ft
from typing import Callable
from components.core.constants.constants import TEXTO_PRINCIPAL
from components.layout.sidebar.sidebar_logo import criar_logo
from components.layout.sidebar.sidebar_reports import criar_menu_relatorios
from components.layout.sidebar.sidebar_dashboard import criar_menu_dashboard
from components.widgets.menu.menu import MENU_ITEMS
from components.widgets.menu.menu_item import criar_item_menu
from components.layout.sidebar.sidebar_footer import criar_rodape_sidebar
from components.layout.search.global_search import criar_busca_sidebar
from components.core.router.rotas_cts import (
    ROTA_DASHBOARD,
    ROTA_RELATORIOS,
    ROTA_CONFIGURACOES,
)


def criar_sidebar_content(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Callable[[str], None],
    cores: dict[str, str],
    alternar_recolhimento: Callable | None = None,
) -> ft.Column:
    """Constrói a visualização padrão (expandida) da barra lateral do sistema."""

    # Cabeçalho da sidebar.
    cabecalho = ft.Column(
        spacing=0,
        controls=[
            ft.Row(
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(expand=True, content=criar_logo(cores)),
                    ft.IconButton(
                        icon=ft.Icons.FIRST_PAGE,
                        icon_size=18,
                        on_click=alternar_recolhimento,
                        visible=alternar_recolhimento is not None,
                    ),
                ],
            ),
            ft.Divider(height=2),
        ],
    )
    busca_sidebar = criar_busca_sidebar(page, cores, mudar_tela)

    # Constrói os itens da navegação normal.
    rota_atual = getattr(page, "route", "") or ""
    controles_navegacao: list[ft.Control] = []
    for icone, texto, rota in MENU_ITEMS:
        if rota == ROTA_RELATORIOS:
            controles_navegacao.extend(
                criar_menu_relatorios(
                    page, dark_mode, cores[TEXTO_PRINCIPAL], mudar_tela
                )
            )
        elif rota == ROTA_DASHBOARD:
            controles_navegacao.extend(
                criar_menu_dashboard(
                    page, dark_mode, cores[TEXTO_PRINCIPAL], mudar_tela
                )
            )
        elif rota == ROTA_CONFIGURACOES:
            continue
        else:
            controles_navegacao.append(
                criar_item_menu(
                    icone, texto, rota, dark_mode,
                    cores[TEXTO_PRINCIPAL], mudar_tela,
                    ativo=rota_atual == rota,
                )
            )

    # Área rolável do menu.
    area_menu = ft.Column(
        controls=controles_navegacao,
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Column(
        controls=[
            cabecalho,
            ft.Container(
                padding=ft.Padding.symmetric(vertical=6),
                content=busca_sidebar,
            ),
            area_menu,
            criar_rodape_sidebar(page, dark_mode, cores, mudar_tela),
        ],
        spacing=0,
        expand=True,
    )
