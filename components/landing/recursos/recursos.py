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
                descricao="Organize perguntas e respostas por curso, semestre e eixo avaliativo.",
                cor_destaque=ROXO_CLARO,
                tag="AVALIAÇÕES",
                acao_texto="Simular uma avaliação →",
                on_acao=lambda e: abrir_modal_simulacao(page, mudar_tela) if page else None,
                scroll_key="recursos-avaliacoes",
            ),

            # Card 2: Indicadores (Abre a página dedicada com 3 eixos e 5 critérios)
            criar_card_responsivo(
                titulo="Indicadores por eixo",
                descricao="Consulte os indicadores e critérios usados na avaliação, organizados por eixo.",
                cor_destaque=CIANO,
                tag="INDICADORES",
                acao_texto="Ver página de indicadores →",
                on_acao=lambda e: mudar_tela("/indicadores") if mudar_tela else None,
                scroll_key="indicadores-card",
            ),

            # Card 3: Sobre (Conhecer o projeto)
            criar_card_responsivo(
                titulo="Resultados e exportação",
                descricao="Acompanhe resultados no dashboard e exporte relatórios em PDF ou dados em CSV.",
                cor_destaque=ROSA,
                tag="INSTITUCIONAL",
                acao_texto="Entender o fluxo ↓",
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
