import flet as ft
from typing import Callable

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    COR_PRIMARIA,
)
from components.core.router.rotas_cts import ROTA_DASHBOARD_AVALIACOES
from components.layout.responsive.responsive import ResponsiveLayout
from utils.services.relatorio.relatorio_utils import obter_semestre

from models.inicio.inicio_graficos import _formatar_data

def _criar_indicador(
    layout: ResponsiveLayout,
    titulo: str,
    valor: str,
    icone: str,
    coluna: dict[str, int],
    contexto: str = "",
) -> ft.Container:
    cores = layout.cores
    return ft.Container(
        col=coluna,
        bgcolor=cores[CARD],
        padding=16,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            titulo,
                            size=12,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                        ft.Icon(icone, size=18, color=COR_PRIMARIA),
                    ],
                ),
                ft.Text(
                    valor,
                    size=26,
                    weight=ft.FontWeight.W_700,
                    color=cores[TEXTO_PRINCIPAL],
                ),
                ft.Text(
                    contexto,
                    size=10,
                    color=cores[TEXTO_SECUNDARIO],
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    visible=bool(contexto),
                ),
            ],
        ),
    )


def _criar_painel_cursos(
    layout: ResponsiveLayout,
    avaliacoes: list[dict],
    cursos: list[dict],
    altura_painel: int,
) -> ft.Container:
    """Exibe avaliações e respostas agrupadas pelos cursos atuais."""
    por_curso: dict[str, dict] = {}

    for curso in cursos:
        nome = str(curso.get("nome") or "").strip()
        if nome:
            por_curso[nome.casefold()] = {
                "nome": nome,
                "avaliacoes": 0,
                "respostas": 0,
            }

    for avaliacao in avaliacoes:
        nome = str(avaliacao.get("curso_nome") or "Curso sem nome").strip()
        chave = nome.casefold()
        if chave not in por_curso:
            # Avaliações órfãs (curso removido do cadastro) não entram nos dados válidos.
            continue
        respostas = avaliacao.get("respostas", {})
        por_curso[chave]["avaliacoes"] += 1
        por_curso[chave]["respostas"] += len(respostas) if isinstance(respostas, dict) else 0

    dados = sorted(
        por_curso.values(),
        key=lambda item: (
            -item["avaliacoes"],
            -item["respostas"],
            item["nome"].casefold(),
        ),
    )
    maior_total = max((item["avaliacoes"] for item in dados), default=0)
    cores = layout.cores

    if dados:
        controles: list[ft.Control] = []
        for item in dados:
            proporcao = item["avaliacoes"] / maior_total if maior_total else 0
            controles.append(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    item["nome"],
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=cores[TEXTO_PRINCIPAL],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{item['avaliacoes']} avaliações",
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                ),
                            ],
                        ),
                        ft.ProgressBar(
                            value=proporcao,
                            color=COR_PRIMARIA,
                            bgcolor=cores[CARD_SECUNDARIO],
                            height=7,
                            border_radius=5,
                        ),
                        ft.Text(
                            f"{item['respostas']} respostas registradas",
                            size=10,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                )
            )
    else:
        controles = [
            ft.Text(
                "Cadastre cursos e registre avaliações para ver a atividade por curso.",
                size=12,
                color=cores[TEXTO_SECUNDARIO],
            )
        ]

    lista_cursos = ft.Column(
        height=max(180, altura_painel - 100),
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=controles,
    )

    return ft.Container(
        height=altura_painel,
        bgcolor=cores[CARD],
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Atividade por curso",
                            size=16,
                            weight=ft.FontWeight.W_700,
                            color=cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            f"{len(dados)} cursos · ordenados por avaliações e respostas.",
                            size=11,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                lista_cursos,
            ],
        ),
    )


def _criar_secao_avaliacoes(
    layout: ResponsiveLayout,
    avaliacoes: list[dict],
    mudar_tela: Callable[[str], None],
) -> ft.Container:
    cores = layout.cores
    linhas = []

    for avaliacao in avaliacoes[:5]:
        respostas = avaliacao.get("respostas", {})
        if not isinstance(respostas, dict):
            respostas = {}
        data = avaliacao.get("data_avaliacao")
        semestre = avaliacao.get("semestre") or obter_semestre(data)
        nome_curso = str(avaliacao.get("curso_nome") or "Curso sem nome")
        descricao = " · ".join(
            parte
            for parte in (
                semestre or "Semestre não informado",
                _formatar_data(data),
                f"{len(respostas)} respostas",
            )
            if parte
        )
        linhas.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=12, horizontal=4),
                ink=True,
                on_click=lambda e: mudar_tela(ROTA_DASHBOARD_AVALIACOES),
                border=ft.Border(
                    bottom=ft.BorderSide(1, cores[BORDA]),
                ),
                content=ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.12, COR_PRIMARIA),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.ASSIGNMENT_OUTLINED,
                                size=18,
                                color=COR_PRIMARIA,
                            ),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=3,
                            controls=[
                                ft.Text(
                                    nome_curso,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=cores[TEXTO_PRINCIPAL],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    descricao,
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                        ft.Icon(
                            ft.Icons.CHEVRON_RIGHT,
                            size=19,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
            )
        )

    if not linhas:
        linhas.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=24, horizontal=8),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Nenhuma avaliação registrada ainda.",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=cores[TEXTO_PRINCIPAL],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Inicie uma avaliação para acompanhar os resultados nesta tela.",
                            size=11,
                            color=layout.cores[TEXTO_SECUNDARIO],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.OutlinedButton(
                            "Iniciar primeira avaliação",
                            icon=ft.Icons.ADD_ROUNDED,
                            on_click=lambda e: mudar_tela("/formulario"),
                        ),
                    ],
                ),
            )
        )

    return ft.Container(
        bgcolor=cores[CARD],
        padding=20,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    "Avaliações recentes",
                                    size=16,
                                    weight=ft.FontWeight.W_700,
                                    color=cores[TEXTO_PRINCIPAL],
                                ),
                                ft.Text(
                                    "Acompanhe os últimos registros da instituição.",
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                ),
                            ],
                        ),
                        ft.TextButton(
                            "Ver todas",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: mudar_tela(ROTA_DASHBOARD_AVALIACOES),
                        ),
                    ],
                ),
                *linhas,
            ],
        ),
    )


