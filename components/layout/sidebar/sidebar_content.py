import flet as ft
from typing import Callable
from components.core.constants.constants import TEXTO_PRINCIPAL
from components.layout.sidebar.sidebar_logo import criar_logo
from components.layout.sidebar.sidebar_reports import criar_menu_relatorios
from components.layout.sidebar.sidebar_dashboard import criar_menu_dashboard
from components.widgets.menu.menu import MENU_ITEMS
from components.widgets.menu.menu_item import criar_item_menu
from components.core.router.rotas_cts import ROTA_DASHBOARD, ROTA_RELATORIOS

def criar_sidebar_content(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Callable[[str], None],
    cores: dict[str, str],
) -> ft.Column:
    """Constrói a visualização padrão (expandida) da barra lateral do sistema."""

    # 1. Estrutura base da Sidebar
    controles: list[ft.Control] = [
        # Logo completo
        criar_logo(
            cores,
        ),

        # Separador
        ft.Divider(
            height=2,
        ),
    ]

    # 2. Construção da lista de navegação
    for icone, texto, rota in MENU_ITEMS:
        if rota == ROTA_RELATORIOS:
            controles.extend(
                criar_menu_relatorios(
                    page, dark_mode, cores[TEXTO_PRINCIPAL], mudar_tela
                )
            )
        elif rota == ROTA_DASHBOARD:
            controles.extend(
                criar_menu_dashboard(
                    page, dark_mode, cores[TEXTO_PRINCIPAL], mudar_tela
                )
            )
        else:
            controles.append(
                criar_item_menu(
                    icone, texto, rota, dark_mode,
                    cores[TEXTO_PRINCIPAL], mudar_tela,
                )
            )

    # 3. Área rolável do menu
    area_menu = ft.Column(
        controls=controles,
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Column(
        controls=[
            area_menu,
        ],
        spacing=0,
        expand=True,
    )
