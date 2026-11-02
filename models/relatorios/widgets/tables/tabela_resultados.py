import flet as ft
from components.core.constants.constants import CARD, TEXTO_PRINCIPAL
from utils.services.relatorio.relatorio_service import listar_resultados_consolidados

# Importa a estrutura puramente visual separada
from .tabela_ui import criar_estrutura_tabela

def criar_tabela_resultados(
    page: ft.Page,
    layout,
    borda_container: ft.Border,
    ao_exportar_csv,
    ao_exportar_pdf,
    secao_filtros: ft.Control | None = None,
) -> ft.Container:
    """Cria a tabela de resultados consolidados e orquestra a lógica de estado/filtros."""

    resultados_iniciais = listar_resultados_consolidados()

    conteudo_tabela = ft.Container(
        expand=True,
        content=ft.Row(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[criar_estrutura_tabela(page, resultados_iniciais)],
        ),
    )

    def atualizar_tabela(
        semestre: str | None = None,
        curso_nome: str | None = None,
        eixo: int | None = None,
    ) -> None:
        """Busca novos dados com base nos filtros e re-renderiza o componente visual interno."""
        resultados_filtrados = listar_resultados_consolidados(
            semestre=semestre,
            eixo=eixo,
            curso_nome=curso_nome,
        )
        conteudo_tabela.content = ft.Row(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[criar_estrutura_tabela(page, resultados_filtrados)],
        )
        page.update()

    conteudo_tabela.atualizar = atualizar_tabela

    # ======================================================
    # BOTÕES DE EXPORTAÇÃO
    # ======================================================
    botao_csv = ft.ElevatedButton(
        "Exportar CSV",
        icon=ft.Icons.TABLE_VIEW,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        on_click=ao_exportar_csv,
    )

    botao_pdf = ft.ElevatedButton(
        "Exportar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
        on_click=ao_exportar_pdf,
    )

    # ======================================================
    # CABEÇALHO DOS RESULTADOS
    # ======================================================
    cabecalho = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=[
            ft.Text(
                "Resultados Consolidados",
                size=18,
                weight="bold",
                color=layout.cores[TEXTO_PRINCIPAL],
            ),
            ft.Row(
                spacing=10,
                controls=[botao_pdf, botao_csv],
            ),
        ],
    )

    # ======================================================
    # CONTAINER FINAL
    # ======================================================
    return ft.Container(
        expand=True,
        bgcolor=layout.cores[CARD],
        padding=25,
        border=borda_container,
        border_radius=10,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                cabecalho,
                ft.Container(height=10),
                secao_filtros if secao_filtros is not None else ft.Container(),
                ft.Container(height=14),
                conteudo_tabela,
            ],
        ),
    )
