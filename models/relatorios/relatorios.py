import flet as ft
from typing import Callable

from components.layout.responsive.responsive import ResponsiveLayout
from components.core.constants.constants import BORDA
from components.core.router.rotas_cts import (
    ROTA_RELATORIOS,
    ROTA_RELATORIOS_DADOS,
)
from components.core.theme.border_utils import criar_borda_uniforme
from models.relatorios.widgets.filtros_relatorios import criar_secao_filtros
from models.relatorios.widgets.tables.tabela_resultados import criar_tabela_resultados
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
) -> ft.View:
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Dados e Exportação",
        subtitulo="Consulte avaliações e exporte resultados em PDF ou CSV.",
        mudar_tela=mudar_tela,
    )
    borda_container = criar_borda_uniforme(layout.cores[BORDA])
    resultados_originais = listar_resultados_avaliacoes()

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

    tabela_resultados = None

    def aplicar_filtros(
        semestre: str | None,
        curso_nome: str | None,
        eixo: int | None,
    ) -> None:
        if tabela_resultados is not None and hasattr(tabela_resultados, "atualizar"):
            tabela_resultados.atualizar(semestre, curso_nome, eixo)

        page.update()

    secao_filtros = criar_secao_filtros(
        layout,
        borda_container,
        page,
        aplicar_filtros,
        exportar_csv_atual,
        exportar_pdf_atual,
        resultados=resultados_originais,
        embutido=True,
    )
    tabela_resultados = criar_tabela_resultados(
        page,
        layout,
        borda_container,
        exportar_csv_atual,
        exportar_pdf_atual,
        secao_filtros=secao_filtros,
    )

    layout.add_content(ft.Container(expand=True, content=tabela_resultados))
    return layout.criar_view(rota)


def ViewRelatorios(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Atalho da seção Relatórios para dados e exportação."""
    return _criar_view_relatorios(
        page, mudar_tela, ROTA_RELATORIOS
    )


def ViewRelatoriosDados(
    page: ft.Page, mudar_tela: Callable[[str], None]
) -> ft.View:
    """Subtela com os dados brutos e as opções de exportação."""
    return _criar_view_relatorios(
        page, mudar_tela, ROTA_RELATORIOS_DADOS
    )
