import flet as ft
from typing import Callable
from components.core.constants.constants import TEXTO_PRINCIPAL
from components.layout.sidebar.sidebar_logo import criar_logo
from components.layout.sidebar.sidebar_items import montar_botoes_menu
from components.widgets.menu.menu import MENU_ITEMS_COLLAPSED
from components.widgets.menu.botao_icon import criar_botao_icon

def criar_sidebar_colapsada(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Callable[[str], None],
    cores: dict[str, str],
) -> ft.Column:
    """
    Constrói a versão retraída (colapsada/mini) da barra lateral.
        Neste estado, a sidebar exibe apenas os ícones para economizar espaço horizontal na tela.
    """

    # 1. Elementos iniciais da Sidebar
    controles: list[ft.Control] = [
        # Logo em versão reduzida
        criar_logo(
            cores,
            compact=True,
        ),

        # Separador
        ft.Divider(
            height=1,
        ),
    ]

    # 2. Botões do menu
    controles.extend(
        montar_botoes_menu(
            MENU_ITEMS_COLLAPSED,
            criar_botao_icon,
            dark_mode,
            cores[TEXTO_PRINCIPAL],
            mudar_tela,
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
