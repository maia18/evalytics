import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    PAGE,
    ROXO_CLARO,
    CIANO,
    ROSA,
    MAX_CONTENT_WIDTH,
)
from components.landing.recursos.card import criar_card_responsivo

def criar_secao_recursos(
    page: ft.Page = None,
    mudar_tela: Optional[Callable[[str], None]] = None,
    ir_para_sobre: Optional[Callable] = None,
) -> ft.Container:
    """
    Constrói a seção de benefícios em grade de 3 colunas:
    1. Avaliações por eixo (Roxo)
    2. Indicadores institucionais (Ciano, com ação para abrir a página dedicada)
    3. Sobre a plataforma (Rosa, com ação de rolagem até a seção Sobre)
    """

    cards = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
        run_spacing=16,
        controls=[
            # Card 1: Avaliações
            criar_card_responsivo(
                titulo="Avaliações por eixo",
                descricao="Organize perguntas e respostas da avaliação institucional estruturadas por curso, semestre e eixo avaliativo.",
                cor_destaque=ROXO_CLARO,
                tag="AVALIAÇÕES",
                scroll_key="recursos-avaliacoes",
            ),

            # Card 2: Indicadores (Abre a página dedicada)
            criar_card_responsivo(
                titulo="Indicadores normativos",
                descricao="Explore os 24 indicadores oficiais do SINAES/MEC, organizados em 5 eixos com escala de pontuação de 1 a 5.",
                cor_destaque=CIANO,
                tag="INDICADORES",
                acao_texto="Ver página de indicadores →",
                on_acao=lambda e: mudar_tela("/indicadores") if mudar_tela else None,
                scroll_key="indicadores-card",
            ),

            # Card 3: Sobre (Substitui Relatórios)
            criar_card_responsivo(
                titulo="Sobre a plataforma",
                descricao="Desenvolvido para transformar o processo de autoavaliação institucional em um ciclo transparente de melhoria contínua.",
                cor_destaque=ROSA,
                tag="INSTITUCIONAL",
                acao_texto="Conhecer o Evalytics ↓",
                on_acao=ir_para_sobre,
                scroll_key="sobre-card",
            ),
        ],
    )

    return ft.Container(
        bgcolor=PAGE,
        padding=ft.Padding.only(left=24, right=24, bottom=48),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=cards,
        ),
    )
