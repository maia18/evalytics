import asyncio
import flet as ft
from typing import Callable

from components.core.constants.constants import (
    BORDA,
    COR_PRIMARIA,
    TEXTO_SECUNDARIO,
)
from components.core.router.rotas_cts import (
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_DASHBOARD_AVALIACOES,
    ROTA_DASHBOARD_RESULTADOS,
)
from components.layout.responsive.responsive import ResponsiveLayout
from components.core.theme.border_utils import criar_borda_uniforme
from database.services.dashboard.firestore_dashboard import obter_dados_dashboard
from models.avaliacoes.avaliacoes import criar_conteudo_avaliacoes
from models.dashboard.views.resultados_view import TelaResultados
from models.relatorios.widgets.filtros_relatorios import criar_secao_filtros
from utils.services.relatorio.relatorio_service import listar_resultados_avaliacoes
from models.dashboard.widgets.graphics.grafico_eixos import criar_grafico_eixos
from models.dashboard.widgets.kpi_cards import criar_kpi_card
from models.dashboard.widgets.grafico_evolucao_semestres import (
    criar_grafico_evolucao_semestres,
)
from models.dashboard.widgets.tabela_cursos_dashboard import (
    criar_tabela_cursos_dashboard,
)
from models.dashboard.widgets.tabela_departamentos_dashboard import (
    criar_tabela_departamentos_dashboard,
)


CORES_BARRAS_GRAFICO_EIXOS = [COR_PRIMARIA, "#34D399", "#F87171"]
NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}


def _criar_filtros(
    dados: dict,
    aplicar,
    limpar,
) -> tuple[ft.Container, ft.Dropdown, ft.Dropdown, ft.Dropdown]:
    dropdown_semestre = ft.Dropdown(
        label="Semestre",
        value="TODOS",
        expand=1,
        text_size=12,
        label_style=ft.TextStyle(size=10),
        dense=True,
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=semestre, text=semestre)
                for semestre in dados["semestres_disponiveis"]
            ],
        ],
    )
    dropdown_curso = ft.Dropdown(
        label="Curso",
        value="TODOS",
        expand=1,
        text_size=12,
        label_style=ft.TextStyle(size=10),
        dense=True,
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=curso, text=curso)
                for curso in dados["cursos_disponiveis"]
            ],
        ],
    )
    dropdown_departamento = ft.Dropdown(
        label="Departamento",
        value="TODOS",
        expand=1,
        text_size=12,
        label_style=ft.TextStyle(size=10),
        dense=True,
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=departamento, text=departamento)
                for departamento in dados["departamentos_disponiveis"]
            ],
        ],
    )
    botao_aplicar = ft.ElevatedButton(
        "Aplicar",
        icon=ft.Icons.FILTER_ALT,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        on_click=aplicar,
        width=112,
        height=40,
    )
    botao_limpar = ft.OutlinedButton(
        "Limpar",
        icon=ft.Icons.CLEAR,
        on_click=limpar,
        width=112,
        height=40,
    )

    colunas_campos = {
        "xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 3, "xxl": 3
    }
    colunas_botoes = {
        "xs": 12, "sm": 12, "md": 12, "lg": 3, "xl": 3, "xxl": 3
    }
    conteudo_filtros = ft.ResponsiveRow(
        spacing=8,
        run_spacing=8,
        controls=[
            ft.Container(
                col=colunas_campos,
                content=ft.Row(controls=[dropdown_semestre]),
            ),
            ft.Container(
                col=colunas_campos,
                content=ft.Row(controls=[dropdown_curso]),
            ),
            ft.Container(
                col=colunas_campos,
                content=ft.Row(controls=[dropdown_departamento]),
            ),
            ft.Container(
                col=colunas_botoes,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=8,
                    controls=[botao_aplicar, botao_limpar],
                ),
            ),
        ],
    )

    container = ft.Container(
        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        border=ft.Border.all(1, "#3A3A3A"),
        border_radius=8,
        content=conteudo_filtros,
    )
    return container, dropdown_semestre, dropdown_curso, dropdown_departamento


