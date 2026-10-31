import flet as ft
from components.landing.palette import (
    PAGE,
    SURFACE,
    SURFACE_ALT,
    BORDER,
    TEXT,
    MUTED,
    ROXO_CLARO,
    CIANO,
    VERDE,
    ROSA,
    MAX_CONTENT_WIDTH,
)

def criar_secao_sobre(page: ft.Page = None) -> ft.Container:
    """
    Constrói a seção institucional 'Sobre o Evalytics'.
    Apresenta a proposta de valor, metodologia e os 3 pilares do ciclo de avaliação com cards de mesmo tamanho.
    """

    def _pilar_card(numero: str, titulo: str, descricao: str, cor: str) -> ft.Container:
        return ft.Container(
            col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
            bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER),
            border_radius=12,
            height=180,
            padding=ft.Padding.only(left=20, right=20, top=18, bottom=18),
            content=ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.12, cor),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    numero,
                                    size=12,
                                    weight=ft.FontWeight.W_700,
                                    color=cor,
                                    font_family="monospace",
                                ),
                            ),
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=cor,
                            ),
                        ],
                    ),
                    ft.Text(
                        titulo,
                        size=15,
                        weight=ft.FontWeight.W_700,
                        color=TEXT,
                    ),
                    ft.Text(
                        descricao,
                        size=12,
                        color=MUTED,
                    ),
                ],
            ),
        )

    pilares = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[
            _pilar_card(
                numero="01",
                titulo="Organizar avaliações",
                descricao="Agrupe avaliações e respostas por curso, semestre e eixo avaliativo.",
                cor=ROXO_CLARO,
            ),
            _pilar_card(
                numero="02",
                titulo="Consultar indicadores",
                descricao="Explore os indicadores institucionais e os critérios de avaliação associados.",
                cor=CIANO,
            ),
            _pilar_card(
                numero="03",
                titulo="Analisar resultados",
                descricao="Consulte os resultados no dashboard e exporte relatórios em PDF ou dados em CSV.",
                cor=VERDE,
            ),
        ],
    )

    return ft.Container(
        key=ft.ScrollKey("sobre"),
        bgcolor=PAGE,
        padding=ft.Padding.only(left=24, right=24, top=32, bottom=64),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Column(
                spacing=28,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Cabeçalho da Seção Sobre
                    ft.Column(
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                                bgcolor=ft.Colors.with_opacity(0.10, ROSA),
                                border=ft.Border.all(1, ft.Colors.with_opacity(0.35, ROSA)),
                                border_radius=16,
                                content=ft.Text(
                                    "SOBRE O EVALYTICS",
                                    size=11,
                                    weight=ft.FontWeight.W_700,
                                    color=ROSA,
                                    font_family="monospace",
                                ),
                            ),
                            ft.Text(
                                "Da avaliação ao relatório, em um só lugar.",
                                size=28,
                                weight=ft.FontWeight.W_700,
                                color=TEXT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                width=540,
                                content=ft.Text(
                                    "No Evalytics, cada avaliação pode ser organizada por curso e semestre. "
                                    "As respostas ficam agrupadas por eixo e podem ser consultadas no dashboard "
                                    "ou exportadas em PDF e CSV.",
                                    size=14,
                                    color=MUTED,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ),
                        ],
                    ),

                    # Grade dos 3 Pilares com alturas padronizadas
                    pilares,
                ],
            ),
        ),
    )
