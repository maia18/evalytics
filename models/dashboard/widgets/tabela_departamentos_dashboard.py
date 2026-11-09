import flet as ft

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.core.theme.border_utils import criar_borda_uniforme


def criar_tabela_departamentos_dashboard(
    layout, dados_por_departamento: list[dict]
) -> ft.Container:
    """Apresenta avaliações, respostas e médias agrupadas por departamento."""

    def celula(
        texto: str,
        proporcao: int,
        *,
        numerica: bool = False,
        negrito: bool = False,
    ) -> ft.Container:
        return ft.Container(
            expand=proporcao,
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            alignment=(
                ft.Alignment.CENTER_RIGHT if numerica else ft.Alignment.CENTER_LEFT
            ),
            content=ft.Text(
                texto,
                size=10,
                color=layout.cores[TEXTO_PRINCIPAL],
                weight=ft.FontWeight.BOLD if negrito else None,
                text_align=ft.TextAlign.RIGHT if numerica else ft.TextAlign.LEFT,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        )

    if not dados_por_departamento:
        conteudo: ft.Control = ft.Text(
            "Nenhum departamento possui cursos cadastrados.",
            size=11,
            color=layout.cores[TEXTO_SECUNDARIO],
        )
    else:
        colunas = [
            ("Departamento", 5, False),
            ("Cursos", 1, True),
            ("Avaliações", 2, True),
            ("Respostas", 2, True),
            ("Média (1–5)", 2, True),
        ]
        linhas: list[ft.Control] = [
            ft.Container(
                bgcolor=layout.cores[CARD_SECUNDARIO],
                content=ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        ft.Container(
                            expand=proporcao,
                            padding=ft.Padding.symmetric(
                                horizontal=14, vertical=14
                            ),
                            alignment=(
                                ft.Alignment.CENTER_RIGHT
                                if numerica
                                else ft.Alignment.CENTER_LEFT
                            ),
                            content=ft.Text(
                                rotulo,
                                size=10,
                                color=layout.cores[TEXTO_SECUNDARIO],
                                weight=ft.FontWeight.BOLD,
                                text_align=(
                                    ft.TextAlign.RIGHT
                                    if numerica
                                    else ft.TextAlign.LEFT
                                ),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        )
                        for rotulo, proporcao, numerica in colunas
                    ],
                ),
            )
        ]
        for indice, item in enumerate(dados_por_departamento):
            media = (
                f"{item['media_geral']:.1f}"
                if item["media_geral"] is not None
                else "—"
            )
            linhas.append(
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        celula(str(item["departamento"]), 5),
                        celula(str(item["cursos"]), 1, numerica=True),
                        celula(str(item["avaliacoes"]), 2, numerica=True),
                        celula(str(item["respostas"]), 2, numerica=True),
                        celula(media, 2, numerica=True, negrito=True),
                    ],
                )
            )
            if indice < len(dados_por_departamento) - 1:
                linhas.append(ft.Divider(height=1, color=layout.cores[BORDA]))
        conteudo = ft.Column(
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=linhas,
        )

    return ft.Container(
        bgcolor=layout.cores[CARD],
        padding=14,
        border_radius=8,
        border=criar_borda_uniforme(layout.cores[BORDA]),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=10,
            controls=[
                ft.Column(
                    spacing=3,
                    controls=[
                        ft.Text(
                            "Resultados por departamento",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            "Cursos, avaliações, respostas e média em cada departamento.",
                            size=10,
                            color=layout.cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                conteudo,
            ],
        ),
    )
