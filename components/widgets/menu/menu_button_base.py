import flet as ft
from typing import Callable, Optional
from components.core.constants.constants import (
    ALTURA_BOTAO_MENU,
    RAIO_BOTAO_MENU,
    PADDING_BOTAO_MENU,
)

def criar_botao_menu_base(
    content: ft.Control,
    rota: str,
    dark_mode: bool,
    mudar_tela: Optional[Callable[[str], None]],
    alignment: Optional[ft.Alignment] = None,
    expand: bool = False,
    on_click: Optional[Callable[[ft.ControlEvent], None]] = None,
    ativo: bool = False,
) -> ft.Container:
    """
    Casca compartilhada de um botão de navegação do menu (sidebar).
        É utilizada tanto pelo botão somente com ícone quanto pelo botão com ícone + texto.
            A diferença visual entre eles fica no parâmetro `content`.
    """

    def executar_click(e: ft.ControlEvent) -> None:
        # Se houver uma ação específica, ela tem prioridade.
        if on_click:
            on_click(e)

        # Caso contrário, utiliza a navegação padrão.
        elif mudar_tela:
            mudar_tela(rota)

    return ft.Container(
        height=ALTURA_BOTAO_MENU,
        alignment=alignment,
        bgcolor=None,
        border_radius=RAIO_BOTAO_MENU,
        content=ft.TextButton(
            expand=expand,
            content=content,

            style=ft.ButtonStyle(
                padding=PADDING_BOTAO_MENU,

                shape=ft.RoundedRectangleBorder(
                    radius=RAIO_BOTAO_MENU,
                ),

                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                    ft.ControlState.HOVERED: ft.Colors.TRANSPARENT,
                    ft.ControlState.PRESSED: ft.Colors.TRANSPARENT,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                animation_duration=150,
            ),

            on_click=executar_click,
        ),
    )
