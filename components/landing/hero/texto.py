import flet as ft
from typing import Callable
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    PAGE,
    BORDER_STRONG,
    BORDER,
)

def criar_hero_texto(
    mudar_tela: Callable[[str], None],
    ir_para_recursos: Callable,
) -> ft.Column:
    """Cria a seção de título, descrição e ações principais do Hero com a paleta Evalytics."""

    return ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Eyebrow / Tag em monospace com pílula estilizada
            ft.Container(
                margin=ft.Margin.only(bottom=18),
                padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                bgcolor=ft.Colors.with_opacity(0.10, ROXO_CLARO),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.35, ROXO_CLARO)),
                border_radius=20,
                content=ft.Row(
                    spacing=6,
                    tight=True,
                    controls=[
                        ft.Container(
                            width=6,
                            height=6,
                            bgcolor=ROXO_CLARO,
                            border_radius=6,
                        ),
                        ft.Text(
                            "AVALIAÇÃO INSTITUCIONAL · EVALYTICS",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=ROXO_CLARO,
                            font_family="monospace",
                        ),
                    ],
                ),
            ),

            # Título principal (h1)
            ft.Container(
                width=580,
                content=ft.Text(
                    "Avaliações institucionais organizadas por curso e eixo.",
                    size=42,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),

            # Parágrafo de apoio (hero-copy)
            ft.Container(
                width=450,
                margin=ft.Margin.only(top=18, bottom=24),
                content=ft.Text(
                    "Organize avaliações por curso, semestre e eixo. Consulte os resultados "
                    "no dashboard e exporte relatórios em PDF ou dados em CSV.",
                    size=15,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),

            # Ações do Hero (botões)
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                wrap=True,
                controls=[
                    # Botão Primário: Acessar plataforma
                    ft.ElevatedButton(
                        "Acessar plataforma",
                        bgcolor=ROXO,
                        color="#ffffff",
                        height=40,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(horizontal=20),
                            elevation={
                                ft.ControlState.DEFAULT: 0,
                                ft.ControlState.HOVERED: 4,
                            },
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
                        height=40,
                        style=ft.ButtonStyle(
                            bgcolor=PAGE,
                            color=TEXT,
                            side=ft.BorderSide(1, BORDER_STRONG),
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(horizontal=20),
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
