import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO_CLARO,
)

def criar_menu_desktop(
    mudar_tela: Callable[[str], None], 
    ir_para_recursos: Callable, 
    ir_para_sobre: Callable,
) -> ft.Row:
    """
    Cria a barra de navegação para desktop.
    Exibe os links: Recursos, Indicadores (abre a página de indicadores),
    Sobre (rola até a seção explicativa) e o botão Entrar.
    """

    def _nav_link(texto: str, on_click: Optional[Callable], cor_hover: str = TEXT) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Text(
                texto,
                size=13,
                weight=ft.FontWeight.W_500,
            ),
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: cor_hover,
                    ft.ControlState.DEFAULT: MUTED,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            ),
            on_click=on_click,
        )

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=28,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # 1. Recursos (âncora)
            _nav_link("Recursos", ir_para_recursos),

            # 2. Indicadores (abre página dedicada)
            _nav_link("Indicadores", lambda e: mudar_tela("/indicadores"), cor_hover=ROXO_CLARO),

            # 3. Sobre
            _nav_link("Sobre", ir_para_sobre),
        ],
    )
