import flet as ft
from components.core.constants.constants import CARD, TEXTO_SECUNDARIO
from utils.services.relatorio.relatorio_service import (
    listar_semestres_disponiveis,
)
from database.services.cursos.firestore_courses import obter_cursos_db
from utils.services.cursos.curso_utils import listar_nomes_cursos_filtraveis

NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

def criar_secao_filtros(
    layout,
    borda_container: ft.Border,
    page: ft.Page,
    ao_filtrar,
    ao_exportar_csv=None,
    ao_exportar_pdf=None,
    resultados: list[dict] | None = None,
    embutido: bool = False,
) -> ft.Container:
    """
    Cria a seção de filtros dos relatórios.
        Os semestres são carregados diretamente das avaliações existentes no Firestore.
    """

    # ======================================================
    # SEMESTRES REAIS
    # ======================================================

    semestres = listar_semestres_disponiveis()

    opcoes_semestre = [
        ft.dropdown.Option(
            key="TODOS",
            text="Todos",
        )
    ]

    opcoes_semestre.extend(
        ft.dropdown.Option(
            key=semestre,
            text=semestre,
        )
        for semestre in semestres
    )

    dropdown_semestre = ft.Dropdown(
        label="Semestre",
        options=opcoes_semestre,
        value="TODOS",
        width=240,
        dense=True,
    )

    cursos = listar_nomes_cursos_filtraveis(
        resultados or [],
        obter_cursos_db(),
    )
    dropdown_curso = ft.Dropdown(
        label="Curso",
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=curso, text=curso)
                for curso in cursos
            ],
        ],
        value="TODOS",
        width=280,
        dense=True,
    )

    # ======================================================
    # EIXOS REAIS
    # ======================================================

    opcoes_eixo = [
        ft.dropdown.Option(
            key="TODOS",
            text="Todos",
        )
    ]

    opcoes_eixo.extend(
        ft.dropdown.Option(
            key=str(eixo_id),
            text=nome,
        )
        for eixo_id, nome in NOMES_EIXOS.items()
    )

    dropdown_eixo = ft.Dropdown(
        label="Eixo Avaliativo",
        options=opcoes_eixo,
        value="TODOS",
        width=280,
        dense=True,
    )

    # ======================================================
    # APLICAR FILTROS
    # ======================================================

    def aplicar_filtros(e=None):
        semestre = dropdown_semestre.value
        curso = dropdown_curso.value
        eixo = dropdown_eixo.value

        semestre_filtro = (
            None
            if semestre in (None, "", "TODOS")
            else semestre
        )

        eixo_filtro = (
            None
            if eixo in (None, "", "TODOS")
            else int(eixo)
        )

        curso_filtro = (
            None
            if curso in (None, "", "TODOS")
            else curso
        )

        ao_filtrar(
            semestre_filtro,
            curso_filtro,
            eixo_filtro,
        )
        atualizar_resumo_filtros()
        page.update()

    # ======================================================
    # LIMPAR FILTROS
    # ======================================================

    def limpar_filtros(e=None):
        dropdown_semestre.value = "TODOS"
        dropdown_curso.value = "TODOS"
        dropdown_eixo.value = "TODOS"

        ao_filtrar(
            None,
            None,
            None,
        )

        atualizar_resumo_filtros()
        page.update()

    # ======================================================
    # BOTÕES
    # ======================================================

    botao_filtrar = ft.ElevatedButton(
        "Aplicar filtros",
        icon=ft.Icons.FILTER_ALT,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        on_click=aplicar_filtros,
    )

    botao_limpar = ft.OutlinedButton(
        "Limpar",
        icon=ft.Icons.CLEAR,
        on_click=limpar_filtros,
    )

    resumo_filtros = ft.Text(
        "",
        visible=False,
        size=12,
        color=layout.cores[TEXTO_SECUNDARIO],
    )

    def atualizar_resumo_filtros():
        filtros_ativos = []

        def rotulo_opcao(dropdown, nome_filtro):
            selecionada = dropdown.value
            if selecionada in (None, "", "TODOS"):
                return None
            for opcao in dropdown.options:
                if str(opcao.key) == str(selecionada):
                    return f"{nome_filtro}: {opcao.text}"
            return f"{nome_filtro}: {selecionada}"

        for dropdown, nome in (
            (dropdown_curso, "Curso"),
            (dropdown_semestre, "Semestre"),
            (dropdown_eixo, "Eixo"),
        ):
            rotulo = rotulo_opcao(dropdown, nome)
            if rotulo:
                filtros_ativos.append(rotulo)

        resumo_filtros.value = " · ".join(filtros_ativos)
        resumo_filtros.visible = bool(filtros_ativos) and not linha_controles.visible

    # ======================================================
    # LAYOUT
    # ======================================================

    linha_controles = ft.Row(
        visible=False,
        wrap=True,
        spacing=18,
        run_spacing=18,
        controls=[
            dropdown_semestre,
            dropdown_curso,
            dropdown_eixo,
            botao_filtrar,
            botao_limpar,
        ],
    )
    icone_filtros = ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, size=20)

    def alternar_filtros(e=None):
        linha_controles.visible = not linha_controles.visible
        atualizar_resumo_filtros()
        icone_filtros.name = (
            ft.Icons.KEYBOARD_ARROW_DOWN
            if linha_controles.visible
            else ft.Icons.KEYBOARD_ARROW_RIGHT
        )
        page.update()

    secao_filtros = ft.Container(
        bgcolor=None if embutido else layout.cores[CARD],
        padding=0 if embutido else ft.Padding.symmetric(horizontal=16, vertical=8),
        border_radius=0 if embutido else 8,
        border=None if embutido else borda_container,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Container(
                    on_click=alternar_filtros,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.FILTER_ALT, size=18),
                                    ft.Text("Filtros", weight="w500"),
                                ],
                            ),
                            icone_filtros,
                        ],
                    ),
                ),
                linha_controles,
                resumo_filtros,
            ],
        ),
    )
    secao_filtros.limpar_filtros = lambda: limpar_filtros()
    return secao_filtros
