import flet as ft
from typing import Callable, Optional
from components.layout.sidebar.sidebar import Sidebar
from components.core.constants.constants import (
    LARGURA_SIDEBAR_MOBILE,
    POSICAO_SIDEBAR_MOBILE_FECHADA,
    DURACAO_ANIMACAO_SIDEBAR_MS,
    SOMBRA_SIDEBAR_MOBILE,
)

def criar_sidebar_desktop(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Optional[Callable[[str], None]],
    collapsed: bool = False,
) -> Sidebar:
    """
    Instancia a Sidebar para a interface Desktop.
        Neste modo, o menu lateral permanece fixo na estrutura principal da página.
    """

    return Sidebar(
        page=page,
        dark_mode=dark_mode,
        mudar_tela=mudar_tela,
        collapsed=collapsed,
    )

def criar_sidebar_mobile(
    page: ft.Page,
    dark_mode: bool,
    mudar_tela: Optional[Callable[[str], None]],
) -> ft.Container:
    """
    Cria a Sidebar para telas reduzidas (Mobile e Tablets).
        Neste cenário, a Sidebar funciona como um Drawer:
            Uma gaveta flutuante que desliza para dentro e para fora da tela sobre o conteúdo principal.
    """

    return ft.Container(
        
        # Posicionamento absoluto
        top=0,
        bottom=0,
        left=POSICAO_SIDEBAR_MOBILE_FECHADA,
        width=LARGURA_SIDEBAR_MOBILE,

        # Animação de abertura/fechamento
        animate_position=ft.Animation(
            DURACAO_ANIMACAO_SIDEBAR_MS,
            ft.AnimationCurve.EASE_OUT,
        ),

        # Sombra da Sidebar sobre o conteúdo
        shadow=ft.BoxShadow(
            blur_radius=25,
            spread_radius=2,
            color=SOMBRA_SIDEBAR_MOBILE,
        ),

        # Conteúdo interno
        content=Sidebar(
            page=page,
            dark_mode=dark_mode,
            mudar_tela=mudar_tela,
            collapsed=False,
            allow_collapse=False,
        ),
    )
