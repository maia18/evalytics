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
from components.landing.helpers.modal_simulacao import abrir_modal_simulacao

def criar_secao_recursos(
    page: ft.Page = None,
    mudar_tela: Optional[Callable[[str], None]] = None,
    ir_para_sobre: Optional[Callable] = None,
) -> ft.Container:
    """
    Constrói a seção de benefícios em grade com 3 cards de mesmo tamanho e botões de ação:
    1. Avaliações por eixo (Roxo, com simulação interativa de avaliação)
    2. Indicadores normativos (Ciano, 3 eixos e 5 critérios de pontuação)
    3. Sobre a plataforma (Rosa, com ação de rolagem até a seção Sobre)
    """

    cards = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
        run_spacing=16,
        controls=[
            # Card 1: Avaliações (com ação de Simular Avaliação)
            criar_card_responsivo(
                titulo="Avaliações por eixo",
                descricao="Organize perguntas e respostas da avaliação institucional estruturadas por curso, semestre e eixo avaliativo.",
                cor_destaque=ROXO_CLARO,
                tag="AVALIAÇÕES",
                acao_texto="Simular uma avaliação →",
                on_acao=lambda e: abrir_modal_simulacao(page, mudar_tela) if page else None,
                scroll_key="recursos-avaliacoes",
            ),

            # Card 2: Indicadores (Abre a página dedicada com 3 eixos e 5 critérios)
            criar_card_responsivo(
                titulo="Indicadores normativos",
                descricao="Explore os 58 indicadores oficiais do SINAES/MEC, organizados em 3 eixos com 5 critérios de pontuação (1 a 5).",
                cor_destaque=CIANO,
                tag="INDICADORES",
                acao_texto="Ver página de indicadores →",
                on_acao=lambda e: mudar_tela("/indicadores") if mudar_tela else None,
                scroll_key="indicadores-card",
            ),

            # Card 3: Sobre (Conhecer o projeto)
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
