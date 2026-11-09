import asyncio
import flet as ft
from utils.services.relatorio.relatorio_service import obter_resumo_eixos

# Importação dos componentes visuais isolados
from models.dashboard.widgets.dashboard_resultado_card import criar_card_eixo

def TelaResultados(page: ft.Page) -> ft.Container:
    """Renderiza a interface principal do dashboard de resultados."""

    # ======================================================
    # ÁREA DOS CARDS
    # ======================================================
    cards_resultados = ft.Column(
        spacing=15,
    )
    resumo_resultados = ft.Text(size=12, color=ft.Colors.GREY_500)
    estado_vazio = ft.Row(
        visible=False,
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ft.Colors.GREY_500),
            ft.Text("Nenhuma avaliação encontrada para estes filtros."),
            ft.OutlinedButton(
                "Limpar filtros",
                icon=ft.Icons.CLEAR,
                on_click=lambda e: getattr(dashboard, "limpar_filtros", lambda: None)(),
            ),
        ],
    )
    versao_consulta = {"atual": 0}

    # ======================================================
    # ATUALIZA DASHBOARD (CONTROLLER LOGIC)
    # ======================================================
    async def _carregar_dashboard(
        semestre: str | None = None,
        curso_nome: str | None = None,
        eixo: int | None = None,
        versao: int = 0,
    ) -> None:
        resumo = await asyncio.to_thread(
            obter_resumo_eixos,
            semestre=semestre,
            curso_nome=curso_nome,
            eixo=eixo,
        )
        if getattr(page, "rota_navegacao_atual", None) != "/dashboard/resultados":
            return
        if versao != versao_consulta["atual"]:
            return
        media_geral = resumo["media_geral"]
        rotulo_media = f"{media_geral:.1f} / 5,0" if media_geral is not None else "—"
        resumo_resultados.value = (
            f"{resumo['avaliacoes']} avaliações · "
            f"{resumo['respostas']} respostas válidas · "
            f"Média geral {rotulo_media}"
        )
        estado_vazio.visible = resumo["avaliacoes"] == 0
        cards_resultados.controls.clear()
        eixos_exibidos = (eixo,) if eixo is not None else (1, 2, 3)
        for eixo_id in eixos_exibidos:
            dados_eixo = resumo["eixos"].get(eixo_id, {})
            cards_resultados.controls.append(
                criar_card_eixo(
                    eixo_id,
                    dados_eixo.get("media"),
                    dados_eixo.get("respostas", 0),
                )
            )

        # Durante a montagem inicial, a view ainda não foi anexada à página;
        # o Navigator fará a primeira atualização ao concluir a navegação.
        page.update()

    def atualizar_dashboard(
        semestre: str | None = None,
        curso_nome: str | None = None,
        eixo: int | None = None,
    ) -> None:
        versao_consulta["atual"] += 1
        page.run_task(
            _carregar_dashboard,
            semestre,
            curso_nome,
            eixo,
            versao_consulta["atual"],
        )

    # O título e a descrição são exibidos pelo cabeçalho da tela responsiva.
    dashboard = ft.Container(
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                estado_vazio,
                resumo_resultados,
                cards_resultados,
            ],
        ),
    )

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================
    atualizar_dashboard()
    
    # Permite que um orquestrador pai atualize o dashboard externamente
    dashboard.atualizar = atualizar_dashboard

    return dashboard
