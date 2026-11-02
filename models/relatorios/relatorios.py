import flet as ft
from typing import Callable

from components.layout.responsive.responsive import ResponsiveLayout
from components.core.constants.constants import BORDA
from components.core.router.rotas_cts import (
    ROTA_RELATORIOS_DASHBOARD,
    ROTA_RELATORIOS_DADOS,
)
from components.core.theme.border_utils import criar_borda_uniforme
from models.relatorios.widgets.filtros_relatorios import criar_secao_filtros
from models.relatorios.widgets.tables.tabela_resultados import criar_tabela_resultados
from models.relatorios.views.resultados_view import TelaResultados
from models.avaliacoes.core.csv.export_csv import exportar_csv
from models.relatorios.core.pdf.relatorios_pdf_utils import processar_exportacao_pdf
from models.relatorios.widgets.modal_filtros_exportacao import (
    abrir_modal_filtros_exportacao,
)
from utils.services.relatorio.relatorio_service import listar_resultados_avaliacoes


def _criar_view_relatorios(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
    rota: str,
    exibir_dashboard: bool,
) -> ft.View:
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Relatórios e Exportações",
        subtitulo="Analise indicadores visuais e exporte resultados consolidados.",
        mudar_tela=mudar_tela,
    )
    borda_container = criar_borda_uniforme(layout.cores[BORDA])
    resultados_originais = listar_resultados_avaliacoes()

    dashboard_visual = TelaResultados(page) if exibir_dashboard else None
    tabela_resultados = None

    def exportar_csv_selecionado(
        resultados: list[dict], _semestre: str, _eixo: int | None
    ) -> None:
        exportar_csv(page, resultados=list(resultados))

    def exportar_csv_atual(e=None) -> None:
        abrir_modal_filtros_exportacao(
            page, resultados_originais, exportar_csv_selecionado,
            "Exportar CSV", "Exportar CSV", ft.Icons.TABLE_VIEW,
            ft.Colors.GREEN_700,
        )

    def exportar_pdf_selecionado(
        resultados: list[dict], semestre: str, eixo: int | None
    ) -> None:
        processar_exportacao_pdf(page, resultados, semestre, eixo)

    def exportar_pdf_atual(e=None) -> None:
        abrir_modal_filtros_exportacao(
            page, resultados_originais, exportar_pdf_selecionado,
            "Gerar relatório PDF", "Gerar PDF", ft.Icons.PICTURE_AS_PDF,
            ft.Colors.RED_700,
        )

    if not exibir_dashboard:
        tabela_resultados = criar_tabela_resultados(
            page, layout, borda_container, exportar_csv_atual, exportar_pdf_atual
        )

    def aplicar_filtros(
        semestre: str | None,
        curso_nome: str | None,
        eixo: int | None,
    ) -> None:
        if dashboard_visual is not None and hasattr(dashboard_visual, "atualizar"):
            dashboard_visual.atualizar(semestre, curso_nome, eixo)

        if tabela_resultados is not None:
            conteudo_tabela = getattr(tabela_resultados, "content", None)
            controles = getattr(conteudo_tabela, "controls", [])
            if len(controles) > 2 and hasattr(controles[2], "atualizar"):
                controles[2].atualizar(semestre, curso_nome, eixo)

        page.update()

    secao_filtros = criar_secao_filtros(
        layout,
        borda_container,
        page,
        aplicar_filtros,
        exportar_csv_atual,
        exportar_pdf_atual,
        resultados=resultados_originais,
    )
    if dashboard_visual is not None:
        dashboard_visual.limpar_filtros = secao_filtros.limpar_filtros

    if dashboard_visual is not None:
        conteudo_principal = dashboard_visual
    else:
        conteudo_principal = ft.Container(
            expand=True,
            padding=ft.Padding.only(top=20),
            content=ft.Column(expand=True, controls=[tabela_resultados]),
        )

    layout.add_content(
        ft.Column(
            expand=True,
            controls=[secao_filtros, conteudo_principal],
        )
    )
    return layout.criar_view(rota)


def ViewRelatorios(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Dashboard executivo (rota padrão e subtela de relatórios)."""
    return _criar_view_relatorios(
        page, mudar_tela, ROTA_RELATORIOS_DASHBOARD, exibir_dashboard=True
    )


def ViewRelatoriosDados(
    page: ft.Page, mudar_tela: Callable[[str], None]
) -> ft.View:
    """Subtela com os dados brutos e as opções de exportação."""
    return _criar_view_relatorios(
        page, mudar_tela, ROTA_RELATORIOS_DADOS, exibir_dashboard=False
    )
