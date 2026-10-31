import flet as ft
from typing import Callable
from components.landing.palette import (
    PAGE,
    TEXT,
    MUTED,
    ACCENT,
    ACCENT_INK,
    MAX_CONTENT_WIDTH,
)

def criar_cta(page: ft.Page = None, mudar_tela: Callable[[str], None] = None) -> ft.Container:
    """
    Cria a seção final de Call to Action (Acompanhe os resultados da sua instituição).
    """

    return ft.Container(
        key=ft.ScrollKey("acessar"),
        bgcolor=PAGE,
        padding=ft.Padding.only(top=24, bottom=72, left=24, right=24),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    # Título
                    ft.Text(
                        "Acompanhe os resultados da sua instituição.",
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    # Parágrafo
                    ft.Container(
                        width=380,
                        margin=ft.Margin.only(top=14, bottom=18),
                        content=ft.Text(
                            "Entre no Evalytics para consultar avaliações, indicadores e relatórios.",
                            size=14,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),

                    # Botão de Ação
                    ft.ElevatedButton(
                        "Entrar na plataforma",
                        bgcolor=ACCENT,
                        color=ACCENT_INK,
                        height=38,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(horizontal=19),
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
    )
