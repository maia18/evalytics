import flet as ft

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.core.theme.border_utils import criar_borda_uniforme


def criar_tabela_cursos_dashboard(
    layout, dados_por_curso: list[dict], altura: int | None = None
) -> ft.Container:
    """Resume avaliações, respostas e média para cada curso selecionado."""

    def criar_celula(
        texto: str,
        proporcao: int,
        *,
        alinhamento: ft.Alignment = ft.Alignment.CENTER_LEFT,
        cor: str = TEXTO_PRINCIPAL,
        negrito: bool = False,
        numerico: bool = False,
    ) -> ft.Container:
        return ft.Container(
            expand=proporcao,
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            alignment=alinhamento,
            content=ft.Text(
                texto,
                size=10,
                color=layout.cores[cor],
                weight=ft.FontWeight.BOLD if negrito else None,
                text_align=ft.TextAlign.RIGHT if numerico else ft.TextAlign.LEFT,
                max_lines=2,
            ),
        )

    if not dados_por_curso:
        conteudo_tabela: ft.Control = ft.Text(
            "Nenhum curso possui dados para os filtros selecionados.",
            color=layout.cores[TEXTO_SECUNDARIO],
        )
    else:
        cabecalho = ft.Container(
            bgcolor=layout.cores[CARD_SECUNDARIO],
            content=ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    criar_celula(
                        "Curso", 6, cor=TEXTO_SECUNDARIO, negrito=True
                    ),
                    criar_celula(
                        "Avaliações",
                        2,
                        alinhamento=ft.Alignment.CENTER_RIGHT,
                        cor=TEXTO_SECUNDARIO,
                        negrito=True,
                        numerico=True,
                    ),
                    criar_celula(
                        "Respostas",
                        2,
                        alinhamento=ft.Alignment.CENTER_RIGHT,
                        cor=TEXTO_SECUNDARIO,
                        negrito=True,
                        numerico=True,
                    ),
                    criar_celula(
                        "Média (1–5)",
                        2,
                        alinhamento=ft.Alignment.CENTER_RIGHT,
                        cor=TEXTO_SECUNDARIO,
                        negrito=True,
                        numerico=True,
                    ),
                ],
            ),
        )
        linhas: list[ft.Control] = [cabecalho]
        for indice, item in enumerate(dados_por_curso):
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
                        criar_celula(str(item["curso"]), 6),
                        criar_celula(
                            str(item["avaliacoes"]),
                            2,
                            alinhamento=ft.Alignment.CENTER_RIGHT,
                            numerico=True,
                        ),
                        criar_celula(
                            str(item["respostas"]),
                            2,
                            alinhamento=ft.Alignment.CENTER_RIGHT,
                            numerico=True,
                        ),
                        criar_celula(
                            media,
                            2,
                            alinhamento=ft.Alignment.CENTER_RIGHT,
                            negrito=True,
                            numerico=True,
                        ),
                    ],
                )
            )
            if indice < len(dados_por_curso) - 1:
                linhas.append(ft.Divider(height=1, color=layout.cores[BORDA]))

        conteudo_tabela = ft.Column(
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=linhas,
        )

    return ft.Container(
        height=altura,
        bgcolor=layout.cores[CARD],
        padding=8,
        border_radius=8,
        border=criar_borda_uniforme(layout.cores[BORDA]),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Visão geral por curso",
                            size=15,
                            weight="bold",
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            "Avaliações realizadas, respostas registradas e média das respostas válidas.",
                            size=10,
                            color=layout.cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                conteudo_tabela,
            ],
        ),
    )
