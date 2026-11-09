import asyncio
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
    resultados_iniciais: list[dict] | None = None,
    carregando: bool = False,
) -> ft.Container:
    """Cria a tabela de resultados consolidados e orquestra a lógica de estado/filtros."""

    resultados_iniciais = (
        resultados_iniciais
        if resultados_iniciais is not None
        else listar_resultados_consolidados()
    )

    estado_tabela = ft.Text(
        "Carregando registros…" if carregando else "",
        size=12,
        color=layout.cores[TEXTO_PRINCIPAL],
        visible=carregando,
    )
    conteudo_tabela = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                estado_tabela,
                ft.Container(
                    expand=True,
                    visible=not carregando,
                    content=criar_estrutura_tabela(page, resultados_iniciais),
                ),
            ],
        ),
    )

    def definir_resultados(resultados: list[dict]) -> None:
        linha_tabela = conteudo_tabela.content.controls[1]
        linha_tabela.content = criar_estrutura_tabela(page, resultados)
        linha_tabela.visible = True
        estado_tabela.value = ""
        estado_tabela.visible = False
        botao_csv.disabled = False
        botao_pdf.disabled = False
        page.update()

    def definir_carregando(ativo: bool, mensagem: str = "Carregando registros…") -> None:
        estado_tabela.value = mensagem
        estado_tabela.visible = ativo
        conteudo_tabela.content.controls[1].visible = not ativo
        botao_csv.disabled = ativo
        botao_pdf.disabled = ativo
        page.update()

    versao_consulta = {"atual": 0}

    def atualizar_tabela(
        semestre: str | None = None,
        curso_nome: str | None = None,
        eixo: int | None = None,
    ) -> None:
        """Busca novos dados com base nos filtros e re-renderiza o componente visual interno."""
        versao_consulta["atual"] += 1
        versao = versao_consulta["atual"]
        rota_consulta = getattr(page, "rota_navegacao_atual", None)

        def consulta_ainda_ativa() -> bool:
            return (
                versao == versao_consulta["atual"]
                and getattr(page, "rota_navegacao_atual", None) == rota_consulta
            )

        async def buscar_resultados() -> None:
            try:
                resultados_filtrados = await asyncio.to_thread(
                    listar_resultados_consolidados,
                    semestre=semestre,
                    eixo=eixo,
                    curso_nome=curso_nome,
                    propagar_erro=True,
                )
                if not consulta_ainda_ativa():
                    return
                conteudo_tabela.content.controls[1].content = criar_estrutura_tabela(
                    page, resultados_filtrados
                )
                conteudo_tabela.content.controls[1].visible = True
                estado_tabela.value = ""
                estado_tabela.visible = False
                botao_csv.disabled = False
                botao_pdf.disabled = False
            except Exception:
                if not consulta_ainda_ativa():
                    return
                estado_tabela.value = "Falha ao consultar os resultados. Tente aplicar os filtros novamente."
                estado_tabela.visible = True
                conteudo_tabela.content.controls[1].visible = False
                botao_csv.disabled = True
                botao_pdf.disabled = True
            if consulta_ainda_ativa():
                page.update()

        definir_carregando(True, "Aplicando filtros…")
        page.run_task(buscar_resultados)

    # ======================================================
    # BOTÕES DE EXPORTAÇÃO
    # ======================================================
    botao_csv = ft.ElevatedButton(
        "Exportar CSV",
        icon=ft.Icons.TABLE_VIEW,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        on_click=ao_exportar_csv,
        disabled=carregando,
    )

    botao_pdf = ft.ElevatedButton(
        "Exportar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
        on_click=ao_exportar_pdf,
        disabled=carregando,
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
    tabela_resultados = ft.Container(
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
    # Os callbacks precisam estar no controle externo retornado pela fábrica,
    # pois é esse card que a tela de relatórios guarda e atualiza.
    tabela_resultados.definir_resultados = definir_resultados
    tabela_resultados.definir_carregando = definir_carregando
    tabela_resultados.atualizar = atualizar_tabela
    return tabela_resultados
