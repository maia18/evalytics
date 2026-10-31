import flet as ft
from typing import Callable
from components.landing.palette import (
    TEXT,
    MUTED,
    ACCENT,
    ACCENT_INK,
    PAGE,
    BORDER_STRONG,
)

def criar_hero_texto(
    mudar_tela: Callable[[str], None],
    ir_para_recursos: Callable,
) -> ft.Column:
    """Cria a seção de título, descrição e ações principais do Hero."""

    return ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Eyebrow / Tag em monospace
            ft.Container(
                margin=ft.Margin.only(bottom=16),
                content=ft.Text(
                    "avaliação institucional por dados",
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=ACCENT,
                    font_family="monospace",
                    text_align=ft.TextAlign.CENTER,
                ),
            ),

            # Título principal (h1)
            ft.Container(
                width=560,
                content=ft.Text(
                    "Avaliações institucionais, organizadas por curso e eixo.",
                    size=42,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),

            # Parágrafo de apoio (hero-copy)
            ft.Container(
                width=430,
                margin=ft.Margin.only(top=18, bottom=24),
                content=ft.Text(
                    "Crie avaliações, acompanhe resultados por curso, "
                    "semestre e eixo avaliativo e exporte relatórios em PDF ou CSV.",
                    size=15,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),

            # Ações do Hero (botões)
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                wrap=True,
                controls=[
                    # Botão Primário: Acessar plataforma
                    ft.ElevatedButton(
                        "Acessar plataforma",
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
                        on_click=lambda e: mudar_tela("/login"),
                    ),

                    # Botão Secundário: Ver recursos
                    ft.OutlinedButton(
                        "Ver recursos",
                        height=38,
                        style=ft.ButtonStyle(
                            bgcolor=PAGE,
                            color=TEXT,
                            side=ft.BorderSide(1, BORDER_STRONG),
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(horizontal=19),
                            text_style=ft.TextStyle(
                                size=13,
                                weight=ft.FontWeight.W_600,
                            ),
                        ),
                        on_click=ir_para_recursos,
                    ),
                ],
            ),
        ],
    )
