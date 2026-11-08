import asyncio
from typing import Callable
import flet as ft
from components.layout.search.search_data import (
    buscar_dados_internos,
    carregar_dados_internos_busca,
    corresponde_busca,
)
from components.core.constants.constants import (
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    SURFACE,
)
from components.core.router.rotas_cts import (
    ROTA_DASHBOARD, ROTA_DASHBOARD_AVALIACOES, ROTA_DASHBOARD_RESULTADOS,
    ROTA_DASHBOARD_VISAO_GERAL, ROTA_AVALIACOES, ROTA_FORMULARIO,
    ROTA_RELATORIOS_DADOS, ROTA_CONFIGURACOES, ROTA_CURSOS, ROTA_CONTA,
    ROTA_INICIO,
)

def criar_busca_sidebar(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
) -> ft.TextField:
    """Cria a barra da sidebar; os resultados aparecem em diálogo separado."""
    destinos = [
        ("Início", ft.Icons.HOME, ROTA_INICIO, None),
        ("Nova avaliação", ft.Icons.ADD_CIRCLE_OUTLINE, ROTA_FORMULARIO, None),
        ("Dashboard", ft.Icons.GRID_VIEW_OUTLINED, ROTA_DASHBOARD, None),
        ("Indicadores", ft.Icons.GRID_VIEW_ROUNDED, ROTA_DASHBOARD_VISAO_GERAL, None),
        ("Acompanhamento", ft.Icons.TABLE_ROWS_ROUNDED, ROTA_DASHBOARD_AVALIACOES, None),
        ("Resultados por eixo", ft.Icons.INSERT_CHART_OUTLINED, ROTA_DASHBOARD_RESULTADOS, None),
        ("Cursos", ft.Icons.MENU_BOOK_OUTLINED, ROTA_CURSOS, None),
        ("Relatórios", ft.Icons.PIE_CHART_OUTLINE, ROTA_RELATORIOS_DADOS, None),
        ("Dados e exportação", ft.Icons.TABLE_VIEW, ROTA_RELATORIOS_DADOS, None),
        ("Configurações", ft.Icons.SETTINGS_OUTLINED, ROTA_CONFIGURACOES, None),
        ("Ajuda e suporte", ft.Icons.HELP_OUTLINE, "__ajuda__", None),
        ("Perfil", ft.Icons.PERSON_OUTLINE, ROTA_CONTA, "Perfil"),
        ("Atividade recente", ft.Icons.HISTORY, ROTA_CONTA, "Atividade recente"),
        ("Preferências", ft.Icons.TUNE_OUTLINED, ROTA_CONTA, "Preferências"),
        ("Segurança", ft.Icons.SECURITY_OUTLINED, ROTA_CONTA, "Segurança"),
        ("Notificações", ft.Icons.NOTIFICATIONS_OUTLINED, ROTA_CONTA, "Notificações"),
        ("Sobre o Evalytics", ft.Icons.INFO_OUTLINE, ROTA_CONTA, "Sobre o Evalytics"),
    ]
    resultados = ft.Column(spacing=2, expand=True, scroll=ft.ScrollMode.AUTO)
    titulo_resultados = ft.Text(
        "Digite um termo para consultar páginas e dados internos.",
        size=11,
        color=cores[TEXTO_SECUNDARIO],
    )
    conteudo_dialogo = ft.Container(
        width=620,
        height=120,
        content=ft.Column(
            spacing=10,
            controls=[titulo_resultados, ft.Divider(height=1), resultados],
        ),
    )
    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text("Busca global", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=conteudo_dialogo,
        actions=[ft.TextButton("Fechar", on_click=lambda e: page.pop_dialog())],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    estado = {"versao": 0}

    def abrir_destino(
        rota: str,
        secao: str | None = None,
        termo_curso: str | None = None,
        termo_avaliacao: str | None = None,
    ) -> None:
        page.pop_dialog()
        if rota == "__ajuda__":
            from components.layout.topbar.core.account_menu import abrir_ajuda

            abrir_ajuda(page, cores, mudar_tela)
            return
        if termo_curso:
            page._busca_cursos_inicial = termo_curso
        if termo_avaliacao:
            page._busca_avaliacoes_termo = termo_avaliacao
        if secao:
            page._conta_secao_ativa = secao
        mudar_tela(rota)

    def criar_resultado(
        titulo: str,
        detalhe: str,
        icone: str,
        rota: str,
        secao: str | None = None,
        termo_curso: str | None = None,
        termo_avaliacao: str | None = None,
    ) -> ft.Control:
        return ft.Container(
            height=54,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=8,
            ink=True,
            tooltip=f"{titulo} — {detalhe}",
            on_click=lambda e: abrir_destino(rota, secao, termo_curso, termo_avaliacao),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(icone, size=18, color=cores[TEXTO_PRINCIPAL]),
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(titulo, size=12, weight=ft.FontWeight.W_600,
                                    color=cores[TEXTO_PRINCIPAL], max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(detalhe, size=10, color=cores[TEXTO_PRINCIPAL],
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD, size=12,
                            color=cores[TEXTO_PRINCIPAL]),
                ],
            ),
        )

    async def executar_busca(consulta: str, versao: int) -> None:
        if not consulta:
            return
        resultados.controls = [ft.Text("Buscando páginas e informações…", size=11)]
        page.update()

        tarefa_cache = getattr(page, "_busca_global_cache_task", None)
        if tarefa_cache is None:
            tarefa_cache = asyncio.create_task(
                asyncio.to_thread(carregar_dados_internos_busca)
            )
            page._busca_global_cache_task = tarefa_cache
        try:
            dados_internos = await tarefa_cache
        except Exception:
            page._busca_global_cache_task = None
            dados_internos = {"cursos": [], "avaliacoes": [], "indicadores": []}
        if versao != estado["versao"]:
            return

        paginas = [
            destino for destino in destinos
            if corresponde_busca(destino[0], consulta.strip())
        ]
        informacoes = buscar_dados_internos(consulta.strip(), dados_internos)
        controles: list[ft.Control] = []
        if paginas:
            controles.append(ft.Text("PÁGINAS", size=10, weight=ft.FontWeight.W_700))
            controles.extend(
                criar_resultado(rotulo, "Abrir tela", icone, rota, secao)
                for rotulo, icone, rota, secao in paginas[:5]
            )
        for categoria in ("Cursos", "Avaliações"):
            grupo = [item for item in informacoes if item.get("categoria") == categoria]
            if not grupo:
                continue
            controles.append(ft.Text(categoria.upper(), size=10, weight=ft.FontWeight.W_700))
            controles.extend(
                criar_resultado(
                    item["titulo"], item["detalhe"], item["icone"], item["rota"],
                    termo_curso=item.get("termo_curso"),
                    termo_avaliacao=item.get("termo_avaliacao"),
                )
                for item in grupo[:8]
            )
        resultados.controls = controles or [
            ft.Container(
                padding=12,
                content=ft.Text(
                    "Nenhum resultado encontrado.",
                    size=11,
                    color=cores[TEXTO_SECUNDARIO],
                ),
            )
        ]
        conteudo_dialogo.height = min(470, max(120, 48 + len(resultados.controls) * 58))
        page.update()

    def submeter_busca(evento=None) -> None:
        consulta = (campo.value or "").strip()
        if not consulta:
            return
        # Guarda a consulta antes de limpar, para o campo já estar pronto
        # para uma nova pesquisa enquanto os resultados são carregados.
        campo.value = ""
        page.update()
        estado["versao"] += 1
        versao = estado["versao"]
        titulo_resultados.value = f'Resultados para “{consulta}”'
        resultados.controls = [ft.Text("Buscando páginas e informações…", size=11)]
        conteudo_dialogo.height = 120
        page.show_dialog(dialogo)
        page.run_task(executar_busca, consulta, versao)

    campo = ft.TextField(
        hint_text="Buscar",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        dense=True,
        border_radius=8,
        text_size=11,
        tooltip="Digite e pressione Enter para pesquisar",
        on_submit=submeter_busca,
    )
    return campo

