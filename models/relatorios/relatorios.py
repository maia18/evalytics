import asyncio
import logging
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

logger = logging.getLogger(__name__)


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
    resultados_originais: list[dict] = []

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

    secao_filtros = criar_secao_filtros(
        layout,
        borda_container,
        page,
        aplicar_filtros,
        exportar_csv_atual,
        exportar_pdf_atual,
        resultados=[],
        embutido=True,
    )
    tabela_resultados = criar_tabela_resultados(
        page,
        layout,
        borda_container,
        exportar_csv_atual,
        exportar_pdf_atual,
        secao_filtros=secao_filtros,
        resultados_iniciais=[],
        carregando=True,
    )
    erro_carregamento = ft.Row(
        visible=False,
        controls=[
            ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.AMBER_400),
            ft.Text("Não foi possível carregar os resultados."),
            ft.TextButton(
                "Tentar novamente",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: tentar_novamente(),
            ),
        ],
    )
    area_conteudo = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[tabela_resultados, erro_carregamento],
        ),
    )
    layout.add_content(area_conteudo)
    view = layout.criar_view(rota)
    geracao = getattr(page, "_relatorios_load_generation", 0) + 1
    page._relatorios_load_generation = geracao

    def tentar_novamente() -> None:
        erro_carregamento.visible = False
        tabela_resultados.definir_carregando(True)
        page.run_task(carregar_relatorios)
        page.update()

    async def carregar_relatorios() -> None:
        try:
            resultados_carregados = await asyncio.wait_for(
                asyncio.to_thread(listar_resultados_avaliacoes, True),
                timeout=45,
            )

            # Evita montar controles e redesenhar uma tela que o usuário já deixou.
            if (
                getattr(page, "rota_navegacao_atual", None) != rota
                or getattr(page, "_relatorios_load_generation", None) != geracao
            ):
                return
            # Mantém os callbacks dos botões ligados à lista que já existe.
            resultados_originais.clear()
            resultados_originais.extend(resultados_carregados)
            secao_filtros.atualizar_opcoes(resultados_carregados)
            tabela_resultados.definir_resultados(resultados_carregados)
            page.update()
        except Exception:
            logger.exception("Falha ao carregar a tela de relatórios.")
            if (
                getattr(page, "rota_navegacao_atual", None) != rota
                or getattr(page, "_relatorios_load_generation", None) != geracao
            ):
                return
            tabela_resultados.definir_carregando(
                True, "Falha ao consultar os resultados."
            )
            erro_carregamento.visible = True
            page.update()

    page.run_task(carregar_relatorios)
    return view


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
