import flet as ft
from typing import Callable
from components.core.constants.constants import TEXTO_PRINCIPAL
from components.layout.sidebar.sidebar_logo import criar_logo
from components.widgets.menu.menu import MENU_ITEMS_COLLAPSED
from components.widgets.menu.botao_icon import criar_botao_icon
from components.layout.sidebar.sidebar_footer import criar_rodape_sidebar
from components.core.router.rotas_cts import ROTA_CONFIGURACOES

def criar_sidebar_colapsada(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Callable[[str], None],
    cores: dict[str, str],
    alternar_recolhimento: Callable | None = None,
) -> ft.Column:
    """
    Constrói a versão retraída (colapsada/mini) da barra lateral.
        Neste estado, a sidebar exibe apenas os ícones para economizar espaço horizontal na tela.
    """

    # 1. Elementos iniciais da Sidebar
    controles: list[ft.Control] = [
        # Logo em versão reduzida
        ft.Column(
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
                        icon_size=18,
                        tooltip="Expandir menu lateral",
                        on_click=alternar_recolhimento,
                        visible=alternar_recolhimento is not None,
                    ),
                ),
                criar_logo(cores, compact=True),
            ],
        ),

        # Separador
        ft.Divider(
            height=1,
        ),
    ]

    # 2. Botões do menu
    rota_atual = getattr(page, "route", "") or ""
    controles.extend(
        criar_botao_icon(
            icone,
            texto,
            rota,
            dark_mode,
            cores[TEXTO_PRINCIPAL],
            mudar_tela,
            ativo=rota_atual == rota or rota_atual.startswith(f"{rota}/"),
        )
        for icone, texto, rota in MENU_ITEMS_COLLAPSED
        if rota != ROTA_CONFIGURACOES
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
            criar_rodape_sidebar(page, dark_mode, cores, mudar_tela, compacta=True),
        ],
        spacing=0,
        expand=True,
    )