def _criar_kpis(layout, dados: dict) -> list[ft.Control]:
    media = dados["media_geral"]
    colunas = {"xs": 12, "sm": 6, "md": 6, "lg": 3, "xl": 3, "xxl": 3}
    return [
        criar_kpi_card(
            layout,
            "Avaliações realizadas",
            f"{dados['avaliacoes']:,}".replace(",", "."),
            ft.Icons.ASSIGNMENT_OUTLINED,
            COR_PRIMARIA,
            col=colunas,
        ),
        criar_kpi_card(
            layout,
            "Respostas registradas",
            f"{dados['respostas']:,}".replace(",", "."),
            ft.Icons.TRENDING_UP,
            COR_PRIMARIA,
            col=colunas,
        ),
        criar_kpi_card(
            layout,
            "Cursos avaliados",
            str(dados["cursos"]),
            ft.Icons.SCHOOL_OUTLINED,
            COR_PRIMARIA,
            col=colunas,
        ),
        criar_kpi_card(
            layout,
            "Média geral (1–5)",
            f"{media:.1f}" if media is not None else "—",
            ft.Icons.STAR_OUTLINE,
            COR_PRIMARIA,
            col=colunas,
        ),
    ]


def _criar_layout(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
    rota: str,
    exibir_visao_geral: bool,
) -> ft.View:
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Indicadores de Avaliação",
        subtitulo="Acompanhe os resultados e a evolução das avaliações institucionais.",
        mudar_tela=mudar_tela,
    )

    if exibir_visao_geral:
        altura_tela = float(getattr(page, "height", 768) or 768)
        altura_card_eixos = max(300, min(420, int(altura_tela * 0.55)))
        altura_card_cursos = max(230, min(320, int(altura_tela * 0.38)))
        dados_iniciais = {
            "avaliacoes": 0,
            "respostas": 0,
            "cursos": 0,
            "media_geral": None,
            "medias_eixos": {},
            "respostas_por_eixo": {},
            "dados_por_curso": [],
            "dados_por_departamento": [],
            "evolucao_semestres": [],
            "semestres_disponiveis": [],
            "cursos_disponiveis": [],
            "departamentos_disponiveis": [],
        }
        seletores = {}
        texto_contexto = ft.Text(
            "Todos os cursos · Todos os semestres · Todos os departamentos",
            size=12,
            color=layout.cores[TEXTO_SECUNDARIO],
        )
        linha_kpis = ft.ResponsiveRow(
            spacing=12,
            run_spacing=12,
            controls=_criar_kpis(layout, dados_iniciais),
        )
        area_eixos = ft.Container(
            content=criar_grafico_eixos(
                layout,
                dados_iniciais["medias_eixos"],
                NOMES_EIXOS,
                CORES_BARRAS_GRAFICO_EIXOS,
                dados_iniciais["respostas_por_eixo"],
                dados_iniciais["media_geral"],
                altura=altura_card_eixos,
            )
        )
        area_cursos = ft.Container(
            content=criar_tabela_cursos_dashboard(
                layout, dados_iniciais["dados_por_curso"],
                altura=altura_card_cursos,
            )
        )
        area_evolucao = ft.Container(
            content=criar_grafico_evolucao_semestres(
                layout, dados_iniciais["evolucao_semestres"]
            )
        )
        area_departamentos = ft.Container(
            content=criar_tabela_departamentos_dashboard(
                layout, dados_iniciais["dados_por_departamento"]
            )
        )
        paineis_analiticos = ft.Column(
            spacing=12,
            controls=[area_eixos, area_cursos, area_departamentos, area_evolucao],
        )

        def atualizar_componentes(dados: dict, selecao: tuple[str, str, str]) -> None:
            linha_kpis.controls = _criar_kpis(layout, dados)
            area_eixos.content = criar_grafico_eixos(
                layout,
                dados["medias_eixos"],
                NOMES_EIXOS,
                CORES_BARRAS_GRAFICO_EIXOS,
                dados["respostas_por_eixo"],
                dados["media_geral"],
                altura=altura_card_eixos,
            )
            area_cursos.content = criar_tabela_cursos_dashboard(
                layout, dados["dados_por_curso"],
                altura=altura_card_cursos,
            )
            area_evolucao.content = criar_grafico_evolucao_semestres(
                layout, dados["evolucao_semestres"]
            )
            area_departamentos.content = criar_tabela_departamentos_dashboard(
                layout, dados["dados_por_departamento"]
            )
            texto_contexto.value = (
                f"{selecao[0] if selecao[0] not in (None, '', 'TODOS') else 'Todos'}"
                f" · {selecao[1] if selecao[1] not in (None, '', 'TODOS') else 'Todos'}"
                f" · {selecao[2] if selecao[2] not in (None, '', 'TODOS') else 'Todos'}"
            )

        async def carregar_dashboard(
            semestre_selecionado=None,
            curso_selecionado=None,
            departamento_selecionado=None,
        ) -> None:
            dados = await asyncio.to_thread(
                obter_dados_dashboard,
                semestre=(semestre_selecionado if semestre_selecionado not in (None, "", "TODOS") else None),
                curso_nome=(curso_selecionado if curso_selecionado not in (None, "", "TODOS") else None),
                departamento=(departamento_selecionado if departamento_selecionado not in (None, "", "TODOS") else None),
            )
            for chave, valores in (
                ("semestre", dados["semestres_disponiveis"]),
                ("curso", dados["cursos_disponiveis"]),
                ("departamento", dados["departamentos_disponiveis"]),
            ):
                seletor = seletores[chave]
                seletor.options = [ft.dropdown.Option(key="TODOS", text="Todos")] + [
                    ft.dropdown.Option(key=valor, text=valor) for valor in valores
                ]
            atualizar_componentes(
                dados,
                (curso_selecionado, semestre_selecionado, departamento_selecionado),
            )
            page.update()

        def aplicar_filtros(e=None) -> None:
            page.run_task(
                carregar_dashboard,
                seletores["semestre"].value,
                seletores["curso"].value,
                seletores["departamento"].value,
            )

        def limpar_filtros(e=None) -> None:
            seletores["semestre"].value = "TODOS"
            seletores["curso"].value = "TODOS"
            seletores["departamento"].value = "TODOS"
            aplicar_filtros()

        (
            filtros,
            dropdown_semestre,
            dropdown_curso,
            dropdown_departamento,
        ) = _criar_filtros(dados_iniciais, aplicar_filtros, limpar_filtros)
        seletores["semestre"] = dropdown_semestre
        seletores["curso"] = dropdown_curso
        seletores["departamento"] = dropdown_departamento

        conteudo = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                filtros,
                texto_contexto,
                linha_kpis,
                paineis_analiticos,
            ],
        )
    else:
        conteudo = criar_conteudo_avaliacoes(layout, mudar_tela, page)

    layout.add_content(ft.Container(expand=True, content=conteudo))
    view = layout.criar_view(rota)
    if exibir_visao_geral:
        page.run_task(carregar_dashboard)
    return view


