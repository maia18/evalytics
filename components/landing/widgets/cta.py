import flet as ft
from typing import Callable
from components.landing.palette import (
    PAGE,
    SURFACE,
    BORDER,
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    MAX_CONTENT_WIDTH,
)

def criar_cta(page: ft.Page = None, mudar_tela: Callable[[str], None] = None) -> ft.Container:
    """
    Cria a seção final de Call to Action (Acompanhe os resultados da sua instituição).
    """

    return ft.Container(
        key=ft.ScrollKey("acessar"),
        bgcolor=PAGE,
        padding=ft.Padding.only(top=16, bottom=72, left=24, right=24),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Container(
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER),
                border_radius=16,
                padding=ft.Padding.symmetric(horizontal=32, vertical=40),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        # Título
                        ft.Text(
                            "Consulte as avaliações da sua instituição.",
                            size=26,
                            weight=ft.FontWeight.W_700,
                            color=TEXT,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        # Parágrafo
                        ft.Container(
                            width=420,
                            margin=ft.Margin.only(top=12, bottom=22),
                            content=ft.Text(
                                "Filtre resultados por curso, semestre e eixo. Acesse o dashboard e as opções de exportação.",
                                size=14,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),

                        # Botão de Ação
                        ft.ElevatedButton(
                            "Acessar a plataforma",
                            bgcolor=ROXO,
                            color="#ffffff",
                            height=40,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding.symmetric(horizontal=24),
                                elevation={
                                    ft.ControlState.DEFAULT: 0,
                                    ft.ControlState.HOVERED: 4,
                                },
                                text_style=ft.TextStyle(
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                            ),
                            on_click=lambda e: mudar_tela("/login") if mudar_tela else None,
                        ),
                    ],
                ),
            ),
        ),
    )
