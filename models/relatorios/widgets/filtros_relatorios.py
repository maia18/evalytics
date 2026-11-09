import flet as ft
from components.core.constants.constants import CARD, TEXTO_SECUNDARIO
from utils.services.relatorio.relatorio_utils import obter_semestre

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
    compacto: bool = False,
) -> ft.Container:
    """
    Cria filtros a partir do mesmo conjunto de resultados exibido na tabela.
    """

    # ======================================================
    # SEMESTRES REAIS
    # ======================================================

    resultados = resultados or []
    def opcoes_semestres(resultados_atuais: list[dict]) -> list[str]:
        valores = set()
        for resultado in resultados_atuais:
            semestre = resultado.get("semestre") or obter_semestre(
                resultado.get("data_avaliacao")
            )
            if semestre:
                valores.add(str(semestre))
        return sorted(valores, reverse=True)

    semestres = opcoes_semestres(resultados)

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
        width=260 if compacto else 240,
        height=60 if compacto else None,
        dense=True,
        label_style=ft.TextStyle(size=11) if compacto else None,
    )

    cursos = sorted(
        {
            str(resultado.get("curso_nome") or "").strip()
            for resultado in resultados
            if str(resultado.get("curso_nome") or "").strip()
        },
        key=str.casefold,
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
        width=260 if compacto else 280,
        height=60 if compacto else None,
        dense=True,
        label_style=ft.TextStyle(size=11) if compacto else None,
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
        width=260 if compacto else 280,
        height=60 if compacto else None,
        dense=True,
        label_style=ft.TextStyle(size=11) if compacto else None,
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
        "Aplicar" if compacto else "Aplicar filtros",
        icon=ft.Icons.FILTER_ALT,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        on_click=aplicar_filtros,
        width=120 if compacto else None,
        height=38 if compacto else None,
    )

    botao_limpar = ft.OutlinedButton(
        "Limpar",
        icon=ft.Icons.CLEAR,
        on_click=limpar_filtros,
        width=120 if compacto else None,
        height=38 if compacto else None,
    )

    resumo_filtros = ft.Text(
        "",
        visible=False,
        size=12,
        color=layout.cores[TEXTO_SECUNDARIO],
    )
    estado_filtros_abertos = {"value": compacto}

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
        resumo_filtros.visible = bool(filtros_ativos) and not estado_filtros_abertos["value"]

    # ======================================================
    # LAYOUT
    # ======================================================

    campos_e_acoes = [
        dropdown_semestre,
        dropdown_curso,
        dropdown_eixo,
        botao_filtrar,
        botao_limpar,
    ]
    linha_controles = None if compacto else ft.Row(
        visible=False,
        wrap=True,
        spacing=18,
        run_spacing=18,
        controls=campos_e_acoes,
    )
    rotulo_filtros = ft.Text(
        "Filtros",
        weight="w500",
        visible=True,
    )

    def alternar_filtros(e=None):
        estado_filtros_abertos["value"] = not estado_filtros_abertos["value"]
        aberto = estado_filtros_abertos["value"]
        rotulo_filtros.visible = not aberto
        if compacto:
            for controle in campos_e_acoes:
                controle.visible = aberto
        else:
            linha_controles.visible = aberto
        atualizar_resumo_filtros()
        page.update()

    if compacto:
        for controle in campos_e_acoes:
            controle.visible = True
        controles_filtros = ft.Row(
            spacing=8,
            run_spacing=8,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=campos_e_acoes,
        )
    else:
        controles_filtros = ft.Column(
            spacing=15,
            controls=[
                ft.Container(
                    on_click=alternar_filtros,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.FILTER_ALT, size=18),
                            ft.Text("Filtros", weight="w500"),
                        ],
                    ),
                ),
                linha_controles,
                resumo_filtros,
            ],
        )

    secao_filtros = ft.Container(
        width=float("inf") if compacto else None,
        bgcolor=None if embutido or compacto else layout.cores[CARD],
        padding=(
            ft.Padding.symmetric(horizontal=0, vertical=8)
            if compacto and not embutido
            else 0
            if embutido
            else ft.Padding.symmetric(horizontal=16, vertical=8)
        ),
        border_radius=0 if embutido else 8,
        border=None if embutido else borda_container,
        content=controles_filtros,
    )
    secao_filtros.limpar_filtros = lambda: limpar_filtros()

    def atualizar_opcoes(resultados_atuais: list[dict]) -> None:
        dropdown_semestre.options = [
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=semestre, text=semestre)
                for semestre in opcoes_semestres(resultados_atuais)
            ],
        ]
        cursos_atuais = sorted(
            {
                str(resultado.get("curso_nome") or "").strip()
                for resultado in resultados_atuais
                if str(resultado.get("curso_nome") or "").strip()
            },
            key=str.casefold,
        )
        dropdown_curso.options = [
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=curso, text=curso)
                for curso in cursos_atuais
            ],
        ]
        dropdown_semestre.value = "TODOS"
        dropdown_curso.value = "TODOS"
        atualizar_resumo_filtros()

    secao_filtros.atualizar_opcoes = atualizar_opcoes
    return secao_filtros
