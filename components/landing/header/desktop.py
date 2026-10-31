import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ACCENT,
    ACCENT_INK,
)

def criar_menu_desktop(
    mudar_tela: Callable[[str], None], 
    ir_para_recursos: Callable, 
    ir_para_indicadores: Optional[Callable] = None,
    ir_para_relatorios: Optional[Callable] = None,
    ir_para_sobre: Optional[Callable] = None,
) -> ft.Row:
    """
    Cria a barra de navegação para desktop.
    Exibe os links: Recursos, Indicadores, Relatórios e o botão de ação Entrar.
    """

    def _nav_link(texto: str, on_click: Optional[Callable]) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Text(
                texto,
                size=13,
                weight=ft.FontWeight.W_500,
            ),
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: TEXT,
                    ft.ControlState.DEFAULT: MUTED,
                },
                overlay_color=ft.Colors.TRANSPARENT,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            ),
            on_click=on_click,
        )

    # Fallback se indicadores/relatorios não forem passados
    handler_indicadores = ir_para_indicadores or ir_para_recursos
    handler_relatorios = ir_para_relatorios or ir_para_sobre or ir_para_recursos

    return ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Links de navegação
            _nav_link("Recursos", ir_para_recursos),
            _nav_link("Indicadores", handler_indicadores),
            _nav_link("Relatórios", handler_relatorios),

            ft.Container(width=4),

            # Botão de ação primário: Entrar
            ft.ElevatedButton(
                "Entrar",
                bgcolor=ACCENT,
                color=ACCENT_INK,
                height=38,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=18),
                    elevation={
                        ft.ControlState.DEFAULT: 0,
                        ft.ControlState.HOVERED: 2,
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