def ViewDashboard(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Subtela Visão Geral dos indicadores institucionais."""
    return _criar_layout(
        page, mudar_tela, ROTA_DASHBOARD_VISAO_GERAL, exibir_visao_geral=True
    )


def ViewDashboardAvaliacoes(
    page: ft.Page, mudar_tela: Callable[[str], None]
) -> ft.View:
    """Subtela de acompanhamento das avaliações registradas."""
    return _criar_layout(
        page, mudar_tela, ROTA_DASHBOARD_AVALIACOES, exibir_visao_geral=False
    )


def ViewDashboardResultados(
    page: ft.Page, mudar_tela: Callable[[str], None]
) -> ft.View:
    """Dashboard analítico com médias e respostas por eixo avaliativo."""
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Resultados por eixo",
        subtitulo="Analise as médias e respostas válidas por eixo avaliativo.",
        mudar_tela=mudar_tela,
    )
    painel_resultados = TelaResultados(page)

    def aplicar_filtros(semestre, curso_nome, eixo) -> None:
        painel_resultados.atualizar(semestre, curso_nome, eixo)

    area_resultados = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.ProgressRing(),
    )
    layout.add_content(
        ft.Column(
            expand=True,
            spacing=8,
            controls=[area_resultados],
        )
    )
    view = layout.criar_view(ROTA_DASHBOARD_RESULTADOS)

    async def carregar_resultados_e_filtros() -> None:
        resultados = await asyncio.to_thread(listar_resultados_avaliacoes)
        if getattr(page, "rota_navegacao_atual", None) != ROTA_DASHBOARD_RESULTADOS:
            return
        filtros = criar_secao_filtros(
            layout,
            criar_borda_uniforme(layout.cores[BORDA]),
            page,
            aplicar_filtros,
            resultados=resultados,
        )
        painel_resultados.limpar_filtros = filtros.limpar_filtros
        area_resultados.content = ft.Column(
            expand=True,
            spacing=8,
            controls=[filtros, ft.Container(expand=True, content=painel_resultados)],
        )
        page.update()

    page.run_task(carregar_resultados_e_filtros)
    return view
