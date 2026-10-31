import flet as ft
from components.landing.palette import PAGE, MAX_CONTENT_WIDTH
from components.landing.recursos.card import criar_card_responsivo

def criar_secao_recursos(page: ft.Page = None) -> ft.Container:
    """
    Constrói a seção de benefícios (Recursos do Evalytics) em grade de 3 colunas.
    """

    cards = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
        run_spacing=12,
        controls=[
            criar_card_responsivo(
                titulo="Avaliações por eixo",
                descricao="Organize perguntas e respostas da avaliação institucional por eixo e curso.",
                scroll_key="recursos-avaliacoes",
            ),
            criar_card_responsivo(
                titulo="Resultados filtráveis",
                descricao="Consulte avaliações, respostas e médias com filtros de curso e semestre.",
                scroll_key="indicadores",
            ),
            criar_card_responsivo(
                titulo="PDF e CSV",
                descricao="Gere a cópia da avaliação em PDF e exporte os dados brutos em CSV.",
                scroll_key="relatorios",
            ),
        ],
    )

    return ft.Container(
        bgcolor=PAGE,
        padding=ft.Padding.only(left=24, right=24, bottom=64),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=cards,
        ),
    )
