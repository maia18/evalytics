import flet as ft
from typing import Callable, Optional

from components.landing.palette import (
    SURFACE,
    SURFACE_ALT,
    BORDER,
    MUTED,
    TEXT,
    ROXO,
    ROXO_CLARO,
    CIANO,
    VERDE,
    ROSA,
    MAX_CONTENT_WIDTH,
)


def _criar_card_lateral(acao: Optional[Callable]) -> ft.Container:
    return ft.Container(
        col={"xs": 12, "sm": 12, "md": 12, "lg": 3, "xl": 3},
        height=300,
        padding=20,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=18,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.OutlinedButton(
                    "Ver recursos",
                    icon=ft.Icons.ARROW_OUTWARD,
                    on_click=acao,
                    style=ft.ButtonStyle(
                        color=TEXT,
                        side=ft.BorderSide(1, ROXO_CLARO),
                        shape=ft.RoundedRectangleBorder(radius=18),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                        text_style=ft.TextStyle(size=11),
                    ),
                ),
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("3", size=44, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.Text("eixos avaliativos", size=15, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.Text(
                            "Consulte os resultados por dimensão da avaliação institucional.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
            ],
        ),
    )


def _criar_linha_eixo(titulo: str, cor: str) -> ft.Column:
    return ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(titulo, size=11, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text("[MÉDIA]", size=10, color=MUTED, font_family="monospace"),
                ],
            ),
            ft.Container(
                height=7,
                bgcolor=SURFACE_ALT,
                border_radius=8,
                content=ft.Container(
                    width=210,
                    height=7,
                    bgcolor=cor,
                    border_radius=8,
                ),
            ),
        ],
    )


def _criar_painel_resultados() -> ft.Container:
    return ft.Container(
        col={"xs": 12, "sm": 12, "md": 12, "lg": 6, "xl": 6},
        height=300,
        padding=18,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=18,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(
                                    width=34,
                                    height=34,
                                    border_radius=17,
                                    bgcolor=ROXO,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(ft.Icons.BOLT, color=ft.Colors.WHITE, size=18),
                                ),
                                ft.Column(
                                    spacing=0,
                                    controls=[
                                        ft.Text("Painel de resultados", size=15, weight=ft.FontWeight.W_600, color=TEXT),
                                        ft.Text("Avaliação institucional", size=10, color=MUTED),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=9, vertical=5),
                            bgcolor=SURFACE_ALT,
                            border=ft.Border.all(1, BORDER),
                            border_radius=16,
                            content=ft.Row(
                                spacing=5,
                                tight=True,
                                controls=[
                                    ft.Container(width=6, height=6, bgcolor=VERDE, border_radius=3),
                                    ft.Text("PRÉVIA ILUSTRATIVA", size=8, color=MUTED, font_family="monospace"),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding.only(left=16, right=16, top=10, bottom=12),
                    bgcolor="#100D18",
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Container(width=7, height=7, bgcolor=ROSA, border_radius=4),
                                    ft.Container(width=7, height=7, bgcolor="#F5A348", border_radius=4),
                                    ft.Container(width=7, height=7, bgcolor=VERDE, border_radius=4),
                                    ft.Container(expand=True),
                                    ft.Text("app.evalytics", size=9, color=MUTED, font_family="monospace"),
                                ],
                            ),
                            ft.Divider(height=1, color=BORDER),
                            ft.Text("Médias por eixo", size=13, weight=ft.FontWeight.W_600, color=TEXT),
                            _criar_linha_eixo("Organização Didático-Pedagógica", ROXO_CLARO),
                            _criar_linha_eixo("Corpo Docente e Tutorial", CIANO),
                            _criar_linha_eixo("Infraestrutura", ROSA),
                        ],
                    ),
                ),
            ],
        ),
    )


def _criar_card_recursos() -> ft.Container:
    recursos = [
        (ft.Icons.EDIT_NOTE, "Avaliações", ROXO_CLARO),
        (ft.Icons.SCHOOL_OUTLINED, "Cursos", CIANO),
        (ft.Icons.INSERT_CHART_OUTLINED, "Relatórios", ROSA),
    ]
    return ft.Container(
        col={"xs": 12, "sm": 12, "md": 12, "lg": 3, "xl": 3},
        height=300,
        padding=20,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=18,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("Tudo em um só lugar", size=16, weight=ft.FontWeight.W_600, color=TEXT, text_align=ft.TextAlign.CENTER),
                        ft.Text(
                            "Avaliações, cursos e análise de resultados.",
                            size=11,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=48,
                            height=58,
                            border_radius=12,
                            bgcolor=ft.Colors.with_opacity(0.12, cor),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(icone, color=cor, size=22),
                        )
                        for icone, _, cor in recursos
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=4,
                    controls=[ft.Text(rotulo, size=9, color=MUTED) for _, rotulo, _ in recursos],
                ),
            ],
        ),
    )


def criar_painel_hero(
    page: ft.Page = None,
    ir_para_recursos: Optional[Callable] = None,
) -> ft.Container:
    """Mostra uma prévia responsiva dos principais espaços do Evalytics."""
    return ft.Container(
        width=MAX_CONTENT_WIDTH,
        padding=ft.Padding.symmetric(horizontal=4, vertical=4),
        content=ft.ResponsiveRow(
            columns=12,
            spacing=12,
            run_spacing=12,
            controls=[
                _criar_card_lateral(ir_para_recursos),
                _criar_painel_resultados(),
                _criar_card_recursos(),
            ],
        ),
    )
