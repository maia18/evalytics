import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO_CLARO,
    SURFACE_ALT,
)

def criar_menu_desktop(
    mudar_tela: Callable[[str], None], 
    ir_para_recursos: Callable, 
    ir_para_sobre: Callable,
) -> ft.Row:
    """
    Cria a barra de navegação para desktop.
    Exibe os links: Recursos, Indicadores (abre a página de indicadores),
    Sobre e Desenvolvedores.
    """

    def _nav_link(texto: str, on_click: Optional[Callable], cor_hover: str = TEXT) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Text(
                texto,
                size=11,
                weight=ft.FontWeight.W_500,
            ),
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: cor_hover,
                    ft.ControlState.DEFAULT: MUTED,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                animation_duration=150,
                text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_500),
            ),
            on_click=on_click,
        )

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # 1. Recursos (âncora)
            _nav_link("Recursos", ir_para_recursos),

            # 2. Indicadores (abre página dedicada)
            _nav_link("Indicadores", lambda e: mudar_tela("/indicadores"), cor_hover=ROXO_CLARO),

            # 3. Sobre
            _nav_link("Sobre", ir_para_sobre),

            # 4. Desenvolvedores
            _nav_link(
                "Desenvolvedores",
                lambda e: mudar_tela("/desenvolvedores"),
                cor_hover=ROXO_CLARO,
            ),
        ],
    )
