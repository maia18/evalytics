import flet as ft
from datetime import datetime
from typing import Callable

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import (
    CARD,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    COR_PRIMARIA,
)
from components.core.constants.texts import (
    TXTS_INICIO,
    TXTS_DASHBOARD,
    TXTS_CURSOS,
    TXTS_RELATORIOS,
    TXTS_CONFIGS,
)
from components.core.router.rotas_cts import ROTA_DASHBOARD_AVALIACOES
from components.layout.responsive.responsive import ResponsiveLayout
from database.services.cursos.firestore_courses import (
    obter_cursos_db,
    curso_esta_ativo,
)
from models.dashboard.widgets.kpi_cards import criar_kpi_card
from models.inicio.widgets.card_inicio import criar_card
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
from utils.services.relatorio.relatorio_utils import obter_semestre


def _chave_data(data) -> float:
    """Gera uma chave de ordenação para datas Firestore, datetime ou ISO."""
    if hasattr(data, "timestamp"):
        try:
            return float(data.timestamp())
        except (TypeError, ValueError, OSError):
            pass
    if isinstance(data, str) and data.strip():
        try:
            valor = datetime.fromisoformat(data.strip().replace("Z", "+00:00"))
            return valor.timestamp()
        except (TypeError, ValueError, OSError):
            pass
    return 0.0


def _formatar_data(data) -> str:
    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y")
    if isinstance(data, str) and data.strip():
        try:
            valor = datetime.fromisoformat(data.strip().replace("Z", "+00:00"))
            return valor.strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return data[:10]
    return "Data não informada"


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


def ViewInicio(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Constrói a tela inicial com boas-vindas, indicadores e atividades recentes."""
    layout = ResponsiveLayout(
        page,
        TXTS_INICIO[0],
        TXTS_INICIO[1],
        mudar_tela=mudar_tela,
    )

    cursos_ativos = sum(1 for curso in obter_cursos_db() if curso_esta_ativo(curso))
    avaliacoes = listar_avaliacoes()
    total_respostas = sum(
        len(avaliacao.get("respostas", {}))
        for avaliacao in avaliacoes
        if isinstance(avaliacao.get("respostas", {}), dict)
    )
    avaliacoes.sort(
        key=lambda item: _chave_data(item.get("data_avaliacao")),
        reverse=True,
    )

    usuario = auth_state.usuario or {}
    nome_usuario = str(usuario.get("displayName") or usuario.get("name") or "").strip()
    primeiro_nome = nome_usuario.split()[0] if nome_usuario else ""
    titulo_boas_vindas = f"Olá, {primeiro_nome}!" if primeiro_nome else "Bem-vindo ao Evalytics"

    hero = ft.Container(
        bgcolor=layout.cores[CARD],
        padding=28,
        border_radius=14,
        border=ft.Border.all(1, layout.cores[BORDA]),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.10, COR_PRIMARIA),
            offset=ft.Offset(0, 8),
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            spacing=20,
            run_spacing=16,
            controls=[
                ft.Column(
                    spacing=8,
                    tight=True,
                    controls=[
                        ft.Text(
                            titulo_boas_vindas,
                            weight=ft.FontWeight.W_700,
                            size=22,
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            "Crie e acompanhe avaliações para entender os resultados da instituição.",
                            size=13,
                            color=layout.cores[TEXTO_SECUNDARIO],
                        ),
                        ft.Container(height=6),
                        ft.ElevatedButton(
                            TXTS_INICIO[3],
                            icon=ft.Icons.ADD_ROUNDED,
                            bgcolor=COR_PRIMARIA,
                            color=ft.Colors.WHITE,
                            height=44,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                            ),
                            on_click=lambda e: mudar_tela("/formulario"),
                        ),
                    ],
                ),
            ],
        ),
    )

    colunas_kpi = {"xs": 12, "sm": 4, "md": 4, "lg": 4}
    indicadores = ft.ResponsiveRow(
        spacing=16,
        run_spacing=12,
        controls=[
            criar_kpi_card(
                layout,
                "Avaliações realizadas",
                str(len(avaliacoes)),
                ft.Icons.ASSIGNMENT_OUTLINED,
                COR_PRIMARIA,
                col=colunas_kpi,
            ),
            criar_kpi_card(
                layout,
                "Cursos ativos",
                str(cursos_ativos),
                ft.Icons.SCHOOL_OUTLINED,
                COR_PRIMARIA,
                col=colunas_kpi,
            ),
            criar_kpi_card(
                layout,
                "Respostas registradas",
                f"{total_respostas:,}".replace(",", "."),
                ft.Icons.FORMAT_LIST_BULLETED,
                COR_PRIMARIA,
                col=colunas_kpi,
            ),
        ],
    )

    atalhos = ft.Column(
        spacing=12,
        controls=[
            ft.Text(
                "Acessos rápidos",
                size=17,
                weight=ft.FontWeight.W_700,
                color=layout.cores[TEXTO_PRINCIPAL],
            ),
            ft.ResponsiveRow(
                spacing=20,
                run_spacing=20,
                controls=[
                    ft.Container(col={"xs": 12, "sm": 6, "md": 4, "lg": 3}, content=criar_card(layout, TXTS_DASHBOARD[0], TXTS_DASHBOARD[1], ft.Icons.GRID_VIEW, "/dashboard", mudar_tela)),
                    ft.Container(col={"xs": 12, "sm": 6, "md": 4, "lg": 3}, content=criar_card(layout, TXTS_CURSOS[0], TXTS_CURSOS[1], ft.Icons.MENU_BOOK, "/cursos", mudar_tela)),
                    ft.Container(col={"xs": 12, "sm": 6, "md": 4, "lg": 3}, content=criar_card(layout, TXTS_RELATORIOS[0], TXTS_RELATORIOS[1], ft.Icons.PIE_CHART, "/relatorios", mudar_tela)),
                    ft.Container(col={"xs": 12, "sm": 6, "md": 4, "lg": 3}, content=criar_card(layout, TXTS_CONFIGS[0], TXTS_CONFIGS[1], ft.Icons.VIEW_COMFY, "/configuracoes", mudar_tela)),
                ],
            ),
        ],
    )

    conteudo = ft.Column(
        expand=True,
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            hero,
            indicadores,
            _criar_secao_avaliacoes(layout, avaliacoes, mudar_tela),
            atalhos,
        ],
    )

    layout.add_content(conteudo)
    return layout.criar_view("/inicio")
