import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    TEXT_BRIGHT,
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
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # 1. Recursos (âncora)
            _nav_link("Recursos", ir_para_recursos),

            # 2. Indicadores (abre página dedicada)
            _nav_link("Indicadores", lambda e: mudar_tela("/indicadores"), cor_hover=ROXO_CLARO),

            # 3. Sobre (substitui relatórios)
            _nav_link("Sobre", ir_para_sobre),

            ft.Container(width=4),

            # 4. Botão de ação: Entrar
            ft.ElevatedButton(
                "Entrar",
                bgcolor=ROXO,
                color=TEXT_BRIGHT,
                height=38,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=18),
                    elevation={
                        ft.ControlState.DEFAULT: 0,
                        ft.ControlState.HOVERED: 3,
                    },
                    text_style=ft.TextStyle(
                        size=13,
                        weight=ft.FontWeight.W_600,
                    ),
                ),
                on_click=lambda e: mudar_tela("/login"),
            ),
        ],
    )
