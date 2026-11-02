import flet as ft
from typing import Callable, Optional
from components.core.constants.constants import (
    HOVER,
    ALTURA_BOTAO_MENU,
    RAIO_BOTAO_MENU,
    PADDING_BOTAO_MENU,
    HOVER_CLARO_BOTAO_MENU,
    COR_PRIMARIA,
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
        border=ft.Border(
            left=ft.BorderSide(2, COR_PRIMARIA if ativo else "#00000000")
        ),

        content=ft.TextButton(
            expand=expand,
            content=content,

            style=ft.ButtonStyle(
                padding=PADDING_BOTAO_MENU,

                shape=ft.RoundedRectangleBorder(
                    radius=RAIO_BOTAO_MENU,
                ),

                # Hover adaptado ao tema atual
                overlay_color=(
                    HOVER
                    if dark_mode
                    else HOVER_CLARO_BOTAO_MENU
                ),
            ),

            on_click=executar_click,
        ),
    )
