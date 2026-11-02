import flet as ft
from utils.services.relatorio.relatorio_service import obter_resumo_eixos

# Importação dos componentes visuais isolados
from .dashboard_cards import criar_card_eixo

def TelaResultados(page: ft.Page) -> ft.Container:
    """Renderiza a interface principal do dashboard de resultados."""

    # ======================================================
    # ÁREA DOS CARDS
    # ======================================================
    cards_resultados = ft.Column(
        spacing=15,
    )
    contexto_resultados = ft.Text(size=12, color=ft.Colors.GREY_500)
    indicadores_resumo = ft.Row(wrap=True, spacing=12, run_spacing=10)

    # ======================================================
    # ATUALIZA DASHBOARD (CONTROLLER LOGIC)
    # ======================================================
    def atualizar_dashboard(
        semestre: str | None = None,
        curso_nome: str | None = None,
        eixo: int | None = None,
    ) -> None:
        resumo = obter_resumo_eixos(
            semestre=semestre,
            curso_nome=curso_nome,
            eixo=eixo,
        )
        rotulo_curso = curso_nome or "Todos os cursos"
        rotulo_semestre = semestre or "Todos os semestres"
        rotulo_eixo = (
            {1: "Organização Didático-Pedagógica", 2: "Corpo Docente e Tutorial", 3: "Infraestrutura"}.get(eixo, "Eixos")
            if eixo is not None
            else "Todos os eixos"
        )
        contexto_resultados.value = f"{rotulo_curso} · {rotulo_semestre} · {rotulo_eixo}"
        media_geral = resumo["media_geral"]
        valores_resumo = [
            ("Avaliações", str(resumo["avaliacoes"])),
            ("Respostas válidas", str(resumo["respostas"])),
            ("Média geral", f"{media_geral:.1f} / 5,0" if media_geral is not None else "—"),
        ]
        indicadores_resumo.controls = [
            ft.Container(
                expand=True,
                padding=12,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.ON_SURFACE),
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(rotulo, size=11, color=ft.Colors.GREY_500),
                        ft.Text(valor, size=18, weight=ft.FontWeight.BOLD),
                    ],
                ),
            )
            for rotulo, valor in valores_resumo
        ]
        cards_resultados.controls.clear()

        if resumo["avaliacoes"] == 0:
            cards_resultados.controls.append(
                ft.Container(
                    padding=24,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.FILTER_ALT_OFF, size=28, color=ft.Colors.GREY_500),
                            ft.Text("Nenhuma avaliação encontrada", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Ajuste os filtros ou limpe a seleção para ver os resultados.", color=ft.Colors.GREY_500),
                            ft.OutlinedButton(
                                "Limpar filtros",
                                icon=ft.Icons.CLEAR,
                                on_click=lambda e: getattr(dashboard, "limpar_filtros", lambda: None)(),
                            ),
                        ],
                    ),
                )
            )
        else:
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

        page.update()

    # ======================================================
    # CABEÇALHO E CONTAINER PRINCIPAL
    # ======================================================
    cabecalho = ft.Column(
        spacing=5,
        controls=[
            ft.Text("Dashboard de Resultados", size=25, weight="bold"),
            ft.Text(
                "Acompanhe o desempenho institucional através dos eixos avaliados.",
                size=14,
                color=ft.Colors.GREY,
            ),
        ],
    )

    dashboard = ft.Container(
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                cabecalho,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                contexto_resultados,
                indicadores_resumo,
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
