import flet as ft
from typing import Callable

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    COR_PRIMARIA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.layout.responsive.responsive import ResponsiveLayout
from models.cursos.core.cursos_controller import carregar_cursos_iniciais
from models.cursos.core.cursos_estatisticas import atualizar_estatisticas
from models.cursos.modals.modal_add import criar_modal_add
from models.cursos.modals.modal_edit import criar_modal_edit
from models.cursos.widgets.campos_curso import criar_campos_formulario_curso
from models.cursos.widgets.stats_cards import criar_stats_card
from models.cursos.widgets.tabela_cursos import ContextoTabelaCursos
from utils.services.cursos.curso_utils import (
    chave_departamento,
    listar_departamentos_unicos,
)


def ViewCursos(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Tela de gestão, busca e manutenção do catálogo de cursos."""
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Gestão de Cursos",
        subtitulo="Adicione, edite ou remova os cursos da instituição.",
        mudar_tela=mudar_tela,
    )
    campos_add = criar_campos_formulario_curso(layout.cores)
    campos_edit = criar_campos_formulario_curso(layout.cores)
    estado = {"linha_atual": None, "id_firebase": None, "cursos": [], "todas_linhas": []}

    tabela_cursos = ft.DataTable(
        heading_row_color=layout.cores[CARD_SECUNDARIO],
        column_spacing=24,
        columns=[
            ft.DataColumn(ft.Text("Código", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
            ft.DataColumn(ft.Text("Nome do Curso", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
            ft.DataColumn(ft.Text("Departamento", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
            ft.DataColumn(ft.Text("Coordenador", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
            ft.DataColumn(ft.Text("Status", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
            ft.DataColumn(ft.Text("Avaliações", weight="bold", color=layout.cores[TEXTO_SECUNDARIO]), numeric=True),
            ft.DataColumn(ft.Text("Ações", weight="bold", color=layout.cores[TEXTO_SECUNDARIO])),
        ],
        rows=[],
    )
    linha_stats = ft.Row(
        spacing=16,
        controls=[
            criar_stats_card("Total de Cursos", "0", layout.cores),
            criar_stats_card("Cursos Ativos", "0", layout.cores),
            criar_stats_card("Departamentos", "0", layout.cores),
        ],
    )
    estado_vazio = ft.Text(color=layout.cores[TEXTO_SECUNDARIO], size=14)
    busca = ft.TextField(
        label="Buscar por nome ou código",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        width=420,
    )
    filtro_departamento = ft.Dropdown(
        label="Departamento",
        value="TODOS",
        width=260,
        dense=True,
        options=[ft.dropdown.Option(key="TODOS", text="Todos")],
    )

    def aplicar_filtros(e=None) -> None:
        cursos = estado["cursos"]
        termo = (busca.value or "").strip().casefold()
        departamento_atual = filtro_departamento.value
        tabela_cursos.rows = [
            linha
            for linha in estado["todas_linhas"]
            if (
                not termo
                or termo in str(linha.cells[0].content.value).casefold()
                or termo in str(linha.cells[1].content.value).casefold()
            )
            and (
                departamento_atual in (None, "", "TODOS")
                or chave_departamento(linha.cells[2].content.value)
                == chave_departamento(departamento_atual)
            )
        ]
        estado_vazio.value = (
            "Nenhum curso cadastrado ainda."
            if not cursos
            else "Nenhum curso encontrado para os filtros selecionados."
        )
        estado_vazio.visible = len(tabela_cursos.rows) == 0
        tabela_cursos.visible = len(tabela_cursos.rows) > 0
        atualizar_estatisticas(page, linha_stats, layout.cores, cursos)

    def atualizar_opcoes_departamentos() -> None:
        departamentos = listar_departamentos_unicos(estado["cursos"])
        selecionado = filtro_departamento.value
        filtro_departamento.options = [
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=departamento, text=departamento)
                for departamento in departamentos
            ],
        ]
        equivalente = next(
            (
                departamento
                for departamento in departamentos
                if chave_departamento(departamento)
                == chave_departamento(selecionado)
            ),
            None,
        )
        filtro_departamento.value = equivalente or "TODOS"
        aplicar_filtros()

    busca.on_submit = aplicar_filtros
    contexto_ref = {}

    def wrapper_atualizar_interface() -> None:
        contexto = contexto_ref.get("contexto")
        if contexto:
            carregar_cursos_iniciais(
                contexto, tabela_cursos, atualizar_opcoes_departamentos
            )

    modal_edit = criar_modal_edit(
        page, estado, campos_edit, wrapper_atualizar_interface, layout.cores
    )
    contexto_tabela = ContextoTabelaCursos(
        page=page,
        tabela_cursos=tabela_cursos,
        atualizar_interface=wrapper_atualizar_interface,
        modal_editar=modal_edit,
        campos_edit=campos_edit,
        estado=estado,
        cores=layout.cores,
    )
    contexto_ref["contexto"] = contexto_tabela
    abrir_modal_add = criar_modal_add(contexto_tabela, campos_add)
    carregar_cursos_iniciais(
        contexto_tabela, tabela_cursos, atualizar_opcoes_departamentos
    )

    conteudo = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=18,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            linha_stats,
            ft.Container(
                bgcolor=layout.cores[CARD],
                padding=ft.Padding.symmetric(horizontal=24, vertical=20),
                border_radius=8,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    spacing=22,
                    controls=[
                        ft.Row(
                            wrap=True,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "Lista de Cursos",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=layout.cores[TEXTO_PRINCIPAL],
                                ),
                                ft.ElevatedButton(
                                    "Adicionar curso",
                                    icon=ft.Icons.ADD,
                                    bgcolor=COR_PRIMARIA,
                                    color=ft.Colors.WHITE,
                                    on_click=abrir_modal_add,
                                ),
                            ],
                        ),
                        ft.Row(
                            wrap=True,
                            spacing=12,
                            run_spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                busca,
                                filtro_departamento,
                                ft.OutlinedButton(
                                    "Aplicar filtros",
                                    icon=ft.Icons.FILTER_ALT,
                                    icon_color=COR_PRIMARIA,
                                    style=ft.ButtonStyle(color=COR_PRIMARIA),
                                    on_click=aplicar_filtros,
                                ),
                            ],
                        ),
                        estado_vazio,
                        tabela_cursos,
                    ],
                ),
            ),
        ],
    )
    layout.add_content(conteudo)
    return layout.criar_view("/cursos")
