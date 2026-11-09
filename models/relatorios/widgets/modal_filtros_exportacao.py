from collections.abc import Callable
import inspect

import flet as ft

from utils.services.relatorio.relatorio_utils import filtrar_resultados, obter_semestre


NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}


def abrir_modal_filtros_exportacao(
    page: ft.Page,
    resultados: list[dict],
    ao_exportar: Callable[[list[dict], str, int | None], None],
    titulo: str,
    texto_botao: str,
    icone: str,
    cor: str,
) -> None:
    """Abre a seleção comum de curso, semestre e eixo para as exportações."""
    if not resultados:
        if inspect.iscoroutinefunction(ao_exportar):
            page.run_task(ao_exportar, [], "Todos", None)
        else:
            ao_exportar([], "Todos", None)
        return

    cursos_disponiveis = sorted(
        {
            str(resultado.get("curso_nome") or resultado.get("curso") or "").strip()
            for resultado in resultados
            if str(resultado.get("curso_nome") or resultado.get("curso") or "").strip()
        },
        key=str.casefold,
    )
    semestres_disponiveis = sorted(
        {
            resultado.get("semestre")
            or obter_semestre(resultado.get("data_avaliacao"))
            for resultado in resultados
            if resultado.get("semestre")
            or obter_semestre(resultado.get("data_avaliacao"))
        },
        reverse=True,
    )

    dropdown_curso = ft.Dropdown(
        label="Curso",
        value="TODOS",
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=curso, text=curso)
                for curso in cursos_disponiveis
            ],
        ],
        autofocus=True,
    )
    dropdown_semestre = ft.Dropdown(
        label="Semestre",
        value="TODOS",
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=semestre, text=semestre)
                for semestre in semestres_disponiveis
            ],
        ],
    )
    dropdown_eixo = ft.Dropdown(
        label="Eixo avaliativo",
        value="TODOS",
        options=[
            ft.dropdown.Option(key="TODOS", text="Todos"),
            *[
                ft.dropdown.Option(key=str(eixo_id), text=nome)
                for eixo_id, nome in NOMES_EIXOS.items()
            ],
        ],
    )

    def fechar_modal() -> None:
        modal.open = False
        page.update()

    async def confirmar_exportacao(e=None) -> None:
        semestre = (
            dropdown_semestre.value
            if dropdown_semestre.value != "TODOS"
            else None
        )
        curso = (
            dropdown_curso.value
            if dropdown_curso.value != "TODOS"
            else None
        )
        eixo = (
            int(dropdown_eixo.value)
            if dropdown_eixo.value != "TODOS"
            else None
        )

        resultados_filtrados = filtrar_resultados(
            resultados,
            semestre=semestre,
            eixo=eixo,
            curso_nome=curso,
        )
        fechar_modal()
        resultado = ao_exportar(resultados_filtrados, semestre or "Todos", eixo)
        if inspect.isawaitable(resultado):
            await resultado

    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, size=20, weight="bold"),
        content=ft.Column(
            width=420,
            height=230,
            spacing=12,
            controls=[
                ft.Text("Escolha os dados que deseja incluir na exportação."),
                dropdown_curso,
                dropdown_semestre,
                dropdown_eixo,
            ],
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: fechar_modal()),
            ft.ElevatedButton(
                texto_botao,
                icon=icone,
                bgcolor=cor,
                color=ft.Colors.WHITE,
                on_click=confirmar_exportacao,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if modal not in page.overlay:
        page.overlay.append(modal)
    modal.open = True
    page.update()
